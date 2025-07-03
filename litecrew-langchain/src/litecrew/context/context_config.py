"""
Context Configuration

Configuration settings for context management system.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ContextCompressionType(Enum):
    """Available context compression types."""
    NONE = "none"
    TRUNCATE = "truncate"
    SLIDING_WINDOW = "sliding_window" 
    SMART_SUMMARY = "smart_summary"


@dataclass
class ContextConfig:
    """
    Configuration for context management system.
    
    Controls memory usage, compression, and persistence behavior.
    """
    
    # Memory limits
    max_size_mb: int = 10  # Maximum total context store size
    max_size_per_task: int = 10240  # 10KB per task context
    max_size_per_agent: int = 20480  # 20KB per agent context
    
    # Context lifecycle
    ttl_seconds: int = 3600  # 1 hour default TTL
    max_items_per_agent: int = 50  # Maximum context items per agent
    cleanup_interval_seconds: int = 300  # 5 minutes cleanup interval
    
    # Compression settings
    compression_type: ContextCompressionType = ContextCompressionType.SLIDING_WINDOW
    compression_ratio: float = 0.5  # Target 50% size reduction
    compression_threshold: float = 0.8  # Compress when 80% of limit reached
    
    # Performance settings
    enable_compression: bool = True
    enable_persistence: bool = False
    enable_metrics: bool = True
    thread_safe: bool = True
    
    # Context merging
    default_merge_strategy: str = "sliding_window"
    max_merge_items: int = 10
    preserve_recent: bool = True
    
    def validate(self) -> bool:
        """Validate configuration values."""
        if self.max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")
        
        if self.max_size_per_task <= 0:
            raise ValueError("max_size_per_task must be positive")
        
        if self.compression_ratio <= 0 or self.compression_ratio >= 1:
            raise ValueError("compression_ratio must be between 0 and 1")
        
        if self.compression_threshold <= 0 or self.compression_threshold >= 1:
            raise ValueError("compression_threshold must be between 0 and 1")
        
        return True