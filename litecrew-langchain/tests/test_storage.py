"""
Tests for the storage layer.
"""

import pytest
import asyncio
import tempfile
import shutil
import json
import time
from pathlib import Path
from typing import Dict, Any

from litecrew.storage import (
    StorageBackend,
    SQLiteStorage,
    RedisCache,
    StorageManager,
    ResultVersion,
    CompressionType
)


class TestSQLiteStorage:
    """Test SQLite storage backend."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def storage(self, temp_dir):
        """Create SQLite storage instance."""
        return SQLiteStorage(Path(temp_dir) / "test.db")
    
    def test_write_and_read(self, storage):
        """Test basic write and read operations."""
        key = "test_key"
        value = {"result": "test", "timestamp": time.time()}
        
        # Write
        start = time.perf_counter()
        storage.write(key, value)
        write_time = (time.perf_counter() - start) * 1000
        assert write_time < 10  # <10ms
        
        # Read
        start = time.perf_counter()
        result = storage.read(key)
        read_time = (time.perf_counter() - start) * 1000
        assert read_time < 5  # <5ms
        
        assert result == value
    
    def test_versioning(self, storage):
        """Test result versioning."""
        key = "versioned_key"
        
        # Write multiple versions
        for i in range(3):
            storage.write(key, {"version": i})
        
        # Get latest version
        latest = storage.read(key)
        assert latest["version"] == 2
        
        # Get specific version
        version_1 = storage.read(key, version=1)
        assert version_1["version"] == 0
        
        # List versions
        versions = storage.list_versions(key)
        assert len(versions) == 3
    
    def test_compression(self, storage):
        """Test data compression."""
        key = "compressed_key"
        large_value = {"data": "x" * 10000}  # 10KB of data
        
        # Write with compression
        storage.write(key, large_value, compress=True)
        
        # Read back
        result = storage.read(key)
        assert result == large_value
        
        # Check storage size is reduced
        raw_size = len(json.dumps(large_value))
        stored_size = storage.get_size(key)
        assert stored_size < raw_size * 0.8  # At least 20% compression
    
    def test_batch_operations(self, storage):
        """Test batch read/write."""
        items = {f"key_{i}": {"value": i} for i in range(10)}
        
        # Batch write
        start = time.perf_counter()
        storage.write_batch(items)
        batch_write_time = (time.perf_counter() - start) * 1000
        assert batch_write_time < 50  # <50ms for 10 items
        
        # Batch read
        keys = list(items.keys())
        start = time.perf_counter()
        results = storage.read_batch(keys)
        batch_read_time = (time.perf_counter() - start) * 1000
        assert batch_read_time < 20  # <20ms for 10 items
        
        assert results == items
    
    def test_search(self, storage):
        """Test search functionality."""
        # Add test data
        storage.write("agent_1_result", {"agent": "researcher", "score": 0.9})
        storage.write("agent_2_result", {"agent": "writer", "score": 0.8})
        storage.write("task_1_output", {"task": "research", "status": "complete"})
        
        # Search by pattern
        agent_results = storage.search("agent_*")
        assert len(agent_results) == 2
        
        # Test that search_by_metadata is not implemented
        with pytest.raises(NotImplementedError):
            storage.search_by_metadata({"score": {"$gte": 0.85}})


class TestRedisCache:
    """Test Redis cache layer."""
    
    @pytest.fixture
    def cache(self):
        """Create Redis cache instance (using mock)."""
        return RedisCache(mock=True)  # Use mock for tests
    
    def test_cache_operations(self, cache):
        """Test basic cache operations."""
        key = "cache_key"
        value = {"cached": True}
        
        # Set
        cache.set(key, value, ttl=60)
        
        # Get
        result = cache.get(key)
        assert result == value
        
        # Delete
        cache.delete(key)
        assert cache.get(key) is None
    
    def test_cache_expiry(self, cache):
        """Test cache TTL."""
        key = "expiring_key"
        value = {"temporary": True}
        
        # Set with 1 second TTL
        cache.set(key, value, ttl=1)
        assert cache.get(key) == value
        
        # Wait for expiry
        time.sleep(1.1)
        assert cache.get(key) is None
    
    def test_cache_stats(self, cache):
        """Test cache statistics."""
        # Perform operations
        cache.set("key1", {"value": 1})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        cache.get("key1")  # Hit
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2/3


class TestStorageManager:
    """Test unified storage manager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create storage manager instance."""
        return StorageManager(
            backend="sqlite",
            cache_enabled=True,
            db_path=Path(temp_dir) / "test.db"
        )
    
    def test_store_result(self, manager):
        """Test storing execution results."""
        result = {
            "crew_id": "test_crew",
            "task_id": "test_task",
            "agent": "researcher",
            "output": "Research findings...",
            "metadata": {
                "duration": 2.5,
                "tokens_used": 150
            }
        }
        
        # Store result
        result_id = manager.store_result(result)
        assert result_id is not None
        
        # Retrieve result
        retrieved = manager.get_result(result_id)
        assert retrieved["output"] == result["output"]
        assert retrieved["metadata"]["tokens_used"] == 150
    
    def test_caching_layer(self, manager):
        """Test cache integration."""
        result = {"data": "cached_data"}
        result_id = manager.store_result(result)
        
        # First read - from storage
        retrieved1 = manager.get_result(result_id)
        assert retrieved1["data"] == "cached_data"
        
        # Second read - from cache (faster)
        start = time.perf_counter()
        retrieved2 = manager.get_result(result_id)
        cache_time = (time.perf_counter() - start) * 1000
        assert cache_time < 1  # <1ms from cache
        assert retrieved2["data"] == "cached_data"
    
    def test_compression_threshold(self, manager):
        """Test automatic compression for large results."""
        small_result = {"data": "small"}
        large_result = {"data": "x" * 10000}
        
        # Small result - no compression
        small_id = manager.store_result(small_result)
        # Check if data size is small (compression happens in SQLite backend)
        small_size = manager._storage.get_size(small_id)
        assert small_size < 1024  # Small data
        
        # Large result - should be compressed
        large_id = manager.store_result(large_result)
        # Check compression happened by comparing sizes
        original_size = len(str(large_result))
        stored_size = manager._storage.get_size(large_id)
        assert stored_size < original_size * 0.8  # At least 20% compression
    
    @pytest.mark.asyncio
    async def test_async_operations(self, manager):
        """Test async storage operations."""
        results = []
        
        # Store multiple results concurrently
        async def store_async(i):
            result = {"task": f"task_{i}", "output": f"output_{i}"}
            return await manager.astore_result(result)
        
        ids = await asyncio.gather(*[store_async(i) for i in range(5)])
        assert len(ids) == 5
        
        # Retrieve concurrently
        async def get_async(result_id):
            return await manager.aget_result(result_id)
        
        retrieved = await asyncio.gather(*[get_async(id) for id in ids])
        assert len(retrieved) == 5
        assert all(r is not None for r in retrieved)


class TestResultVersioning:
    """Test result versioning functionality."""
    
    def test_version_creation(self):
        """Test creating result versions."""
        original = {"output": "v1"}
        version = ResultVersion.create(original)
        
        assert version.version == 1
        assert version.data == original
        assert version.parent_version is None
        assert version.timestamp is not None
    
    def test_version_chain(self):
        """Test version chain management."""
        v1 = ResultVersion.create({"output": "v1"})
        v2 = ResultVersion.create({"output": "v2"}, parent=v1)
        v3 = ResultVersion.create({"output": "v3"}, parent=v2)
        
        # Check chain
        assert v3.parent_version == 2
        assert v2.parent_version == 1
        assert v1.parent_version is None
        
        # Get version history
        history = v3.get_history([v1, v2, v3])
        assert len(history) == 3
        assert history[0].version == 1
        assert history[2].version == 3


def test_storage_metrics():
    """Test storage performance metrics."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = StorageManager(
            backend="sqlite",
            cache_enabled=True,
            db_path=Path(temp_dir) / "test.db"
        )
        
        # Store multiple results
        for i in range(100):
            manager.store_result({
                "task": f"task_{i}",
                "output": "x" * (i * 100),  # Varying sizes
                "metadata": {"index": i}
            })
        
        metrics = manager.get_metrics()
        
        # Check metrics
        assert metrics["total_stored"] == 100
        assert metrics["average_write_time_ms"] < 10
        assert metrics["average_read_time_ms"] < 5
        assert metrics["cache_hit_rate"] >= 0  # May be 0 if no cache hits yet
        assert 0 < metrics["compression_ratio"] < 1  # Compression ratio between 0 and 1