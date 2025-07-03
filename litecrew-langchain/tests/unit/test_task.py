"""
Unit tests for LiteTask.
"""

import time
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from litecrew.task import LiteTask, TaskOutput
from litecrew.agent import LiteAgent


class TestLiteTask:
    """Test LiteTask functionality and performance."""
    
    def test_task_creation(self, sample_task_config):
        """Test basic task creation."""
        task = LiteTask(**sample_task_config)
        
        assert task.description == "Analyze the test results"
        assert task.expected_output == "A detailed analysis report"
        assert task.async_execution is False
        assert task.output is None
        
    def test_task_creation_performance(self):
        """Test that task creation is fast (<1ms)."""
        times = []
        
        for i in range(100):
            start = time.perf_counter()
            task = LiteTask(
                description=f"Task {i}",
                expected_output=f"Output {i}"
            )
            duration = time.perf_counter() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        # Should create in less than 1ms on average
        assert avg_time < 0.001, f"Average task creation took {avg_time*1000:.2f}ms"
        
    def test_context_passing(self):
        """Test context passing between tasks."""
        from unittest.mock import Mock
        
        # Create mock agents
        agent1 = Mock()
        agent1.role = "Agent1"
        agent2 = Mock()
        agent2.role = "Agent2"
        
        # Create tasks with outputs
        task1 = LiteTask(description="First task", agent=agent1)
        task1.output = TaskOutput(raw="First result", agent_role="Agent1")
        
        task2 = LiteTask(description="Second task", agent=agent2)
        task2.output = TaskOutput(raw="Second result", agent_role="Agent2")
        
        # Create task with context
        task3 = LiteTask(
            description="Use context from previous tasks",
            context=[task1, task2]
        )
        
        # Build context
        context = task3._build_context()
        
        assert "First result" in context
        assert "Second result" in context
        assert "Agent1" in context
        assert "Agent2" in context
        
    def test_execute_without_agent(self):
        """Test that execute fails without agent."""
        task = LiteTask(description="No agent task")
        
        with pytest.raises(ValueError, match="No agent assigned"):
            task.execute()
            
    def test_execute_with_agent(self):
        """Test task execution with agent."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.role = "Test Agent"
        mock_agent.execute.return_value = "Task completed successfully"
        
        task = LiteTask(
            description="Test task",
            expected_output="Success message",
            agent=mock_agent
        )
        
        output = task.execute()
        
        assert isinstance(output, TaskOutput)
        assert output.raw == "Task completed successfully"
        assert output.agent_role == "Test Agent"
        assert output.timestamp is not None
        
        # Check agent was called correctly
        mock_agent.execute.assert_called_once_with("Test task", "")
        
    def test_execute_with_context(self):
        """Test execution with context from previous tasks."""
        # Setup previous tasks
        task1 = LiteTask(description="Generate data")
        task1.output = TaskOutput(raw="Generated data: [1,2,3]")
        
        # Create mock agent
        mock_agent = Mock()
        mock_agent.role = "Analyzer"
        mock_agent.execute.return_value = "Analysis complete"
        
        # Create task with context
        task2 = LiteTask(
            description="Analyze data",
            agent=mock_agent,
            context=[task1]
        )
        
        output = task2.execute()
        
        # Check context was passed
        call_args = mock_agent.execute.call_args[0]
        assert "Generated data: [1,2,3]" in call_args[1]  # context argument
        
    def test_execute_with_crew_context(self):
        """Test execution with crew context."""
        mock_agent = Mock()
        mock_agent.execute.return_value = "Done"
        
        task = LiteTask(
            description="Task with crew context",
            agent=mock_agent
        )
        
        crew_context = {"crew_info": "Important context"}
        output = task.execute(crew_context=crew_context)
        
        # Check crew context was included
        call_args = mock_agent.execute.call_args[0]
        assert "crew_info" in call_args[1]
        
    def test_execute_error_handling(self):
        """Test error handling during execution."""
        mock_agent = Mock()
        mock_agent.role = "Faulty Agent"
        mock_agent.execute.side_effect = Exception("Agent error")
        
        task = LiteTask(
            description="This will fail",
            agent=mock_agent
        )
        
        with pytest.raises(Exception, match="Agent error"):
            task.execute()
            
        # Output should still be created with error
        assert task.output is not None
        assert "Task execution failed" in task.output.raw
        
    def test_callback_execution(self):
        """Test callback is called after execution."""
        callback_called = False
        callback_output = None
        
        def test_callback(output):
            nonlocal callback_called, callback_output
            callback_called = True
            callback_output = output
            
        mock_agent = Mock()
        mock_agent.execute.return_value = "Callback test"
        
        task = LiteTask(
            description="Test callback",
            agent=mock_agent,
            callback=test_callback
        )
        
        output = task.execute()
        
        assert callback_called
        assert callback_output == output
        
    def test_async_execution_flag(self):
        """Test async execution flag."""
        task = LiteTask(
            description="Async task",
            async_execution=True
        )
        
        assert task.async_execution is True
        
    def test_task_output_string(self):
        """Test TaskOutput string representation."""
        output = TaskOutput(raw="Test output")
        
        assert str(output) == "Test output"
        
    def test_task_string_representation(self):
        """Test task string representation."""
        task = LiteTask(
            description="This is a very long task description that should be truncated"
        )
        
        task_str = str(task)
        
        assert "This is a very long task description that should b..." in task_str
        
    def test_context_latency(self):
        """Test context passing has minimal latency."""
        # Create 10 context tasks
        context_tasks = []
        for i in range(10):
            task = LiteTask(description=f"Context task {i}")
            task.output = TaskOutput(raw=f"Result {i}")
            context_tasks.append(task)
            
        # Create task with all context
        main_task = LiteTask(
            description="Main task",
            context=context_tasks
        )
        
        # Measure context building time
        start = time.perf_counter()
        context = main_task._build_context()
        duration = time.perf_counter() - start
        
        # Should be very fast (<0.1ms)
        assert duration < 0.0001, f"Context building took {duration*1000:.2f}ms"
        assert len(context) > 0
        
    def test_pydantic_model_validation(self):
        """Test that LiteTask validates fields properly."""
        # Should work with minimal fields
        task = LiteTask(description="Minimal task")
        assert task.expected_output == ""
        assert task.tools == []
        assert task.context is None
        
        # Should accept all fields
        task_full = LiteTask(
            description="Full task",
            expected_output="Expected",
            tools=["tool1", "tool2"],
            async_execution=True,
            callback=lambda x: x
        )
        assert len(task_full.tools) == 2
        assert task_full.async_execution is True