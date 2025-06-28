# validate_no_telemetry.py
import os
import ast
import subprocess

def scan_for_telemetry(directory):
    """Scan Python files for telemetry code"""
    telemetry_keywords = [
        'telemetry', 'analytics', 'tracking', 'segment',
        'mixpanel', 'amplitude', 'posthog', 'sentry'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk(directory):
        # Skip test and example directories
        if 'test' in root or 'example' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Check for keywords
                for keyword in telemetry_keywords:
                    if keyword.lower() in content.lower():
                        # Validate it's not a comment
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if keyword.lower() in line.lower() and not line.strip().startswith('#'):
                                issues.append(f"{filepath}:{i+1} - Found '{keyword}'")
    
    return issues

def check_dependencies():
    """Check for analytics dependencies in requirements"""
    req_files = [
        "/opt/litecrewai/app/requirements.txt",
        "/opt/litecrewai/app/setup.py",
        "/opt/litecrewai/app/pyproject.toml"
    ]
    
    analytics_packages = [
        'analytics-python', 'mixpanel', 'segment', 
        'amplitude', 'posthog', 'sentry-sdk'
    ]
    
    issues = []
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
                for package in analytics_packages:
                    if package in content:
                        issues.append(f"{req_file} - Found package '{package}'")
    
    return issues

def check_env_vars():
    """Check for telemetry-related environment variables"""
    env_file = "/opt/litecrewai/app/.env.example"
    telemetry_vars = [
        'TELEMETRY', 'ANALYTICS', 'TRACKING', 'SEGMENT',
        'MIXPANEL', 'SENTRY', 'POSTHOG'
    ]
    
    issues = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            for var in telemetry_vars:
                if var in content.upper():
                    issues.append(f".env.example - Found variable containing '{var}'")
    
    return issues

if __name__ == "__main__":
    print("🔍 Scanning for telemetry...")
    
    # Scan code
    code_issues = scan_for_telemetry("/opt/litecrewai/app")
    if code_issues:
        print("❌ Found telemetry in code:")
        for issue in code_issues[:5]:  # Show first 5
            print(f"  - {issue}")
        if len(code_issues) > 5:
            print(f"  ... and {len(code_issues) - 5} more")
    else:
        print("✅ No telemetry found in code")
    
    # Check dependencies
    dep_issues = check_dependencies()
    if dep_issues:
        print("❌ Found analytics dependencies:")
        for issue in dep_issues:
            print(f"  - {issue}")
    else:
        print("✅ No analytics dependencies")
    
    # Check env vars
    env_issues = check_env_vars()
    if env_issues:
        print("❌ Found telemetry env vars:")
        for issue in env_issues:
            print(f"  - {issue}")
    else:
        print("✅ No telemetry env vars")
    
    # Final verdict
    if not code_issues and not dep_issues and not env_issues:
        print("\n✅ Telemetry completely removed!")
    else:
        print(f"\n❌ Found {len(code_issues) + len(dep_issues) + len(env_issues)} telemetry issues")
        exit(1)