"""
Production Features Demo for LiteCrew.

This example demonstrates:
1. Testing framework with performance benchmarking
2. Debugging tools with execution tracing and profiling
3. Human-in-the-loop with approval flows
"""

import time
from pathlib import Path

from litecrew.agent import Agent as LiteAgent
from litecrew.crew import Crew as LiteCrew
from litecrew.task import LiteTask

# Testing imports
from litecrew.testing import (
    CrewTestRunner,
    MockLLMProvider,
    TestCase,
    TestSuite,
    create_test_crew,
)

# Debugging imports
from litecrew.debugging import (
    ExecutionProfiler,
    ExecutionReplayer,
    ExecutionTracer,
    TraceEventType,
    trace_execution,
)

# Human interaction imports
from litecrew.human import (
    HumanAgent,
    HumanInterface,
    InterventionType,
    requires_approval,
)


def demo_testing_framework():
    """Demonstrate the testing framework."""
    print("\n=== TESTING FRAMEWORK DEMO ===\n")
    
    # Create a test suite
    suite = TestSuite(
        name="LiteCrew Integration Tests",
        description="Test suite for crew functionality"
    )
    
    # Test 1: Basic crew execution
    test1 = TestCase(
        name="Basic Crew Test",
        description="Test basic crew with 2 agents and 3 tasks",
        crew_config=create_test_crew(
            name="Test Crew 1",
            num_agents=2,
            num_tasks=3
        ),
        expected_outputs={
            "crew_output": ""  # Any output is acceptable
        },
        performance_thresholds={
            "execution_time": 5.0,  # Max 5 seconds
            "memory_delta_mb": 50.0  # Max 50MB increase
        }
    )
    suite.add_test(test1)
    
    # Test 2: Performance test
    test2 = TestCase(
        name="Performance Test",
        description="Test crew performance with larger workload",
        crew_config=create_test_crew(
            name="Performance Crew",
            num_agents=4,
            num_tasks=10
        ),
        performance_thresholds={
            "execution_time": 10.0,
            "throughput": 1.0  # At least 1 task/second
        }
    )
    suite.add_test(test2)
    
    # Create test runner
    runner = CrewTestRunner(
        verbose=True,
        parallel=True,
        max_workers=2
    )
    
    # Use mock LLM for testing
    mock_llm = MockLLMProvider(
        responses={
            "Test task": "Task completed successfully",
            "default": "Mock response"
        },
        response_time=0.05,
        error_rate=0.1  # 10% error rate for testing
    )
    
    print(f"Running test suite with {len(suite.test_cases)} tests...")
    
    # Run tests
    with MockLLMProvider(response_time=0.01):  # Fast mock responses
        results = runner.run_test_suite(suite)
    
    # Display results
    summary = results.get_summary()
    print(f"\nTest Results:")
    print(f"  Pass rate: {summary['pass_rate']*100:.1f}%")
    print(f"  Total time: {summary['total_execution_time']:.3f}s")
    
    # Show mock LLM metrics
    print(f"\nMock LLM Metrics:")
    print(f"  Total calls: {mock_llm.get_metrics()['call_count']}")
    print(f"  Error rate: {mock_llm.get_metrics()['error_rate']*100:.1f}%")


def demo_debugging_tools():
    """Demonstrate debugging and profiling tools."""
    print("\n=== DEBUGGING TOOLS DEMO ===\n")
    
    # Create a crew for debugging
    researcher = LiteAgent(
        role="Researcher",
        goal="Research topics thoroughly",
        backstory="Expert researcher with attention to detail"
    )
    
    writer = LiteAgent(
        role="Writer",
        goal="Write clear and engaging content",
        backstory="Professional writer with years of experience"
    )
    
    tasks = [
        LiteTask(
            description="Research the topic of AI safety",
            agent=researcher,
            expected_output="Comprehensive research findings"
        ),
        LiteTask(
            description="Write an article about the research",
            agent=writer,
            expected_output="Well-written article"
        )
    ]
    
    crew = LiteCrew(
        name="Content Creation Crew",
        agents=[researcher, writer],
        tasks=tasks
    )
    
    # 1. Execution Tracing
    print("1. Execution Tracing")
    print("-" * 40)
    
    tracer = ExecutionTracer(
        trace_llm_calls=True,
        trace_memory=True,
        auto_save=True,
        save_path=Path("traces")
    )
    
    # Trace crew execution
    with trace_execution(tracer, crew) as t:
        # Simulate some events
        t.trace_agent_start(researcher, tasks[0])
        t.trace_llm_call("Research AI safety", "gpt-4", temperature=0.7)
        t.trace_llm_response("AI safety is a critical field...", tokens_used=150)
        t.trace_agent_end(researcher, tasks[0].output)
        
        t.trace_agent_start(writer, tasks[1])
        t.trace_llm_call("Write article about AI safety", "gpt-4", temperature=0.8)
        t.trace_llm_response("# The Importance of AI Safety\n\n...", tokens_used=500)
        t.trace_agent_end(writer, tasks[1].output)
    
    trace = tracer.get_trace()
    print(f"Trace captured with {len(trace.events)} events")
    print(f"Total duration: {trace.get_duration():.3f}s")
    
    # Show timeline
    timeline = trace.get_timeline()
    print("\nExecution Timeline:")
    for event in timeline[:5]:  # Show first 5 events
        print(f"  [{event['time']:.3f}s] {event['type']}: {event['component']}")
    
    # 2. Execution Profiling
    print("\n2. Performance Profiling")
    print("-" * 40)
    
    profiler = ExecutionProfiler()
    profiler.start_profiling()
    
    # Simulate some work
    for i in range(3):
        start = time.perf_counter()
        time.sleep(0.1)  # Simulate agent work
        profiler.record_timing(f"agent_{i}", time.perf_counter() - start)
        profiler.increment_counter("tasks_completed")
    
    profiler.increment_counter("llm_calls", 5)
    
    profile_results = profiler.stop_profiling()
    
    print(f"Total execution time: {profile_results['total_execution_time']:.3f}s")
    print("\nComponent Timings:")
    for component, stats in profile_results['component_timings'].items():
        print(f"  {component}: {stats['average']:.3f}s avg ({stats['count']} calls)")
    
    print("\nCounters:")
    for name, value in profile_results['counters'].items():
        print(f"  {name}: {value}")
    
    # 3. Trace Replay
    print("\n3. Trace Replay")
    print("-" * 40)
    
    if trace:
        replayer = ExecutionReplayer(trace)
        
        # Get summary
        summary = replayer.get_summary()
        print(f"Replaying trace: {summary['trace_id']}")
        print(f"Total events: {summary['total_events']}")
        print(f"Duration: {summary['duration']:.3f}s")
        
        # Find specific events
        llm_events = replayer.find_events(event_type=TraceEventType.LLM_CALL)
        print(f"\nFound {len(llm_events)} LLM calls")
        
        # Replay at high speed
        print("\nReplaying at 10x speed...")
        
        def replay_callback(event):
            if event.event_type in [TraceEventType.AGENT_START, TraceEventType.AGENT_END]:
                print(f"  Replaying: {event.component}")
        
        replayer.replay(speed=10.0, callback=replay_callback)


def demo_human_in_the_loop():
    """Demonstrate human-in-the-loop features."""
    print("\n=== HUMAN-IN-THE-LOOP DEMO ===\n")
    
    # Create human interface
    interface = HumanInterface(
        auto_approve=False,  # Require manual approval
        default_timeout=30.0
    )
    
    # 1. Approval Flows
    print("1. Approval Flows")
    print("-" * 40)
    
    # Create a sensitive function that requires approval
    @requires_approval(interface, InterventionType.REVIEW)
    def delete_important_data(data_id: str):
        return f"Data {data_id} has been deleted"
    
    # Request approval for a critical action
    print("Requesting approval for critical action...")
    
    request = interface.request_approval(
        component="data_manager",
        content="Delete customer database backup from 2023?",
        request_type=InterventionType.APPROVAL,
        context={
            "severity": "high",
            "reversible": False,
            "affected_records": 50000
        },
        options=["approve", "reject", "defer"]
    )
    
    print(f"Approval request created: {request.id}")
    print(f"Status: {request.status.value}")
    
    # Simulate human response (in real use, this would be from UI)
    print("\nSimulating human rejection...")
    interface.respond_to_approval(
        request.id,
        "reject",
        "Too risky - need backup verification first",
        responder="admin"
    )
    
    print(f"Updated status: {request.status.value}")
    print(f"Response: {request.response}")
    
    # 2. Human Agent
    print("\n2. Human Agent Integration")
    print("-" * 40)
    
    # Create interface with auto-approval for demo
    auto_interface = HumanInterface(auto_approve=True)
    
    # Create human agent
    human_expert = HumanAgent(
        interface=auto_interface,
        role="Domain Expert",
        goal="Provide expert judgment on complex decisions",
        backstory="Senior expert with 20 years of experience"
    )
    
    # Create a crew with human agent
    ai_agent = LiteAgent(
        role="AI Assistant",
        goal="Gather and prepare information",
        backstory="Efficient AI assistant"
    )
    
    tasks = [
        LiteTask(
            description="Analyze market data and identify key trends",
            agent=ai_agent,
            expected_output="Market analysis report"
        ),
        LiteTask(
            description="Review analysis and provide strategic recommendations",
            agent=human_expert,
            expected_output="Strategic recommendations"
        )
    ]
    
    crew = LiteCrew(
        name="Human-AI Collaboration Crew",
        agents=[ai_agent, human_expert],
        tasks=tasks
    )
    
    print("Executing crew with human expert...")
    # In real execution, human would provide input
    # Here we use auto-approve for demo
    
    # 3. Feedback Collection
    print("\n3. Feedback Collection")
    print("-" * 40)
    
    # Provide feedback on agent performance
    feedback1 = interface.provide_feedback(
        component="ai_agent",
        feedback_type="quality",
        rating=0.85,
        comment="Good analysis but missed some edge cases",
        suggestions=["Consider seasonal variations", "Include competitor data"]
    )
    
    feedback2 = interface.provide_feedback(
        component="human_expert",
        feedback_type="efficiency",
        rating=0.95,
        comment="Excellent insights provided quickly"
    )
    
    print(f"Collected {len(interface._feedback_history)} feedback entries")
    
    # Show metrics
    metrics = interface.get_metrics()
    print("\nHuman Interaction Metrics:")
    print(f"  Total approvals: {metrics['total_approvals']}")
    print(f"  Approval rate: {metrics['approval_rate']*100:.1f}%")
    print(f"  Average rating: {metrics['avg_rating']:.2f}")
    
    # Show approval history
    history = interface.get_approval_history(limit=5)
    if history:
        print(f"\nRecent Approvals:")
        for req in history:
            print(f"  - {req.component}: {req.status.value} - {req.response}")


def main():
    """Run all production feature demos."""
    print("LiteCrew Production Features Demo")
    print("=================================")
    
    # Run demos
    demo_testing_framework()
    demo_debugging_tools()
    demo_human_in_the_loop()
    
    print("\n✅ All production features demonstrated successfully!")
    print("\nKey Takeaways:")
    print("- Testing framework enables automated crew testing with performance benchmarks")
    print("- Debugging tools provide detailed execution traces and profiling")
    print("- Human-in-the-loop enables approval flows and human-AI collaboration")


if __name__ == "__main__":
    main()