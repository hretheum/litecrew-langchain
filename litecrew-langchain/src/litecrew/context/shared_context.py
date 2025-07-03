"""
Shared Context Store

Thread-safe shared context storage for LiteCrew agents and tasks.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from uuid import uuid4
import sys
import gzip
import pickle

from .context_config import ContextConfig


@dataclass
class ContextMetadata:
    """
    Metadata for context items.
    
    Tracks origin, timing, and usage information for context management.
    """
    
    item_id: str = field(default_factory=lambda: str(uuid4()))
    agent_role: Optional[str] = None
    task_description: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    priority: int = 1  # 1=low, 2=medium, 3=high
    compressed: bool = False
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if context item has expired."""
        if self.ttl_seconds is None:
            return False
        
        age_seconds = (datetime.now() - self.timestamp).total_seconds()
        return age_seconds > self.ttl_seconds
    
    def update_access(self):
        """Update access tracking."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class SharedContextStore:
    """
    Thread-safe shared context storage for crew members.
    
    Provides efficient storage, retrieval, and management of context data
    shared between agents and tasks in a crew.
    """
    
    def __init__(self, config: Optional[ContextConfig] = None):
        """
        Initialize shared context store.
        
        Args:
            config: Context configuration, uses defaults if None
        """
        self.config = config or ContextConfig()
        self.config.validate()
        
        # Thread-safe storage
        self._contexts: Dict[str, Any] = {}
        self._metadata: Dict[str, ContextMetadata] = {}
        self._agent_contexts: Dict[str, List[str]] = {}  # agent_role -> context_keys
        self._current_size = 0
        
        # Thread safety
        if self.config.thread_safe:
            self._lock = threading.RLock()
        else:
            self._lock = None
        
        # Cleanup tracking
        self._last_cleanup = time.time()
        
        # Metrics
        self._metrics = {
            'total_items': 0,
            'total_size_bytes': 0,
            'access_count': 0,
            'compression_count': 0,
            'cleanup_count': 0
        }
    
    def _acquire_lock(self):
        """Acquire lock if thread safety enabled."""
        if self._lock:
            self._lock.acquire()
    
    def _release_lock(self):
        """Release lock if thread safety enabled."""
        if self._lock:
            self._lock.release()
    
    def store_context(self, 
                     key: str, 
                     value: Any, 
                     metadata: Optional[ContextMetadata] = None) -> bool:
        """
        Store context item with metadata.
        
        Args:
            key: Unique context identifier
            value: Context data to store
            metadata: Optional metadata, creates default if None
            
        Returns:
            bool: True if stored successfully, False if rejected
        """
        self._acquire_lock()
        try:
            # Create metadata if not provided
            if metadata is None:
                metadata = ContextMetadata()
            
            # Calculate size
            try:
                if isinstance(value, str):
                    size_bytes = len(value.encode('utf-8'))
                else:
                    size_bytes = sys.getsizeof(value)
            except:
                size_bytes = sys.getsizeof(str(value))
            
            metadata.size_bytes = size_bytes
            
            # Check size limits
            if size_bytes > self.config.max_size_per_task:
                return False
            
            # Check if we need to make space
            if self._current_size + size_bytes > self.config.max_size_mb * 1024 * 1024:
                if not self._make_space(size_bytes):
                    return False
            
            # Store context and metadata
            self._contexts[key] = value
            self._metadata[key] = metadata
            self._current_size += size_bytes
            
            # Track by agent if specified
            if metadata.agent_role:
                if metadata.agent_role not in self._agent_contexts:
                    self._agent_contexts[metadata.agent_role] = []
                self._agent_contexts[metadata.agent_role].append(key)
                
                # Limit items per agent
                agent_keys = self._agent_contexts[metadata.agent_role]
                if len(agent_keys) > self.config.max_items_per_agent:
                    # Remove oldest items
                    to_remove = agent_keys[:-self.config.max_items_per_agent]
                    for old_key in to_remove:
                        self._remove_item(old_key)
            
            # Update metrics
            self._metrics['total_items'] += 1
            self._metrics['total_size_bytes'] = self._current_size
            
            # Periodic cleanup
            if (time.time() - self._last_cleanup) > self.config.cleanup_interval_seconds:
                self._cleanup_expired()
            
            return True
            
        finally:
            self._release_lock()
    
    def get_context(self, key: str) -> Tuple[Optional[Any], Optional[ContextMetadata]]:
        """
        Retrieve context item and its metadata.
        
        Args:
            key: Context identifier
            
        Returns:
            Tuple of (value, metadata) or (None, None) if not found
        """
        self._acquire_lock()
        try:
            if key not in self._contexts:
                return None, None
            
            metadata = self._metadata[key]
            
            # Check if expired
            if metadata.is_expired():
                self._remove_item(key)
                return None, None
            
            # Update access tracking
            metadata.update_access()
            self._metrics['access_count'] += 1
            
            return self._contexts[key], metadata
            
        finally:
            self._release_lock()
    
    def get_agent_context(self, 
                         agent_role: str, 
                         max_items: int = 5,
                         include_recent_only: bool = True) -> str:
        """
        Get formatted context for a specific agent.
        
        Args:
            agent_role: Agent role to get context for
            max_items: Maximum number of context items to include
            include_recent_only: Whether to prioritize recent items
            
        Returns:
            Formatted context string
        """
        self._acquire_lock()
        try:
            if agent_role not in self._agent_contexts:
                return ""
            
            agent_keys = self._agent_contexts[agent_role]
            if not agent_keys:
                return ""
            
            # Get valid contexts with metadata
            valid_contexts = []
            for key in agent_keys:
                value, metadata = self.get_context(key)
                if value is not None and metadata is not None:
                    valid_contexts.append((key, value, metadata))
            
            # Sort by timestamp if including recent only
            if include_recent_only:
                valid_contexts.sort(key=lambda x: x[2].timestamp, reverse=True)
            
            # Limit to max_items
            valid_contexts = valid_contexts[:max_items]
            
            # Format context
            context_parts = []
            for key, value, metadata in valid_contexts:
                timestamp_str = metadata.timestamp.strftime("%H:%M:%S")
                if metadata.task_description:
                    header = f"[{timestamp_str}] {metadata.task_description}:"
                else:
                    header = f"[{timestamp_str}] Context:"
                
                context_parts.append(f"{header}\n{str(value)}")
            
            return "\n\n".join(context_parts)
            
        finally:
            self._release_lock()
    
    def get_relevant_context(self, 
                           query: str, 
                           max_items: int = 5) -> str:
        """
        Get context relevant to a query string.
        
        Args:
            query: Query to find relevant context for
            max_items: Maximum number of items to return
            
        Returns:
            Formatted relevant context
        """
        self._acquire_lock()
        try:
            query_lower = query.lower()
            relevant_items = []
            
            for key, metadata in self._metadata.items():
                if metadata.is_expired():
                    continue
                
                value, _ = self.get_context(key)
                if value is None:
                    continue
                
                # Simple relevance scoring
                score = 0
                value_str = str(value).lower()
                
                # Check for query terms in context
                for term in query_lower.split():
                    if term in value_str:
                        score += 1
                
                # Boost recent items
                age_minutes = (datetime.now() - metadata.timestamp).total_seconds() / 60
                if age_minutes < 10:
                    score += 2
                elif age_minutes < 60:
                    score += 1
                
                # Boost high priority items
                score += metadata.priority
                
                if score > 0:
                    relevant_items.append((score, key, value, metadata))
            
            # Sort by relevance score
            relevant_items.sort(key=lambda x: x[0], reverse=True)
            
            # Format top items
            context_parts = []
            for score, key, value, metadata in relevant_items[:max_items]:
                timestamp_str = metadata.timestamp.strftime("%H:%M:%S")
                context_parts.append(f"[{timestamp_str}] {str(value)}")
            
            return "\n\n".join(context_parts)
            
        finally:
            self._release_lock()
    
    def _make_space(self, needed_bytes: int) -> bool:
        """
        Make space by removing old or low-priority items.
        
        Args:
            needed_bytes: Bytes needed to be freed
            
        Returns:
            bool: True if enough space was made
        """
        # Get all items sorted by priority and age
        items_to_consider = []
        for key, metadata in self._metadata.items():
            # Priority: expired items first, then by priority and age
            if metadata.is_expired():
                priority = 0  # Remove expired first
            else:
                age_minutes = (datetime.now() - metadata.timestamp).total_seconds() / 60
                priority = metadata.priority * 1000 - age_minutes  # Higher priority and recent = higher score
            
            items_to_consider.append((priority, key, metadata.size_bytes))
        
        # Sort by priority (lower = remove first)
        items_to_consider.sort(key=lambda x: x[0])
        
        freed_bytes = 0
        for priority, key, size_bytes in items_to_consider:
            if freed_bytes >= needed_bytes:
                break
            
            self._remove_item(key)
            freed_bytes += size_bytes
        
        return freed_bytes >= needed_bytes
    
    def _remove_item(self, key: str):
        """Remove item from store."""
        if key in self._contexts:
            # Update size tracking
            metadata = self._metadata.get(key)
            if metadata:
                self._current_size -= metadata.size_bytes
            
            # Remove from storage
            del self._contexts[key]
            del self._metadata[key]
            
            # Remove from agent tracking
            if metadata and metadata.agent_role:
                agent_keys = self._agent_contexts.get(metadata.agent_role, [])
                if key in agent_keys:
                    agent_keys.remove(key)
            
            # Update metrics
            self._metrics['total_items'] -= 1
            self._metrics['total_size_bytes'] = self._current_size
    
    def _cleanup_expired(self):
        """Remove expired context items."""
        self._last_cleanup = time.time()
        
        expired_keys = []
        for key, metadata in self._metadata.items():
            if metadata.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_item(key)
        
        if expired_keys:
            self._metrics['cleanup_count'] += 1
    
    def clear_agent_context(self, agent_role: str):
        """Clear all context for a specific agent."""
        self._acquire_lock()
        try:
            if agent_role in self._agent_contexts:
                keys_to_remove = self._agent_contexts[agent_role].copy()
                for key in keys_to_remove:
                    self._remove_item(key)
                del self._agent_contexts[agent_role]
        finally:
            self._release_lock()
    
    def clear_all(self):
        """Clear all context data."""
        self._acquire_lock()
        try:
            self._contexts.clear()
            self._metadata.clear()
            self._agent_contexts.clear()
            self._current_size = 0
            self._metrics = {
                'total_items': 0,
                'total_size_bytes': 0,
                'access_count': 0,
                'compression_count': 0,
                'cleanup_count': 0
            }
        finally:
            self._release_lock()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get context store metrics."""
        self._acquire_lock()
        try:
            return {
                **self._metrics,
                'current_size_mb': self._current_size / (1024 * 1024),
                'utilization_percent': (self._current_size / (self.config.max_size_mb * 1024 * 1024)) * 100,
                'agent_count': len(self._agent_contexts),
                'avg_item_size_bytes': self._current_size / max(1, self._metrics['total_items'])
            }
        finally:
            self._release_lock()
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information."""
        self._acquire_lock()
        try:
            return {
                'metrics': self.get_metrics(),
                'config': {
                    'max_size_mb': self.config.max_size_mb,
                    'max_size_per_task': self.config.max_size_per_task,
                    'ttl_seconds': self.config.ttl_seconds,
                    'compression_enabled': self.config.enable_compression
                },
                'agents': {
                    agent_role: len(keys) 
                    for agent_role, keys in self._agent_contexts.items()
                }
            }
        finally:
            self._release_lock()