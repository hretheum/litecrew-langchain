# validate_agent_architecture.py
import time
import psutil
import os
from litecrewai.agent import Agent

def test_agent_creation():
    """Test agent creation performance"""
    start = time.time()
    
    agent = Agent(
        role="Test Agent",
        goal="Perform test tasks",
        tools=["calculator"],
        llm="ollama/mistral"
    )
    
    creation_time = time.time() - start
    print(f"Agent creation time: {creation_time*1000:.1f}ms")
    
    assert creation_time < 0.1, f"Creation too slow: {creation_time}s"
    assert agent.role == "Test Agent"
    assert agent.goal == "Perform test tasks"
    assert "calculator" in agent.tools
    
    return agent

def test_memory_usage():
    """Test agent memory footprint"""
    # Get baseline memory
    process = psutil.Process(os.getpid())
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create multiple agents
    agents = []
    for i in range(10):
        agent = Agent(
            role=f"Agent {i}",
            goal=f"Goal {i}",
            tools=["web_search", "calculator"],
            llm="ollama/mistral"
        )
        agents.append(agent)
    
    # Measure memory
    current_memory = process.memory_info().rss / 1024 / 1024
    memory_per_agent = (current_memory - baseline_memory) / 10
    
    print(f"Memory per agent: {memory_per_agent:.1f}MB")
    assert memory_per_agent < 10, f"Too much memory: {memory_per_agent:.1f}MB"

def test_execution():
    """Test agent execution"""
    agent = Agent(
        role="Calculator",
        goal="Perform calculations",
        tools=["calculator"],
        llm="ollama/mistral"
    )
    
    # Simple task
    start = time.time()
    result = agent.execute("What is 2 + 2?")
    execution_time = time.time() - start
    
    print(f"Execution time: {execution_time:.2f}s")
    print(f"Result: {result}")
    
    assert execution_time < 5, f"Execution too slow: {execution_time}s"
    assert result is not None
    assert "4" in str(result) or "four" in str(result).lower()

def test_serialization():
    """Test agent serialization"""
    agent = Agent(
        role="Serializable Agent",
        goal="Test serialization",
        tools=["web_search"],
        llm="ollama/phi"
    )
    
    # Serialize
    serialized = agent.to_dict()
    assert isinstance(serialized, dict)
    assert serialized["role"] == "Serializable Agent"
    
    # Deserialize
    agent2 = Agent.from_dict(serialized)
    assert agent2.role == agent.role
    assert agent2.goal == agent.goal
    assert agent2.tools == agent.tools
    
    print("✅ Serialization working")

def test_type_hints():
    """Test type hint coverage"""
    import inspect
    from typing import get_type_hints
    
    # Get all methods
    methods = inspect.getmembers(Agent, predicate=inspect.ismethod)
    
    typed_methods = 0
    total_methods = 0
    
    for name, method in methods:
        if not name.startswith('_'):
            total_methods += 1
            try:
                hints = get_type_hints(method)
                if hints:
                    typed_methods += 1
            except:
                pass
    
    coverage = typed_methods / total_methods * 100 if total_methods > 0 else 0
    print(f"Type hint coverage: {coverage:.1f}%")
    assert coverage > 80, f"Low type coverage: {coverage:.1f}%"

if __name__ == "__main__":
    print("🔍 Validating agent architecture...\n")
    
    # Test creation
    agent = test_agent_creation()
    print("✅ Agent creation validated")
    
    # Test memory
    test_memory_usage()
    print("✅ Memory usage validated")
    
    # Test execution
    test_execution()
    print("✅ Execution validated")
    
    # Test serialization
    test_serialization()
    
    # Test types
    test_type_hints()
    
    print("\n✅ Agent architecture validation complete!")