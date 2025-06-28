# validate_memory_system.py
import time
import sqlite3
import os
from litecrewai.memory import Memory, MemoryType

def test_memory_creation():
    """Test memory system initialization"""
    memory = Memory(agent_id="test_agent")
    
    # Check database created
    db_path = memory.db_path
    assert os.path.exists(db_path), "Memory database not created"
    
    # Check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ["short_term", "long_term", "semantic", "episodic"]
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"
    
    conn.close()
    return memory

def test_store_performance():
    """Test memory storage performance"""
    memory = Memory(agent_id="perf_test")
    
    # Test single store
    start = time.time()
    memory.store("test_key", "test_value", MemoryType.FACT)
    store_time = (time.time() - start) * 1000
    
    print(f"Single store time: {store_time:.1f}ms")
    assert store_time < 10, f"Store too slow: {store_time}ms"
    
    # Test bulk store
    start = time.time()
    for i in range(100):
        memory.store(f"key_{i}", f"value_{i}", MemoryType.FACT)
    bulk_time = time.time() - start
    
    print(f"100 stores time: {bulk_time:.2f}s")
    assert bulk_time < 1, f"Bulk store too slow: {bulk_time}s"

def test_retrieve_performance():
    """Test memory retrieval performance"""
    memory = Memory(agent_id="retrieve_test")
    
    # Populate with data
    for i in range(1000):
        memory.store(
            f"fact_{i}", 
            f"This is fact number {i} about topic {i % 10}",
            MemoryType.FACT
        )
    
    # Test retrieval
    start = time.time()
    results = memory.retrieve("topic 5", limit=10)
    retrieve_time = (time.time() - start) * 1000
    
    print(f"Retrieve from 1000 items: {retrieve_time:.1f}ms")
    assert retrieve_time < 50, f"Retrieve too slow: {retrieve_time}ms"
    assert len(results) <= 10
    assert all("topic 5" in r or "fact_5" in r for r in results)

def test_memory_limits():
    """Test memory size limits"""
    memory = Memory(agent_id="limit_test", max_size_mb=1)  # 1MB limit for test
    
    # Fill memory
    large_value = "x" * 1000  # 1KB
    stored = 0
    
    for i in range(2000):  # Try to store 2MB
        try:
            memory.store(f"large_{i}", large_value, MemoryType.FACT)
            stored += 1
        except:
            break
    
    # Check size limit enforced
    size_mb = memory.get_size_mb()
    print(f"Memory size: {size_mb:.2f}MB (stored {stored} items)")
    assert size_mb <= 1.1, f"Memory limit not enforced: {size_mb}MB"

def test_memory_types():
    """Test different memory types"""
    memory = Memory(agent_id="type_test")
    
    # Store different types
    memory.store("name", "John", MemoryType.FACT)
    memory.store("recent_query", "What's the weather?", MemoryType.SHORT_TERM)
    memory.store("conversation", ["Hi", "Hello", "How are you?"], MemoryType.EPISODIC)
    
    # Retrieve by type
    facts = memory.retrieve_by_type(MemoryType.FACT)
    assert any("John" in f for f in facts)
    
    short_term = memory.retrieve_by_type(MemoryType.SHORT_TERM)
    assert any("weather" in s for s in short_term)
    
    print("✅ Memory types working correctly")

def test_memory_operations():
    """Test memory operations"""
    memory = Memory(agent_id="ops_test")
    
    # Store some data
    for i in range(20):
        memory.store(f"old_{i}", f"value_{i}", MemoryType.FACT)
    
    time.sleep(1)  # Wait to create time difference
    
    for i in range(10):
        memory.store(f"new_{i}", f"value_{i}", MemoryType.FACT)
    
    # Test forget old
    forgotten = memory.forget(older_than_seconds=0.5)
    print(f"Forgotten {forgotten} old memories")
    assert forgotten >= 20
    
    # Test summarize
    summary = memory.summarize()
    assert isinstance(summary, str)
    assert len(summary) > 0
    print(f"Memory summary: {summary[:100]}...")
    
    # Test export/import
    exported = memory.export()
    assert isinstance(exported, dict)
    
    memory2 = Memory(agent_id="import_test")
    memory2.import_data(exported)
    assert memory2.get_size_mb() > 0

if __name__ == "__main__":
    print("🔍 Validating memory system...\n")
    
    # Test creation
    memory = test_memory_creation()
    print("✅ Memory system initialized")
    
    # Test performance
    test_store_performance()
    print("✅ Store performance validated")
    
    test_retrieve_performance()
    print("✅ Retrieve performance validated")
    
    # Test limits
    test_memory_limits()
    print("✅ Memory limits enforced")
    
    # Test types
    test_memory_types()
    
    # Test operations
    test_memory_operations()
    print("✅ Memory operations validated")
    
    print("\n✅ Memory system validation complete!")