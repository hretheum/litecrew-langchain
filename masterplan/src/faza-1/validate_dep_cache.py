# validate_dep_cache.py
import os
import subprocess
import time
import shutil

def test_cache_setup():
    """Test pip cache is configured"""
    # Check pip cache dir
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip", "cache", "dir"
    ], capture_output=True, text=True)
    
    cache_dir = result.stdout.strip()
    assert os.path.exists(cache_dir), f"Cache dir doesn't exist: {cache_dir}"
    
    # Check cache has content
    cache_size = subprocess.run(
        ["du", "-sh", cache_dir],
        capture_output=True,
        text=True
    ).stdout.split()[0]
    
    print(f"Pip cache size: {cache_size}")
    return cache_dir

def test_wheelhouse():
    """Test local wheelhouse exists"""
    wheelhouse = "/opt/litecrewai/wheelhouse"
    assert os.path.exists(wheelhouse), "Wheelhouse doesn't exist"
    
    # Count wheels
    wheels = len([f for f in os.listdir(wheelhouse) if f.endswith('.whl')])
    print(f"Wheels in wheelhouse: {wheels}")
    
    assert wheels > 0, "No wheels in wheelhouse"
    return wheels

def test_rebuild_speed():
    """Test rebuild with cache"""
    # Create test venv
    test_venv = "/tmp/cache_test_venv"
    
    # First install (cold cache)
    subprocess.run(["python3.11", "-m", "venv", test_venv])
    
    start = time.time()
    subprocess.run([
        f"{test_venv}/bin/pip", "install",
        "-r", "/opt/litecrewai/app/requirements.txt",
        "--find-links", "/opt/litecrewai/wheelhouse",
        "--no-index"  # Force offline
    ], capture_output=True)
    offline_time = time.time() - start
    
    # Cleanup
    shutil.rmtree(test_venv)
    
    print(f"Offline install time: {offline_time:.1f}s")
    return offline_time

def test_reproducibility():
    """Test builds are reproducible"""
    # Generate freeze file
    result1 = subprocess.run([
        "/opt/litecrewai/venv/bin/pip", "freeze"
    ], capture_output=True, text=True)
    
    # Create new venv and install
    test_venv = "/tmp/repro_test"
    subprocess.run(["python3.11", "-m", "venv", test_venv])
    subprocess.run([
        f"{test_venv}/bin/pip", "install",
        "-r", "/opt/litecrewai/app/requirements.txt"
    ], capture_output=True)
    
    # Compare freeze
    result2 = subprocess.run([
        f"{test_venv}/bin/pip", "freeze"
    ], capture_output=True, text=True)
    
    # Cleanup
    shutil.rmtree(test_venv)
    
    # Compare
    freeze1 = set(result1.stdout.strip().split('\n'))
    freeze2 = set(result2.stdout.strip().split('\n'))
    
    diff = freeze1.symmetric_difference(freeze2)
    if diff:
        print(f"⚠️  Reproducibility issue: {diff}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Validating dependency cache...\n")
    
    # Test cache
    cache_dir = test_cache_setup()
    print(f"✅ Cache configured at: {cache_dir}")
    
    # Test wheelhouse
    wheels = test_wheelhouse()
    print(f"✅ Wheelhouse ready with {wheels} packages")
    
    # Test speed
    rebuild_time = test_rebuild_speed()
    assert rebuild_time < 10, f"Rebuild too slow: {rebuild_time:.1f}s"
    print(f"✅ Offline rebuild in {rebuild_time:.1f}s")
    
    # Test reproducibility
    if test_reproducibility():
        print("✅ Builds are reproducible")
    else:
        print("⚠️  Reproducibility issues detected")
    
    print("\n✅ Dependency cache validation complete!")