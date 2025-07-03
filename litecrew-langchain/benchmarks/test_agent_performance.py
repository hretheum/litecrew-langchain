"""
Benchmark LiteAgent performance.
"""

import time
import statistics
import psutil
import gc
from typing import List

from litecrew.agent import LiteAgent


def benchmark_agent_creation(num_agents: int = 100) -> dict:
    """Benchmark agent creation time."""
    times = []
    
    for i in range(num_agents):
        gc.collect()  # Clean garbage before measurement
        
        start = time.perf_counter()
        agent = LiteAgent(
            role=f"Agent {i}",
            goal=f"Goal for agent {i}",
            backstory=f"Backstory for agent {i}",
            verbose=False,
            memory=False  # Disable memory for pure creation test
        )
        creation_time = time.perf_counter() - start
        times.append(creation_time)
    
    return {
        "count": num_agents,
        "mean_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "stdev_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
    }


def benchmark_memory_usage() -> dict:
    """Benchmark memory usage per agent."""
    process = psutil.Process()
    gc.collect()
    
    # Baseline memory
    baseline_mb = process.memory_info().rss / 1024 / 1024
    
    # Create agents
    agents = []
    for i in range(10):
        agent = LiteAgent(
            role=f"Memory Test Agent {i}",
            goal=f"Test memory usage {i}",
            backstory=f"Created for memory testing {i}",
            verbose=False,
            memory=True  # Enable memory to test full agent
        )
        agents.append(agent)
    
    # Memory after creating agents
    gc.collect()
    after_mb = process.memory_info().rss / 1024 / 1024
    
    total_increase_mb = after_mb - baseline_mb
    per_agent_mb = total_increase_mb / len(agents)
    
    return {
        "baseline_mb": baseline_mb,
        "after_mb": after_mb,
        "total_increase_mb": total_increase_mb,
        "agents_created": len(agents),
        "per_agent_mb": per_agent_mb,
    }


def benchmark_with_tools() -> dict:
    """Benchmark agent creation with tools."""
    from langchain.tools import Tool
    
    # Create dummy tools
    tools = [
        Tool(
            name=f"tool_{i}",
            description=f"Test tool {i}",
            func=lambda x: f"Result from tool {i}"
        )
        for i in range(5)
    ]
    
    times = []
    for i in range(20):
        start = time.perf_counter()
        agent = LiteAgent(
            role=f"Tool Agent {i}",
            goal="Test with tools",
            backstory="Has many tools",
            tools=tools,
            verbose=False
        )
        creation_time = time.perf_counter() - start
        times.append(creation_time)
    
    return {
        "tools_count": len(tools),
        "runs": len(times),
        "mean_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
    }


def main():
    """Run all benchmarks."""
    print("LiteAgent Performance Benchmarks")
    print("=" * 50)
    
    # Benchmark 1: Agent creation
    print("\n1. Agent Creation Performance:")
    creation_stats = benchmark_agent_creation(100)
    print(f"   Created {creation_stats['count']} agents")
    print(f"   Mean time:   {creation_stats['mean_ms']:.2f}ms")
    print(f"   Median time: {creation_stats['median_ms']:.2f}ms")
    print(f"   Min time:    {creation_stats['min_ms']:.2f}ms")
    print(f"   Max time:    {creation_stats['max_ms']:.2f}ms")
    
    # Check against target
    target_ms = 10
    if creation_stats['mean_ms'] < target_ms:
        print(f"   ✅ PASS: Mean time < {target_ms}ms")
    else:
        print(f"   ❌ FAIL: Mean time >= {target_ms}ms")
    
    # Benchmark 2: Memory usage
    print("\n2. Memory Usage:")
    memory_stats = benchmark_memory_usage()
    print(f"   Baseline:    {memory_stats['baseline_mb']:.1f}MB")
    print(f"   After:       {memory_stats['after_mb']:.1f}MB") 
    print(f"   Increase:    {memory_stats['total_increase_mb']:.1f}MB")
    print(f"   Per agent:   {memory_stats['per_agent_mb']:.2f}MB")
    
    # Check against target
    target_per_agent_mb = 5
    if memory_stats['per_agent_mb'] < target_per_agent_mb:
        print(f"   ✅ PASS: Per agent < {target_per_agent_mb}MB")
    else:
        print(f"   ❌ FAIL: Per agent >= {target_per_agent_mb}MB")
    
    # Benchmark 3: With tools
    print("\n3. Agent with Tools:")
    tools_stats = benchmark_with_tools()
    print(f"   Tools count: {tools_stats['tools_count']}")
    print(f"   Mean time:   {tools_stats['mean_ms']:.2f}ms")
    print(f"   Median time: {tools_stats['median_ms']:.2f}ms")
    
    print("\n" + "=" * 50)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()