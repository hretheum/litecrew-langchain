# validate_requirements.py
import os
import subprocess
import re

def check_requirements_structure():
    """Check all requirements files exist"""
    required_files = [
        "requirements.txt",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/optional.txt",
        "constraints.txt"
    ]
    
    base_dir = "/opt/litecrewai/app"
    missing = []
    
    for req_file in required_files:
        path = os.path.join(base_dir, req_file)
        if not os.path.exists(path):
            missing.append(req_file)
        else:
            # Check if pinned
            with open(path, 'r') as f:
                content = f.read()
                # Count unpinned dependencies
                unpinned = len(re.findall(r'^[a-zA-Z][^=<>]*$', content, re.MULTILINE))
                if unpinned > 0:
                    print(f"⚠️  {req_file} has {unpinned} unpinned dependencies")
    
    return missing

def test_pip_compile():
    """Test pip-compile works correctly"""
    os.chdir("/opt/litecrewai/app")
    
    # Test compile
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-compile",
        "requirements/base.txt",
        "--output-file", "/tmp/test-requirements.txt"
    ], capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ pip-compile failed: {result.stderr.decode()}")
        return False
    
    # Check output
    with open("/tmp/test-requirements.txt", 'r') as f:
        compiled = f.read()
        # Should have hashes
        assert "--hash=sha256:" in compiled, "No hashes in compiled requirements"
    
    return True

def check_security():
    """Run security check on dependencies"""
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-audit",
        "-r", "/opt/litecrewai/app/requirements.txt"
    ], capture_output=True, text=True)
    
    if "No known vulnerabilities" in result.stdout:
        return True, []
    else:
        # Parse vulnerabilities
        vulns = []
        for line in result.stdout.split('\n'):
            if 'VULNERABILITY' in line:
                vulns.append(line.strip())
        return False, vulns

def check_licenses():
    """Check dependency licenses"""
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/pip-licenses",
        "--format=json"
    ], capture_output=True, text=True)
    
    import json
    licenses = json.loads(result.stdout)
    
    # Check for problematic licenses
    problematic = ['GPL', 'AGPL', 'LGPL']
    issues = []
    
    for package in licenses:
        license_name = package.get('License', '')
        for prob in problematic:
            if prob in license_name:
                issues.append(f"{package['Name']}: {license_name}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Validating requirements structure...\n")
    
    # Check structure
    missing = check_requirements_structure()
    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print("✅ All requirements files present")
    
    # Test pip-compile
    if test_pip_compile():
        print("✅ pip-compile working")
    else:
        print("❌ pip-compile failed")
    
    # Security check
    secure, vulns = check_security()
    if secure:
        print("✅ No security vulnerabilities")
    else:
        print(f"❌ Security issues found: {len(vulns)}")
        for vuln in vulns[:3]:
            print(f"  - {vuln}")
    
    # License check
    license_issues = check_licenses()
    if license_issues:
        print(f"⚠️  Potential license issues: {license_issues}")
    else:
        print("✅ All licenses compatible")
    
    print("\n✅ Requirements validation complete!")