# validate_python_env.py
import subprocess
import os
import toml

def test_venv():
    """Test virtual environment setup"""
    venv_python = "/opt/litecrewai/venv/bin/python"
    
    # Check venv exists
    assert os.path.exists(venv_python), "Venv not found"
    
    # Check Python version
    result = subprocess.run([venv_python, "--version"], capture_output=True, text=True)
    assert "3.11" in result.stdout, f"Wrong Python version: {result.stdout}"
    
    # Check installed packages
    packages = ["black", "ruff", "mypy", "pytest", "pre-commit"]
    result = subprocess.run([venv_python, "-m", "pip", "list"], capture_output=True, text=True)
    
    for package in packages:
        assert package in result.stdout, f"Missing package: {package}"
    
    print("✅ Virtual environment validated")

def test_precommit():
    """Test pre-commit configuration"""
    config_path = "/opt/litecrewai/.pre-commit-config.yaml"
    assert os.path.exists(config_path), "Pre-commit config not found"
    
    # Check hooks are installed
    git_dir = "/opt/litecrewai/.git/hooks"
    assert os.path.exists(f"{git_dir}/pre-commit"), "Pre-commit hook not installed"
    
    print("✅ Pre-commit validated")

def test_pyproject():
    """Test pyproject.toml configuration"""
    config_path = "/opt/litecrewai/pyproject.toml"
    assert os.path.exists(config_path), "pyproject.toml not found"
    
    config = toml.load(config_path)
    
    # Check tool configurations
    assert "tool" in config, "No tool section"
    assert "black" in config["tool"], "Black not configured"
    assert "ruff" in config["tool"], "Ruff not configured"
    assert "mypy" in config["tool"], "Mypy not configured"
    
    print("✅ pyproject.toml validated")

if __name__ == "__main__":
    test_venv()
    test_precommit()
    test_pyproject()
    print("✅ All Python environment checks passed!")