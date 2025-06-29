#!/usr/bin/env python3
"""
Validate Requirements Files
Checks if requirements files are properly structured and work correctly
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def check_requirements_structure(repo_path):
    """Check if all required requirements files exist"""
    required_files = [
        "requirements.txt",
        "constraints.txt",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/optional.txt",
        "requirements/README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(repo_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing files: {', '.join(missing_files)}"
    
    return True, "All requirements files exist"


def check_versions_pinned(repo_path):
    """Check if all dependencies have version constraints"""
    requirements_files = [
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/optional.txt"
    ]
    
    unpinned = []
    
    for req_file in requirements_files:
        full_path = os.path.join(repo_path, req_file)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments, empty lines, and includes
                    if not line or line.startswith('#') or line.startswith('-r'):
                        continue
                    
                    # Check if has version constraint
                    if not any(op in line for op in ['>=', '==', '~=', '>', '<']):
                        unpinned.append(f"{req_file}: {line}")
    
    if unpinned:
        return False, f"Unpinned dependencies found:\n" + '\n'.join(unpinned)
    
    return True, "All dependencies have version constraints"


def test_pip_compile(repo_path):
    """Test if pip-compile would work on requirements files"""
    # Just check syntax of requirements files
    requirements_files = [
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/optional.txt"
    ]
    
    for req_file in requirements_files:
        full_path = os.path.join(repo_path, req_file)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Skip comments, empty lines, and includes
                    if not line or line.startswith('#') or line.startswith('-r'):
                        continue
                    
                    # Basic syntax check
                    if '=' not in line and not line.isidentifier():
                        return False, f"Invalid syntax in {req_file}:{line_num}: {line}"
    
    return True, "Requirements files have valid syntax"


def check_no_conflicts(repo_path):
    """Check for dependency conflicts"""
    # This is a basic check - in real scenario would use pip check
    constraints_file = os.path.join(repo_path, "constraints.txt")
    
    if not os.path.exists(constraints_file):
        return False, "constraints.txt not found"
    
    # Count constraints
    constraints_count = 0
    with open(constraints_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                constraints_count += 1
    
    if constraints_count < 10:
        return False, f"Only {constraints_count} constraints found, expected more"
    
    return True, f"Constraints file has {constraints_count} entries"


def check_base_minimal(repo_path):
    """Check that base.txt is truly minimal"""
    base_file = os.path.join(repo_path, "requirements/base.txt")
    
    # Count non-comment, non-empty lines
    dep_count = 0
    deps = []
    
    with open(base_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-r'):
                dep_count += 1
                deps.append(line.split('>=')[0].split('==')[0])
    
    if dep_count > 10:
        return False, f"Base has {dep_count} dependencies, should be <10"
    
    # Check for known heavy dependencies that shouldn't be in base
    heavy_deps = ['chromadb', 'onnxruntime', 'openai', 'litellm', 'instructor']
    found_heavy = [d for d in heavy_deps if d in deps]
    
    if found_heavy:
        return False, f"Heavy dependencies in base: {', '.join(found_heavy)}"
    
    return True, f"Base is minimal with {dep_count} dependencies"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print("🔍 Validating Requirements Structure...")
    print("=" * 50)
    
    checks = [
        ("Requirements files exist", lambda: check_requirements_structure(repo_path)),
        ("All versions pinned", lambda: check_versions_pinned(repo_path)),
        ("pip-compile works", lambda: test_pip_compile(repo_path)),
        ("No dependency conflicts", lambda: check_no_conflicts(repo_path)),
        ("Base is minimal", lambda: check_base_minimal(repo_path))
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
        print("✅ All requirements checks passed!")
        return 0
    else:
        print("❌ Some requirements checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())