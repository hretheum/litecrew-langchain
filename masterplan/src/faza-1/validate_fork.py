#!/usr/bin/env python3
"""
Validate CrewAI Fork
Checks if the fork was created successfully
"""

import os
import subprocess
import sys
from pathlib import Path


def check_repo_exists(repo_path):
    """Check if repository exists and is a git repo"""
    if not os.path.exists(repo_path):
        return False, f"Repository path {repo_path} does not exist"
    
    git_dir = os.path.join(repo_path, '.git')
    if not os.path.exists(git_dir):
        return False, f"No .git directory found in {repo_path}"
    
    return True, "Repository exists"


def check_branch(repo_path, branch_name):
    """Check if specific branch exists"""
    try:
        result = subprocess.run(
            ['git', 'branch', '--list', branch_name],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if branch_name in result.stdout:
            return True, f"Branch '{branch_name}' exists"
        else:
            return False, f"Branch '{branch_name}' not found"
    except Exception as e:
        return False, f"Error checking branch: {str(e)}"


def check_report_exists(report_path):
    """Check if analysis report was generated"""
    if os.path.exists(report_path):
        size = os.path.getsize(report_path)
        if size > 1000:  # At least 1KB
            return True, f"Report exists ({size} bytes)"
        else:
            return False, "Report exists but is too small"
    else:
        return False, "Report not found"


def check_no_remote_origin(repo_path):
    """Check that original remote was removed"""
    try:
        result = subprocess.run(
            ['git', 'remote', '-v'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if 'crewAIInc/crewAI' in result.stdout:
            return False, "Original CrewAI remote still present"
        else:
            return True, "Original remote removed"
    except Exception as e:
        return False, f"Error checking remotes: {str(e)}"


def main():
    """Run all validation checks"""
    repo_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai-fork"
    report_path = "/Users/hretheum/dev/bezrobocie/crewAI/crewai_analysis_report.md"
    branch_name = "lite-personal"
    
    print("🔍 Validating CrewAI Fork...")
    print("=" * 50)
    
    checks = [
        ("Repository exists", lambda: check_repo_exists(repo_path)),
        ("Branch 'lite-personal' created", lambda: check_branch(repo_path, branch_name)),
        ("Analysis report generated", lambda: check_report_exists(report_path)),
        ("No connection to original repo", lambda: check_no_remote_origin(repo_path))
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
        print("✅ All validation checks passed!")
        return 0
    else:
        print("❌ Some validation checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())