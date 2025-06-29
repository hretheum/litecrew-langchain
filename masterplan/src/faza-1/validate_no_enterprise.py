#!/usr/bin/env python3
"""
Validate No Enterprise Features
Checks if enterprise features were completely removed from CrewAI
"""

import os
import subprocess
import sys
from pathlib import Path


def check_no_enterprise_directories(repo_path):
    """Check that enterprise directories were removed"""
    enterprise_dirs = [
        "src/crewai/cli/authentication",
        "src/crewai/cli/deploy",
        "src/crewai/cli/organization",
        "src/crewai/cli/tools",
        "docs/en/enterprise",
        "docs/pt-BR/enterprise",
        "tests/cli/authentication",
        "tests/cli/deploy",
        "tests/cli/organization",
        "tests/cli/tools",
        "docs/images/enterprise"
    ]
    
    found_dirs = []
    for dir_path in enterprise_dirs:
        full_path = os.path.join(repo_path, dir_path)
        if os.path.exists(full_path):
            found_dirs.append(dir_path)
    
    if found_dirs:
        return False, f"Found enterprise directories: {', '.join(found_dirs)}"
    
    return True, "All enterprise directories removed"


def check_no_enterprise_files(repo_path):
    """Check that enterprise-specific files were removed"""
    enterprise_files = [
        "src/crewai/cli/plus_api.py",
        "docs/enterprise-api.yaml",
        "tests/cli/test_plus_api.py"
    ]
    
    found_files = []
    for file_path in enterprise_files:
        full_path = os.path.join(repo_path, file_path)
        if os.path.exists(full_path):
            found_files.append(file_path)
    
    if found_files:
        return False, f"Found enterprise files: {', '.join(found_files)}"
    
    return True, "All enterprise files removed"


def check_no_enterprise_dependencies(repo_path):
    """Check that enterprise dependencies were removed"""
    enterprise_deps = [
        "auth0-python",
        "stripe",
        "boto3",  # AWS SDK
        "google-cloud",
        "azure",
        "datadog",
        "newrelic"
    ]
    
    pyproject_path = os.path.join(repo_path, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        return False, "pyproject.toml not found"
    
    with open(pyproject_path, 'r') as f:
        content = f.read().lower()
    
    found_deps = []
    for dep in enterprise_deps:
        if dep.lower() in content:
            found_deps.append(dep)
    
    if found_deps:
        return False, f"Found enterprise dependencies: {', '.join(found_deps)}"
    
    return True, "No enterprise dependencies"


def check_single_user_mode(repo_path):
    """Check that code is simplified for single-user"""
    multi_user_keywords = [
        "multi_tenant",
        "organization_id",
        "team_id",
        "rbac",
        "permissions",
        "sso",
        "saml",
        "oauth",
        "PlusAPI",
        "PlusAPIMixin"
    ]
    
    found_keywords = []
    
    # Search in Python files
    for keyword in multi_user_keywords:
        try:
            result = subprocess.run(
                ['grep', '-r', '--include=*.py', keyword, 'src/'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                # Filter out false positives
                lines = result.stdout.strip().split('\n')
                valid_lines = [l for l in lines if 'test' not in l.lower() and 'example' not in l.lower()]
                if valid_lines:
                    found_keywords.append(f"{keyword} ({len(valid_lines)} occurrences)")
        except Exception:
            pass
    
    if found_keywords:
        return False, f"Found multi-user keywords: {', '.join(found_keywords[:5])}"
    
    return True, "Code simplified for single-user"


def check_core_functionality_intact(repo_path):
    """Check that core modules still exist"""
    core_modules = [
        "src/crewai/agent.py",
        "src/crewai/task.py",
        "src/crewai/crew.py",
        "src/crewai/memory",
        "src/crewai/tools",
        "src/crewai/flow",
        "src/crewai/knowledge"
    ]
    
    missing_modules = []
    for module in core_modules:
        full_path = os.path.join(repo_path, module)
        if not os.path.exists(full_path):
            missing_modules.append(module)
    
    if missing_modules:
        return False, f"Missing core modules: {', '.join(missing_modules)}"
    
    return True, "All core modules intact"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print("🔍 Validating Enterprise Feature Removal...")
    print("=" * 50)
    
    checks = [
        ("No enterprise directories", lambda: check_no_enterprise_directories(repo_path)),
        ("No enterprise files", lambda: check_no_enterprise_files(repo_path)),
        ("No enterprise dependencies", lambda: check_no_enterprise_dependencies(repo_path)),
        ("Single-user mode", lambda: check_single_user_mode(repo_path)),
        ("Core functionality intact", lambda: check_core_functionality_intact(repo_path))
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {message}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    # Check repository size reduction
    try:
        result = subprocess.run(
            ['du', '-sh', repo_path],
            capture_output=True,
            text=True
        )
        size = result.stdout.strip().split('\t')[0]
        print(f"📊 Repository size: {size}")
    except Exception:
        pass
    
    if all_passed:
        print("✅ All enterprise removal checks passed!")
        return 0
    else:
        print("❌ Some enterprise removal checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())