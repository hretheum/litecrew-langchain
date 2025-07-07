"""Performance benchmarks for multi-process engine"""

import time
import asyncio
import psutil
import os
from typing import List

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask
from litecrew.processes import (
    ProcessFactory,
    ConversationalProcess,
    DebateProcess,
    PanelProcess
)
from litecrew.crew import LiteCrew


def test_process_instantiation():
    """Test process instantiation performance"""
    print("\n=== Process Instantiation Performance ===")
    
    process_types = ['sequential', 'hierarchical', 'conversational', 'debate', 'panel']
    
    for process_type in process_types:
        times = []
        for _ in range(100):
            start = time.perf_counter()
            process = ProcessFactory.create(process_type)
            duration = (time.perf_counter() - start) * 1000  # ms
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        print(f"{process_type}: {avg_time:.3f}ms (target: <10ms)")
        assert avg_time < 10, f"{process_type} instantiation too slow: {avg_time:.3f}ms"


def test_process_memory_overhead():
    """Test memory overhead of processes"""
    print("\n=== Process Memory Overhead ===")
    
    process = psutil.Process(os.getpid())
    
    # Baseline
    baseline = process.memory_info().rss
    
    # Create many processes
    processes = []
    for process_type in ['conversational', 'debate', 'panel']:
        for _ in range(50):
            p = ProcessFactory.create(process_type, {"verbose": True})
            processes.append(p)
    
    # Measure after
    after = process.memory_info().rss
    
    # Calculate overhead per process
    total_processes = len(processes)
    overhead_mb = (after - baseline) / (1024 * 1024) / total_processes
    
    print(f"Memory per process: {overhead_mb:.3f}MB (target: <1MB)")
    assert overhead_mb < 1, f"Process memory overhead too high: {overhead_mb:.3f}MB"


async def test_process_switching():
    """Test switching between process types"""
    print("\n=== Process Switching Performance ===")
    
    # Create crew
    agents = [
        LiteAgent(role=f"Agent{i}", goal="Work", backstory="Pro") 
        for i in range(3)
    ]
    tasks = [LiteTask(description=f"Task {i}") for i in range(3)]
    
    crew = LiteCrew(agents=agents, tasks=tasks, process="sequential")
    
    # Test switching between all process types
    process_types = ['hierarchical', 'conversational', 'debate', 'panel', 'sequential']
    
    switch_times = []
    for process_type in process_types:
        start = time.perf_counter()
        crew.switch_process(process_type)
        duration = (time.perf_counter() - start) * 1000  # ms
        switch_times.append(duration)
        print(f"Switch to {process_type}: {duration:.3f}ms")
    
    avg_switch = sum(switch_times) / len(switch_times)
    print(f"\nAverage switch time: {avg_switch:.3f}ms (target: <5ms)")
    assert avg_switch < 5, f"Process switching too slow: {avg_switch:.3f}ms"


async def test_turn_distribution():
    """Test turn distribution fairness in conversational process"""
    print("\n=== Turn Distribution Fairness ===")
    
    agents = [
        LiteAgent(role=f"Speaker{i}", goal="Discuss", backstory="Expert")
        for i in range(4)
    ]
    task = LiteTask(description="Discuss topic", expected_output="Consensus")
    
    # Mock execution
    for agent in agents:
        agent.execute = lambda desc, ctx: f"Response from {agent.role}"
    
    process = ConversationalProcess()
    process.min_turns = 3
    process.max_turns = 15
    
    result = await process.execute(agents, [task])
    
    # Check turn distribution
    turn_counts = result.metadata.get('agent_turns', {})
    
    if turn_counts:
        min_turns = min(turn_counts.values())
        max_turns = max(turn_counts.values())
        deviation = (max_turns - min_turns) / max(1, min_turns) * 100
        
        print(f"Turn counts: {turn_counts}")
        print(f"Turn deviation: {deviation:.1f}% (target: <20%)")
        
        assert deviation < 20, f"Turn distribution unfair: {deviation:.1f}% deviation"


async def test_conversation_flow_natural():
    """Test natural conversation flow metrics"""
    print("\n=== Conversation Flow Metrics ===")
    
    agents = [
        LiteAgent(role="Alice", goal="Collaborate", backstory="Designer"),
        LiteAgent(role="Bob", goal="Build", backstory="Developer"),
        LiteAgent(role="Carol", goal="Test", backstory="QA Engineer")
    ]
    task = LiteTask(description="Design new feature", expected_output="Feature spec")
    
    # Mock varied responses
    responses = {
        "Alice": ["I propose a clean UI design", "The user flow should be intuitive", "Let me refine the mockups"],
        "Bob": ["I can implement this with React", "We'll need API endpoints", "Performance looks good"],
        "Carol": ["We should test edge cases", "Accessibility is important", "I'll write test scenarios"]
    }
    
    response_counters = {agent.role: 0 for agent in agents}
    
    def mock_execute(agent_role):
        def execute(desc, ctx):
            idx = response_counters[agent_role]
            response_counters[agent_role] = (idx + 1) % len(responses[agent_role])
            return responses[agent_role][idx]
        return execute
    
    for agent in agents:
        agent.execute = mock_execute(agent.role)
    
    process = ConversationalProcess()
    process.min_turns = 2
    process.max_turns = 10
    
    start = time.perf_counter()
    result = await process.execute(agents, [task])
    duration = time.perf_counter() - start
    
    print(f"Conversation duration: {duration:.3f}s")
    print(f"Total turns: {len(result.turns)}")
    print(f"Min turns reached: {result.metadata.get('min_turns_reached', False)}")
    
    # Check flow metrics
    assert len(result.turns) >= 6  # At least min_turns per agent
    assert duration < 1.0  # Should be fast


def main():
    """Run all benchmarks"""
    print("Running Multi-Process Engine Performance Benchmarks...")
    
    # Synchronous tests
    test_process_instantiation()
    test_process_memory_overhead()
    
    # Async tests
    asyncio.run(test_process_switching())
    asyncio.run(test_turn_distribution())
    asyncio.run(test_conversation_flow_natural())
    
    print("\n✅ All performance benchmarks passed!")


if __name__ == "__main__":
    main()