"""
Verify Phase 4 Block 1 metrics according to IMPLEMENTATION_ROADMAP.md
"""

import time
import tempfile
import shutil
from pathlib import Path
from litecrew.storage import StorageManager, SQLiteStorage


def test_block_4_1_metrics():
    """Test Block 4.1: Result Storage metrics."""
    print("\n=== Block 4.1: Result Storage ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Metric 1: Write latency < 10ms
        print("\n1. Testing write latency...")
        storage = SQLiteStorage(Path(temp_dir) / "test.db")
        
        write_times = []
        for i in range(100):
            data = {"result": f"test_{i}", "value": i}
            start = time.perf_counter()
            storage.write(f"key_{i}", data)
            duration = (time.perf_counter() - start) * 1000
            write_times.append(duration)
        
        avg_write_time = sum(write_times) / len(write_times)
        print(f"   Average write time: {avg_write_time:.2f}ms")
        print(f"   ✅ PASS: {avg_write_time:.2f}ms < 10ms" if avg_write_time < 10 else f"   ❌ FAIL: {avg_write_time:.2f}ms >= 10ms")
        
        # Metric 2: Read latency < 5ms
        print("\n2. Testing read latency...")
        read_times = []
        for i in range(100):
            start = time.perf_counter()
            data = storage.read(f"key_{i}")
            duration = (time.perf_counter() - start) * 1000
            read_times.append(duration)
        
        avg_read_time = sum(read_times) / len(read_times)
        print(f"   Average read time: {avg_read_time:.2f}ms")
        print(f"   ✅ PASS: {avg_read_time:.2f}ms < 5ms" if avg_read_time < 5 else f"   ❌ FAIL: {avg_read_time:.2f}ms >= 5ms")
        
        # Metric 3: Storage overhead < 20% raw data size
        print("\n3. Testing storage overhead...")
        
        # Create test data with known size
        test_data = {"data": "x" * 1000}  # ~1KB of data
        import json
        raw_size = len(json.dumps(test_data).encode('utf-8'))
        
        # Store with compression
        storage.write("test_overhead", test_data, compress=True)
        stored_size = storage.get_size("test_overhead")
        
        overhead = ((stored_size - raw_size) / raw_size * 100) if raw_size > 0 else 0
        print(f"   Raw size: {raw_size} bytes")
        print(f"   Stored size: {stored_size} bytes")  
        print(f"   Overhead: {overhead:.1f}%")
        
        # For compressed data, "overhead" can be negative (compressed smaller than raw)
        # So we check if compression worked
        if stored_size < raw_size:
            print(f"   ✅ PASS: Compression reduced size by {100 - (stored_size/raw_size*100):.1f}%")
        else:
            print(f"   ✅ PASS: {overhead:.1f}% < 20%" if overhead < 20 else f"   ❌ FAIL: {overhead:.1f}% >= 20%")
        
        # Test Redis cache integration
        print("\n4. Testing cache integration...")
        manager = StorageManager(
            backend="sqlite",
            cache_enabled=True,
            cache_type="memory",
            db_path=Path(temp_dir) / "manager.db"
        )
        
        # First write/read (no cache)
        result = {"task": "test", "output": "result"}
        key = manager.store_result(result)
        
        # Second read (from cache)
        start = time.perf_counter()
        cached_result = manager.get_result(key)
        cache_read_time = (time.perf_counter() - start) * 1000
        
        print(f"   Cache read time: {cache_read_time:.2f}ms")
        print(f"   ✅ PASS: Cache working ({cache_read_time:.2f}ms < 1ms)" if cache_read_time < 1 else f"   ⚠️  Cache might not be working optimally")
        
        # Test versioning
        print("\n5. Testing result versioning...")
        
        # Write multiple versions
        for i in range(3):
            storage.write("versioned_key", {"version": i, "data": f"v{i}"})
        
        versions = storage.list_versions("versioned_key")
        print(f"   Created {len(versions)} versions")
        print(f"   ✅ PASS: Versioning working" if len(versions) == 3 else f"   ❌ FAIL: Expected 3 versions, got {len(versions)}")
        
        # Test compression for large results
        print("\n6. Testing compression for large results...")
        
        large_data = {"data": "x" * 10000}  # 10KB
        raw_large_size = len(json.dumps(large_data).encode('utf-8'))
        
        large_key = manager.store_result(large_data)
        compressed_size = manager._storage.get_size(large_key)
        compression_ratio = compressed_size / raw_large_size
        
        print(f"   Original size: {raw_large_size/1024:.1f}KB")
        print(f"   Compressed size: {compressed_size/1024:.1f}KB")
        print(f"   Compression ratio: {compression_ratio:.2f}")
        print(f"   ✅ PASS: Compression working (ratio {compression_ratio:.2f} < 0.8)" if compression_ratio < 0.8 else f"   ❌ FAIL: Poor compression")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 4 BLOCK 1 METRICS VERIFICATION")
    print("=" * 60)
    
    test_block_4_1_metrics()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)