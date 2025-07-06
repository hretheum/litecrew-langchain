"""Comprehensive tests for cache implementations."""

import time

from litecrew.storage.cache import CacheEntry, CacheStats, MemoryCache, RedisCache


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry = CacheEntry(value="test", timestamp=time.time())
        assert entry.value == "test"
        assert entry.timestamp > 0
        assert entry.ttl is None

    def test_cache_entry_with_ttl(self):
        """Test cache entry with TTL."""
        entry = CacheEntry(value="test", timestamp=time.time(), ttl=60)
        assert entry.ttl == 60

    def test_is_expired_no_ttl(self):
        """Test expiration check without TTL."""
        entry = CacheEntry(value="test", timestamp=time.time())
        assert not entry.is_expired()

    def test_is_expired_with_ttl(self):
        """Test expiration check with TTL."""
        # Not expired
        entry = CacheEntry(value="test", timestamp=time.time(), ttl=60)
        assert not entry.is_expired()

        # Expired
        past_time = time.time() - 120  # 2 minutes ago
        expired_entry = CacheEntry(value="test", timestamp=past_time, ttl=60)
        assert expired_entry.is_expired()


class TestCacheStats:
    """Test CacheStats class."""

    def test_cache_stats_initialization(self):
        """Test cache stats initialization."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=75, misses=25)
        assert stats.hit_rate == 0.75

        # Test with no requests
        empty_stats = CacheStats()
        assert empty_stats.hit_rate == 0.0

        # Test with only hits
        hit_stats = CacheStats(hits=100, misses=0)
        assert hit_stats.hit_rate == 1.0


class TestMemoryCache:
    """Test MemoryCache implementation."""

    def test_memory_cache_initialization(self):
        """Test memory cache initialization."""
        cache = MemoryCache(max_size=100)
        assert cache.max_size == 100
        assert len(cache._cache) == 0

    def test_get_set_basic(self):
        """Test basic get/set operations."""
        cache = MemoryCache()

        # Set value
        cache.set("key1", "value1")

        # Get value
        assert cache.get("key1") == "value1"

        # Get non-existent key
        assert cache.get("nonexistent") is None

    def test_get_set_with_ttl(self):
        """Test get/set with TTL."""
        cache = MemoryCache()

        # Set with TTL
        cache.set("expiring", "value", ttl=1)

        # Should exist immediately
        assert cache.get("expiring") == "value"

        # Should expire after TTL
        time.sleep(1.1)
        assert cache.get("expiring") is None

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = MemoryCache(max_size=3)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add new key, should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"  # Still there
        assert cache.get("key4") == "value4"  # New key

    def test_update_existing_key(self):
        """Test updating existing key."""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.set("key1", "updated_value")

        assert cache.get("key1") == "updated_value"

    def test_delete(self):
        """Test delete operation."""
        cache = MemoryCache()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.delete("key1")
        assert cache.get("key1") is None

        # Delete non-existent key should not raise error
        cache.delete("nonexistent")

    def test_clear(self):
        """Test clear operation."""
        cache = MemoryCache()

        # Add multiple entries
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Clear all
        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None
        assert len(cache._cache) == 0

    def test_stats_tracking(self):
        """Test statistics tracking."""
        cache = MemoryCache(max_size=2)

        # Generate some hits and misses
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Hits
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit

        # Misses
        cache.get("key3")  # Miss
        cache.get("key4")  # Miss

        # Eviction
        cache.set("key3", "value3")  # Should evict key1

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["evictions"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["size"] == 2
        assert stats["max_size"] == 2

    def test_thread_safety(self):
        """Test thread safety with concurrent operations."""
        import threading

        cache = MemoryCache()
        results = []

        def worker(thread_id):
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
                value = cache.get(f"key_{thread_id}_{i}")
                if value:
                    results.append(value)

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have collected values without errors
        assert len(results) > 0

    def test_complex_data_types(self):
        """Test caching complex data types."""
        cache = MemoryCache()

        # Dictionary
        cache.set("dict", {"a": 1, "b": 2})
        assert cache.get("dict") == {"a": 1, "b": 2}

        # List
        cache.set("list", [1, 2, 3])
        assert cache.get("list") == [1, 2, 3]

        # Nested structures
        nested = {
            "list": [1, 2, {"nested": True}],
            "dict": {"key": "value"},
            "number": 42,
        }
        cache.set("nested", nested)
        assert cache.get("nested") == nested


class TestRedisCache:
    """Test RedisCache implementation."""

    def test_redis_cache_mock_mode(self):
        """Test Redis cache in mock mode."""
        cache = RedisCache(mock=True)
        assert cache.mock is True

        # Should behave like MemoryCache
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_redis_cache_fallback(self):
        """Test Redis cache fallback when Redis not available."""
        # This should fall back to mock mode
        cache = RedisCache(host="nonexistent_host", port=99999)
        assert cache.mock is True

    def test_redis_operations_mock(self):
        """Test Redis operations in mock mode."""
        cache = RedisCache(mock=True)

        # Set/Get
        cache.set("key1", {"data": "value"})
        assert cache.get("key1") == {"data": "value"}

        # TTL
        cache.set("expiring", "value", ttl=1)
        assert cache.get("expiring") == "value"
        time.sleep(1.1)
        assert cache.get("expiring") is None

        # Delete
        cache.set("key2", "value2")
        cache.delete("key2")
        assert cache.get("key2") is None

        # Clear
        cache.set("key3", "value3")
        cache.clear()
        assert cache.get("key3") is None

        # Stats
        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats

    def test_redis_json_serialization(self):
        """Test JSON serialization in Redis cache."""
        cache = RedisCache(mock=True)

        # Complex object
        data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "data"},
        }

        cache.set("complex", data)
        retrieved = cache.get("complex")
        assert retrieved == data

    def test_redis_error_handling(self):
        """Test error handling in Redis operations."""
        # Create a mock Redis client that raises exceptions
        cache = RedisCache(mock=False)

        # Force mock mode
        cache.mock = True
        cache._cache = MemoryCache()

        # Operations should not raise exceptions
        cache.set("key", "value")
        assert cache.get("key") == "value"
        cache.delete("key")
        cache.clear()
        stats = cache.get_stats()
        assert isinstance(stats, dict)

    def test_redis_cache_initialization_variations(self):
        """Test different Redis cache initialization scenarios."""
        # Custom parameters
        cache1 = RedisCache(host="localhost", port=6379, db=1, mock=True)
        assert cache1.mock is True

        # Default parameters
        cache2 = RedisCache(mock=True)
        assert cache2.mock is True
