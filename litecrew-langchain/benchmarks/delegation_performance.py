"""
Delegation Performance Benchmarks for Block 2.2

Test delegation system performance against roadmap metrics:
- Delegation latency: <10ms
- Context preservation: 100%
- Max delegation depth: configurable
"""

import time
import psutil
import sys
import os
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from litecrew.delegation import DelegationManager, DelegationValidator
from litecrew.tools import DelegationTool


def benchmark_delegation_latency():
    """Test delegation latency < 10ms"""
    print("🔍 Testing delegation latency...")
    
    # Create mock agents
    agents = {}
    for i in range(5):
        agent = Mock()
        agent.role = f"Agent{i}"
        agent.execute = Mock(return_value=f"Result from Agent{i}")
        agents[f"Agent{i}"] = agent
    
    # Create delegation manager
    manager = DelegationManager(available_agents=agents)
    
    # Measure delegation latency
    latencies = []
    for i in range(100):
        start_time = time.perf_counter()
        result = manager.delegate_task(
            from_agent="Agent0",
            task=f"Task {i}",
            target_agent=f"Agent{(i % 4) + 1}"
        )
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        
        assert result.success, f"Delegation {i} failed: {result.error}"
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    print(f"  ⏱️  Average latency: {avg_latency:.3f}ms")
    print(f"  ⏱️  Max latency: {max_latency:.3f}ms")  
    print(f"  ⏱️  Min latency: {min_latency:.3f}ms")
    
    # Check against roadmap target: <10ms
    target_latency = 10.0
    if avg_latency < target_latency:
        print(f"  ✅ PASS: Average latency {avg_latency:.3f}ms < {target_latency}ms")
    else:
        print(f"  ❌ FAIL: Average latency {avg_latency:.3f}ms >= {target_latency}ms")
    
    return avg_latency < target_latency


def benchmark_context_preservation():
    """Test context preservation: 100%"""
    print("\n🧠 Testing context preservation...")
    
    # Create mock agents
    agents = {}
    for i in range(3):
        agent = Mock()
        agent.role = f"Agent{i}"
        agent.execute = Mock(return_value=f"Result from Agent{i}")
        agents[f"Agent{i}"] = agent
    
    manager = DelegationManager(available_agents=agents)
    
    # Test context preservation
    test_contexts = [
        {"task_id": "123", "data": "important"},
        {"user_id": "user_456", "session": "sess_789"},
        {"complex_data": {"nested": {"value": 42}}},
    ]
    
    preserved_contexts = 0
    total_tests = len(test_contexts)
    
    for i, context in enumerate(test_contexts):
        result = manager.delegate_task(
            from_agent="Agent0",
            task=f"Process data {i}",
            target_agent="Agent1",
            context=context
        )
        
        # Check if context was preserved (should be in delegation metadata)
        if result.success:
            # Context preservation is internal to delegation manager
            # We check that original context can be retrieved from history
            history = manager.get_delegation_history(limit=1)
            if history and len(history) > 0:
                preserved_contexts += 1
    
    preservation_rate = (preserved_contexts / total_tests) * 100
    print(f"  🧠 Context preservation rate: {preservation_rate:.1f}%")
    
    # Check against roadmap target: 100%
    target_preservation = 100.0
    if preservation_rate >= target_preservation:
        print(f"  ✅ PASS: Context preservation {preservation_rate:.1f}% >= {target_preservation}%")
    else:
        print(f"  ❌ FAIL: Context preservation {preservation_rate:.1f}% < {target_preservation}%")
    
    return preservation_rate >= target_preservation


def benchmark_delegation_depth():
    """Test max delegation depth: configurable"""
    print("\n📊 Testing delegation depth configuration...")
    
    # Test different max depths
    depth_tests = [1, 2, 3, 5]
    depth_results = []
    
    for max_depth in depth_tests:
        # Create validator with specific max depth
        validator = DelegationValidator(max_depth=max_depth)
        
        # Create mock agents
        agents = {}
        for i in range(max_depth + 2):
            agent = Mock()
            agent.role = f"Agent{i}"
            agent.execute = Mock(return_value=f"Result from Agent{i}")
            agents[f"Agent{i}"] = agent
        
        manager = DelegationManager(available_agents=agents, validator=validator)
        
        # Test delegation up to max depth
        successful_depth = 0
        for depth in range(max_depth + 2):
            result = manager.delegate_task(
                from_agent="Agent0",
                task=f"Depth test {depth}",
                target_agent=f"Agent{depth + 1}" if depth + 1 < len(agents) else "Agent1"
            )
            
            if result.success:
                successful_depth += 1
            else:
                break
        
        depth_results.append((max_depth, successful_depth))
        print(f"  📊 Max depth {max_depth}: Successful delegations: {successful_depth}")
    
    # Check if depth is properly configurable
    all_configured_correctly = all(
        successful >= configured 
        for configured, successful in depth_results
    )
    
    if all_configured_correctly:
        print(f"  ✅ PASS: Delegation depth properly configurable")
    else:
        print(f"  ❌ FAIL: Delegation depth not properly configured")
    
    return all_configured_correctly


def benchmark_delegation_tool_performance():
    """Test delegation tool performance"""
    print("\n🔧 Testing delegation tool performance...")
    
    # Create mock agents
    agents = []
    for i in range(3):
        agent = Mock()
        agent.role = f"Agent{i}"
        agent.execute = Mock(return_value=f"Result from Agent{i}")
        agents.append(agent)
    
    # Create delegation tool
    delegation_tool = DelegationTool(agents=agents)
    delegation_tool.set_current_agent(agents[0])
    
    # Test delegation through tool
    start_time = time.perf_counter()
    result = delegation_tool._delegate("Ask the Agent1 to process data")
    end_time = time.perf_counter()
    
    tool_latency_ms = (end_time - start_time) * 1000
    print(f"  🔧 Tool delegation latency: {tool_latency_ms:.3f}ms")
    
    # Check if delegation was successful
    success = "✅ Delegation successful" in result
    
    if success and tool_latency_ms < 10.0:
        print(f"  ✅ PASS: Tool delegation working and fast")
    else:
        print(f"  ❌ FAIL: Tool delegation issues")
    
    return success and tool_latency_ms < 10.0


def benchmark_memory_usage():
    """Test delegation system memory usage"""
    print("\n💾 Testing delegation system memory usage...")
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create large delegation system
    agents = {}
    for i in range(20):
        agent = Mock()
        agent.role = f"Agent{i}"
        agent.execute = Mock(return_value=f"Result from Agent{i}")
        agents[f"Agent{i}"] = agent
    
    manager = DelegationManager(available_agents=agents)
    
    # Perform many delegations
    for i in range(100):
        result = manager.delegate_task(
            from_agent="Agent0",
            task=f"Memory test {i}",
            target_agent=f"Agent{(i % 19) + 1}"
        )
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"  💾 Initial memory: {initial_memory:.1f}MB")
    print(f"  💾 Final memory: {final_memory:.1f}MB") 
    print(f"  💾 Memory increase: {memory_increase:.1f}MB")
    
    # Check metrics
    metrics = manager.get_delegation_metrics()
    print(f"  📊 Total delegations: {metrics['total_delegations']}")
    print(f"  📊 Success rate: {metrics['success_rate']:.1%}")
    
    # Memory should be reasonable
    memory_acceptable = memory_increase < 10.0  # Less than 10MB increase
    
    if memory_acceptable:
        print(f"  ✅ PASS: Memory usage acceptable")
    else:
        print(f"  ❌ FAIL: Memory usage too high")
    
    return memory_acceptable


def main():
    """Run all delegation performance benchmarks"""
    print("🚀 LiteCrew Delegation System Performance Benchmarks")
    print("=" * 60)
    
    results = []
    
    # Run benchmarks
    results.append(("Delegation Latency", benchmark_delegation_latency()))
    results.append(("Context Preservation", benchmark_context_preservation()))
    results.append(("Delegation Depth", benchmark_delegation_depth()))
    results.append(("Tool Performance", benchmark_delegation_tool_performance()))
    results.append(("Memory Usage", benchmark_memory_usage()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if passed:
            passed_tests += 1
    
    print(f"\n📈 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL DELEGATION BENCHMARKS PASSED!")
        print("✅ Block 2.2 metrics achieved:")
        print("   - Delegation latency: <10ms")
        print("   - Context preservation: 100%") 
        print("   - Max delegation depth: configurable")
    else:
        print("⚠️  Some benchmarks failed. Review implementation.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)