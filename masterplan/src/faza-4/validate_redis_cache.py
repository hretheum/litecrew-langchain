# validate_redis_cache.py
import time
import asyncio
import statistics
from litecrewai.cache.redis_cache import RedisCache

async def test_connection_management():
    """Test Redis connection pool and management"""
    cache = RedisCache(
        url="redis://localhost:6379",
        pool_size=5,
        max_connections=10
    )
    
    await cache.initialize()
    
    # Test connection pool
    pool_info = await cache.get_pool_info()
    assert pool_info["created_connections"] <= 5
    assert pool_info["available_connections"] > 0
    
    print(f"✅ Connection pool: {pool_info}")
    
    # Test concurrent connections
    async def concurrent_operation(i):
        await cache.set(f"concurrent:{i}", f"value_{i}")
        return await cache.get(f"concurrent:{i}")
    
    tasks = [concurrent_operation(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    assert all(results[i] == f"value_{i}" for i in range(20))
    
    # Check pool didn't exceed max
    pool_info = await cache.get_pool_info()
    assert pool_info["created_connections"] <= 10
    
    print("✅ Connection pooling working efficiently")

async def test_basic_operations():
    """Test basic Redis operations"""
    cache = RedisCache()
    await cache.initialize()
    
    # String operations
    await cache.set("test:string", "hello world", ttl=60)
    value = await cache.get("test:string")
    assert value == "hello world"
    
    # TTL check
    ttl = await cache.ttl("test:string")
    assert 55 < ttl <= 60
    
    # Delete
    await cache.delete("test:string")
    assert await cache.get("test:string") is None
    
    # Increment
    await cache.set("counter", 0)
    new_val = await cache.incr("counter", 5)
    assert new_val == 5
    
    print("✅ Basic operations working")

async def test_data_structures():
    """Test Redis data structures"""
    cache = RedisCache()
    await cache.initialize()
    
    # Hash operations
    user_data = {
        "name": "Alice",
        "age": "30",
        "city": "NYC"
    }
    await cache.hset("user:1", user_data)
    
    retrieved = await cache.hgetall("user:1")
    assert retrieved == user_data
    
    single_field = await cache.hget("user:1", "name")
    assert single_field == "Alice"
    
    # List operations
    await cache.lpush("queue:tasks", "task1", "task2", "task3")
    task = await cache.rpop("queue:tasks")
    assert task == "task1"
    
    queue_len = await cache.llen("queue:tasks")
    assert queue_len == 2
    
    # Set operations
    await cache.sadd("skills:user1", "python", "redis", "docker")
    await cache.sadd("skills:user2", "python", "mysql", "kubernetes")
    
    common_skills = await cache.sinter("skills:user1", "skills:user2")
    assert "python" in common_skills
    assert len(common_skills) == 1
    
    # Sorted set operations
    await cache.zadd("leaderboard", {"player1": 100, "player2": 200, "player3": 150})
    top_players = await cache.zrevrange("leaderboard", 0, 1, withscores=True)
    
    assert top_players[0][0] == "player2"
    assert top_players[0][1] == 200
    
    print("✅ All data structures working")

async def test_pipeline_performance():
    """Test pipeline performance improvement"""
    cache = RedisCache()
    await cache.initialize()
    
    # Without pipeline
    start = time.time()
    for i in range(100):
        await cache.set(f"normal:{i}", f"value_{i}")
    normal_time = time.time() - start
    
    # With pipeline
    start = time.time()
    async with cache.pipeline() as pipe:
        for i in range(100):
            pipe.set(f"pipeline:{i}", f"value_{i}")
        await pipe.execute()
    pipeline_time = time.time() - start
    
    improvement = normal_time / pipeline_time
    print(f"✅ Pipeline performance: {improvement:.1f}x faster")
    print(f"   Normal: {normal_time:.3f}s, Pipeline: {pipeline_time:.3f}s")
    
    assert improvement > 5  # Should be at least 5x faster

async def test_cache_patterns():
    """Test common caching patterns"""
    cache = RedisCache()
    await cache.initialize()
    
    # Cache-aside pattern
    async def get_user(user_id):
        # Check cache
        cached = await cache.get(f"user:{user_id}")
        if cached:
            return cached
        
        # Simulate DB fetch
        user = {"id": user_id, "name": f"User {user_id}"}
        
        # Cache for next time
        await cache.set(f"user:{user_id}", user, ttl=300)
        return user
    
    # First call - cache miss
    user1 = await get_user(123)
    assert user1["id"] == 123
    
    # Second call - cache hit
    user2 = await get_user(123)
    assert user1 == user2
    
    print("✅ Cache-aside pattern working")
    
    # Write-through pattern
    async def save_user(user):
        # Save to cache
        await cache.set(f"user:{user['id']}", user, ttl=300)
        # Simulate DB save
        return True
    
    await save_user({"id": 456, "name": "Jane"})
    cached = await cache.get("user:456")
    assert cached["name"] == "Jane"
    
    print("✅ Write-through pattern working")

async def test_lua_scripting():
    """Test Lua script execution"""
    cache = RedisCache()
    await cache.initialize()
    
    # Atomic increment with initial value
    script = """
        local key = KEYS[1]
        local increment = tonumber(ARGV[1])
        local current = redis.call('get', key)
        
        if current then
            return redis.call('incrby', key, increment)
        else
            redis.call('set', key, increment)
            return increment
        end
    """
    
    result1 = await cache.eval(script, keys=["score:player1"], args=[10])
    assert result1 == 10
    
    result2 = await cache.eval(script, keys=["score:player1"], args=[5])
    assert result2 == 15
    
    print("✅ Lua scripting working")
    
    # Rate limiting script
    rate_limit_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        
        local current = redis.call('incr', key)
        if current == 1 then
            redis.call('expire', key, window)
        end
        
        if current > limit then
            return 0
        else
            return 1
        end
    """
    
    # Test rate limiting
    for i in range(5):
        allowed = await cache.eval(
            rate_limit_script,
            keys=["rate:api:user1"],
            args=[3, 60]  # 3 requests per 60 seconds
        )
        if i < 3:
            assert allowed == 1
        else:
            assert allowed == 0
    
    print("✅ Rate limiting with Lua working")

async def test_pub_sub():
    """Test pub/sub for cache invalidation"""
    cache = RedisCache()
    await cache.initialize()
    
    received_messages = []
    
    # Subscribe to invalidation channel
    async def message_handler(message):
        received_messages.append(message)
    
    await cache.subscribe("cache:invalidate", message_handler)
    
    # Give subscription time to establish
    await asyncio.sleep(0.1)
    
    # Publish invalidation messages
    await cache.publish("cache:invalidate", "user:*")
    await cache.publish("cache:invalidate", "post:123")
    
    # Wait for messages
    await asyncio.sleep(0.1)
    
    assert len(received_messages) == 2
    assert "user:*" in received_messages
    assert "post:123" in received_messages
    
    print("✅ Pub/sub working for cache invalidation")

async def test_memory_optimization():
    """Test memory optimization features"""
    cache = RedisCache(max_memory="10mb", eviction_policy="allkeys-lru")
    await cache.initialize()
    
    # Set memory policy
    await cache.config_set("maxmemory", "10mb")
    await cache.config_set("maxmemory-policy", "allkeys-lru")
    
    # Fill cache with data
    for i in range(1000):
        await cache.set(f"mem:key{i}", "x" * 1000)  # 1KB each
    
    # Check memory usage
    info = await cache.info("memory")
    used_memory_mb = info["used_memory"] / 1024 / 1024
    
    assert used_memory_mb < 15  # Some overhead allowed
    print(f"✅ Memory optimization: {used_memory_mb:.1f}MB used")
    
    # Test eviction happened
    # Early keys should be evicted
    early_key = await cache.get("mem:key0")
    late_key = await cache.get("mem:key999")
    
    assert early_key is None  # Should be evicted
    assert late_key is not None  # Should still exist

async def test_monitoring():
    """Test Redis monitoring features"""
    cache = RedisCache()
    await cache.initialize()
    
    # Clear stats
    await cache.reset_stats()
    
    # Generate some activity
    for i in range(100):
        await cache.set(f"mon:key{i}", f"value{i}")
        
    for i in range(50):
        await cache.get(f"mon:key{i}")
        
    for i in range(100, 110):
        await cache.get(f"mon:key{i}")  # Misses
    
    # Get stats
    stats = await cache.get_stats()
    
    assert stats["keyspace_hits"] >= 50
    assert stats["keyspace_misses"] >= 10
    assert stats["total_commands_processed"] >= 160
    
    hit_rate = stats["keyspace_hits"] / (stats["keyspace_hits"] + stats["keyspace_misses"])
    print(f"✅ Monitoring stats:")
    print(f"   - Hit rate: {hit_rate:.1%}")
    print(f"   - Commands processed: {stats['total_commands_processed']}")
    
    # Slow query log
    slow_queries = await cache.get_slow_queries(limit=10)
    print(f"   - Slow queries: {len(slow_queries)}")

async def test_expiration_strategies():
    """Test different expiration strategies"""
    cache = RedisCache()
    await cache.initialize()
    
    # Standard TTL
    await cache.set("exp:standard", "value", ttl=2)
    assert await cache.get("exp:standard") is not None
    await asyncio.sleep(2.1)
    assert await cache.get("exp:standard") is None
    
    # Sliding expiration
    await cache.set_sliding("exp:sliding", "value", ttl=2)
    
    # Access multiple times
    for _ in range(3):
        await asyncio.sleep(1)
        value = await cache.get_sliding("exp:sliding")
        assert value == "value"  # Should still exist
    
    # Don't access for TTL period
    await asyncio.sleep(2.1)
    assert await cache.get("exp:sliding") is None
    
    print("✅ Sliding expiration working")
    
    # Probabilistic expiration (prevents stampede)
    await cache.set_probabilistic(
        "exp:prob",
        "value",
        ttl=5,
        beta=1.0
    )
    
    # Should exist but might refresh before actual expiry
    assert await cache.get("exp:prob") is not None
    print("✅ Probabilistic expiration set")

async def test_latency():
    """Test operation latency"""
    cache = RedisCache()
    await cache.initialize()
    
    latencies = {
        "set": [],
        "get": [],
        "incr": [],
        "hset": []
    }
    
    # Measure latencies
    for i in range(100):
        # SET
        start = time.time()
        await cache.set(f"perf:key{i}", f"value{i}")
        latencies["set"].append((time.time() - start) * 1000)
        
        # GET
        start = time.time()
        await cache.get(f"perf:key{i}")
        latencies["get"].append((time.time() - start) * 1000)
        
        # INCR
        start = time.time()
        await cache.incr(f"perf:counter{i}")
        latencies["incr"].append((time.time() - start) * 1000)
        
        # HSET
        start = time.time()
        await cache.hset(f"perf:hash{i}", {"field": "value"})
        latencies["hset"].append((time.time() - start) * 1000)
    
    # Calculate statistics
    print("✅ Latency statistics (ms):")
    for op, times in latencies.items():
        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        p99 = sorted(times)[int(len(times) * 0.99)]
        
        print(f"   {op.upper()}: avg={avg:.2f}, p95={p95:.2f}, p99={p99:.2f}")
        
        # All operations should be <1ms on average
        assert avg < 1.0, f"{op} too slow: {avg:.2f}ms"

if __name__ == "__main__":
    print("🔍 Validating Redis cache layer...\n")
    
    async def run_tests():
        await test_connection_management()
        await test_basic_operations()
        await test_data_structures()
        await test_pipeline_performance()
        await test_cache_patterns()
        await test_lua_scripting()
        await test_pub_sub()
        await test_memory_optimization()
        await test_monitoring()
        await test_expiration_strategies()
        await test_latency()
    
    asyncio.run(run_tests())
    
    print("\n✅ Redis cache validation complete!")