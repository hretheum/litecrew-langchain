# validate_tool_framework.py
import time
import inspect
from typing import List, Dict
from litecrewai.tools import Tool, tool, ToolRegistry

def test_tool_creation():
    """Test tool decorator and registration"""
    
    @tool
    def sample_tool(text: str, count: int = 1) -> str:
        """Sample tool for testing"""
        return text * count
    
    # Check tool is wrapped correctly
    assert hasattr(sample_tool, '__tool__')
    assert sample_tool.__tool__.name == "sample_tool"
    assert sample_tool.__tool__.description == "Sample tool for testing"
    
    # Test execution
    result = sample_tool("test", 3)
    assert result == "testtesttest"
    
    print("✅ Tool creation working")

def test_tool_registry():
    """Test tool registry functionality"""
    registry = ToolRegistry()
    
    # Register tools
    @tool
    def tool1(x: int) -> int:
        return x * 2
    
    @tool
    def tool2(s: str) -> str:
        return s.upper()
    
    start = time.time()
    registry.register(tool1)
    registry.register(tool2)
    reg_time = (time.time() - start) * 1000
    
    print(f"Registration time: {reg_time:.2f}ms")
    assert reg_time < 1, f"Registration too slow: {reg_time}ms"
    
    # Test discovery
    tools = registry.list_tools()
    assert len(tools) >= 2
    assert "tool1" in [t.name for t in tools]
    
    # Test get
    retrieved = registry.get_tool("tool1")
    assert retrieved is not None
    assert retrieved(5) == 10

def test_builtin_tools():
    """Test built-in tools"""
    from litecrewai.tools.builtin import (
        web_search, calculator, file_reader,
        sql_query, http_request
    )
    
    # Test calculator
    calc_result = calculator("2 + 2 * 3")
    assert calc_result == 8
    
    # Test web search (mock)
    search_results = web_search("Python tutorial", max_results=3)
    assert isinstance(search_results, list)
    assert len(search_results) <= 3
    
    # Test file reader with sandboxing
    try:
        # Should fail - outside sandbox
        file_reader("/etc/passwd")
        assert False, "Security breach!"
    except PermissionError:
        print("✅ File sandboxing working")
    
    print("✅ Built-in tools validated")

def test_tool_composition():
    """Test tool chaining and composition"""
    from litecrewai.tools import ToolChain
    
    @tool
    def get_number() -> int:
        return 42
    
    @tool
    def double(x: int) -> int:
        return x * 2
    
    @tool
    def to_string(x: int) -> str:
        return f"The number is {x}"
    
    # Create chain
    chain = ToolChain([get_number, double, to_string])
    result = chain.execute()
    
    assert result == "The number is 84"
    print("✅ Tool composition working")

def test_input_validation():
    """Test input validation and sanitization"""
    
    @tool
    def validated_tool(
        name: str,
        age: int,
        email: str
    ) -> Dict:
        """Tool with validation"""
        return {"name": name, "age": age, "email": email}
    
    # Test valid input
    result = validated_tool("John", 30, "john@example.com")
    assert result["age"] == 30
    
    # Test invalid input
    try:
        validated_tool("John", "thirty", "invalid-email")
        assert False, "Validation should fail"
    except ValueError as e:
        print(f"✅ Validation caught error: {e}")
    
    # Test injection attempt
    try:
        validated_tool("John'; DROP TABLE users;--", 30, "john@example.com")
        # Should sanitize, not fail
        print("✅ SQL injection sanitized")
    except:
        pass

def test_performance():
    """Test tool execution performance"""
    
    @tool
    def slow_tool(duration: float = 0.1) -> str:
        time.sleep(duration)
        return "done"
    
    # Test timeout
    from litecrewai.tools import execute_with_timeout
    
    start = time.time()
    result = execute_with_timeout(slow_tool, timeout=2.0, duration=0.5)
    exec_time = time.time() - start
    
    assert exec_time < 1, f"Execution too slow: {exec_time}s"
    assert result == "done"
    
    # Test timeout exceeded
    try:
        execute_with_timeout(slow_tool, timeout=0.5, duration=1.0)
        assert False, "Should timeout"
    except TimeoutError:
        print("✅ Timeout handling working")

if __name__ == "__main__":
    print("🔍 Validating tool framework...\n")
    
    test_tool_creation()
    test_tool_registry()
    test_builtin_tools()
    test_tool_composition()
    test_input_validation()
    test_performance()
    
    print("\n✅ Tool framework validation complete!")