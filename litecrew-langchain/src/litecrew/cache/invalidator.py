"""
Cache invalidation strategies.
"""

import fnmatch
from typing import List, Set, Optional
from litecrew.cache.multilevel import MultiLevelCache


class CacheInvalidator:
    """Handles cache invalidation with various strategies."""

    def __init__(self, cache: MultiLevelCache):
        self.cache = cache

    def invalidate(self, key: str) -> None:
        """Invalidate a single key."""
        self.cache.delete(key)

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Glob-style pattern (e.g., "user:*", "cache:prefix:*")

        Returns:
            Number of keys invalidated
        """
        invalidated = 0

        # Get all keys from all levels
        all_keys = set()

        # L1 keys
        if hasattr(self.cache.l1._cache, "_cache"):
            all_keys.update(self.cache.l1._cache._cache.keys())

        # L2 keys (if we had access to Redis keys)
        # In real implementation, would use Redis SCAN

        # L3 keys
        if self.cache.l3:
            all_keys.update(self.cache.l3._index.keys())

        # Find matching keys
        for key in all_keys:
            if fnmatch.fnmatch(key, pattern):
                self.cache.delete(key)
                invalidated += 1

        return invalidated

    def invalidate_with_dependencies(self, key: str) -> Set[str]:
        """
        Invalidate a key and all dependent keys.

        Returns:
            Set of all invalidated keys
        """
        invalidated = {key}
        to_check = [key]

        while to_check:
            current = to_check.pop()
            self.cache.delete(current)

            # Find all keys that depend on current
            for k, deps in self.cache._dependencies.items():
                if current in deps and k not in invalidated:
                    invalidated.add(k)
                    to_check.append(k)

        return invalidated

    def invalidate_batch(self, keys: List[str]) -> None:
        """Invalidate multiple keys at once."""
        for key in keys:
            self.cache.delete(key)

    def invalidate_all(self) -> None:
        """Clear entire cache."""
        self.cache.l1.clear()
        self.cache.l2.clear()
        if self.cache.l3:
            self.cache.l3.clear()

        # Clear metadata
        self.cache._access_counts.clear()
        self.cache._key_levels.clear()
        self.cache._dependencies.clear()

    def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalidate all keys with a specific tag.

        Note: This requires maintaining a tag index, which would be
        implemented in a production system.
        """
        # For now, use pattern matching
        return self.invalidate_pattern(f"*:{tag}:*")
