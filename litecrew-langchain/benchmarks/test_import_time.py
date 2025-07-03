"""
Benchmark import time for LiteCrew.
"""

import subprocess
import sys
import time
import statistics


def measure_import_time(package: str, runs: int = 10) -> dict:
    """Measure import time for a package."""
    times = []
    
    for _ in range(runs):
        # Run in subprocess to ensure clean import
        cmd = [
            sys.executable, 
            "-c", 
            f"import time; start=time.perf_counter(); import {package}; print(time.perf_counter()-start)"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import_time = float(result.stdout.strip())
            times.append(import_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "runs": len(times),
    }


def main():
    """Run import time benchmarks."""
    print("Import Time Benchmark")
    print("=" * 50)
    
    # Benchmark LiteCrew
    print("\nMeasuring LiteCrew import time...")
    litecrew_stats = measure_import_time("litecrew")
    
    print(f"\nLiteCrew Import Time:")
    print(f"  Mean:   {litecrew_stats['mean']*1000:.2f}ms")
    print(f"  Median: {litecrew_stats['median']*1000:.2f}ms")
    print(f"  StdDev: {litecrew_stats['stdev']*1000:.2f}ms")
    print(f"  Min:    {litecrew_stats['min']*1000:.2f}ms")
    print(f"  Max:    {litecrew_stats['max']*1000:.2f}ms")
    
    # Check if we meet our target
    target_ms = 10  # 10ms target
    if litecrew_stats['mean'] * 1000 < target_ms:
        print(f"\n✅ PASS: Import time ({litecrew_stats['mean']*1000:.2f}ms) < {target_ms}ms")
    else:
        print(f"\n❌ FAIL: Import time ({litecrew_stats['mean']*1000:.2f}ms) >= {target_ms}ms")
    
    # Compare with other packages for reference
    print("\n" + "=" * 50)
    print("Comparison with other packages:")
    
    for package in ["langchain", "pydantic", "fastapi"]:
        try:
            stats = measure_import_time(package, runs=3)
            print(f"\n{package}:")
            print(f"  Mean: {stats['mean']*1000:.2f}ms")
        except:
            print(f"\n{package}: Failed to measure")


if __name__ == "__main__":
    main()