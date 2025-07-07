"""Benchmark agent type system performance."""

import time
from statistics import mean, stdev

from litecrew.agent import Agent
from litecrew.agent_types import AgentTypeFactory


def benchmark_agent_creation():
    """Benchmark agent creation with and without types."""
    iterations = 100
    
    # Baseline: Regular agent
    regular_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        agent = Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
        end = time.perf_counter()
        regular_times.append((end - start) * 1000)  # Convert to ms
    
    # Typed agents
    typed_times = {}
    for agent_type in ["conversational", "thinking", "moderator", "critic"]:
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            agent = Agent(
                role="Test Agent",
                goal="Test goal",
                backstory="Test backstory",
                type=agent_type,
                type_config={}
            )
            end = time.perf_counter()
            times.append((end - start) * 1000)
        typed_times[agent_type] = times
    
    # Results
    print("Agent Creation Performance:")
    print(f"Regular Agent: {mean(regular_times):.2f}ms ± {stdev(regular_times):.2f}ms")
    for agent_type, times in typed_times.items():
        overhead = mean(times) - mean(regular_times)
        print(f"{agent_type.capitalize()} Agent: {mean(times):.2f}ms ± {stdev(times):.2f}ms (overhead: {overhead:.2f}ms)")
    
    # Check if overhead is within spec (<5ms)
    max_overhead = max(mean(times) - mean(regular_times) for times in typed_times.values())
    print(f"\nMax type overhead: {max_overhead:.2f}ms")
    assert max_overhead < 5, f"Type overhead {max_overhead:.2f}ms exceeds 5ms limit"


def benchmark_type_operations():
    """Benchmark type-specific operations."""
    iterations = 1000
    
    # Type factory operations
    factory_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        types = AgentTypeFactory.list_types()
        info = AgentTypeFactory.get_type_info("critic")
        end = time.perf_counter()
        factory_times.append((end - start) * 1000)
    
    print("\nType Factory Operations:")
    print(f"List + Get Info: {mean(factory_times):.3f}ms ± {stdev(factory_times):.3f}ms")
    
    # Type validation
    agent = Agent(
        role="Test",
        goal="Test",
        backstory="Test",
        type="moderator",
        type_config={"moderation_style": "balanced"}
    )
    
    validation_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        agent.validate_type_config()
        end = time.perf_counter()
        validation_times.append((end - start) * 1000)
    
    print(f"Type Validation: {mean(validation_times):.3f}ms ± {stdev(validation_times):.3f}ms")
    
    # Get type info
    info_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        agent.get_type_info()
        end = time.perf_counter()
        info_times.append((end - start) * 1000)
    
    print(f"Get Type Info: {mean(info_times):.3f}ms ± {stdev(info_times):.3f}ms")


def benchmark_memory_usage():
    """Estimate memory usage of typed agents."""
    import sys
    
    # Regular agent
    regular_agent = Agent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory"
    )
    regular_size = sys.getsizeof(regular_agent.__dict__)
    
    # Typed agent
    typed_agent = Agent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory",
        type="critic",
        type_config={"criticism_level": "moderate"}
    )
    typed_size = sys.getsizeof(typed_agent.__dict__)
    
    overhead = typed_size - regular_size
    print(f"\nMemory Usage:")
    print(f"Regular Agent: ~{regular_size} bytes")
    print(f"Typed Agent: ~{typed_size} bytes")
    print(f"Type System Overhead: ~{overhead} bytes ({overhead/1024:.2f} KB)")
    
    # Check if memory overhead is reasonable (<1KB as documented)
    assert overhead < 1024, f"Memory overhead {overhead} bytes exceeds 1KB limit"


if __name__ == "__main__":
    print("=== Agent Type System Performance Benchmarks ===\n")
    
    benchmark_agent_creation()
    print()
    benchmark_type_operations()
    print()
    benchmark_memory_usage()
    
    print("\n✅ All performance metrics within specifications!")