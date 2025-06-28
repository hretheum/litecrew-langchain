# validate_data_access_layer.py
import asyncio
import time
from unittest.mock import Mock, AsyncMock
import sqlite3
from litecrewai.dal import (
    DatabaseConnection, AgentRepository, TaskRepository,
    QueryBuilder, TransactionManager
)

async def test_repository_pattern():
    """Test repository implementation"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db)
    
    # Test create
    agent_data = {
        "name": "test_agent",
        "role": "assistant",
        "config": {"model": "gpt-3.5"}
    }
    
    agent_id = await agent_repo.create(agent_data)
    assert agent_id is not None
    print(f"✅ Created agent: {agent_id}")
    
    # Test read
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    assert agent.name == "test_agent"
    assert agent.role == "assistant"
    
    # Test update
    await agent_repo.update(agent_id, {"role": "researcher"})
    updated = await agent_repo.find(agent_id)
    assert updated.role == "researcher"
    
    # Test delete
    await agent_repo.delete(agent_id)
    deleted = await agent_repo.find(agent_id)
    assert deleted is None
    
    print("✅ CRUD operations working")

async def test_query_builder():
    """Test query builder functionality"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Insert test data
    for i in range(20):
        await task_repo.create({
            "description": f"Task {i}",
            "status": "pending" if i % 2 == 0 else "completed",
            "priority": i % 5,
            "agent_id": f"agent_{i % 3}"
        })
    
    # Test complex query
    results = await task_repo.query() \
        .where("status", "=", "pending") \
        .where("priority", ">=", 3) \
        .order_by("priority", "DESC") \
        .limit(5) \
        .execute()
    
    assert len(results) <= 5
    assert all(t.status == "pending" for t in results)
    assert all(t.priority >= 3 for t in results)
    
    # Check ordering
    priorities = [t.priority for t in results]
    assert priorities == sorted(priorities, reverse=True)
    
    print(f"✅ Query builder: found {len(results)} matching tasks")
    
    # Test aggregation
    count = await task_repo.query() \
        .where("status", "=", "completed") \
        .count()
    
    assert count == 10
    print(f"✅ Aggregation: {count} completed tasks")

async def test_transactions():
    """Test transaction support"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db)
    task_repo = TaskRepository(db)
    
    # Successful transaction
    async with db.transaction() as tx:
        agent_id = await agent_repo.create({
            "name": "tx_agent",
            "role": "assistant"
        }, tx)
        
        task_id = await task_repo.create({
            "description": "Transaction task",
            "agent_id": agent_id
        }, tx)
        
        # Should be visible within transaction
        agent = await agent_repo.find(agent_id, tx)
        assert agent is not None
    
    # Should be committed
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    print("✅ Transaction commit working")
    
    # Failed transaction
    try:
        async with db.transaction() as tx:
            agent_id2 = await agent_repo.create({
                "name": "tx_agent2",
                "role": "assistant"
            }, tx)
            
            # Force error
            raise Exception("Rollback test")
            
    except Exception:
        pass
    
    # Should be rolled back
    agent2 = await agent_repo.find_by("name", "tx_agent2")
    assert agent2 is None
    print("✅ Transaction rollback working")

async def test_connection_pooling():
    """Test connection pool functionality"""
    pool = DatabaseConnection(
        ":memory:",
        pool_size=5,
        max_overflow=2
    )
    await pool.initialize()
    
    # Test concurrent connections
    async def query_task(i):
        repo = AgentRepository(pool)
        await repo.create({
            "name": f"agent_{i}",
            "role": "assistant"
        })
        await asyncio.sleep(0.1)  # Simulate work
        return i
    
    # Run concurrent tasks
    start = time.time()
    tasks = [query_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start
    
    assert len(results) == 10
    assert duration < 2.0  # Should be concurrent
    
    print(f"✅ Connection pooling: 10 tasks in {duration:.2f}s")
    
    # Check pool stats
    stats = pool.get_pool_stats()
    assert stats["size"] <= 7  # pool_size + max_overflow
    assert stats["in_use"] == 0  # All returned
    print(f"✅ Pool stats: {stats}")

async def test_caching_layer():
    """Test query result caching"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    # Create repo with caching
    agent_repo = AgentRepository(db, enable_cache=True)
    
    # Create test agent
    agent_id = await agent_repo.create({
        "name": "cached_agent",
        "role": "assistant"
    })
    
    # First query (cache miss)
    start = time.time()
    agent1 = await agent_repo.find_cached(agent_id, ttl=60)
    time1 = time.time() - start
    
    # Second query (cache hit)
    start = time.time()
    agent2 = await agent_repo.find_cached(agent_id, ttl=60)
    time2 = time.time() - start
    
    assert agent1.id == agent2.id
    assert time2 < time1 / 10  # Much faster
    
    print(f"✅ Caching: {time1*1000:.1f}ms → {time2*1000:.1f}ms")
    
    # Test cache invalidation
    await agent_repo.update(agent_id, {"role": "researcher"})
    
    # Should get fresh data
    agent3 = await agent_repo.find_cached(agent_id, ttl=60)
    assert agent3.role == "researcher"
    print("✅ Cache invalidation working")

async def test_batch_operations():
    """Test batch insert/update/delete"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Batch create
    tasks_data = [
        {"description": f"Batch task {i}", "status": "pending"}
        for i in range(100)
    ]
    
    start = time.time()
    task_ids = await task_repo.create_many(tasks_data)
    batch_time = time.time() - start
    
    assert len(task_ids) == 100
    print(f"✅ Batch insert: 100 records in {batch_time:.2f}s")
    
    # Batch update
    updates = [
        {"id": task_id, "status": "completed"}
        for task_id in task_ids[:50]
    ]
    
    await task_repo.update_many(updates)
    
    # Verify
    completed = await task_repo.query() \
        .where("status", "=", "completed") \
        .count()
    
    assert completed == 50
    print("✅ Batch update: 50 records")
    
    # Batch delete
    await task_repo.delete_many(task_ids[50:])
    
    total = await task_repo.query().count()
    assert total == 50
    print("✅ Batch delete: 50 records")

async def test_pagination():
    """Test pagination helpers"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    task_repo = TaskRepository(db)
    
    # Insert test data
    for i in range(100):
        await task_repo.create({
            "description": f"Page task {i}",
            "priority": i
        })
    
    # Test pagination
    page1 = await task_repo.query() \
        .order_by("priority", "DESC") \
        .paginate(page=1, per_page=10)
    
    assert len(page1.items) == 10
    assert page1.total == 100
    assert page1.pages == 10
    assert page1.has_next == True
    assert page1.has_prev == False
    
    # Check correct items
    priorities = [t.priority for t in page1.items]
    assert priorities == list(range(99, 89, -1))
    
    print(f"✅ Pagination: page 1/{page1.pages}")
    
    # Test page 2
    page2 = await task_repo.query() \
        .order_by("priority", "DESC") \
        .paginate(page=2, per_page=10)
    
    assert page2.has_prev == True
    priorities2 = [t.priority for t in page2.items]
    assert priorities2 == list(range(89, 79, -1))

async def test_soft_deletes():
    """Test soft delete functionality"""
    db = DatabaseConnection(":memory:")
    await db.initialize()
    
    agent_repo = AgentRepository(db, soft_delete=True)
    
    # Create and soft delete
    agent_id = await agent_repo.create({
        "name": "soft_delete_test",
        "role": "assistant"
    })
    
    await agent_repo.delete(agent_id)
    
    # Should not be found normally
    agent = await agent_repo.find(agent_id)
    assert agent is None
    
    # But still in database
    agent = await agent_repo.find_with_deleted(agent_id)
    assert agent is not None
    assert agent.deleted_at is not None
    
    print("✅ Soft delete working")
    
    # Test restore
    await agent_repo.restore(agent_id)
    agent = await agent_repo.find(agent_id)
    assert agent is not None
    assert agent.deleted_at is None
    
    print("✅ Soft delete restore working")

if __name__ == "__main__":
    print("🔍 Validating data access layer...\n")
    
    async def run_tests():
        await test_repository_pattern()
        await test_query_builder()
        await test_transactions()
        await test_connection_pooling()
        await test_caching_layer()
        await test_batch_operations()
        await test_pagination()
        await test_soft_deletes()
    
    asyncio.run(run_tests())
    
    print("\n✅ Data access layer validation complete!")