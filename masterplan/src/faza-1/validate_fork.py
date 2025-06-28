# validate_fork.py
import os
import subprocess
import git

def test_repo_structure():
    """Test forked repository structure"""
    repo_path = "/opt/litecrewai/app"
    
    # Check repo exists
    assert os.path.exists(f"{repo_path}/.git"), "Git repo not found"
    
    # Open repo
    repo = git.Repo(repo_path)
    
    # Check branch
    assert "lite-personal" in [b.name for b in repo.branches], "lite-personal branch not found"
    
    # Check no upstream remote
    remotes = [r.name for r in repo.remotes]
    assert "upstream" not in remotes, "Upstream remote should be removed"
    
    # Check report exists
    assert os.path.exists(f"{repo_path}/FORK_ANALYSIS.md"), "Analysis report not found"
    
    print("✅ Fork structure validated")

def test_repo_size():
    """Test repository size after fork"""
    repo_path = "/opt/litecrewai/app"
    
    # Get repo size
    result = subprocess.run(
        ["du", "-sh", repo_path],
        capture_output=True,
        text=True
    )
    size = result.stdout.split()[0]
    
    print(f"Repository size: {size}")
    
    # Count files
    result = subprocess.run(
        ["find", repo_path, "-type", "f", "-name", "*.py", "|", "wc", "-l"],
        shell=True,
        capture_output=True,
        text=True
    )
    py_files = int(result.stdout.strip())
    
    print(f"Python files: {py_files}")
    assert py_files > 10, "Too few Python files"

if __name__ == "__main__":
    test_repo_structure()
    test_repo_size()
    print("✅ Fork validation passed!")