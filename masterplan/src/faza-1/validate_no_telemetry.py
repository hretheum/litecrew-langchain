#!/usr/bin/env python3
"""
Validate No Telemetry
Checks if telemetry was completely removed from CrewAI
"""

import os
import subprocess
import sys
from pathlib import Path


def search_for_telemetry_references(repo_path):
    """Search for any remaining telemetry references"""
    telemetry_keywords = [
        "telemetry",
        "analytics",
        "tracking",
        "segment",
        "mixpanel",
        "opentelemetry",
        "telemetry.crewai.com"
    ]
    
    found_references = []
    
    for keyword in telemetry_keywords:
        # Search in Python files
        try:
            result = subprocess.run(
                ['grep', '-r', '-i', '--include=*.py', keyword, '.'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Filter out false positives
                    if ('telemetry_removed' not in line.lower() and
                        'telemetry removed' not in line.lower() and
                        '# telemetry' not in line.lower() and
                        'stub' not in line.lower()):
                        found_references.append(f"{keyword}: {line}")
        except Exception as e:
            return False, f"Error searching for {keyword}: {str(e)}"
    
    if found_references:
        return False, f"Found {len(found_references)} telemetry references:\n" + '\n'.join(found_references[:10])
    
    return True, "No telemetry references found"


def check_telemetry_directory_removed(repo_path):
    """Check that telemetry directory was removed"""
    telemetry_dirs = [
        "src/crewai/telemetry",
        "tests/telemetry"
    ]
    
    for dir_path in telemetry_dirs:
        full_path = os.path.join(repo_path, dir_path)
        if os.path.exists(full_path):
            return False, f"Telemetry directory still exists: {dir_path}"
    
    return True, "Telemetry directories removed"


def check_no_external_analytics_deps(repo_path):
    """Check for external analytics dependencies"""
    analytics_packages = [
        "segment",
        "mixpanel",
        "amplitude",
        "datadog",
        "newrelic",
        "sentry",
        "opentelemetry"
    ]
    
    # Check in requirements files
    requirements_files = [
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "requirements/base.txt"
    ]
    
    found_packages = []
    
    for req_file in requirements_files:
        file_path = os.path.join(repo_path, req_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().lower()
                for package in analytics_packages:
                    if package in content:
                        # Check if it's not in a comment
                        lines = content.split('\n')
                        for line in lines:
                            if package in line and not line.strip().startswith('#'):
                                found_packages.append(f"{package} in {req_file}")
    
    if found_packages:
        return False, f"Found analytics packages: {', '.join(found_packages)}"
    
    return True, "No external analytics dependencies"


def check_code_compiles(repo_path):
    """Basic check if Python files still compile"""
    try:
        # Try to compile a few key files
        key_files = [
            "src/crewai/__init__.py",
            "src/crewai/agent.py",
            "src/crewai/crew.py",
            "src/crewai/task.py"
        ]
        
        for file_path in key_files:
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', full_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return False, f"Compilation failed for {file_path}: {result.stderr}"
        
        return True, "Code compiles successfully"
    except Exception as e:
        return False, f"Error checking compilation: {str(e)}"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print("🔍 Validating Telemetry Removal...")
    print("=" * 50)
    
    checks = [
        ("Zero telemetry calls in code", lambda: search_for_telemetry_references(repo_path)),
        ("No external analytics dependencies", lambda: check_no_external_analytics_deps(repo_path)),
        ("Telemetry directories removed", lambda: check_telemetry_directory_removed(repo_path)),
        ("Code still compiles", lambda: check_code_compiles(repo_path))
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {message}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✅ All telemetry removal checks passed!")
        return 0
    else:
        print("❌ Some telemetry removal checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())