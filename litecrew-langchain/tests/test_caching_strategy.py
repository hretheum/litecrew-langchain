"""
Tests for advanced caching strategy.
"""

import pytest
import time
import asyncio
from typing import Dict, Any, List

from litecrew.cache import (
    MultiLevelCache,
    CacheWarmer,
    CacheInvalidator,
    CacheMetrics,
    CachePolicy,
    L1Cache,
    L2Cache,
    L3Cache
)


class TestMultiLevelCache:
    """Test multi-level cache implementation."""
    
    def test_cache_levels(self):
        """Test L1, L2, L3 cache levels."""
        cache = MultiLevelCache(
            l1_size=10,    # 10 entries in memory
            l2_size=100,   # 100 entries in Redis
            l3_enabled=True  # Disk cache enabled
        )
        
        # Test L1 (memory) cache
        cache.set("key1", {"data": "value1"}, level=1)
        assert cache.get("key1") is not None
        assert cache.get_level("key1") == 1
        
        # Test L2 (Redis) cache
        cache.set("key2", {"data": "value2"}, level=2)
        assert cache.get("key2") is not None
        assert cache.get_level("key2") == 2
        
        # Test L3 (disk) cache
        cache.set("key3", {"data": "value3"}, level=3)
        assert cache.get("key3") is not None
        assert cache.get_level("key3") == 3
    
    def test_cache_promotion(self):
        """Test automatic cache level promotion."""
        cache = MultiLevelCache()
        
        # Start in L3 (cold)
        cache.set("key1", {"data": "value1"}, level=3)
        
        # Access multiple times
        for _ in range(5):
            cache.get("key1")
        
        # Should be promoted to L2
        assert cache.get_level("key1") == 2
        
        # Access more times
        for _ in range(10):
            cache.get("key1")
        
        # Should be promoted to L1
        assert cache.get_level("key1") == 1
    
    def test_cache_eviction(self):
        """Test cache eviction policies."""
        # Small L1 cache for testing
        cache = MultiLevelCache(l1_size=3)
        
        # Fill L1 cache
        cache.set("key1", {"data": "value1"}, level=1)
        cache.set("key2", {"data": "value2"}, level=1)
        cache.set("key3", {"data": "value3"}, level=1)
        
        # Add one more - should evict least recently used
        cache.set("key4", {"data": "value4"}, level=1)
        
        # key1 should be evicted to L2
        assert cache.get_level("key1") == 2
        assert cache.get_level("key4") == 1
    
    def test_cache_invalidation_patterns(self):
        """Test different invalidation patterns."""
        cache = MultiLevelCache()
        invalidator = CacheInvalidator(cache)
        
        # Add test data
        cache.set("user:123:profile", {"name": "John"})
        cache.set("user:123:settings", {"theme": "dark"})
        cache.set("user:456:profile", {"name": "Jane"})
        cache.set("post:789:data", {"title": "Test"})
        
        # Pattern invalidation
        invalidator.invalidate_pattern("user:123:*")
        
        assert cache.get("user:123:profile") is None
        assert cache.get("user:123:settings") is None
        assert cache.get("user:456:profile") is not None
        assert cache.get("post:789:data") is not None
    
    def test_cache_dependencies(self):
        """Test cache dependency tracking."""
        cache = MultiLevelCache()
        invalidator = CacheInvalidator(cache)
        
        # Set up dependencies
        cache.set("parent", {"data": "parent"})
        cache.set("child1", {"data": "child1"}, dependencies=["parent"])
        cache.set("child2", {"data": "child2"}, dependencies=["parent"])
        cache.set("grandchild", {"data": "grandchild"}, dependencies=["child1"])
        
        # Invalidate parent - should cascade
        invalidator.invalidate_with_dependencies("parent")
        
        assert cache.get("parent") is None
        assert cache.get("child1") is None
        assert cache.get("child2") is None
        assert cache.get("grandchild") is None


class TestCacheWarmer:
    """Test cache warming functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """Test warming cache with precomputed data."""
        cache = MultiLevelCache()
        warmer = CacheWarmer(cache)
        
        # Define warming tasks
        async def compute_expensive_data(key: str) -> Dict[str, Any]:
            await asyncio.sleep(0.01)  # Simulate computation
            return {"key": key, "computed": True, "timestamp": time.time()}
        
        # Warm cache with multiple keys
        keys_to_warm = [f"expensive:{i}" for i in range(10)]
        
        start_time = time.time()
        await warmer.warm_cache(keys_to_warm, compute_expensive_data)
        warm_time = time.time() - start_time
        
        # Verify all keys are cached
        for key in keys_to_warm:
            assert cache.get(key) is not None
            assert cache.get(key)["computed"] is True
        
        # Accessing should be fast now
        start_time = time.time()
        for key in keys_to_warm:
            cache.get(key)
        access_time = time.time() - start_time
        
        # Access should be much faster than warming
        assert access_time < warm_time / 10
    
    def test_scheduled_warming(self):
        """Test scheduled cache warming."""
        cache = MultiLevelCache()
        warmer = CacheWarmer(cache)
        
        # Schedule warming tasks
        def warm_user_data():
            for i in range(5):
                cache.set(f"user:{i}", {"id": i, "warmed_at": time.time()})
        
        def warm_config_data():
            cache.set("config:main", {"version": "1.0", "warmed": True})
        
        # Add warming schedules
        warmer.schedule_warming(warm_user_data, interval=60)  # Every minute
        warmer.schedule_warming(warm_config_data, interval=300)  # Every 5 minutes
        
        # Trigger immediate warming
        warmer.warm_now()
        
        # Verify data is warmed
        assert cache.get("user:0") is not None
        assert cache.get("config:main") is not None


class TestCacheMetrics:
    """Test cache metrics and monitoring."""
    
    def test_cache_metrics_collection(self):
        """Test collecting cache performance metrics."""
        cache = MultiLevelCache()
        
        # Perform operations
        cache.set("key1", {"data": "value1"})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        cache.get("key1")  # Hit
        cache.set("key2", {"data": "value2"})
        cache.get("key2")  # Hit
        
        metrics = cache.get_metrics()
        
        assert metrics.hits == 3
        assert metrics.misses == 1
        assert metrics.hit_rate > 0.7  # 75%
        assert metrics.total_operations == 6
        
        # Check level-specific metrics
        assert metrics.l1_hits >= 0
        assert metrics.l2_hits >= 0
        assert metrics.l3_hits >= 0
    
    def test_cache_size_metrics(self):
        """Test cache size tracking."""
        cache = MultiLevelCache(l1_size=10)
        
        # Add data of various sizes
        for i in range(20):
            data = {"id": i, "data": "x" * (i * 100)}
            cache.set(f"key{i}", data)
        
        metrics = cache.get_metrics()
        
        assert metrics.l1_entries <= 10  # L1 size limit
        assert metrics.l2_entries > 0     # Overflow to L2
        assert metrics.total_size_bytes > 0
        assert metrics.average_entry_size > 0
    
    def test_cache_latency_metrics(self):
        """Test cache operation latency tracking."""
        cache = MultiLevelCache()
        
        # Perform operations with timing
        for i in range(100):
            cache.set(f"key{i}", {"data": f"value{i}"})
            cache.get(f"key{i}")
        
        metrics = cache.get_metrics()
        
        assert metrics.average_get_latency_ms < 1  # Should be <1ms
        assert metrics.average_set_latency_ms < 1  # Should be <1ms
        assert metrics.p95_get_latency_ms < 2      # 95th percentile
        assert metrics.p99_get_latency_ms < 5      # 99th percentile


class TestCachePolicy:
    """Test cache policies and configuration."""
    
    def test_ttl_policy(self):
        """Test time-to-live cache policy."""
        policy = CachePolicy(
            default_ttl=60,  # 1 minute default
            ttl_by_pattern={
                "session:*": 1800,     # 30 minutes for sessions
                "temp:*": 10,          # 10 seconds for temp data
                "permanent:*": None    # No expiry
            }
        )
        
        cache = MultiLevelCache(policy=policy)
        
        # Test different TTLs
        cache.set("session:123", {"user": "john"})
        cache.set("temp:456", {"data": "temporary"})
        cache.set("permanent:789", {"data": "forever"})
        cache.set("default:000", {"data": "default"})
        
        # Verify TTLs are applied
        assert cache.get_ttl("session:123") == 1800
        assert cache.get_ttl("temp:456") == 10
        assert cache.get_ttl("permanent:789") is None
        assert cache.get_ttl("default:000") == 60
    
    def test_size_policy(self):
        """Test cache size limits and policies."""
        policy = CachePolicy(
            max_entry_size=1024 * 1024,  # 1MB max per entry
            compression_threshold=10 * 1024,  # Compress >10KB
            reject_oversized=True
        )
        
        cache = MultiLevelCache(policy=policy)
        
        # Small entry - should work
        small_data = {"data": "small"}
        cache.set("small", small_data)
        assert cache.get("small") is not None
        
        # Large entry - should be compressed
        large_data = {"data": "x" * 20000}  # ~20KB
        cache.set("large", large_data)
        retrieved = cache.get("large")
        assert retrieved is not None
        assert retrieved["data"] == large_data["data"]
        
        # Oversized entry - should be rejected
        oversized_data = {"data": "x" * 2000000}  # ~2MB
        with pytest.raises(ValueError):
            cache.set("oversized", oversized_data)
    
    def test_access_pattern_policy(self):
        """Test policies based on access patterns."""
        policy = CachePolicy(
            promotion_threshold=3,     # Promote after 3 accesses
            demotion_timeout=300,      # Demote after 5 min inactive
            adaptive_ttl=True          # Adjust TTL based on access
        )
        
        cache = MultiLevelCache(policy=policy)
        
        # New entry starts in L3
        cache.set("data", {"value": "test"})
        assert cache.get_level("data") == 3
        
        # Access multiple times
        for _ in range(3):
            cache.get("data")
        
        # Should be promoted
        assert cache.get_level("data") <= 2
        
        # Test adaptive TTL
        initial_ttl = cache.get_ttl("data")
        
        # More accesses should extend TTL
        for _ in range(10):
            cache.get("data")
            time.sleep(0.01)
        
        new_ttl = cache.get_ttl("data")
        assert new_ttl > initial_ttl  # TTL extended due to frequent access


def test_cache_integration():
    """Test complete caching strategy integration."""
    # Create multi-level cache with policies
    policy = CachePolicy(
        default_ttl=300,
        promotion_threshold=5,
        compression_threshold=1024,
        ttl_by_pattern={
            "crew:*:state": 3600,    # 1 hour for crew states
            "result:*": 1800,        # 30 min for results
            "temp:*": 60             # 1 min for temp data
        }
    )
    
    cache = MultiLevelCache(
        l1_size=100,
        l2_size=1000,
        l3_enabled=True,
        policy=policy
    )
    
    warmer = CacheWarmer(cache)
    invalidator = CacheInvalidator(cache)
    
    # Simulate crew execution caching
    crew_id = "crew_123"
    
    # Cache crew state
    cache.set(f"crew:{crew_id}:state", {
        "status": "running",
        "tasks_completed": 5,
        "agents": ["researcher", "writer"]
    })
    
    # Cache task results
    for i in range(10):
        cache.set(f"result:{crew_id}:task_{i}", {
            "output": f"Task {i} completed",
            "duration": 2.5 + i * 0.1
        })
    
    # Warm cache with expensive computations
    def compute_analytics():
        # Simulate expensive analytics
        total_duration = sum(
            cache.get(f"result:{crew_id}:task_{i}")["duration"]
            for i in range(10)
            if cache.get(f"result:{crew_id}:task_{i}")
        )
        cache.set(f"crew:{crew_id}:analytics", {
            "total_duration": total_duration,
            "average_duration": total_duration / 10
        })
    
    warmer.warm_now(compute_analytics)
    
    # Test metrics
    metrics = cache.get_metrics()
    print(f"\nCache Integration Metrics:")
    print(f"Hit rate: {metrics.hit_rate:.1%}")
    print(f"L1 entries: {metrics.l1_entries}")
    print(f"L2 entries: {metrics.l2_entries}")
    print(f"Average latency: {metrics.average_get_latency_ms:.2f}ms")
    
    assert metrics.hit_rate > 0.7  # Good hit rate
    assert metrics.average_get_latency_ms < 1  # Fast access