"""
Advanced Orchestration Demo for LiteCrew.

This example demonstrates:
1. Dynamic task planning with goal decomposition
2. Conditional flows with if/else and loops
3. Parallel execution with dependency resolution
"""

import time
from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask
from litecrew.orchestration import (
    # Planning
    TaskPlanner,
    ReasoningEngine,
    # Flows
    FlowBuilder,
    FlowCondition,
    ConditionOperator,
    FlowExecutor,
    # Parallel
    ParallelTask,
    ParallelOrchestrator,
    ExecutionMode,
)


def demo_planning_and_reasoning():
    """Demonstrate dynamic task planning and reasoning."""
    print("\n=== PLANNING & REASONING DEMO ===\n")
    
    # Create agents
    agents = [
        LiteAgent(
            role="Data Collector",
            goal="Gather and validate data from various sources",
            backstory="Expert in data collection and validation"
        ),
        LiteAgent(
            role="Data Analyst",
            goal="Analyze data and extract insights",
            backstory="Skilled data analyst with statistical expertise"
        ),
        LiteAgent(
            role="Report Writer",
            goal="Create comprehensive reports",
            backstory="Professional technical writer"
        )
    ]
    
    # Create planner
    planner = TaskPlanner(enable_reasoning=True, max_steps=10)
    
    # Complex goal
    goal = """
    Create a comprehensive market analysis report that includes:
    1. Current market trends data
    2. Competitor analysis
    3. Future predictions
    4. Strategic recommendations
    """
    
    # Create plan
    print("Creating execution plan...")
    plan = planner.create_plan(goal, agents)
    
    # Display plan
    print(f"\nGenerated plan with {len(plan.steps)} steps:")
    for i, step in enumerate(plan.steps):
        print(f"\n{i+1}. {step.description}")
        print(f"   Agent: {step.agent.role if step.agent else 'Unassigned'}")
        print(f"   Dependencies: {step.dependencies}")
        if step.reasoning:
            print(f"   Reasoning: {step.reasoning[:100]}...")
    
    # Validate plan
    is_valid, issues = planner.validate_plan(plan)
    print(f"\nPlan validation: {'PASSED' if is_valid else 'FAILED'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Optimize plan
    optimized_plan = planner.optimize_plan(plan)
    if "parallel_groups" in optimized_plan.context:
        print(f"\nIdentified parallel execution opportunities:")
        for group in optimized_plan.context["parallel_groups"]:
            print(f"  - Tasks {group} can run in parallel")
    
    # Show metrics
    metrics = planner.get_metrics()
    print(f"\nPlanning metrics:")
    print(f"  - Planning time: {metrics['avg_planning_time']:.3f}s")
    print(f"  - Total plans created: {metrics['total_plans_created']}")


def demo_conditional_flows():
    """Demonstrate conditional flows with branching and loops."""
    print("\n=== CONDITIONAL FLOWS DEMO ===\n")
    
    # Create agents
    quality_checker = LiteAgent(
        role="Quality Checker",
        goal="Check data quality",
        backstory="Quality assurance specialist"
    )
    
    processor = LiteAgent(
        role="Data Processor",
        goal="Process and transform data",
        backstory="Data processing expert"
    )
    
    # Build flow
    builder = FlowBuilder("Data Processing Workflow")
    
    # Task 1: Check quality
    check_task = LiteTask(
        description="Check data quality score",
        agent=quality_checker,
        expected_output="Quality score between 0 and 1"
    )
    check_id = builder.add_task(check_task, quality_checker)
    
    # Condition: If quality > 0.8
    condition = FlowCondition(
        "$quality_score",
        ConditionOperator.GREATER_THAN,
        0.8
    )
    
    # Good quality path
    process_task = LiteTask(
        description="Process high-quality data",
        agent=processor,
        expected_output="Processed data"
    )
    process_id = builder.add_task(process_task, processor)
    
    # Poor quality path - loop for cleaning
    clean_task = LiteTask(
        description="Clean and improve data quality",
        agent=processor,
        expected_output="Cleaned data"
    )
    clean_id = builder.add_task(clean_task, processor)
    
    # Add condition node
    cond_id = builder.add_condition(condition, process_id, clean_id)
    
    # Add loop for retrying
    loop_condition = FlowCondition(
        "$retry_count",
        ConditionOperator.LESS_THAN,
        3
    )
    loop_id = builder.add_loop(
        loop_condition,
        [clean_id, check_id],
        max_iterations=3
    )
    
    flow = builder.flow  # Direct access for demo
    
    # Execute flow
    executor = FlowExecutor(enable_debugging=True)
    
    print("Executing conditional flow...")
    context = executor.execute(flow, {"quality_score": 0.6, "retry_count": 0})
    
    print(f"\nExecution completed:")
    print(f"  - Nodes executed: {len(flow.execution_path)}")
    print(f"  - Final context: {context}")
    
    # Show metrics
    metrics = executor.get_metrics()
    print(f"\nFlow execution metrics:")
    print(f"  - Branch evaluations: {metrics['branch_evaluations']}")
    print(f"  - Loop iterations: {metrics['loop_iterations']}")
    print(f"  - Avg execution time: {metrics.get('avg_execution_time', 0):.3f}s")


def demo_parallel_execution():
    """Demonstrate parallel task execution."""
    print("\n=== PARALLEL EXECUTION DEMO ===\n")
    
    # Create agents
    agents = [
        LiteAgent(
            role=f"Worker {i}",
            goal="Execute assigned tasks",
            backstory=f"Specialized worker {i}"
        )
        for i in range(4)
    ]
    
    # Create tasks with dependencies
    tasks = []
    
    # Layer 1: Data collection (can run in parallel)
    for i in range(3):
        task = ParallelTask(
            id=f"collect_{i}",
            task=LiteTask(
                description=f"Collect data from source {i}",
                agent=agents[i],
                expected_output=f"Data from source {i}"
            ),
            agent=agents[i],
            dependencies=set()
        )
        tasks.append(task)
    
    # Layer 2: Data processing (depends on collection)
    process_task = ParallelTask(
        id="process",
        task=LiteTask(
            description="Process all collected data",
            agent=agents[0],
            expected_output="Processed dataset"
        ),
        agent=agents[0],
        dependencies={"collect_0", "collect_1", "collect_2"}
    )
    tasks.append(process_task)
    
    # Layer 3: Analysis tasks (can run in parallel after processing)
    for i in range(2):
        task = ParallelTask(
            id=f"analyze_{i}",
            task=LiteTask(
                description=f"Analyze aspect {i} of processed data",
                agent=agents[i+1],
                expected_output=f"Analysis report {i}"
            ),
            agent=agents[i+1],
            dependencies={"process"}
        )
        tasks.append(task)
    
    # Layer 4: Final report (depends on all analyses)
    report_task = ParallelTask(
        id="report",
        task=LiteTask(
            description="Generate final report",
            agent=agents[3],
            expected_output="Final comprehensive report"
        ),
        agent=agents[3],
        dependencies={"analyze_0", "analyze_1"}
    )
    tasks.append(report_task)
    
    # Execute with orchestrator
    orchestrator = ParallelOrchestrator(auto_optimize=True)
    
    print("Executing parallel workflow...")
    print(f"Total tasks: {len(tasks)}")
    print(f"Dependency layers: 4")
    
    start_time = time.perf_counter()
    results = orchestrator.execute_workflow(tasks)
    execution_time = time.perf_counter() - start_time
    
    print(f"\nExecution completed in {execution_time:.3f}s")
    print(f"Results collected: {len(results)}")
    
    # Calculate theoretical sequential time
    sequential_time = len(tasks) * 0.1  # Assuming 0.1s per task
    speedup = sequential_time / execution_time
    
    print(f"\nPerformance metrics:")
    print(f"  - Sequential time (theoretical): {sequential_time:.3f}s")
    print(f"  - Parallel execution time: {execution_time:.3f}s")
    print(f"  - Speedup: {speedup:.2f}x")
    
    # Show detailed metrics
    metrics = orchestrator.executor.get_metrics()
    print(f"\nDetailed metrics:")
    print(f"  - Parallel groups executed: {metrics['parallel_groups']}")
    print(f"  - Average speedup: {metrics.get('avg_speedup', 0):.2f}x")
    print(f"  - Tasks executed: {metrics['total_tasks']}")
    
    orchestrator.shutdown()


def main():
    """Run all demos."""
    print("LiteCrew Advanced Orchestration Demo")
    print("====================================")
    
    # Run demos
    demo_planning_and_reasoning()
    demo_conditional_flows()
    demo_parallel_execution()
    
    print("\n✅ All demos completed successfully!")


if __name__ == "__main__":
    main()