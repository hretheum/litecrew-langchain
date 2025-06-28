# validate_query_cache.py
import time
import hashlib
import asyncio
from datetime import datetime
from litecrewai.cache.query_cache import (
    QueryResultCache, QueryFingerprint,
    InvalidationStrategy
)

async def test_query_fingerprinting():
    """Test query normalization and fingerprinting"""
    cache = QueryResultCache()
    
    # Different queries that are semantically same
    queries = [
        ("SELECT * FROM users WHERE id = ?", [1]),
        ("SELECT * FROM users WHERE id=?", [1]),
        ("SELECT   *   FROM   users   WHERE   id = ?", [1]),
        ("select * from users where id = ?", [1]),
    ]
    
    fingerprints = set()
    for query, params in queries:
        fp = cache.get_fingerprint(query, params)
        fingerprints.add(fp.hash)
    
    # All should have same fingerprint
    assert len(fingerprints) == 1
    print("✅ Query normalization working")
    
    # Different params should have different fingerprint
    fp1 = cache.get_fingerprint("SELECT * FROM users WHERE id = ?", [1])
    fp2 = cache.get_fingerprint("SELECT * FROM users WHERE id = ?", [2])
    assert fp1.hash != fp2.hash
    
    # Extract table dependencies
    fp = cache.get_fingerprint(
        "SELECT u.*, p.* FROM users u JOIN posts p ON u.id = p.user_id WHERE u.status = ?",
        ["active"]
    )
    assert "users" in fp.tables
    assert "posts" in fp.tables
    print("✅ Table extraction working")

async def test_caching_decorator():
    """Test caching decorator functionality"""
    cache = QueryResultCache()
    
    call_count = 0
    
    @cache.cached(ttl=60)
    async def get_expensive_data(param: int):
        nonlocal call_count
        call_count += 1
        # Simulate expensive operation
        await asyncio.sleep(0.1)
        return {"result": param * 2, "timestamp": time.time()}
    
    # First call - cache miss
    result1 = await get_expensive_data(5)
    assert result1["result"] == 10
    assert call_count == 1
    
    # Second call - cache hit
    result2 = await get_expensive_data(5)
    assert result2 == result1  # Exact same object
    assert call_count == 1  # Not called again
    
    # Different param - cache miss
    result3 = await get_expensive_data(10)
    assert result3["result"] == 20
    assert call_count == 2
    
    print("✅ Caching decorator working")

async def test_smart_invalidation():
    """Test intelligent cache invalidation"""
    cache = QueryResultCache()
    
    # Cache some queries
    await cache.store(
        "SELECT * FROM users WHERE status = ?",
        ["active"],
        [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
        tags=["users", "status:active"]
    )
    
    await cache.store(
        "SELECT * FROM posts WHERE user_id = ?",
        [1],
        [{"id": 101, "title": "Post 1"}],
        tags=["posts", "user:1"]
    )
    
    await cache.store(
        "SELECT COUNT(*) FROM users",
        [],
        [{"count": 100}],
        tags=["users", "aggregate"]
    )
    
    # Invalidate by table
    await cache.invalidate_table("users")
    
    # Users queries should be gone
    assert await cache.get("SELECT * FROM users WHERE status = ?", ["active"]) is None
    assert await cache.get("SELECT COUNT(*) FROM users", []) is None
    
    # Posts query should remain
    assert await cache.get("SELECT * FROM posts WHERE user_id = ?", [1]) is not None
    
    print("✅ Table-based invalidation working")
    
    # Test tag-based invalidation
    await cache.store(
        "SELECT * FROM orders WHERE user_id = ?",
        [1],
        [{"id": 1001, "total": 99.99}],
        tags=["orders", "user:1"]
    )
    
    # Invalidate all user:1 data
    await cache.invalidate_tag("user:1")
    
    assert await cache.get("SELECT * FROM posts WHERE user_id = ?", [1]) is None
    assert await cache.get("SELECT * FROM orders WHERE user_id = ?", [1]) is None
    
    print("✅ Tag-based invalidation working")

async def test_compression():
    """Test result compression"""
    cache_plain = QueryResultCache(compression=False)
    cache_compressed = QueryResultCache(compression=True)
    
    # Large result set
    large_result = [
        {"id": i, "data": "x" * 100, "values": list(range(100))}
        for i in range(100)
    ]
    
    # Store in both caches
    query = "SELECT * FROM large_table"
    
    await cache_plain.store(query, [], large_result)
    await cache_compressed.store(query, [], large_result)
    
    # Compare sizes
    size_plain = cache_plain.get_entry_size(query, [])
    size_compressed = cache_compressed.get_entry_size(query, [])
    
    compression_ratio = 1 - (size_compressed / size_plain)
    print(f"✅ Compression ratio: {compression_ratio:.1%}")
    print(f"   Plain: {size_plain:,} bytes")
    print(f"   Compressed: {size_compressed:,} bytes")
    
    assert compression_ratio > 0.5  # At least 50% compression
    
    # Verify data integrity
    result = await cache_compressed.get(query, [])
    assert result == large_result

async def test_refresh_ahead():
    """Test refresh-ahead functionality"""
    cache = QueryResultCache()
    
    refresh_count = 0
    
    async def data_fetcher():
        nonlocal refresh_count
        refresh_count += 1
        return [{"count": refresh_count, "time": time.time()}]
    
    # Schedule refresh-ahead
    await cache.schedule_refresh(
        query="SELECT COUNT(*) FROM active_users",
        params=[],
        fetcher=data_fetcher,
        interval=1,  # Every 1 second
        ttl=10
    )
    
    # Initial fetch
    await asyncio.sleep(0.1)
    result1 = await cache.get("SELECT COUNT(*) FROM active_users", [])
    assert result1[0]["count"] == 1
    
    # Wait for refresh
    await asyncio.sleep(1.2)
    result2 = await cache.get("SELECT COUNT(*) FROM active_users", [])
    assert result2[0]["count"] == 2  # Refreshed
    
    # Stop refresh
    await cache.stop_refresh("SELECT COUNT(*) FROM active_users", [])
    
    print(f"✅ Refresh-ahead working ({refresh_count} refreshes)")

async def test_partial_results():
    """Test partial result caching"""
    cache = QueryResultCache()
    
    # Large dataset
    full_data = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
    
    # Cache with pagination info
    await cache.store_partial(
        query="SELECT * FROM items ORDER BY id",
        params=[],
        result=full_data[:100],
        offset=0,
        limit=100,
        total_count=1000
    )
    
    # Retrieve partial
    cached = await cache.get_partial(
        "SELECT * FROM items ORDER BY id",
        [],
        offset=0,
        limit=100
    )
    
    assert cached is not None
    assert len(cached["data"]) == 100
    assert cached["total_count"] == 1000
    assert cached["has_more"] == True
    
    print("✅ Partial result caching working")

async def test_dependency_tracking():
    """Test query dependency tracking"""
    cache = QueryResultCache()
    
    # Define query dependencies
    await cache.add_dependency(
        parent="SELECT * FROM user_stats WHERE user_id = ?",
        child="SELECT * FROM users WHERE id = ?"
    )
    
    # Cache both queries
    await cache.store(
        "SELECT * FROM users WHERE id = ?",
        [1],
        [{"id": 1, "name": "John"}]
    )
    
    await cache.store(
        "SELECT * FROM user_stats WHERE user_id = ?",
        [1],
        [{"user_id": 1, "total_posts": 50}]
    )
    
    # Invalidate parent - should invalidate child too
    await cache.invalidate(
        "SELECT * FROM users WHERE id = ?",
        [1]
    )
    
    # Both should be invalidated
    assert await cache.get("SELECT * FROM users WHERE id = ?", [1]) is None
    assert await cache.get("SELECT * FROM user_stats WHERE user_id = ?", [1]) is None
    
    print("✅ Dependency tracking working")

async def test_analytics():
    """Test cache analytics"""
    cache = QueryResultCache()
    
    # Generate activity
    queries = [
        ("SELECT * FROM users WHERE id = ?", [1]),
        ("SELECT * FROM users WHERE id = ?", [2]),
        ("SELECT * FROM posts WHERE user_id = ?", [1]),
        ("SELECT COUNT(*) FROM users", []),
    ]
    
    # Cache queries
    for query, params in queries:
        await cache.store(query, params, [{"dummy": "data"}])
    
    # Generate hits and misses
    for _ in range(10):
        await cache.get("SELECT * FROM users WHERE id = ?", [1])  # Hits
    
    for i in range(5):
        await cache.get("SELECT * FROM users WHERE id = ?", [i + 10])  # Misses
    
    # Get analytics
    stats = await cache.get_analytics()
    
    assert stats.total_queries == 4
    assert stats.cache_hits >= 10
    assert stats.cache_misses >= 5
    assert stats.hit_rate > 0.6
    
    print(f"✅ Analytics:")
    print(f"   - Hit rate: {stats.hit_rate:.1%}")
    print(f"   - Total queries cached: {stats.total_queries}")
    print(f"   - Memory used: {stats.memory_used_mb:.1f}MB")
    
    # Top queries
    top_queries = stats.get_top_queries(2)
    assert len(top_queries) >= 1
    assert top_queries[0]["hits"] >= 10

async def test_performance():
    """Test cache performance"""
    cache = QueryResultCache()
    
    # Prepare test data
    queries = []
    for i in range(100):
        query = f"SELECT * FROM table_{i % 10} WHERE id = ?"
        params = [i]
        result = [{"id": i, "data": f"value_{i}"}]
        queries.append((query, params, result))
    
    # Store all
    start = time.time()
    for query, params, result in queries:
        await cache.store(query, params, result)
    store_time = time.time() - start
    
    print(f"✅ Store performance: {len(queries)/store_time:.0f} ops/sec")
    
    # Retrieve all
    start = time.time()
    hits = 0
    for query, params, _ in queries:
        if await cache.get(query, params):
            hits += 1
    get_time = time.time() - start
    
    assert hits == len(queries)
    avg_lookup = (get_time / len(queries)) * 1000
    
    print(f"✅ Lookup performance: {avg_lookup:.2f}ms avg")
    assert avg_lookup < 5  # Should be <5ms

async def test_memory_limit():
    """Test memory limit enforcement"""
    cache = QueryResultCache(max_size_mb=1)  # 1MB limit
    
    # Fill cache
    stored = 0
    for i in range(1000):
        query = f"SELECT * FROM test WHERE id = {i}"
        # ~1KB per entry
        result = [{"data": "x" * 1000}]
        
        if await cache.store(query, [], result):
            stored += 1
        else:
            break
    
    print(f"✅ Memory limit: stored {stored} entries in 1MB")
    
    # Check size
    stats = await cache.get_analytics()
    assert stats.memory_used_mb <= 1.1  # Some overhead

if __name__ == "__main__":
    print("🔍 Validating query result cache...\n")
    
    async def run_tests():
        await test_query_fingerprinting()
        await test_caching_decorator()
        await test_smart_invalidation()
        await test_compression()
        await test_refresh_ahead()
        await test_partial_results()
        await test_dependency_tracking()
        await test_analytics()
        await test_performance()
        await test_memory_limit()
    
    asyncio.run(run_tests())
    
    print("\n✅ Query cache validation complete!")