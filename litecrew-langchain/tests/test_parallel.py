"""
Tests for Parallel Execution system.
"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput
from litecrew.orchestration.parallel import (
    DependencyResolver,
    ExecutionGroup,
    ExecutionMode,
    ParallelExecutor,
    ParallelOrchestrator,
    ParallelTask,
)


class TestParallelExecution:
    """Test parallel execution functionality."""
    
    @pytest.fixture
    def agents(self):
        """Create test agents."""
        return [
            LiteAgent(role=f"Agent{i}", goal="Execute tasks", backstory="Test agent")
            for i in range(5)
        ]
    
    @pytest.fixture
    def executor(self):
        """Create parallel executor."""
        return ParallelExecutor(max_workers=3)
    
    def create_test_tasks(self, agents, count=5, execution_time=0.1):
        """Create test tasks with mocked execution."""
        tasks = []
        
        for i in range(count):
            task = ParallelTask(
                id=f"task_{i}",
                task=LiteTask(
                    description=f"Task {i}",
                    agent=agents[i % len(agents)],
                    expected_output="Done"
                ),
                agent=agents[i % len(agents)]
            )
            
            # Mock execution with delay
            def mock_execute(t, context, delay=execution_time):
                time.sleep(delay)
                return TaskOutput(raw=f"Result {t.description}", task_id="1")
            
            task.agent.execute_task = MagicMock(side_effect=lambda t, c: mock_execute(t, c))
            tasks.append(task)
        
        return tasks
    
    def test_parallel_speedup(self, agents, executor):
        """Test parallel execution achieves >3x speedup."""
        # Create 6 tasks that take 0.1s each
        tasks = self.create_test_tasks(agents, count=6, execution_time=0.1)
        
        # Execute sequentially
        start_seq = time.perf_counter()
        executor.execute_tasks(tasks, mode=ExecutionMode.SEQUENTIAL)
        seq_time = time.perf_counter() - start_seq
        
        # Reset tasks
        for task in tasks:
            task.status = "pending"
            task.result = None
        
        # Execute in parallel
        start_par = time.perf_counter()
        executor.execute_tasks(tasks, mode=ExecutionMode.PARALLEL)
        par_time = time.perf_counter() - start_par
        
        # Calculate speedup
        speedup = seq_time / par_time
        assert speedup > 3.0  # >3x speedup requirement
        
        # Check metrics
        metrics = executor.get_metrics()
        assert metrics["avg_speedup"] > 3.0
    
    def test_dependency_resolution(self, agents):
        """Test dependency resolution for parallel groups."""
        # Create tasks with dependencies
        tasks = []
        
        # Layer 1: No dependencies (can run in parallel)
        for i in range(3):
            task = ParallelTask(
                id=f"layer1_task_{i}",
                task=LiteTask(description=f"L1 Task {i}", agent=agents[0], expected_output="Done"),
                agent=agents[0],
                dependencies=set()
            )
            tasks.append(task)
        
        # Layer 2: Depends on layer 1 (can run in parallel after layer 1)
        for i in range(2):
            task = ParallelTask(
                id=f"layer2_task_{i}",
                task=LiteTask(description=f"L2 Task {i}", agent=agents[1], expected_output="Done"),
                agent=agents[1],
                dependencies={f"layer1_task_{j}" for j in range(3)}
            )
            tasks.append(task)
        
        # Layer 3: Depends on layer 2
        task = ParallelTask(
            id="layer3_task",
            task=LiteTask(description="L3 Task", agent=agents[2], expected_output="Done"),
            agent=agents[2],
            dependencies={f"layer2_task_{j}" for j in range(2)}
        )
        tasks.append(task)
        
        # Create execution groups
        groups = DependencyResolver.create_execution_groups(tasks)
        
        # Should have 3 groups (one per layer)
        assert len(groups) == 3
        assert len(groups[0].tasks) == 3  # Layer 1
        assert len(groups[1].tasks) == 2  # Layer 2
        assert len(groups[2].tasks) == 1  # Layer 3
    
    def test_async_execution(self, agents, executor):
        """Test async/await execution support."""
        # Create tasks
        tasks = self.create_test_tasks(agents, count=4, execution_time=0.05)
        
        # Execute async
        start_time = time.perf_counter()
        results = executor.execute_tasks(tasks, mode=ExecutionMode.ASYNC)
        async_time = time.perf_counter() - start_time
        
        # Should complete faster than sequential
        expected_sequential_time = 0.05 * 4  # 0.2s
        assert async_time < expected_sequential_time
        assert len(results) == 4
        
        # Check async metrics
        metrics = executor.get_metrics()
        assert metrics["async_tasks"] > 0
    
    def test_thread_pool_management(self, agents):
        """Test thread pool scales correctly."""
        # Test different worker counts
        for max_workers in [1, 3, 5]:
            executor = ParallelExecutor(max_workers=max_workers)
            
            # Create more tasks than workers
            tasks = self.create_test_tasks(agents, count=10, execution_time=0.01)
            
            # Execute
            start_time = time.perf_counter()
            results = executor.execute_tasks(tasks, mode=ExecutionMode.PARALLEL)
            execution_time = time.perf_counter() - start_time
            
            # Should use all workers efficiently
            assert len(results) == 10
            
            # Execution time should scale with worker count
            min_expected_time = (10 * 0.01) / max_workers * 0.8  # 80% efficiency
            assert execution_time > min_expected_time
            
            executor.shutdown()
    
    def test_task_timeout(self, agents, executor):
        """Test task timeout handling."""
        # Create task with timeout
        task = ParallelTask(
            id="timeout_task",
            task=LiteTask(description="Slow task", agent=agents[0], expected_output="Done"),
            agent=agents[0],
            timeout=0.1  # 100ms timeout
        )
        
        # Mock slow execution
        def slow_execute(t, context):
            time.sleep(0.5)  # 500ms - will timeout
            return TaskOutput(raw="Should not reach", task_id="1")
        
        task.agent.execute_task = MagicMock(side_effect=slow_execute)
        
        # Execute with timeout
        with pytest.raises(Exception):
            executor.execute_tasks([task])
        
        # Task should be marked as failed
        assert task.status == "failed"
        assert task.error is not None
    
    def test_execution_groups(self, agents, executor):
        """Test execution group handling."""
        # Create multiple groups
        groups = []
        
        for g in range(3):
            group = ExecutionGroup(
                id=f"group_{g}",
                mode=ExecutionMode.PARALLEL if g < 2 else ExecutionMode.SEQUENTIAL
            )
            
            # Add tasks to group
            for t in range(3):
                task = ParallelTask(
                    id=f"group_{g}_task_{t}",
                    task=LiteTask(description=f"G{g}T{t}", agent=agents[0], expected_output="Done"),
                    agent=agents[0]
                )
                task.agent.execute_task = MagicMock(
                    return_value=TaskOutput(raw=f"Result G{g}T{t}", task_id="1")
                )
                group.add_task(task)
            
            groups.append(group)
        
        # Execute groups
        results = executor.execute_groups(groups)
        
        # Check results structure
        assert len(results) == 3
        for g in range(3):
            assert f"group_{g}" in results
            assert len(results[f"group_{g}"]) == 3
    
    def test_orchestrator_workflow(self, agents):
        """Test high-level orchestrator."""
        orchestrator = ParallelOrchestrator(auto_optimize=True)
        
        # Create workflow with dependencies
        tasks = []
        
        # Independent tasks
        for i in range(4):
            task = ParallelTask(
                id=f"independent_{i}",
                task=LiteTask(description=f"Ind {i}", agent=agents[i], expected_output="Done"),
                agent=agents[i]
            )
            task.agent.execute_task = MagicMock(
                return_value=TaskOutput(raw=f"Result {i}", task_id=str(i))
            )
            tasks.append(task)
        
        # Dependent task
        final_task = ParallelTask(
            id="final",
            task=LiteTask(description="Final", agent=agents[0], expected_output="Done"),
            agent=agents[0],
            dependencies={f"independent_{i}" for i in range(4)}
        )
        final_task.agent.execute_task = MagicMock(
            return_value=TaskOutput(raw="Final result", task_id="final")
        )
        tasks.append(final_task)
        
        # Execute workflow
        results = orchestrator.execute_workflow(tasks)
        
        # All tasks should complete
        assert len(results) == 5
        assert all(f"independent_{i}" in results for i in range(4))
        assert "final" in results
        
        # Check optimization happened
        metrics = orchestrator.executor.get_metrics()
        assert metrics["parallel_groups"] > 0
        
        orchestrator.shutdown()
    
    def test_concurrent_constraint(self, agents):
        """Test concurrent execution respects max_workers."""
        executor = ParallelExecutor(max_workers=2)
        
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        
        def tracked_execute(t, context):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            time.sleep(0.05)
            concurrent_count -= 1
            return TaskOutput(raw="Done", task_id="1")
        
        # Create tasks with tracked execution
        tasks = []
        for i in range(6):
            task = ParallelTask(
                id=f"task_{i}",
                task=LiteTask(description=f"Task {i}", agent=agents[0], expected_output="Done"),
                agent=agents[0]
            )
            task.agent.execute_task = MagicMock(side_effect=tracked_execute)
            tasks.append(task)
        
        # Execute
        executor.execute_tasks(tasks, mode=ExecutionMode.PARALLEL)
        
        # Should not exceed max_workers
        assert max_concurrent <= 2
        
        executor.shutdown()