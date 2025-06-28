# validate_no_enterprise.py
import os
import json
import subprocess

def check_removed_modules():
    """Check that enterprise modules are removed"""
    removed_modules = [
        'enterprise', 'cloud', 'billing', 'teams',
        'auth/sso', 'auth/saml', 'multi_tenant'
    ]
    
    app_dir = "/opt/litecrewai/app"
    issues = []
    
    for module in removed_modules:
        module_path = os.path.join(app_dir, module.replace('/', os.sep))
        if os.path.exists(module_path):
            issues.append(f"Enterprise module still exists: {module}")
    
    return issues

def check_cloud_dependencies():
    """Check for cloud provider dependencies"""
    cloud_packages = [
        'boto3', 'google-cloud', 'azure', 'stripe',
        'auth0', 'okta', 'datadog', 'newrelic'
    ]
    
    # Check in requirements
    req_file = "/opt/litecrewai/app/requirements.txt"
    issues = []
    
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            content = f.read().lower()
            for package in cloud_packages:
                if package in content:
                    issues.append(f"Cloud dependency found: {package}")
    
    return issues

def check_single_user():
    """Verify single-user simplification"""
    app_dir = "/opt/litecrewai/app"
    
    # Check for user/auth models
    auth_indicators = [
        'class User', 'class Team', 'class Organization',
        'def authenticate', 'def authorize', 'permissions.py'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for indicator in auth_indicators:
                        if indicator in content:
                            issues.append(f"Multi-user code in {filepath}: {indicator}")
    
    return issues

def calculate_size_reduction():
    """Calculate repository size reduction"""
    # This would compare with original size stored during fork
    result = subprocess.run(
        ["du", "-sh", "/opt/litecrewai/app"],
        capture_output=True,
        text=True
    )
    current_size = result.stdout.split()[0]
    
    print(f"Current repository size: {current_size}")
    
    # Count Python files
    result = subprocess.run(
        ["find", "/opt/litecrewai/app", "-name", "*.py", "-type", "f", "|", "wc", "-l"],
        shell=True,
        capture_output=True,
        text=True
    )
    py_files = int(result.stdout.strip())
    print(f"Python files remaining: {py_files}")

if __name__ == "__main__":
    print("🔍 Validating enterprise feature removal...")
    
    # Check modules
    module_issues = check_removed_modules()
    if module_issues:
        print("❌ Enterprise modules found:")
        for issue in module_issues:
            print(f"  - {issue}")
    else:
        print("✅ Enterprise modules removed")
    
    # Check dependencies
    dep_issues = check_cloud_dependencies()
    if dep_issues:
        print("❌ Cloud dependencies found:")
        for issue in dep_issues:
            print(f"  - {issue}")
    else:
        print("✅ Cloud dependencies removed")
    
    # Check single-user
    user_issues = check_single_user()
    if user_issues:
        print("❌ Multi-user code found:")
        for issue in user_issues[:3]:
            print(f"  - {issue}")
    else:
        print("✅ Simplified to single-user")
    
    # Size calculation
    calculate_size_reduction()
    
    # Final verdict
    total_issues = len(module_issues) + len(dep_issues) + len(user_issues)
    if total_issues == 0:
        print("\n✅ Enterprise features successfully removed!")
    else:
        print(f"\n❌ Found {total_issues} enterprise-related issues")
        exit(1)