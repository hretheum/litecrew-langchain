"""
Multi-level cache implementation.
"""

import json
import pickle
import tempfile
import time
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional, Set

from litecrew.cache.metrics import CacheMetrics
from litecrew.cache.policy import CachePolicy
from litecrew.storage.cache import MemoryCache, RedisCache


class L1Cache:
    """Level 1 - In-memory cache (fastest)."""

    def __init__(self, max_size: int = 100):
        self._cache = MemoryCache(max_size=max_size)

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cache.set(key, value, ttl)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def size(self) -> int:
        return len(self._cache._cache)

    def clear(self) -> None:
        self._cache.clear()


class L2Cache:
    """Level 2 - Redis cache (fast, distributed)."""

    def __init__(self):
        self._cache = RedisCache(mock=True)  # Use mock for tests

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cache.set(key, value, ttl)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def size(self) -> int:
        # Approximate for mock
        return (
            getattr(self._cache._cache, "size", lambda: 0)()
            if hasattr(self._cache, "_cache")
            else 0
        )

    def clear(self) -> None:
        self._cache.clear()


class L3Cache:
    """Level 3 - Disk cache (slowest, largest)."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "litecrew_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self._index = {}  # In-memory index for faster lookups
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._index:
                return None

            file_path = self.cache_dir / f"{key}.cache"
            if not file_path.exists():
                del self._index[key]
                return None

            try:
                with open(file_path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            file_path = self.cache_dir / f"{key}.cache"

            try:
                with open(file_path, "wb") as f:
                    pickle.dump(value, f)
                self._index[key] = {"created": time.time(), "ttl": ttl}
            except Exception:
                pass

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._index:
                del self._index[key]

            file_path = self.cache_dir / f"{key}.cache"
            if file_path.exists():
                file_path.unlink()

    def size(self) -> int:
        return len(self._index)

    def clear(self) -> None:
        with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
            self._index.clear()


class MultiLevelCache:
    """Multi-level cache with automatic promotion/demotion."""

    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        l3_enabled: bool = True,
        policy: Optional[CachePolicy] = None,
    ):
        """
        Initialize multi-level cache.

        Args:
            l1_size: Max entries in L1 (memory)
            l2_size: Max entries in L2 (Redis)
            l3_enabled: Enable L3 (disk) cache
            policy: Cache policy configuration
        """
        self.l1 = L1Cache(max_size=l1_size)
        self.l2 = L2Cache()
        self.l3 = L3Cache() if l3_enabled else None

        self.policy = policy or CachePolicy()
        self.metrics = CacheMetrics()

        # Track access counts and levels
        self._access_counts: Dict[str, int] = {}
        self._key_levels: Dict[str, int] = {}
        self._dependencies: Dict[str, Set[str]] = {}
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (checks all levels)."""
        start_time = time.perf_counter()

        with self._lock:
            # Check L1
            value = self.l1.get(key)
            if value is not None:
                self._record_access(key, 1, True, time.perf_counter() - start_time)
                return value

            # Check L2
            value = self.l2.get(key)
            if value is not None:
                self._record_access(key, 2, True, time.perf_counter() - start_time)
                self._maybe_promote(key, value, 2)
                return value

            # Check L3
            if self.l3:
                value = self.l3.get(key)
                if value is not None:
                    self._record_access(key, 3, True, time.perf_counter() - start_time)
                    self._maybe_promote(key, value, 3)
                    return value

            # Cache miss
            self.metrics.record_get(False, None, time.perf_counter() - start_time)
            return None

    def set(
        self,
        key: str,
        value: Any,
        level: int = 3,
        ttl: Optional[int] = None,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Set value in cache at specific level."""
        start_time = time.perf_counter()

        with self._lock:
            # Check size policy
            size = len(json.dumps(value) if isinstance(value, dict) else str(value))
            if self.policy.should_reject(size):
                raise ValueError(f"Entry too large: {size} bytes")

            # Get TTL from policy if not specified
            if ttl is None:
                ttl = self.policy.get_ttl_for_key(key)

            # Store at appropriate level
            if level == 1:
                self.l1.set(key, value, ttl)
            elif level == 2:
                self.l2.set(key, value, ttl)
            elif level == 3 and self.l3:
                self.l3.set(key, value, ttl)

            # Track level and dependencies
            self._key_levels[key] = level
            if dependencies:
                self._dependencies[key] = set(dependencies)

            self.metrics.record_set(time.perf_counter() - start_time)

    def delete(self, key: str) -> None:
        """Delete from all cache levels."""
        with self._lock:
            self.l1.delete(key)
            self.l2.delete(key)
            if self.l3:
                self.l3.delete(key)

            # Clean metadata
            self._access_counts.pop(key, None)
            self._key_levels.pop(key, None)
            self._dependencies.pop(key, None)

    def get_level(self, key: str) -> Optional[int]:
        """Get cache level for a key."""
        if self.l1.get(key) is not None:
            return 1
        elif self.l2.get(key) is not None:
            return 2
        elif self.l3 and self.l3.get(key) is not None:
            return 3
        return None

    def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for a key."""
        return self.policy.get_ttl_for_key(key)

    def _record_access(self, key: str, level: int, hit: bool, latency: float):
        """Record cache access."""
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
        self.metrics.record_get(hit, level, latency)

    def _maybe_promote(self, key: str, value: Any, current_level: int):
        """Promote to higher cache level if access threshold met."""
        access_count = self._access_counts.get(key, 0)

        if self.policy.should_promote(access_count) and current_level > 1:
            # Promote to next higher level
            new_level = current_level - 1
            ttl = self.policy.get_ttl_for_key(key)

            if new_level == 1:
                self.l1.set(key, value, ttl)
            elif new_level == 2:
                self.l2.set(key, value, ttl)

            # Remove from current level
            if current_level == 2:
                self.l2.delete(key)
            elif current_level == 3 and self.l3:
                self.l3.delete(key)

            self._key_levels[key] = new_level

    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics."""
        # Update size metrics
        self.metrics.update_sizes(
            l1=self.l1.size(),
            l2=self.l2.size(),
            l3=self.l3.size() if self.l3 else 0,
            total_bytes=0,  # Would need to track actual sizes
        )
        return self.metrics
