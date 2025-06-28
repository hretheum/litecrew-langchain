## 📦 FAZA 4: STORAGE I PERSISTENCE

[← Powrót do README](./README.md) | [← Faza 3: LLM](./faza-3-LLM.md) | [Następna faza: API →](./faza-5-api.md)

### Blok 4.1: Database Design and Implementation

**Czas**: 8h
**Cel**: Optymalny storage layer

#### Zadania Atomowe:

##### Task 4.1.1: Design Optimal Schema (3h)

**Cel**: Skalowalny i wydajny schemat bazy danych

**Prompt dla AI Agent**:

```
Zaprojektuj optymalny schemat bazy danych dla LiteCrewAI.

Tabele do zaprojektowania:
1. Core tables:
   - agents (id, name, role, config, created_at, stats)
   - tasks (id, description, agent_id, status, result, metadata)
   - executions (id, task_id, started_at, completed_at, cost, tokens)
   - memories (id, agent_id, content, embedding, importance, accessed_at)

2. Supporting tables:
   - tools (id, name, description, config, usage_count)
   - conversations (id, agent_id, messages, context)
   - costs (id, timestamp, model, tokens, cost_usd, task_id)
   - errors (id, timestamp, error_type, details, task_id)

3. Optimization features:
   - Proper indexes for common queries
   - Partitioning for time-series data
   - JSON columns for flexible data
   - Full-text search on content
   - Materialized views for analytics

4. Constraints and triggers:
   - Foreign keys with CASCADE
   - Check constraints for data validity
   - Triggers for updated_at
   - Automatic archival of old data

5. Migration strategy:
   - Version tracking
   - Rollback capability
   - Zero-downtime migrations
   - Data integrity checks

Schema powinien:
- Wspierać 1M+ tasks
- Query performance <50ms
- Storage efficient
- Extension friendly

Przykład DDL:
[→ Zobacz plik: schema.sql](./src/faza-4/schema.sql)

```
**Metryki Sukcesu**:
- ✅ Schema supports all features
- ✅ Queries optimized
- ✅ Storage efficient
- ✅ Migration ready

**Walidacja**:
[→ Zobacz plik: validate_database_schema.py](./src/faza-4/validate_database_schema.py)

##### Task 4.1.2: Implement Data Access Layer (3h)

**Cel**: Clean, efficient data access layer

**Prompt dla AI Agent**:

```
Zaimplementuj Data Access Layer (DAL) dla LiteCrewAI.

Komponenty:
1. Repository pattern:
   - BaseRepository (CRUD operations)
   - AgentRepository
   - TaskRepository
   - MemoryRepository
   - CostRepository

2. Query builders:
   - Fluent interface
   - Type-safe queries
   - SQL injection prevention
   - Query optimization

3. Connection management:
   - Connection pooling
   - Transaction support
   - Read/write splitting
   - Retry logic

4. Caching layer:
   - Query result caching
   - Entity caching
   - Cache invalidation
   - TTL management

5. Advanced features:
   - Batch operations
   - Lazy loading
   - Eager loading
   - Pagination helpers
   - Soft deletes

Przykład użycia:
```python
# Initialize repositories
agent_repo = AgentRepository(db)
task_repo = TaskRepository(db)

# Create agent
agent = Agent(name="researcher", role="research")
agent_id = await agent_repo.create(agent)

# Query with builder
tasks = await task_repo.query()
    .where("status", "=", "pending")
    .where("priority", ">", 5)
    .order_by("created_at", "DESC")
    .limit(10)
    .include("agent")  # Eager load
    .execute()

# Transaction example
async with db.transaction() as tx:
    task = await task_repo.create(task_data, tx)
    await agent_repo.update(agent_id, {"last_task": task.id}, tx)
    # Auto-commit or rollback

# Batch operations
await task_repo.create_many([task1, task2, task3])

# Caching
cached_agent = await agent_repo.find_cached(agent_id, ttl=300)
```

Layer powinien być testable i mockable.

```
**Metryki Sukcesu**:
- ✅ Clean API
- ✅ <10ms for simple queries
- ✅ Transaction support
- ✅ 100% test coverage

**Walidacja**:
[→ Zobacz plik: validate_data_access_layer.py](./src/faza-4/validate_data_access_layer.py)

##### Task 4.1.3: Add Vector Storage Support (2h)

**Cel**: Wsparcie dla vector embeddings

**Prompt dla AI Agent**:

```
Dodaj wsparcie dla vector storage w LiteCrewAI używając sqlite-vec.

Komponenty:
1. Vector storage setup:
   - Install sqlite-vec extension
   - Create vector tables
   - Index configuration
   - Dimension management

2. Embedding operations:
   - Store embeddings
   - Similarity search
   - Batch operations
   - Hybrid search (vector + keyword)

3. Vector indexes:
   - HNSW index
   - IVF index
   - Optimization settings
   - Rebuild strategies

4. Integration features:
   - Automatic embedding on insert
   - Embedding cache
   - Multiple embedding models
   - Dimension reduction

5. Search capabilities:
   - k-NN search
   - Range search
   - Filtered search
   - Re-ranking

Przykład:
```python
# Initialize vector store
vector_store = VectorStore(
    db=db,
    embedding_model="nomic-embed-text",
    dimension=768
)

# Store document with embedding
doc_id = await vector_store.add_document(
    content="LiteCrewAI is a lightweight agent framework",
    metadata={"source": "readme", "type": "description"}
)

# Search similar documents
results = await vector_store.search(
    query="agent framework for AI",
    k=5,
    filter={"type": "description"}
)

for result in results:
    print(f"Score: {result.score:.3f} - {result.content[:50]}...")

# Hybrid search (vector + keyword)
results = await vector_store.hybrid_search(
    vector_query="AI agents",
    keyword_query="framework OR library",
    k=10,
    alpha=0.7  # 70% vector, 30% keyword
)

# Batch operations
embeddings = await vector_store.embed_batch([doc1, doc2, doc3])
await vector_store.add_many(documents_with_embeddings)
```

```
**Metryki Sukcesu**:
- ✅ Vector search <100ms
- ✅ 95%+ recall@10
- ✅ Batch embedding efficient
- ✅ Hybrid search works

**Walidacja**:
[→ Zobacz plik: validate_vector_storage.py](./src/faza-4/validate_vector_storage.py)

### Blok 4.2: Cache Implementation

**Czas**: 6h
**Cel**: Wielopoziomowy system cache

#### Zadania Atomowe:

##### Task 4.2.1: Design Multi-Level Cache (2h)

**Cel**: Efektywny multi-level cache system

**Prompt dla AI Agent**:

```
Zaprojektuj wielopoziomowy system cache dla LiteCrewAI.

Poziomy cache:
1. L1 - In-memory (process):
   - LRU cache w pamięci procesu
   - Ultra-fast (<1ms)
   - Limited size (100MB)
   - Per-worker isolation

2. L2 - Redis (shared):
   - Shared między workers
   - Fast (1-5ms)
   - Larger size (1GB)
   - Persistence optional

3. L3 - SQLite (persistent):
   - Disk-based
   - Slower (5-20ms)
   - Unlimited size
   - Queryable

Cache strategies:
1. Write strategies:
   - Write-through
   - Write-back
   - Write-around

2. Eviction policies:
   - LRU (Least Recently Used)
   - LFU (Least Frequently Used)
   - TTL-based
   - Size-based

3. Cache patterns:
   - Cache-aside
   - Read-through
   - Write-through
   - Refresh-ahead

Features:
- Automatic tier migration
- Cache warming
- Distributed invalidation
- Compression support
- Statistics tracking

Przykład:
```python
# Initialize multi-level cache
cache = MultiLevelCache(
    l1_size_mb=100,
    l2_size_mb=1000,
    l3_enabled=True,
    compression=True
)

# Simple usage
await cache.set("user:123", user_data, ttl=3600)
user = await cache.get("user:123")  # Checks L1→L2→L3

# Tagged caching
await cache.set("post:456", post_data, tags=["user:123", "posts"])
await cache.invalidate_tag("user:123")  # Invalidates related

# Batch operations
await cache.mset({
    "key1": value1,
    "key2": value2
})

# Cache statistics
stats = cache.get_stats()
print(f"L1 hit rate: {stats.l1_hit_rate:.1%}")
print(f"L2 hit rate: {stats.l2_hit_rate:.1%}")
```

```
**Metryki Sukcesu**:
- ✅ L1 latency <1ms
- ✅ L2 latency <5ms
- ✅ 90%+ combined hit rate
- ✅ Automatic tier migration

**Walidacja**:
[→ Zobacz plik: validate_multi_level_cache.py](./src/faza-4/validate_multi_level_cache.py)

##### Task 4.2.2: Implement Redis Cache Layer (2h)

**Cel**: Wydajny Redis cache layer

**Prompt dla AI Agent**:

```
Zaimplementuj Redis cache layer dla LiteCrewAI z advanced features.

Funkcjonalności:
1. Connection management:
   - Connection pooling
   - Sentinel support
   - Cluster support
   - Automatic reconnection
   - Pipeline batching

2. Data structures:
   - Strings (basic cache)
   - Hashes (object cache)
   - Lists (queues)
   - Sets (tags, relationships)
   - Sorted sets (rankings, scores)
   - Streams (event logs)

3. Advanced caching:
   - Sliding expiration
   - Probabilistic expiration
   - Cache stampede prevention
   - Lazy deletion
   - Memory optimization

4. Patterns implementation:
   - Cache-aside pattern
   - Write-through pattern
   - Event sourcing
   - Pub/sub for invalidation
   - Lua scripting

5. Monitoring:
   - Memory usage tracking
   - Hit/miss ratios
   - Slow query log
   - Key distribution
   - Hot key detection

Przykład użycia:
```python
# Initialize Redis cache
redis_cache = RedisCache(
    url="redis://localhost:6379",
    pool_size=10,
    max_memory="100mb",
    eviction_policy="allkeys-lru"
)

# Basic operations
await redis_cache.set("key", value, ttl=3600)
value = await redis_cache.get("key")

# Atomic operations
new_value = await redis_cache.incr("counter", 1)
await redis_cache.expire("counter", 3600)

# Hash operations (object cache)
await redis_cache.hset("user:123", {
    "name": "John",
    "email": "john@example.com",
    "score": 100
})
user = await redis_cache.hgetall("user:123")

# Set operations (tags)
await redis_cache.sadd("tag:python", "post:1", "post:2")
posts = await redis_cache.smembers("tag:python")

# Pipeline for performance
async with redis_cache.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.incr("counter")
    results = await pipe.execute()

# Lua script for atomic operations
script = """
    local key = KEYS[1]
    local value = redis.call('get', key)
    if value then
        return redis.call('incr', key)
    else
        redis.call('set', key, 1)
        return 1
    end
"""
result = await redis_cache.eval(script, keys=["visitor_count"])

# Pub/sub for cache invalidation
await redis_cache.publish("cache_invalidate", "user:*")
```

Include monitoring dashboard.

```
**Metryki Sukcesu**:
- ✅ <1ms latency for basic ops
- ✅ Pipeline 10x faster
- ✅ Memory usage optimized
- ✅ Connection pool efficient

**Walidacja**:
[→ Zobacz plik: validate_redis_cache.py](./src/faza-4/validate_redis_cache.py)

##### Task 4.2.3: Build Query Result Cache (2h)

**Cel**: Inteligentny cache dla query results

**Prompt dla AI Agent**:

```
Zbuduj inteligentny query result cache dla LiteCrewAI.

Funkcjonalności:
1. Query fingerprinting:
   - SQL normalization
   - Parameter extraction
   - Query pattern detection
   - Semantic hashing

2. Smart invalidation:
   - Table-based invalidation
   - Row-level tracking
   - Dependency graphs
   - Time-based expiry

3. Result optimization:
   - Compression
   - Partial results
   - Incremental updates
   - Result streaming

4. Cache strategies:
   - Read-through
   - Refresh-ahead
   - Write-behind
   - Lazy loading

5. Analytics:
   - Hit rate by query type
   - Cache efficiency
   - Memory usage
   - Performance impact

Przykład:
```python
# Initialize query cache
query_cache = QueryResultCache(
    max_size_mb=500,
    ttl_default=3600,
    compression=True
)

# Automatic caching with decorator
@query_cache.cached(ttl=7200)
async def get_user_stats(user_id: int):
    return await db.query(
        "SELECT * FROM user_stats WHERE user_id = ?",
        user_id
    )

# Manual caching
query = "SELECT * FROM agents WHERE status = ?"
params = ["active"]

result = await query_cache.get_or_fetch(
    query=query,
    params=params,
    fetcher=lambda: db.execute(query, params),
    ttl=3600,
    tags=["agents", "status"]
)

# Invalidation
await query_cache.invalidate_table("agents")
await query_cache.invalidate_tag("status")

# Refresh-ahead for important queries
await query_cache.schedule_refresh(
    query="SELECT COUNT(*) FROM tasks",
    interval=300,  # Every 5 minutes
    priority="high"
)

# Analytics
stats = query_cache.get_analytics()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Top queries: {stats.top_queries}")
print(f"Memory saved: {stats.bytes_saved:,}")
```

System powinien być transparent dla aplikacji.

```
**Metryki Sukcesu**:
- ✅ 80%+ hit rate
- ✅ <5ms cache lookup
- ✅ Automatic invalidation
- ✅ 50%+ memory savings

**Walidacja**:
[→ Zobacz plik: validate_query_cache.py](./src/faza-4/validate_query_cache.py)

---

## 


---

[← Powrót do README](./README.md) | [← Faza 3: LLM](./faza-3-LLM.md) | [Następna faza: API →](./faza-5-api.md)
