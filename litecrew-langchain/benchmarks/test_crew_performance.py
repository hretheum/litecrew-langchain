"""
Benchmark LiteCrew performance.
"""

import time
import statistics
import gc
from typing import List

from litecrew.crew import LiteCrew, ProcessType
from litecrew.agent import LiteAgent
from litecrew.task import LiteTask


def benchmark_crew_creation(num_agents: int = 10, num_tasks: int = 20) -> dict:
    """Benchmark crew creation time."""
    times = []
    
    # Pre-create agents and tasks to isolate crew creation
    agents = [
        LiteAgent(
            role=f"Agent{i}",
            goal=f"Goal{i}",
            backstory=f"Backstory{i}"
        )
        for i in range(num_agents)
    ]
    
    tasks = [
        LiteTask(
            description=f"Task{i}: Perform analysis",
            agent=agents[i % len(agents)]
        )
        for i in range(num_tasks)
    ]
    
    # Benchmark crew creation
    for _ in range(100):
        gc.collect()
        
        start = time.perf_counter()
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process=ProcessType.SEQUENTIAL
        )
        creation_time = time.perf_counter() - start
        times.append(creation_time)
    
    return {
        "agent_count": num_agents,
        "task_count": num_tasks,
        "mean_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
    }


def benchmark_crew_startup() -> dict:
    """Benchmark full crew startup including agent/task creation."""
    times = []
    
    for _ in range(50):
        gc.collect()
        
        start = time.perf_counter()
        
        # Create everything from scratch
        agents = [
            LiteAgent(
                role=f"Agent{i}",
                goal=f"Goal{i}",
                backstory=f"Story{i}"
            )
            for i in range(5)
        ]
        
        tasks = [
            LiteTask(
                description=f"Task{i}",
                agent=agents[i % 5]
            )
            for i in range(10)
        ]
        
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process=ProcessType.SEQUENTIAL
        )
        
        total_time = time.perf_counter() - start
        times.append(total_time)
    
    return {
        "mean_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
    }


def benchmark_crew_memory() -> dict:
    """Benchmark memory usage for crews of different sizes."""
    import psutil
    
    results = {}
    crew_sizes = [(5, 10), (10, 20), (20, 40), (50, 100)]
    
    for num_agents, num_tasks in crew_sizes:
        gc.collect()
        process = psutil.Process()
        before_memory = process.memory_info().rss
        
        # Create crew
        agents = [
            LiteAgent(
                role=f"Agent{i}",
                goal=f"Goal for agent {i}",
                backstory=f"Detailed backstory for agent {i}"
            )
            for i in range(num_agents)
        ]
        
        tasks = [
            LiteTask(
                description=f"Task {i}: Complex analysis task",
                expected_output=f"Detailed output for task {i}",
                agent=agents[i % num_agents]
            )
            for i in range(num_tasks)
        ]
        
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process=ProcessType.SEQUENTIAL
        )
        
        # Force GC and measure
        gc.collect()
        after_memory = process.memory_info().rss
        memory_increase = (after_memory - before_memory) / 1024 / 1024  # MB
        
        # Calculate using crew's estimation
        estimated_memory = crew.memory_usage() / 1024 / 1024  # MB
        
        results[f"{num_agents}a_{num_tasks}t"] = {
            "agents": num_agents,
            "tasks": num_tasks,
            "measured_mb": memory_increase,
            "estimated_mb": estimated_memory,
            "per_agent_kb": (memory_increase * 1024) / num_agents,
        }
    
    return results


def benchmark_process_types() -> dict:
    """Compare performance of different process types."""
    # Create standard crew setup
    agents = [
        LiteAgent(
            role=f"Agent{i}",
            goal=f"Goal{i}",
            backstory=f"Story{i}"
        )
        for i in range(5)
    ]
    
    tasks = [
        LiteTask(
            description=f"Task{i}",
            agent=agents[i % 5]
        )
        for i in range(10)
    ]
    
    results = {}
    
    for process_type in [ProcessType.SEQUENTIAL, ProcessType.HIERARCHICAL]:
        times = []
        
        for _ in range(50):
            start = time.perf_counter()
            crew = LiteCrew(
                agents=agents,
                tasks=tasks,
                process=process_type
            )
            duration = time.perf_counter() - start
            times.append(duration)
        
        results[process_type.value] = {
            "mean_ms": statistics.mean(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
        }
    
    return results


def main():
    """Run all benchmarks."""
    print("LiteCrew Performance Benchmarks")
    print("=" * 50)
    
    # Benchmark 1: Crew creation
    print("\n1. Crew Creation Performance:")
    creation_stats = benchmark_crew_creation(10, 20)
    print(f"   Agents: {creation_stats['agent_count']}, Tasks: {creation_stats['task_count']}")
    print(f"   Mean time:   {creation_stats['mean_ms']:.3f}ms")
    print(f"   Median time: {creation_stats['median_ms']:.3f}ms")
    
    # Check target
    target_ms = 50.0
    if creation_stats['mean_ms'] < target_ms:
        print(f"   ✅ PASS: Mean time < {target_ms}ms")
    else:
        print(f"   ❌ FAIL: Mean time >= {target_ms}ms")
    
    # Benchmark 2: Full startup
    print("\n2. Full Startup Time (5 agents, 10 tasks):")
    startup_stats = benchmark_crew_startup()
    print(f"   Mean time:   {startup_stats['mean_ms']:.3f}ms")
    print(f"   Median time: {startup_stats['median_ms']:.3f}ms")
    
    # Benchmark 3: Memory usage
    print("\n3. Memory Usage by Crew Size:")
    memory_stats = benchmark_crew_memory()
    for key, stats in memory_stats.items():
        print(f"   {stats['agents']} agents, {stats['tasks']} tasks:")
        print(f"     Measured: {stats['measured_mb']:.1f}MB")
        print(f"     Estimated: {stats['estimated_mb']:.1f}MB")
        print(f"     Per agent: {stats['per_agent_kb']:.0f}KB")
    
    # Check memory target
    largest_crew = memory_stats["50a_100t"]
    if largest_crew["per_agent_kb"] < 1024:  # <1MB per agent
        print("   ✅ PASS: Per-agent memory < 1MB")
    else:
        print("   ❌ FAIL: Per-agent memory >= 1MB")
    
    # Benchmark 4: Process types
    print("\n4. Process Type Comparison:")
    process_stats = benchmark_process_types()
    for process_type, stats in process_stats.items():
        print(f"   {process_type}: {stats['mean_ms']:.3f}ms (median: {stats['median_ms']:.3f}ms)")
    
    print("\n" + "=" * 50)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()