"""
Benchmark LiteTask performance.
"""

import time
import statistics
import gc
from typing import List

from litecrew.task import LiteTask, TaskOutput
from litecrew.agent import LiteAgent


def benchmark_task_creation(num_tasks: int = 1000) -> dict:
    """Benchmark task creation time."""
    times = []
    
    for i in range(num_tasks):
        gc.collect()
        
        start = time.perf_counter()
        task = LiteTask(
            description=f"Task {i}: Perform analysis on dataset",
            expected_output=f"Analysis report for dataset {i}",
            async_execution=i % 2 == 0  # Mix async and sync
        )
        creation_time = time.perf_counter() - start
        times.append(creation_time)
    
    return {
        "count": num_tasks,
        "mean_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "total_ms": sum(times) * 1000,
    }


def benchmark_context_passing(context_sizes: List[int] = [1, 5, 10, 20]) -> dict:
    """Benchmark context passing performance."""
    results = {}
    
    for size in context_sizes:
        # Create context tasks
        context_tasks = []
        for i in range(size):
            task = LiteTask(description=f"Context task {i}")
            task.output = TaskOutput(
                raw=f"This is the output from context task {i} with some data"
            )
            context_tasks.append(task)
        
        # Create main task with context
        main_task = LiteTask(
            description="Process all context",
            context=context_tasks
        )
        
        # Measure context building
        times = []
        for _ in range(100):
            start = time.perf_counter()
            context = main_task._build_context()
            duration = time.perf_counter() - start
            times.append(duration)
        
        results[f"context_{size}"] = {
            "size": size,
            "mean_us": statistics.mean(times) * 1000000,  # microseconds
            "median_us": statistics.median(times) * 1000000,
            "context_length": len(context),
        }
    
    return results


def benchmark_task_execution() -> dict:
    """Benchmark task execution overhead."""
    # Create mock agent
    class MockAgent:
        def __init__(self):
            self.role = "Benchmark Agent"
            self.execution_time = 0.001  # 1ms simulated work
            
        def execute(self, task: str, context: str = "") -> str:
            # Simulate some work
            start = time.perf_counter()
            while time.perf_counter() - start < self.execution_time:
                pass
            return f"Completed: {task[:50]}"
    
    agent = MockAgent()
    
    # Benchmark single task
    single_times = []
    for i in range(100):
        task = LiteTask(
            description=f"Benchmark task {i}",
            agent=agent
        )
        
        start = time.perf_counter()
        output = task.execute()
        duration = time.perf_counter() - start
        single_times.append(duration)
    
    # Benchmark with context
    context_task = LiteTask(description="Generate context")
    context_task.output = TaskOutput(raw="Context data " * 100)
    
    context_times = []
    for i in range(100):
        task = LiteTask(
            description=f"Task with context {i}",
            agent=agent,
            context=[context_task]
        )
        
        start = time.perf_counter()
        output = task.execute()
        duration = time.perf_counter() - start
        context_times.append(duration)
    
    return {
        "single_task": {
            "mean_ms": statistics.mean(single_times) * 1000,
            "overhead_ms": (statistics.mean(single_times) - agent.execution_time) * 1000,
        },
        "with_context": {
            "mean_ms": statistics.mean(context_times) * 1000,
            "overhead_ms": (statistics.mean(context_times) - agent.execution_time) * 1000,
        }
    }


def benchmark_parallel_tasks(num_tasks: int = 10) -> dict:
    """Benchmark parallel task creation and setup."""
    start = time.perf_counter()
    
    tasks = []
    for i in range(num_tasks):
        task = LiteTask(
            description=f"Parallel task {i}",
            expected_output=f"Result {i}",
            async_execution=True
        )
        tasks.append(task)
    
    # Setup dependencies (each depends on previous)
    for i in range(1, len(tasks)):
        tasks[i].context = [tasks[i-1]]
    
    total_time = time.perf_counter() - start
    
    return {
        "num_tasks": num_tasks,
        "total_setup_ms": total_time * 1000,
        "per_task_ms": (total_time / num_tasks) * 1000,
    }


def main():
    """Run all benchmarks."""
    print("LiteTask Performance Benchmarks")
    print("=" * 50)
    
    # Benchmark 1: Task creation
    print("\n1. Task Creation Performance:")
    creation_stats = benchmark_task_creation(1000)
    print(f"   Created {creation_stats['count']} tasks")
    print(f"   Mean time:   {creation_stats['mean_ms']:.3f}ms")
    print(f"   Median time: {creation_stats['median_ms']:.3f}ms")
    print(f"   Total time:  {creation_stats['total_ms']:.1f}ms")
    
    # Check target
    target_ms = 1.0
    if creation_stats['mean_ms'] < target_ms:
        print(f"   ✅ PASS: Mean time < {target_ms}ms")
    else:
        print(f"   ❌ FAIL: Mean time >= {target_ms}ms")
    
    # Benchmark 2: Context passing
    print("\n2. Context Passing Performance:")
    context_stats = benchmark_context_passing()
    for key, stats in context_stats.items():
        print(f"   {key}: {stats['mean_us']:.1f}μs (median: {stats['median_us']:.1f}μs)")
    
    # Check latency
    max_latency_us = 100  # 0.1ms = 100μs
    all_fast = all(s['mean_us'] < max_latency_us for s in context_stats.values())
    if all_fast:
        print(f"   ✅ PASS: All context operations < {max_latency_us}μs")
    else:
        print(f"   ❌ FAIL: Some context operations >= {max_latency_us}μs")
    
    # Benchmark 3: Task execution
    print("\n3. Task Execution Overhead:")
    exec_stats = benchmark_task_execution()
    print(f"   Single task overhead: {exec_stats['single_task']['overhead_ms']:.2f}ms")
    print(f"   With context overhead: {exec_stats['with_context']['overhead_ms']:.2f}ms")
    
    # Benchmark 4: Parallel setup
    print("\n4. Parallel Task Setup:")
    parallel_stats = benchmark_parallel_tasks(100)
    print(f"   Tasks: {parallel_stats['num_tasks']}")
    print(f"   Total setup: {parallel_stats['total_setup_ms']:.1f}ms")
    print(f"   Per task: {parallel_stats['per_task_ms']:.3f}ms")
    
    print("\n" + "=" * 50)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()