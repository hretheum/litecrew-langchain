# validate_dependencies.py
import subprocess
import pkg_resources
import os

def count_dependencies():
    """Count and analyze dependencies"""
    # Get installed packages
    installed = {pkg.key: pkg for pkg in pkg_resources.working_set}
    
    # Filter out standard library
    external = []
    for name, pkg in installed.items():
        if not pkg.location.startswith('/usr/lib/python'):
            external.append((name, pkg.version))
    
    print(f"Total external packages: {len(external)}")
    
    # List them
    print("\nInstalled packages:")
    for name, version in sorted(external):
        print(f"  - {name}=={version}")
    
    return len(external)

def check_install_time():
    """Measure clean install time"""
    print("\n🕐 Testing install time...")
    
    # Create temp venv
    subprocess.run(["python3.11", "-m", "venv", "/tmp/test_venv"])
    
    # Time the install
    start = subprocess.time.time()
    result = subprocess.run([
        "/tmp/test_venv/bin/pip", "install", "-r", 
        "/opt/litecrewai/app/requirements.txt", "--no-cache-dir"
    ], capture_output=True)
    
    install_time = subprocess.time.time() - start
    
    # Cleanup
    subprocess.run(["rm", "-rf", "/tmp/test_venv"])
    
    print(f"Install time: {install_time:.1f}s")
    return install_time

def check_package_size():
    """Check total size of installed packages"""
    venv_path = "/opt/litecrewai/venv"
    site_packages = os.path.join(venv_path, "lib/python3.11/site-packages")
    
    # Get size
    result = subprocess.run(
        ["du", "-sh", site_packages],
        capture_output=True,
        text=True
    )
    size = result.stdout.split()[0]
    
    # Convert to MB
    if size.endswith('M'):
        size_mb = float(size[:-1])
    elif size.endswith('G'):
        size_mb = float(size[:-1]) * 1024
    else:
        size_mb = 0
    
    print(f"\nSite-packages size: {size} ({size_mb:.0f} MB)")
    return size_mb

def check_core_imports():
    """Verify core functionality still works"""
    core_imports = [
        "from litecrewai import Agent, Task, Crew",
        "from litecrewai.tools import Tool",
        "from litecrewai.memory import Memory"
    ]
    
    print("\n🔍 Testing core imports...")
    issues = []
    
    for import_stmt in core_imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except ImportError as e:
            issues.append(f"Failed: {import_stmt} - {e}")
            print(f"❌ {import_stmt}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Validating optimized dependencies...\n")
    
    # Count packages
    package_count = count_dependencies()
    assert package_count <= 15, f"Too many packages: {package_count}"
    
    # Check install time
    install_time = check_install_time()
    assert install_time < 30, f"Install too slow: {install_time:.1f}s"
    
    # Check size
    size_mb = check_package_size()
    assert size_mb < 100, f"Packages too large: {size_mb:.0f}MB"
    
    # Check imports
    import_issues = check_core_imports()
    assert len(import_issues) == 0, f"Import issues: {import_issues}"
    
    print("\n✅ All dependency checks passed!")