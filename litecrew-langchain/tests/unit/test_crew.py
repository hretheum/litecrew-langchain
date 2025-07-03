"""
Unit tests for LiteCrew orchestration engine.
"""

import time
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from litecrew.crew import LiteCrew, CrewOutput, ProcessType
from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput


class TestLiteCrew:
    """Test LiteCrew functionality and performance."""
    
    def test_crew_creation(self):
        """Test basic crew creation."""
        agents = [
            LiteAgent(role="Researcher", goal="Find information", backstory="Expert researcher"),
            LiteAgent(role="Writer", goal="Write content", backstory="Professional writer"),
        ]
        
        tasks = [
            LiteTask(description="Research topic", agent=agents[0]),
            LiteTask(description="Write article", agent=agents[1]),
        ]
        
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process="sequential"
        )
        
        assert len(crew.agents) == 2
        assert len(crew.tasks) == 2
        assert crew.process == ProcessType.SEQUENTIAL
        
    def test_crew_creation_performance(self):
        """Test that crew creation is fast (<50ms)."""
        # Create agents
        agents = [
            LiteAgent(role=f"Agent{i}", goal=f"Goal{i}", backstory=f"Story{i}")
            for i in range(10)
        ]
        
        # Create tasks
        tasks = [
            LiteTask(description=f"Task{i}", agent=agents[i % len(agents)])
            for i in range(20)
        ]
        
        # Measure crew creation time
        start = time.perf_counter()
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process="sequential"
        )
        duration = time.perf_counter() - start
        
        assert duration < 0.05  # 50ms
        assert len(crew.agents) == 10
        assert len(crew.tasks) == 20
        
    def test_sequential_process(self):
        """Test sequential task execution."""
        # Create agents with mocked execute
        agent1 = LiteAgent(role="Agent1", goal="Test 1", backstory="Test agent 1")
        agent2 = LiteAgent(role="Agent2", goal="Test 2", backstory="Test agent 2")
        
        # Mock the execute method
        with patch.object(agent1, 'execute', return_value="Result 1") as mock1:
            with patch.object(agent2, 'execute', return_value="Result 2") as mock2:
                # Create tasks
                task1 = LiteTask(description="Task 1", agent=agent1)
                task2 = LiteTask(description="Task 2", agent=agent2)
                
                # Create crew
                crew = LiteCrew(
                    agents=[agent1, agent2],
                    tasks=[task1, task2],
                    process="sequential"
                )
                
                # Execute
                result = crew.kickoff()
                
                # Verify execution order
                assert mock1.called
                assert mock2.called
                assert task1.output is not None
                assert task2.output is not None
                assert isinstance(result, CrewOutput)
        
    def test_hierarchical_process(self):
        """Test hierarchical task execution."""
        # Create real agents
        manager = LiteAgent(role="Manager", goal="Manage team", backstory="Experienced manager")
        worker1 = LiteAgent(role="Worker1", goal="Do work", backstory="Hard worker")
        worker2 = LiteAgent(role="Worker2", goal="Do work", backstory="Dedicated worker")
        
        # Mock execute methods
        with patch.object(manager, 'execute', return_value="Delegated to workers") as mock_mgr:
            with patch.object(worker1, 'execute', return_value="Work done 1"):
                with patch.object(worker2, 'execute', return_value="Work done 2"):
                    # Create tasks
                    manager_task = LiteTask(description="Manage project", agent=manager)
                    worker_task1 = LiteTask(description="Do work 1", agent=worker1)
                    worker_task2 = LiteTask(description="Do work 2", agent=worker2)
                    
                    # Create crew with manager as first agent
                    crew = LiteCrew(
                        agents=[manager, worker1, worker2],
                        tasks=[manager_task, worker_task1, worker_task2],
                        process="hierarchical"
                    )
                    
                    # Execute
                    result = crew.kickoff()
                    
                    # Manager should coordinate
                    assert mock_mgr.called
                    assert isinstance(result, CrewOutput)
        
    def test_task_dependencies(self):
        """Test task execution with dependencies."""
        agent = LiteAgent(role="Agent", goal="Complete tasks", backstory="Versatile agent")
        
        with patch.object(agent, 'execute', return_value="Done") as mock_exec:
            # Create tasks with dependencies
            task1 = LiteTask(description="First task", agent=agent)
            task2 = LiteTask(description="Second task", agent=agent, context=[task1])
            task3 = LiteTask(description="Third task", agent=agent, context=[task1, task2])
            
            crew = LiteCrew(
                agents=[agent],
                tasks=[task1, task2, task3],
                process="sequential"
            )
            
            # Execute
            result = crew.kickoff()
            
            # Check all tasks executed
            assert mock_exec.call_count == 3
            assert all(task.output for task in [task1, task2, task3])
        
    def test_progress_tracking(self):
        """Test progress tracking during execution."""
        agent = LiteAgent(role="Agent", goal="Track progress", backstory="Detail-oriented")
        
        with patch.object(agent, 'execute', return_value="Done"):
            tasks = [LiteTask(description=f"Task {i}", agent=agent) for i in range(5)]
            
            crew = LiteCrew(
                agents=[agent],
                tasks=tasks,
                process="sequential",
                verbose=True
            )
            
            # Track progress
            progress_updates = []
            
            def track_progress(update):
                progress_updates.append(update)
                
            crew.on_progress = track_progress
            
            # Execute
            result = crew.kickoff()
            
            # Should have progress updates
            assert len(progress_updates) > 0
        
    def test_memory_usage(self):
        """Test memory footprint for multiple agents."""
        import psutil
        import gc
        
        gc.collect()
        process = psutil.Process()
        before_memory = process.memory_info().rss
        
        # Create 10 agents and 20 tasks
        agents = [
            LiteAgent(role=f"Agent{i}", goal=f"Goal{i}", backstory=f"Story{i}")
            for i in range(10)
        ]
        
        tasks = [
            LiteTask(description=f"Task{i}", agent=agents[i % 10])
            for i in range(20)
        ]
        
        crew = LiteCrew(
            agents=agents,
            tasks=tasks,
            process="sequential"
        )
        
        # Force garbage collection
        gc.collect()
        after_memory = process.memory_info().rss
        memory_increase = (after_memory - before_memory) / 1024 / 1024  # MB
        
        # Should use less than 50MB for 10 agents
        assert memory_increase < 50
        
    def test_error_handling(self):
        """Test error handling during execution."""
        # Create agent that fails
        agent = LiteAgent(role="FailingAgent", goal="Fail gracefully", backstory="Test agent")
        
        with patch.object(agent, 'execute', side_effect=Exception("Task failed")):
            task = LiteTask(description="Failing task", agent=agent)
            
            crew = LiteCrew(
                agents=[agent],
                tasks=[task],
                process="sequential"
            )
            
            # Should handle error gracefully
            with pytest.raises(Exception):
                crew.kickoff()
            
    def test_crew_output(self):
        """Test CrewOutput structure."""
        agent = LiteAgent(role="Agent", goal="Complete tasks", backstory="Test agent")
        
        with patch.object(agent, 'execute', return_value="Task completed"):
            task = LiteTask(description="Test task", agent=agent)
            
            crew = LiteCrew(
                agents=[agent],
                tasks=[task],
                process="sequential"
            )
            
            result = crew.kickoff()
            
            assert isinstance(result, CrewOutput)
            assert result.raw is not None
            assert result.tasks_output is not None
            assert len(result.tasks_output) == 1
        
    def test_crew_metrics(self):
        """Test crew execution metrics."""
        agent = LiteAgent(role="Agent", goal="Track metrics", backstory="Test agent")
        
        with patch.object(agent, 'execute', return_value="Done"):
            tasks = [LiteTask(description=f"Task {i}", agent=agent) for i in range(3)]
            
            crew = LiteCrew(
                agents=[agent],
                tasks=tasks,
                process="sequential"
            )
            
            start = time.perf_counter()
            result = crew.kickoff()
            duration = time.perf_counter() - start
            
            # Check metrics
            assert crew.usage_metrics is not None
            assert "total_time" in crew.usage_metrics
            assert "task_count" in crew.usage_metrics
            assert crew.usage_metrics["task_count"] == 3
        
    def test_process_type_validation(self):
        """Test process type validation."""
        agent = LiteAgent(role="Agent", goal="Test validation", backstory="Test agent")
        task = LiteTask(description="Task", agent=agent)
        
        # Valid process types
        for process in ["sequential", "hierarchical"]:
            crew = LiteCrew(
                agents=[agent],
                tasks=[task],
                process=process
            )
            assert crew.process in [ProcessType.SEQUENTIAL, ProcessType.HIERARCHICAL]
            
        # Invalid process type
        with pytest.raises(ValueError):
            crew = LiteCrew(
                agents=[agent],
                tasks=[task],
                process="invalid"
            )