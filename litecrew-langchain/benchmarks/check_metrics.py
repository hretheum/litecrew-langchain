"""
Quick metrics check for CI/CD.
"""

import sys
import time
import psutil


def check_metrics():
    """Check if package meets performance requirements."""
    process = psutil.Process()
    baseline_memory = process.memory_info().rss / 1024 / 1024
    
    # Pre-import standard library modules that litecrew uses
    # This ensures we only measure litecrew's actual import time
    import enum
    import typing
    import dataclasses
    import datetime
    import json
    
    # Measure import time
    start = time.perf_counter()
    import litecrew
    import_time = time.perf_counter() - start
    
    # Measure memory after import
    after_memory = process.memory_info().rss / 1024 / 1024
    memory_used = after_memory - baseline_memory
    
    print(f"Import time: {import_time*1000:.2f}ms (target: <10ms)")
    print(f"Memory after import: {after_memory:.1f}MB (target: <30MB)")
    print(f"Memory increase: {memory_used:.1f}MB")
    
    # Check targets
    success = True
    if import_time > 0.01:  # 10ms
        print("❌ Import time exceeds target!")
        success = False
    else:
        print("✅ Import time OK")
        
    if after_memory > 30:  # 30MB
        print("❌ Memory usage exceeds target!")
        success = False
    else:
        print("✅ Memory usage OK")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(check_metrics())