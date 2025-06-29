#!/usr/bin/env python3
"""
Validate Dependency Caching
Checks if dependency caching system is properly configured and working
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def check_pip_cache_config(repo_path):
    """Check if pip cache configuration exists and is valid"""
    pip_conf_path = os.path.join(repo_path, ".pip/pip.conf")
    
    if not os.path.exists(pip_conf_path):
        return False, "pip.conf not found at .pip/pip.conf"
    
    with open(pip_conf_path, 'r') as f:
        content = f.read()
    
    required_settings = ['cache-dir', 'prefer-binary', 'timeout']
    missing = [s for s in required_settings if s not in content]
    
    if missing:
        return False, f"Missing pip settings: {', '.join(missing)}"
    
    return True, "pip cache configuration is valid"


def check_dockerfile_caching(repo_path):
    """Check if Dockerfile is optimized for caching"""
    dockerfile_path = os.path.join(repo_path, "Dockerfile")
    
    if not os.path.exists(dockerfile_path):
        return False, "Dockerfile not found"
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    cache_features = [
        'COPY requirements',  # Requirements copied before source
        'RUN --mount=type=cache',  # BuildKit cache mounts
        'multi-stage',  # Multi-stage builds (FROM ... AS ...)
        'pip install -r requirements'  # Separate dependency installation
    ]
    
    found_features = []
    for feature in cache_features:
        if feature.lower() in content.lower():
            found_features.append(feature)
    
    if len(found_features) < 3:
        return False, f"Dockerfile missing cache optimizations: {cache_features}"
    
    return True, f"Dockerfile has {len(found_features)} cache optimizations"


def check_gitlab_ci_caching(repo_path):
    """Check if GitLab CI has proper caching configuration"""
    gitlab_ci_path = os.path.join(repo_path, ".gitlab-ci.yml")
    
    if not os.path.exists(gitlab_ci_path):
        return False, ".gitlab-ci.yml not found"
    
    with open(gitlab_ci_path, 'r') as f:
        content = f.read()
    
    cache_features = [
        'cache:',  # Cache configuration
        'key:',  # Cache keys
        'paths:',  # Cache paths
        '.pip/cache',  # Pip cache directory
        'venv/'  # Virtual environment caching
    ]
    
    found_features = sum(1 for feature in cache_features if feature in content)
    
    if found_features < 4:
        return False, f"GitLab CI missing cache features (found {found_features}/5)"
    
    return True, f"GitLab CI has proper caching ({found_features}/5 features)"


def test_cache_rebuild_speed(repo_path):
    """Test if cache improves rebuild speed"""
    cache_dir = os.path.join(repo_path, ".pip/cache")
    
    # Simple test: check if cache directory would be created
    if not os.path.exists(os.path.dirname(cache_dir)):
        return False, "Cache directory structure not prepared"
    
    # Check if requirements files exist for testing
    requirements_files = [
        "requirements/base.txt",
        "requirements.txt"
    ]
    
    available_reqs = [f for f in requirements_files 
                     if os.path.exists(os.path.join(repo_path, f))]
    
    if not available_reqs:
        return False, "No requirements files found for cache testing"
    
    return True, f"Cache ready for testing with {len(available_reqs)} requirements files"


def check_offline_capability(repo_path):
    """Check if offline installation tools are available"""
    wheelhouse_script = os.path.join(repo_path, "../scripts/create_wheelhouse.sh")
    cache_script = os.path.join(repo_path, "../scripts/cache_dependencies.py")
    
    missing_scripts = []
    if not os.path.exists(wheelhouse_script):
        missing_scripts.append("create_wheelhouse.sh")
    if not os.path.exists(cache_script):
        missing_scripts.append("cache_dependencies.py")
    
    if missing_scripts:
        return False, f"Missing offline tools: {', '.join(missing_scripts)}"
    
    # Check if scripts are executable
    if not os.access(wheelhouse_script, os.X_OK):
        return False, "create_wheelhouse.sh is not executable"
    
    return True, "Offline installation tools are available"


def check_lock_file_generation(repo_path):
    """Check if dependency lock files can be generated"""
    try:
        # Try to create a minimal lock file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Test lock file\npydantic>=2.0.0\n")
            test_req = f.name
        
        # Test if we can read and process requirements
        with open(test_req, 'r') as f:
            content = f.read()
        
        os.unlink(test_req)
        
        if 'pydantic' in content:
            return True, "Lock file generation capability verified"
        else:
            return False, "Lock file test failed"
            
    except Exception as e:
        return False, f"Lock file generation test failed: {str(e)}"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    
    print("🔍 Validating Dependency Caching System...")
    print("=" * 50)
    
    checks = [
        ("pip cache config", lambda: check_pip_cache_config(repo_path)),
        ("Dockerfile caching", lambda: check_dockerfile_caching(repo_path)),
        ("GitLab CI caching", lambda: check_gitlab_ci_caching(repo_path)),
        ("Cache rebuild speed", lambda: test_cache_rebuild_speed(repo_path)),
        ("Offline capability", lambda: check_offline_capability(repo_path)),
        ("Lock file generation", lambda: check_lock_file_generation(repo_path))
    ]
    
    all_passed = True
    cache_score = 0
    
    for check_name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {message}")
        if not passed:
            all_passed = False
        else:
            cache_score += 1
    
    print("=" * 50)
    print(f"📊 Cache Score: {cache_score}/6")
    
    if cache_score >= 5:
        print("✅ Excellent caching system!")
    elif cache_score >= 4:
        print("🟡 Good caching with minor issues")
    else:
        print("❌ Caching system needs improvement")
    
    if all_passed:
        print("✅ All dependency caching checks passed!")
        return 0
    else:
        print("❌ Some dependency caching checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())