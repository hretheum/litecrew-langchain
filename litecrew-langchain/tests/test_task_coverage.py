"""Tests for task to improve coverage."""

import pytest
from unittest.mock import Mock
from litecrew.task import LiteTask, TaskOutput


class TestLiteTaskCoverage:
    """Tests for LiteTask to improve coverage."""
    
    def test_task_alias(self):
        """Test that Task alias works correctly."""
        from litecrew.task import Task
        
        # Should be able to create Task using alias
        task = Task(description="Test task with alias")
        
        # Should be instance of LiteTask
        assert isinstance(task, LiteTask)
        assert task.description == "Test task with alias"
    
    def test_str_method(self):
        """Test __str__ method."""
        task = LiteTask(
            description="This is a very long task description that should be truncated in the string representation"
        )
        
        # Should truncate to 50 characters
        str_repr = str(task)
        assert str_repr.startswith("Task: This is a very long task description that should")
        assert str_repr.endswith("...")
        assert len(str_repr) == len("Task: ") + 50 + len("...")
    
    def test_str_method_short_description(self):
        """Test __str__ method with short description."""
        task = LiteTask(description="Short task")
        
        # Should show full description
        str_repr = str(task)
        assert str_repr == "Task: Short task..."
    
    def test_execute_without_agent(self):
        """Test executing task without agent raises error."""
        task = LiteTask(description="Test task")
        
        # Should raise ValueError when no agent is assigned
        with pytest.raises(ValueError, match="No agent assigned to execute this task"):
            task.execute()
    
    def test_execute_with_callback(self):
        """Test task execution with callback."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.role = "test_role"
        mock_agent.execute.return_value = "Test result"
        
        # Create mock callback
        mock_callback = Mock()
        
        # Create task with callback
        task = LiteTask(
            description="Test task",
            agent=mock_agent,
            callback=mock_callback
        )
        
        # Execute task
        result = task.execute()
        
        # Verify callback was called
        mock_callback.assert_called_once()
        assert result.raw == "Test result"
    
    def test_execute_with_crew_context(self):
        """Test task execution with crew context."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.role = "test_role"
        mock_agent.execute.return_value = "Test result"
        
        # Create task
        task = LiteTask(description="Test task", agent=mock_agent)
        
        # Execute with crew context
        crew_context = {"key": "value"}
        result = task.execute(crew_context=crew_context)
        
        # Verify context was passed
        mock_agent.execute.assert_called_once()
        args = mock_agent.execute.call_args[0]
        assert "{'key': 'value'}" in args[1]
        assert result.raw == "Test result"
    
    def test_build_context_with_dependent_tasks(self):
        """Test building context from dependent tasks."""
        # Create mock agents
        mock_agent1 = Mock()
        mock_agent1.role = "agent1"
        mock_agent2 = Mock()
        mock_agent2.role = "agent2"
        
        # Create dependent tasks with outputs
        task1 = LiteTask(description="Task 1", agent=mock_agent1)
        task1.output = TaskOutput(raw="Output 1", agent_role="agent1")
        
        task2 = LiteTask(description="Task 2", agent=mock_agent2)
        task2.output = TaskOutput(raw="Output 2", agent_role="agent2")
        
        # Create main task with context
        main_task = LiteTask(
            description="Main task",
            agent=mock_agent1,
            context=[task1, task2]
        )
        
        # Build context
        context = main_task._build_context()
        
        # Verify context includes both outputs
        assert "Output from agent1:" in context
        assert "Output 1" in context
        assert "Output from agent2:" in context
        assert "Output 2" in context
    
    def test_task_output_str_method(self):
        """Test TaskOutput __str__ method."""
        output = TaskOutput(raw="Test output")
        assert str(output) == "Test output"
    
    def test_execute_with_agent_exception(self):
        """Test task execution when agent raises exception."""
        # Create mock agent that raises exception
        mock_agent = Mock()
        mock_agent.role = "test_role"
        mock_agent.execute.side_effect = Exception("Test exception")
        
        # Create task
        task = LiteTask(description="Test task", agent=mock_agent)
        
        # Should raise exception and create error output
        with pytest.raises(Exception, match="Test exception"):
            task.execute()
        
        # Should have created error output
        assert task.output is not None
        assert "Task execution failed: Test exception" in task.output.raw
        assert task.output.agent_role == "test_role"
        assert task.output.task_id == str(id(task))
    
    def test_execute_with_agent_without_role(self):
        """Test task execution with agent that has no role attribute."""
        # Create mock agent without role
        mock_agent = Mock()
        mock_agent.execute.side_effect = Exception("Test exception")
        # Remove role attribute to simulate hasattr(agent, "role") == False
        delattr(mock_agent, "role")
        
        # Create task
        task = LiteTask(description="Test task", agent=mock_agent)
        
        # Should raise exception and create error output with None role
        with pytest.raises(Exception, match="Test exception"):
            task.execute()
        
        # Should have created error output with None role
        assert task.output is not None
        assert task.output.agent_role is None