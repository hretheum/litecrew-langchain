"""
Cache policies and configuration.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CachePolicy:
    """Defines caching policies and rules."""
    
    # TTL policies
    default_ttl: int = 3600  # 1 hour default
    ttl_by_pattern: Dict[str, Optional[int]] = field(default_factory=dict)
    adaptive_ttl: bool = False  # Adjust TTL based on access patterns
    
    # Size policies
    max_entry_size: int = 10 * 1024 * 1024  # 10MB max
    compression_threshold: int = 1024  # Compress if >1KB
    reject_oversized: bool = True
    
    # Promotion/demotion policies
    promotion_threshold: int = 3  # Accesses before promotion
    demotion_timeout: int = 300  # Seconds before demotion
    
    # Eviction policies
    eviction_policy: str = "lru"  # lru, lfu, fifo
    
    def get_ttl_for_key(self, key: str) -> Optional[int]:
        """Get TTL for a specific key based on patterns."""
        for pattern, ttl in self.ttl_by_pattern.items():
            if self._matches_pattern(key, pattern):
                return ttl
        return self.default_ttl
    
    def should_compress(self, size: int) -> bool:
        """Determine if data should be compressed."""
        return size > self.compression_threshold
    
    def should_reject(self, size: int) -> bool:
        """Determine if data should be rejected."""
        return self.reject_oversized and size > self.max_entry_size
    
    def should_promote(self, access_count: int) -> bool:
        """Determine if entry should be promoted to higher cache level."""
        return access_count >= self.promotion_threshold
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple glob matching)."""
        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])
        return key == pattern