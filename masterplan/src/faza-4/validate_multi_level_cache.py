# validate_multi_level_cache.py
import time
import asyncio
import psutil
import pickle
from litecrewai.cache import MultiLevelCache, CacheStats

async def test_cache_levels():
    """Test all cache levels work correctly"""
    cache = MultiLevelCache(
        l1_size_mb=10,
        l2_size_mb=50,
        l3_enabled=True
    )
    
    await cache.initialize()
    
    # Test data
    test_key = "test:123"
    test_value = {"data": "x" * 1000, "number": 42}
    
    # Set in cache (goes to L1)
    await cache.set(test_key, test_value, ttl=3600)
    
    # Get from L1 (fast)
    start = time.time()
    value_l1 = await cache.get(test_key)
    l1_time = (time.time() - start) * 1000
    
    assert value_l1 == test_value
    assert l1_time < 1.0
    print(f"✅ L1 hit: {l1_time:.2f}ms")
    
    # Clear L1 to test L2
    cache._l1_cache.clear()
    
    # Get from L2
    start = time.time()
    value_l2 = await cache.get(test_key)
    l2_time = (time.time() - start) * 1000
    
    assert value_l2 == test_value
    assert l2_time < 5.0
    print(f"✅ L2 hit: {l2_time:.2f}ms")
    
    # Clear L1 and L2 to test L3
    cache._l1_cache.clear()
    await cache._l2_cache.flushall()
    
    # Get from L3
    start = time.time()
    value_l3 = await cache.get(test_key)
    l3_time = (time.time() - start) * 1000
    
    assert value_l3 == test_value
    assert l3_time < 20.0
    print(f"✅ L3 hit: {l3_time:.2f}ms")

async def test_tier_migration():
    """Test automatic tier migration"""
    cache = MultiLevelCache(
        l1_size_mb=1,  # Very small for testing
        l2_size_mb=10,
        l3_enabled=True
    )
    
    await cache.initialize()
    
    # Fill L1 cache
    for i in range(20):
        await cache.set(f"key:{i}", f"value_{i}" * 100)
    
    # Check L1 size is limited
    l1_stats = cache.get_l1_stats()
    assert l1_stats["size_mb"] <= 1.1  # Some overhead
    
    # Older items should migrate to L2
    l2_count = await cache._l2_cache.dbsize()
    assert l2_count > 0
    
    print(f"✅ Tier migration: L1={l1_stats['count']}, L2={l2_count}")
    
    # Access old item - should promote back to L1
    old_value = await cache.get("key:0")
    assert old_value is not None
    
    # Should now be in L1
    assert "key:0" in cache._l1_cache

async def test_cache_strategies():
    """Test different cache strategies"""
    # Write-through cache
    cache_wt = MultiLevelCache(strategy="write_through")
    await cache_wt.initialize()
    
    # Write should go to all levels
    await cache_wt.set("wt:1", "value1")
    
    # Check all levels have it
    assert "wt:1" in cache_wt._l1_cache
    assert await cache_wt._l2_cache.exists("wt:1")
    
    print("✅ Write-through strategy working")
    
    # Write-back cache (lazy write)
    cache_wb = MultiLevelCache(strategy="write_back")
    await cache_wb.initialize()
    
    # Write only to L1 initially
    await cache_wb.set("wb:1", "value1")
    assert "wb:1" in cache_wb._l1_cache
    assert not await cache_wb._l2_cache.exists("wb:1")
    
    # Force flush
    await cache_wb.flush()
    assert await cache_wb._l2_cache.exists("wb:1")
    
    print("✅ Write-back strategy working")

async def test_eviction_policies():
    """Test different eviction policies"""
    # LRU eviction
    cache_lru = MultiLevelCache(
        l1_size_mb=1,
        eviction_policy="lru"
    )
    await cache_lru.initialize()
    
    # Add items
    for i in range(10):
        await cache_lru.set(f"lru:{i}", "x" * 10000)
    
    # Access some items to make them recently used
    await cache_lru.get("lru:0")
    await cache_lru.get("lru:1")
    
    # Add more to trigger eviction
    for i in range(10, 15):
        await cache_lru.set(f"lru:{i}", "x" * 10000)
    
    # Early items (except 0,1) should be evicted
    assert await cache_lru.get("lru:0") is not None
    assert await cache_lru.get("lru:1") is not None
    assert await cache_lru.get("lru:5") is None  # Should be evicted
    
    print("✅ LRU eviction working")
    
    # TTL eviction
    cache_ttl = MultiLevelCache()
    await cache_ttl.initialize()
    
    # Set with short TTL
    await cache_ttl.set("ttl:1", "value", ttl=1)
    assert await cache_ttl.get("ttl:1") is not None
    
    # Wait for expiry
    await asyncio.sleep(1.1)
    assert await cache_ttl.get("ttl:1") is None
    
    print("✅ TTL eviction working")

async def test_tagged_caching():
    """Test tag-based cache invalidation"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Set items with tags
    await cache.set("user:123:profile", {"name": "John"}, tags=["user:123"])
    await cache.set("user:123:posts", ["post1", "post2"], tags=["user:123", "posts"])
    await cache.set("user:456:profile", {"name": "Jane"}, tags=["user:456"])
    await cache.set("global:stats", {"total": 100}, tags=["global"])
    
    # Invalidate by tag
    await cache.invalidate_tag("user:123")
    
    # user:123 items should be gone
    assert await cache.get("user:123:profile") is None
    assert await cache.get("user:123:posts") is None
    
    # Others should remain
    assert await cache.get("user:456:profile") is not None
    assert await cache.get("global:stats") is not None
    
    print("✅ Tagged invalidation working")

async def test_batch_operations():
    """Test batch cache operations"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Batch set
    batch_data = {
        f"batch:{i}": f"value_{i}"
        for i in range(100)
    }
    
    start = time.time()
    await cache.mset(batch_data, ttl=3600)
    batch_set_time = time.time() - start
    
    print(f"✅ Batch set: 100 items in {batch_set_time:.2f}s")
    
    # Batch get
    keys = list(batch_data.keys())
    start = time.time()
    values = await cache.mget(keys)
    batch_get_time = time.time() - start
    
    assert len(values) == 100
    assert all(v is not None for v in values)
    print(f"✅ Batch get: 100 items in {batch_get_time:.2f}s")
    
    # Batch delete
    await cache.mdelete(keys[:50])
    remaining = await cache.mget(keys)
    assert sum(1 for v in remaining if v is not None) == 50

async def test_compression():
    """Test cache compression"""
    # Large data for compression test
    large_data = {
        "text": "x" * 10000,
        "numbers": list(range(1000)),
        "nested": {"data": "y" * 5000}
    }
    
    # Cache without compression
    cache_plain = MultiLevelCache(compression=False)
    await cache_plain.initialize()
    
    await cache_plain.set("plain:1", large_data)
    size_plain = cache_plain.get_size("plain:1")
    
    # Cache with compression
    cache_compressed = MultiLevelCache(compression=True)
    await cache_compressed.initialize()
    
    await cache_compressed.set("compressed:1", large_data)
    size_compressed = cache_compressed.get_size("compressed:1")
    
    # Verify compression works
    assert size_compressed < size_plain * 0.5  # At least 50% compression
    
    # Verify data integrity
    data_retrieved = await cache_compressed.get("compressed:1")
    assert data_retrieved == large_data
    
    print(f"✅ Compression: {size_plain} → {size_compressed} bytes "
          f"({(1 - size_compressed/size_plain)*100:.1f}% reduction)")

async def test_cache_warming():
    """Test cache warming functionality"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Define warming data
    warming_data = {
        "config:app": {"version": "1.0", "features": ["a", "b"]},
        "config:limits": {"rate_limit": 100, "max_users": 1000},
        "static:countries": ["US", "UK", "CA", "AU"],
    }
    
    # Warm cache
    await cache.warm(warming_data)
    
    # All items should be in L1
    for key in warming_data:
        assert key in cache._l1_cache
        value = await cache.get(key)
        assert value == warming_data[key]
    
    print(f"✅ Cache warming: {len(warming_data)} items pre-loaded")

async def test_distributed_invalidation():
    """Test distributed cache invalidation"""
    # Simulate two cache instances
    cache1 = MultiLevelCache(instance_id="node1")
    cache2 = MultiLevelCache(instance_id="node2")
    
    await cache1.initialize()
    await cache2.initialize()
    
    # Set in cache1
    await cache1.set("shared:1", "value1")
    
    # Should propagate to shared L2
    value = await cache2.get("shared:1")
    assert value == "value1"
    
    # Invalidate from cache2
    await cache2.invalidate("shared:1", broadcast=True)
    
    # Should be gone from both
    assert await cache1.get("shared:1") is None
    assert await cache2.get("shared:1") is None
    
    print("✅ Distributed invalidation working")

async def test_cache_statistics():
    """Test cache statistics tracking"""
    cache = MultiLevelCache()
    await cache.initialize()
    
    # Generate some activity
    for i in range(100):
        await cache.set(f"stat:{i}", f"value_{i}")
    
    # Some hits
    for i in range(50):
        await cache.get(f"stat:{i}")
    
    # Some misses
    for i in range(100, 110):
        await cache.get(f"stat:{i}")
    
    # Get statistics
    stats = cache.get_stats()
    
    assert stats.total_requests == 60  # 50 hits + 10 misses
    assert stats.l1_hits == 50
    assert stats.misses == 10
    assert stats.l1_hit_rate > 0.8
    
    print(f"✅ Cache statistics:")
    print(f"   - Total requests: {stats.total_requests}")
    print(f"   - L1 hit rate: {stats.l1_hit_rate:.1%}")
    print(f"   - L2 hit rate: {stats.l2_hit_rate:.1%}")
    print(f"   - Overall hit rate: {stats.overall_hit_rate:.1%}")

if __name__ == "__main__":
    print("🔍 Validating multi-level cache...\n")
    
    async def run_tests():
        await test_cache_levels()
        await test_tier_migration()
        await test_cache_strategies()
        await test_eviction_policies()
        await test_tagged_caching()
        await test_batch_operations()
        await test_compression()
        await test_cache_warming()
        await test_distributed_invalidation()
        await test_cache_statistics()
    
    asyncio.run(run_tests())
    
    print("\n✅ Multi-level cache validation complete!")