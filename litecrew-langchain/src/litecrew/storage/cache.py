"""
Cache implementations for storage layer.
"""

import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Optional

import redis


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    value: Any
    timestamp: float
    ttl: Optional[int] = None

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache:
    """In-memory LRU cache implementation."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        with self._lock:
            # Remove if exists (to update position)
            if key in self._cache:
                del self._cache[key]

            # Add new entry
            self._cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

            # Evict oldest if over limit
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats.evictions += 1

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "evictions": self._stats.evictions,
            "hit_rate": self._stats.hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
        }


class RedisCache:
    """Redis cache implementation (with mock mode for testing)."""

    def __init__(
        self, host: str = "localhost", port: int = 6379, db: int = 0, mock: bool = False
    ):
        """
        Initialize Redis cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            mock: Use mock implementation for testing
        """
        self.mock = mock

        if mock:
            # Use in-memory cache for testing
            self._cache = MemoryCache()
        else:
            try:
                import redis

                self._client = redis.Redis(
                    host=host, port=port, db=db, decode_responses=True
                )
                # Test connection
                self._client.ping()
            except ImportError:
                # Fallback to memory cache if redis not installed
                self.mock = True
                self._cache = MemoryCache()
            except Exception:
                # Fallback if Redis not available
                self.mock = True
                self._cache = MemoryCache()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.mock:
            return self._cache.get(key)

        try:
            value = self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if self.mock:
            self._cache.set(key, value, ttl)
            return

        try:
            serialized = json.dumps(value)
            if ttl:
                self._client.setex(key, ttl, serialized)
            else:
                self._client.set(key, serialized)
        except (redis.RedisError, ConnectionError, TimeoutError):
            # Fail silently for cache operations - it's non-critical
            pass

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if self.mock:
            self._cache.delete(key)
            return

        try:
            self._client.delete(key)
        except (redis.RedisError, ConnectionError, KeyError):
            # Ignore cache deletion errors - key might not exist
            pass

    def clear(self) -> None:
        """Clear all cache entries."""
        if self.mock:
            self._cache.clear()
            return

        try:
            self._client.flushdb()
        except (redis.RedisError, ConnectionError, KeyError):
            # Ignore cache deletion errors - key might not exist
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.mock:
            return self._cache.get_stats()

        # Redis doesn't track hit/miss stats by default
        # Would need to implement custom tracking
        try:
            info = self._client.info("stats")
            return {
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "evictions": info.get("evicted_keys", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0)
                    / (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                    if (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                    > 0
                    else 0.0
                ),
            }
        except Exception:
            return {"hits": 0, "misses": 0, "evictions": 0, "hit_rate": 0.0}
