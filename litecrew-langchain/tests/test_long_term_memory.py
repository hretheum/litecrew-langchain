"""
Tests for long-term memory implementation.
"""

import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from litecrew.memory.long_term import LongTermMemory, MemoryItem


class TestLongTermMemory:
    """Test long-term memory functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test database."""
        with TemporaryDirectory() as td:
            yield Path(td)
    
    @pytest.fixture
    def memory(self, temp_dir):
        """Create LongTermMemory instance."""
        return LongTermMemory(
            db_path=temp_dir / "test_memory.db",
            max_items=100,
            importance_threshold=0.1,
            decay_rate=0.95
        )
    
    def test_memory_creation_and_retrieval(self, memory):
        """Test basic memory creation and retrieval."""
        # Add memory
        item = memory.add(
            content="The AI framework benchmark showed LangChain is 408x faster than CrewAI",
            importance=0.8,
            metadata={"category": "benchmark", "source": "test"}
        )
        
        assert item.id
        assert item.content
        assert item.importance == 0.8
        assert item.metadata["category"] == "benchmark"
        
        # Test search
        results = memory.search("benchmark", top_k=1)
        assert len(results) == 1
        assert results[0].id == item.id
        assert results[0].access_count == 1  # Boosted by search
    
    def test_memory_search_performance(self, memory):
        """Test memory search performance meets requirements."""
        # Add 1000 memories
        for i in range(1000):
            memory.add(
                content=f"Memory item {i} with various content about topic {i % 10}",
                importance=0.5 + (i % 5) * 0.1
            )
        
        # Test search performance
        start_time = time.perf_counter()
        results = memory.search("topic 5", top_k=10)
        search_time = (time.perf_counter() - start_time) * 1000  # ms
        
        assert search_time < 50  # Should be <50ms
        assert len(results) <= 10
        print(f"Search time for 1000 items: {search_time:.2f}ms")
    
    def test_memory_importance_decay(self, memory):
        """Test importance decay over time."""
        # Add memory with high importance
        item = memory.add("Important information", importance=0.9)
        initial_importance = item.importance
        
        # Simulate time passing (1 day)
        item.last_accessed = time.time() - 86400
        item.decay_importance(decay_rate=0.95)
        
        assert item.importance < initial_importance
        assert item.importance == pytest.approx(0.9 * 0.95, rel=0.01)
    
    def test_memory_compression(self, memory):
        """Test memory compression and storage efficiency."""
        # Add memories with varying importance
        for i in range(50):
            memory.add(
                content=f"Memory {i}",
                importance=0.05 if i < 25 else 0.5  # Half below threshold
            )
        
        # Apply decay to push some below threshold
        for item in memory._memory_index.values():
            if item.importance < 0.2:
                item.importance = 0.05
        
        # Compress
        stats = memory.compress()
        
        assert stats["removed_count"] > 0
        assert stats["compression_ratio"] > 0
        assert len(memory._memory_index) < stats["initial_count"]
        
        # Verify storage efficiency
        remaining = list(memory._memory_index.values())
        assert all(m.importance >= memory.importance_threshold for m in remaining)
    
    def test_storage_efficiency(self, memory):
        """Test storage efficiency meets >80% requirement."""
        # Add 100 diverse memories
        for i in range(100):
            memory.add(
                content=f"This is memory item {i} with some longer content to test storage. " * 5,
                importance=0.5,
                metadata={"index": i, "category": f"cat_{i % 5}"}
            )
        
        stats = memory.get_stats()
        
        # Check that storage is efficient
        # Rough estimate: 100 items * ~300 bytes each = 30KB raw
        # With indexes and metadata, should be under 60KB
        assert stats["storage_size_kb"] < 60
        assert stats["total_memories"] == 100
        
        print(f"Storage size for 100 items: {stats['storage_size_kb']:.2f}KB")
    
    def test_relevance_accuracy(self, memory):
        """Test relevance accuracy meets >85% requirement."""
        # Add diverse memories
        topics = ["AI", "benchmark", "performance", "memory", "testing"]
        for topic in topics:
            for i in range(10):
                memory.add(
                    content=f"{topic}: Example content {i} about {topic} with details",
                    importance=0.6,
                    metadata={"topic": topic}
                )
        
        # Test relevance for each topic
        correct_retrievals = 0
        total_retrievals = 0
        
        for topic in topics:
            results = memory.search(topic, top_k=5)
            for result in results:
                total_retrievals += 1
                if topic.lower() in result.content.lower():
                    correct_retrievals += 1
        
        accuracy = correct_retrievals / total_retrievals if total_retrievals > 0 else 0
        assert accuracy > 0.85  # >85% accuracy requirement
        
        print(f"Relevance accuracy: {accuracy * 100:.1f}%")
    
    def test_time_range_queries(self, memory):
        """Test querying memories by time range."""
        # Add memories at different times
        now = time.time()
        
        # Add old memory
        old_item = memory.add("Old memory", importance=0.7)
        memory.conn.execute(
            "UPDATE memories SET timestamp = ? WHERE id = ?",
            (now - 86400 * 2, old_item.id)  # 2 days ago
        )
        
        # Add recent memories
        for i in range(5):
            memory.add(f"Recent memory {i}", importance=0.6)
        
        # Query last 24 hours
        recent = memory.get_by_timerange(
            start_time=now - 86400,
            end_time=now
        )
        
        assert len(recent) == 5
        assert all("Recent" in m.content for m in recent)
    
    def test_memory_persistence(self, temp_dir):
        """Test memory persistence across sessions."""
        db_path = temp_dir / "persist_test.db"
        
        # First session
        memory1 = LongTermMemory(db_path=db_path)
        memory1.add("Persistent memory 1", importance=0.8)
        memory1.add("Persistent memory 2", importance=0.7)
        memory1.close()
        
        # Second session
        memory2 = LongTermMemory(db_path=db_path)
        
        # Check memories are loaded
        assert len(memory2._memory_index) == 2
        results = memory2.search("Persistent", top_k=2)
        assert len(results) == 2
        
        memory2.close()
    
    def test_concurrent_access_safety(self, memory):
        """Test thread safety for concurrent access."""
        import threading
        
        def add_memories(thread_id):
            for i in range(10):
                memory.add(
                    f"Thread {thread_id} memory {i}",
                    importance=0.5
                )
        
        # Create threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_memories, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify all memories were added
        assert len(memory._memory_index) == 50
    
    def test_metadata_filtering(self, memory):
        """Test filtering by metadata."""
        # Add memories with metadata
        memory.add("Task completed", importance=0.7, metadata={"type": "task", "status": "done"})
        memory.add("Agent created", importance=0.6, metadata={"type": "agent", "name": "researcher"})
        memory.add("Error occurred", importance=0.9, metadata={"type": "error", "severity": "high"})
        
        # Search and filter by importance
        high_importance = memory.search("", top_k=10, min_importance=0.8)
        assert len(high_importance) == 1
        assert high_importance[0].metadata["type"] == "error"