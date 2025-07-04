"""Extended tests for LiteTask functionality to improve coverage."""

from datetime import datetime
from unittest.mock import Mock, MagicMock

import pytest

from litecrew.task import LiteTask, TaskOutput, Task


class TestTaskOutput:
    """Test TaskOutput functionality."""
    
    def test_task_output_creation(self):
        """Test creating TaskOutput with all fields."""
        output = TaskOutput(
            raw="Test output",
            task_id="task-123",
            agent_role="TestAgent"
        )
        
        assert output.raw == "Test output"
        assert output.task_id == "task-123"
        assert output.agent_role == "TestAgent"
        assert isinstance(output.timestamp, datetime)
    
    def test_task_output_str_representation(self):
        """Test TaskOutput string representation."""
        output = TaskOutput(raw="Test output result")
        assert str(output) == "Test output result"

    def test_task_output_default_timestamp(self):
        """Test that timestamp is automatically set."""
        output = TaskOutput(raw="Test")
        assert output.timestamp is not None
        assert isinstance(output.timestamp, datetime)


class TestLiteTask:
    """Test LiteTask functionality."""
    
    def test_task_creation_basic(self):
        """Test basic task creation."""
        task = LiteTask(
            description="Test task",
            expected_output="Expected result"
        )
        
        assert task.description == "Test task"
        assert task.expected_output == "Expected result"
        assert task.agent is None
        assert task.context is None
        assert task.tools == []
        assert task.output is None
        assert task.async_execution == False
        assert task.callback is None

    def test_task_execution_no_agent(self):
        """Test task execution without agent raises error."""
        task = LiteTask(description="Test task")
        
        with pytest.raises(ValueError) as exc:
            task.execute()
        
        assert "No agent assigned to execute this task" in str(exc.value)

    def test_task_execution_with_agent(self):
        """Test successful task execution with agent."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.role = "TestAgent"
        mock_agent.execute.return_value = "Task completed successfully"
        
        task = LiteTask(
            description="Test task",
            agent=mock_agent
        )
        
        # Execute task
        result = task.execute()
        
        # Verify execution
        mock_agent.execute.assert_called_once_with("Test task", "")
        assert isinstance(result, TaskOutput)
        assert result.raw == "Task completed successfully"
        assert result.agent_role == "TestAgent"
        assert task.output == result

    def test_task_execution_with_callback(self):
        """Test task execution with callback function."""
        # Create mock agent and callback
        mock_agent = Mock()
        mock_agent.role = "TestAgent"
        mock_agent.execute.return_value = "Task result"
        
        mock_callback = Mock()
        
        task = LiteTask(
            description="Test task",
            agent=mock_agent,
            callback=mock_callback
        )
        
        # Execute task
        result = task.execute()
        
        # Verify callback was called
        mock_callback.assert_called_once_with(result)

    def test_task_execution_with_crew_context(self):
        """Test task execution with crew context."""
        mock_agent = Mock()
        mock_agent.role = "TestAgent"  # Set proper role
        mock_agent.execute.return_value = "Task result"
        
        task = LiteTask(
            description="Test task",
            agent=mock_agent
        )
        
        crew_context = {"previous_results": "Some context"}
        
        # Execute with context
        task.execute(crew_context)
        
        # Verify context was passed
        expected_context = str(crew_context)
        mock_agent.execute.assert_called_once_with("Test task", expected_context)

    def test_task_execution_with_task_context(self):
        """Test task execution with context from other tasks."""
        # Create previous task with output
        prev_agent = Mock()
        prev_agent.role = "PrevAgent"
        
        prev_task = LiteTask(
            description="Previous task",
            agent=prev_agent
        )
        prev_task.output = TaskOutput(
            raw="Previous result",
            agent_role="PrevAgent"
        )
        
        # Create current task with context
        mock_agent = Mock()
        mock_agent.role = "CurrentAgent"
        mock_agent.execute.return_value = "Current result"
        
        task = LiteTask(
            description="Current task",
            agent=mock_agent,
            context=[prev_task]
        )
        
        # Execute task
        task.execute()
        
        # Verify context was built correctly
        expected_context = "Output from PrevAgent:\nPrevious result"
        mock_agent.execute.assert_called_once_with("Current task", expected_context)

    def test_task_execution_failure_handling(self):
        """Test task execution failure creates error output."""
        mock_agent = Mock()
        mock_agent.role = "TestAgent"
        mock_agent.execute.side_effect = Exception("Execution failed")
        
        task = LiteTask(
            description="Test task",
            agent=mock_agent
        )
        
        # Execute should raise exception but create error output
        with pytest.raises(Exception):
            task.execute()
        
        # Verify error output was created
        assert task.output is not None
        assert "Task execution failed: Execution failed" in task.output.raw
        assert task.output.agent_role == "TestAgent"

    def test_build_context_no_context(self):
        """Test building context when no context tasks provided."""
        task = LiteTask(description="Test task")
        context = task._build_context()
        assert context == ""

    def test_build_context_with_tasks_no_output(self):
        """Test building context with tasks that have no output."""
        prev_task = LiteTask(description="Previous task")
        # No output set
        
        task = LiteTask(
            description="Current task",
            context=[prev_task]
        )
        
        context = task._build_context()
        assert context == ""

    def test_task_str_representation(self):
        """Test task string representation."""
        task = LiteTask(description="This is a very long task description that should be truncated")
        str_repr = str(task)
        assert str_repr.startswith("Task: This is a very long task description that should")
        assert str_repr.endswith("...")

    def test_task_alias_compatibility(self):
        """Test that Task alias works for CrewAI compatibility."""
        # Task should be an alias for LiteTask
        assert Task == LiteTask
        
        # Should be able to create using Task
        task = Task(description="Test task")
        assert isinstance(task, LiteTask)

    def test_task_agent_without_role(self):
        """Test task execution with agent that has no role attribute."""
        # Create a simple object without role attribute
        class SimpleAgent:
            def execute(self, description, context):
                return "Result"
        
        mock_agent = SimpleAgent()
        
        task = LiteTask(
            description="Test task",
            agent=mock_agent
        )
        
        result = task.execute()
        assert result.agent_role is None

    def test_task_context_with_agent_no_role(self):
        """Test context building with task agent that has no role."""
        # Create a simple agent without role
        class SimpleAgent:
            def execute(self, description, context):
                return "Result"
        
        prev_agent = SimpleAgent()
        
        prev_task = LiteTask(
            description="Previous task",
            agent=prev_agent
        )
        prev_task.output = TaskOutput(raw="Previous result")
        
        task = LiteTask(
            description="Current task",
            context=[prev_task]
        )
        
        context = task._build_context()
        assert "Output from previous task:\nPrevious result" in context