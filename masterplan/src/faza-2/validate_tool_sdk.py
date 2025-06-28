# validate_tool_sdk.py
import os
import subprocess
import tempfile
import json
from pathlib import Path

def test_cli_tool_creation():
    """Test CLI tool generator"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool_name = "test_weather"
        
        # Run tool creator
        result = subprocess.run([
            "litecrewai", "create-tool", tool_name,
            "--output", tmpdir
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Tool creation failed: {result.stderr}"
        
        # Check generated files
        tool_dir = Path(tmpdir) / tool_name
        assert tool_dir.exists()
        
        expected_files = [
            f"{tool_name}.py",
            f"test_{tool_name}.py",
            "requirements.txt",
            "README.md",
            "setup.py",
            ".gitignore"
        ]
        
        for file in expected_files:
            assert (tool_dir / file).exists(), f"Missing file: {file}"
        
        # Check content
        tool_file = tool_dir / f"{tool_name}.py"
        content = tool_file.read_text()
        assert "@tool" in content
        assert "def test_weather" in content
        assert '"""' in content  # Docstring
        
        print("✅ CLI tool creation validated")
        return tool_dir

def test_generated_tool():
    """Test that generated tool works"""
    tool_dir = test_cli_tool_creation()
    
    # Run tests on generated tool
    result = subprocess.run([
        "python", "-m", "pytest",
        str(tool_dir / "test_test_weather.py"),
        "-v"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Generated tests failed: {result.stderr}"
    print("✅ Generated tool tests pass")

def test_tool_packaging():
    """Test tool packaging system"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal tool
        tool_dir = Path(tmpdir) / "my_tool"
        tool_dir.mkdir()
        
        # Write tool file
        (tool_dir / "my_tool.py").write_text("""
from litecrewai.tools import tool

@tool
def my_tool(text: str) -> str:
    \"\"\"My custom tool\"\"\"
    return text.upper()
""")
        
        # Write setup.py
        (tool_dir / "setup.py").write_text("""
from setuptools import setup

setup(
    name="my_tool",
    version="1.0.0",
    py_modules=["my_tool"],
    install_requires=["litecrewai>=0.1.0"]
)
""")
        
        # Package tool
        os.chdir(tool_dir)
        result = subprocess.run([
            "python", "setup.py", "bdist_wheel"
        ], capture_output=True)
        
        assert result.returncode == 0
        assert (tool_dir / "dist").exists()
        assert any(f.endswith(".whl") for f in os.listdir(tool_dir / "dist"))
        
        print("✅ Tool packaging validated")

def test_documentation_generator():
    """Test documentation generation"""
    # Create test tool with docstring
    test_code = '''
from litecrewai.tools import tool

@tool
def advanced_calculator(
    expression: str,
    precision: int = 2,
    use_radians: bool = True
) -> float:
    """
    Advanced calculator with scientific functions.
    
    Args:
        expression: Mathematical expression to evaluate
        precision: Decimal places in result
        use_radians: Use radians for trig functions
        
    Returns:
        Calculated result
        
    Examples:
        >>> advanced_calculator("sin(pi/2)")
        1.0
        >>> advanced_calculator("2 ** 10", precision=0)
        1024.0
    """
    # Implementation here
    return eval(expression)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
        f.write(test_code)
        f.flush()
        
        # Generate documentation
        result = subprocess.run([
            "litecrewai", "generate-docs",
            "--tool", f.name,
            "--format", "markdown"
        ], capture_output=True, text=True)
        
        docs = result.stdout
        
        # Check documentation content
        assert "# advanced_calculator" in docs
        assert "Mathematical expression to evaluate" in docs
        assert "Examples:" in docs
        assert "sin(pi/2)" in docs
        
        print("✅ Documentation generation validated")

def test_development_tools():
    """Test development utilities"""
    # Test debug mode
    os.environ["LITECREWAI_DEBUG"] = "1"
    
    from litecrewai.tools.debug import ToolDebugger
    from litecrewai.tools import tool
    
    @tool
    def debug_test(x: int) -> int:
        return x * 2
    
    debugger = ToolDebugger()
    
    # Wrap tool with debugger
    wrapped = debugger.wrap(debug_test)
    
    # Execute and check debug info
    result = wrapped(5)
    assert result == 10
    
    debug_info = debugger.get_last_execution()
    assert debug_info["tool_name"] == "debug_test"
    assert debug_info["args"] == {"x": 5}
    assert debug_info["result"] == 10
    assert "execution_time" in debug_info
    assert "memory_used" in debug_info
    
    print("✅ Development tools validated")

def test_ide_integration():
    """Test IDE integration files"""
    # Check VS Code snippets
    snippets_file = Path.home() / ".config/Code/User/snippets/litecrewai.json"
    
    if snippets_file.exists():
        snippets = json.loads(snippets_file.read_text())
        assert "LiteCrewAI Tool" in snippets
        print("✅ VS Code integration found")
    else:
        print("⚠️  VS Code snippets not installed")
    
    # Check for .editorconfig
    editorconfig = Path("/opt/litecrewai/app/.editorconfig")
    if editorconfig.exists():
        content = editorconfig.read_text()
        assert "indent_size = 4" in content
        print("✅ EditorConfig present")

if __name__ == "__main__":
    print("🔍 Validating Tool Development Kit...\n")
    
    # Check if CLI is installed
    result = subprocess.run(["which", "litecrewai"], capture_output=True)
    if result.returncode != 0:
        print("⚠️  LiteCrewAI CLI not installed")
        print("Skipping CLI-based tests")
    else:
        test_cli_tool_creation()
        test_generated_tool()
        test_documentation_generator()
    
    test_tool_packaging()
    test_development_tools()
    test_ide_integration()
    
    print("\n✅ Tool Development Kit validation complete!")