"""
Long-term memory implementation with persistence and advanced features.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MemoryItem:
    """A single memory item with metadata."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    importance: float = 0.5  # 0-1 scale
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def decay_importance(self, decay_rate: float = 0.95) -> None:
        """Apply time-based decay to importance score."""
        time_elapsed = time.time() - self.last_accessed
        days_elapsed = time_elapsed / (24 * 3600)
        self.importance *= (decay_rate ** days_elapsed)
    
    def boost_importance(self, boost_factor: float = 1.1) -> None:
        """Boost importance when accessed."""
        self.importance = min(1.0, self.importance * boost_factor)
        self.access_count += 1
        self.last_accessed = time.time()


class LongTermMemory:
    """Persistent long-term memory with indexing and search capabilities."""
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        max_items: int = 10000,
        importance_threshold: float = 0.1,
        decay_rate: float = 0.95,
        compression_ratio: float = 0.8,
    ):
        """Initialize long-term memory.
        
        Args:
            db_path: Path to SQLite database
            max_items: Maximum number of items to store
            importance_threshold: Minimum importance to keep item
            decay_rate: Daily decay rate for importance
            compression_ratio: Target compression ratio for storage
        """
        self.db_path = db_path or Path("long_term_memory.db")
        self.max_items = max_items
        self.importance_threshold = importance_threshold
        self.decay_rate = decay_rate
        self.compression_ratio = compression_ratio
        
        # Initialize vectorizer for semantic search
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self._vectors = None
        self._memory_index = {}
        
        # Create database
        self._init_db()
        
        # Load existing memories
        self._load_memories()
    
    def _init_db(self) -> None:
        """Initialize SQLite database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                importance REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL NOT NULL,
                metadata TEXT,
                embedding TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp DESC)
        """)
        
        self.conn.commit()
    
    def _load_memories(self) -> None:
        """Load memories from database into index."""
        cursor = self.conn.execute("""
            SELECT * FROM memories 
            ORDER BY importance DESC
            LIMIT ?
        """, (self.max_items,))
        
        memories = []
        for row in cursor:
            memory = MemoryItem(
                id=row['id'],
                content=row['content'],
                timestamp=row['timestamp'],
                importance=row['importance'],
                access_count=row['access_count'],
                last_accessed=row['last_accessed'],
                metadata=json.loads(row['metadata'] or '{}'),
                embedding=json.loads(row['embedding'] or 'null')
            )
            self._memory_index[memory.id] = memory
            memories.append(memory)
        
        # Update vectorizer if we have memories
        if memories:
            contents = [m.content for m in memories]
            self._vectors = self.vectorizer.fit_transform(contents)
    
    def add(
        self,
        content: str,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryItem:
        """Add a new memory item.
        
        Args:
            content: Memory content
            importance: Initial importance score (0-1)
            metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        memory = MemoryItem(
            content=content,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Store in database
        self.conn.execute("""
            INSERT INTO memories (id, content, timestamp, importance, 
                                access_count, last_accessed, metadata, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.content,
            memory.timestamp,
            memory.importance,
            memory.access_count,
            memory.last_accessed,
            json.dumps(memory.metadata),
            json.dumps(memory.embedding)
        ))
        self.conn.commit()
        
        # Add to index
        self._memory_index[memory.id] = memory
        
        # Update vectors
        self._update_vectors()
        
        # Cleanup if needed
        if len(self._memory_index) > self.max_items:
            self._cleanup()
        
        return memory
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_importance: Optional[float] = None
    ) -> List[MemoryItem]:
        """Search memories using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_importance: Minimum importance threshold
            
        Returns:
            List of matching memories
        """
        if not self._memory_index:
            return []
        
        # Apply decay to all memories
        for memory in self._memory_index.values():
            memory.decay_importance(self.decay_rate)
        
        # Filter by importance if specified
        min_imp = min_importance or self.importance_threshold
        candidates = [
            m for m in self._memory_index.values()
            if m.importance >= min_imp
        ]
        
        if not candidates:
            return []
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Get candidate vectors
        candidate_contents = [m.content for m in candidates]
        candidate_vectors = self.vectorizer.transform(candidate_contents)
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, candidate_vectors)[0]
        
        # Sort by combined score (similarity * importance)
        scored_candidates = [
            (candidates[i], similarities[i] * candidates[i].importance)
            for i in range(len(candidates))
        ]
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results and boost their importance
        results = []
        for memory, score in scored_candidates[:top_k]:
            memory.boost_importance()
            self._update_memory_db(memory)
            results.append(memory)
        
        return results
    
    def get_by_timerange(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """Get memories within a time range.
        
        Args:
            start_time: Start timestamp (default: 24h ago)
            end_time: End timestamp (default: now)
            limit: Maximum number of results
            
        Returns:
            List of memories in time range
        """
        if start_time is None:
            start_time = time.time() - 86400  # 24 hours ago
        if end_time is None:
            end_time = time.time()
        
        cursor = self.conn.execute("""
            SELECT * FROM memories
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (start_time, end_time, limit))
        
        results = []
        for row in cursor:
            memory = self._row_to_memory(row)
            results.append(memory)
        
        return results
    
    def compress(self) -> Dict[str, Any]:
        """Compress memory by removing low-importance items.
        
        Returns:
            Compression statistics
        """
        initial_count = len(self._memory_index)
        
        # Apply decay
        for memory in self._memory_index.values():
            memory.decay_importance(self.decay_rate)
        
        # Find items below threshold
        to_remove = [
            m for m in self._memory_index.values()
            if m.importance < self.importance_threshold
        ]
        
        # Remove from database and index
        for memory in to_remove:
            self.conn.execute("DELETE FROM memories WHERE id = ?", (memory.id,))
            del self._memory_index[memory.id]
        
        self.conn.commit()
        
        # Update vectors
        self._update_vectors()
        
        final_count = len(self._memory_index)
        
        return {
            "initial_count": initial_count,
            "removed_count": len(to_remove),
            "final_count": final_count,
            "compression_ratio": 1 - (final_count / initial_count) if initial_count > 0 else 0
        }
    
    def _update_memory_db(self, memory: MemoryItem) -> None:
        """Update memory in database."""
        self.conn.execute("""
            UPDATE memories
            SET importance = ?, access_count = ?, last_accessed = ?
            WHERE id = ?
        """, (memory.importance, memory.access_count, memory.last_accessed, memory.id))
        self.conn.commit()
    
    def _update_vectors(self) -> None:
        """Update TF-IDF vectors for all memories."""
        if not self._memory_index:
            self._vectors = None
            return
        
        contents = [m.content for m in self._memory_index.values()]
        self._vectors = self.vectorizer.fit_transform(contents)
    
    def _cleanup(self) -> None:
        """Remove least important memories to stay under limit."""
        # Sort by importance
        sorted_memories = sorted(
            self._memory_index.values(),
            key=lambda m: m.importance,
            reverse=True
        )
        
        # Keep only top max_items
        to_keep = sorted_memories[:self.max_items]
        to_remove = sorted_memories[self.max_items:]
        
        # Remove from database
        for memory in to_remove:
            self.conn.execute("DELETE FROM memories WHERE id = ?", (memory.id,))
            del self._memory_index[memory.id]
        
        self.conn.commit()
        self._update_vectors()
    
    def _row_to_memory(self, row: sqlite3.Row) -> MemoryItem:
        """Convert database row to MemoryItem."""
        return MemoryItem(
            id=row['id'],
            content=row['content'],
            timestamp=row['timestamp'],
            importance=row['importance'],
            access_count=row['access_count'],
            last_accessed=row['last_accessed'],
            metadata=json.loads(row['metadata'] or '{}'),
            embedding=json.loads(row['embedding'] or 'null')
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self._memory_index:
            return {
                "total_memories": 0,
                "avg_importance": 0,
                "avg_access_count": 0,
                "storage_size_kb": 0
            }
        
        memories = list(self._memory_index.values())
        
        # Calculate storage size
        db_size = self.db_path.stat().st_size / 1024 if self.db_path.exists() else 0
        
        return {
            "total_memories": len(memories),
            "avg_importance": np.mean([m.importance for m in memories]),
            "avg_access_count": np.mean([m.access_count for m in memories]),
            "max_importance": max(m.importance for m in memories),
            "min_importance": min(m.importance for m in memories),
            "storage_size_kb": db_size,
            "compression_ratio": self.compression_ratio
        }
    
    def close(self) -> None:
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()