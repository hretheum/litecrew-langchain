"""Tests for uncovered lines in SequentialProcess."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from litecrew.processes.sequential import SequentialProcess
from litecrew.processes.base import ProcessConfig
from litecrew.task import TaskOutput


class TestSequentialProcessCoverage:
    """Tests for uncovered lines in SequentialProcess."""
    
    @pytest.mark.asyncio
    async def test_context_index_bounds_checking(self):
        """Test context index bounds checking."""
        process = SequentialProcess()
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock tasks
        task1 = Mock()
        task1.description = "Task 1"
        task1.agent = None
        task1.agent_role = None
        task1.context = None
        
        task2 = Mock()
        task2.description = "Task 2"
        task2.agent = None
        task2.agent_role = None
        task2.context = [0]  # Valid context index
        
        task3 = Mock()
        task3.description = "Task 3"
        task3.agent = None
        task3.agent_role = None
        task3.context = [10]  # Invalid context index (out of bounds)
        
        tasks = [task1, task2, task3]
        
        # Mock task execution
        task1_output = TaskOutput(raw="Task 1 result", task=task1)
        task2_output = TaskOutput(raw="Task 2 result", task=task2)
        task3_output = TaskOutput(raw="Task 3 result", task=task3)
        
        with patch.object(process, '_emit_event'), \
             patch.object(task1, 'execute_async', new_callable=AsyncMock, return_value=task1_output), \
             patch.object(task2, 'execute_async', new_callable=AsyncMock, return_value=task2_output), \
             patch.object(task3, 'execute_async', new_callable=AsyncMock, return_value=task3_output):
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            assert len(result.tasks_output) == 3
            
            # Check that context was set on task2 (valid index)
            assert hasattr(task2, '_context_outputs')
            assert len(task2._context_outputs) == 1
            
            # Check that context was NOT set on task3 (invalid index)
            assert not hasattr(task3, '_context_outputs')
    
    @pytest.mark.asyncio
    async def test_verbose_print_truncation(self):
        """Test verbose print with description truncation."""
        config = ProcessConfig(verbose=True)
        process = SequentialProcess(config)
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock task with long description
        task = Mock()
        task.description = "This is a very long task description that should be truncated in the verbose output to show only the first 50 characters for better readability and testing purposes"
        task.agent = None
        task.agent_role = None
        task.context = None
        
        tasks = [task]
        
        # Mock task execution
        task_output = TaskOutput(raw="Task result", task=task)
        
        with patch.object(process, '_emit_event'), \
             patch.object(task, 'execute_async', new_callable=AsyncMock, return_value=task_output), \
             patch('builtins.print') as mock_print:
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            
            # Check that print was called with truncated description
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "Executing task 1/1:" in call_args
            assert "This is a very long task description that should be" in call_args
            assert "..." in call_args
            # Should NOT contain the full description
            assert "testing purposes" not in call_args
    
    @pytest.mark.asyncio
    async def test_non_task_output_wrapping(self):
        """Test wrapping non-TaskOutput objects."""
        process = SequentialProcess()
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock task
        task = Mock()
        task.description = "Task 1"
        task.agent = None
        task.agent_role = None
        task.context = None
        
        tasks = [task]
        
        # Mock task execution returning string instead of TaskOutput
        with patch.object(process, '_emit_event'), \
             patch.object(task, 'execute_async', new_callable=AsyncMock, return_value="Simple string result"):
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            assert len(result.tasks_output) == 1
            
            # Check that string was wrapped in TaskOutput
            assert isinstance(result.tasks_output[0], TaskOutput)
            assert result.tasks_output[0].raw == "Simple string result"
            assert result.tasks_output[0].task == task
    
    @pytest.mark.asyncio
    async def test_context_with_negative_index(self):
        """Test context with negative index."""
        process = SequentialProcess()
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock tasks
        task1 = Mock()
        task1.description = "Task 1"
        task1.agent = None
        task1.agent_role = None
        task1.context = None
        
        task2 = Mock()
        task2.description = "Task 2"
        task2.agent = None
        task2.agent_role = None
        task2.context = [-1]  # Negative index
        
        tasks = [task1, task2]
        
        # Mock task execution
        task1_output = TaskOutput(raw="Task 1 result", task=task1)
        task2_output = TaskOutput(raw="Task 2 result", task=task2)
        
        with patch.object(process, '_emit_event'), \
             patch.object(task1, 'execute_async', new_callable=AsyncMock, return_value=task1_output), \
             patch.object(task2, 'execute_async', new_callable=AsyncMock, return_value=task2_output):
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            assert len(result.tasks_output) == 2
            
            # Check that context was NOT set on task2 (negative index)
            assert not hasattr(task2, '_context_outputs')
    
    @pytest.mark.asyncio
    async def test_context_with_zero_index(self):
        """Test context with zero index."""
        process = SequentialProcess()
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock tasks
        task1 = Mock()
        task1.description = "Task 1"
        task1.agent = None
        task1.agent_role = None
        task1.context = None
        
        task2 = Mock()
        task2.description = "Task 2"
        task2.agent = None
        task2.agent_role = None
        task2.context = [0]  # Zero index - should be valid
        
        tasks = [task1, task2]
        
        # Mock task execution
        task1_output = TaskOutput(raw="Task 1 result", task=task1)
        task2_output = TaskOutput(raw="Task 2 result", task=task2)
        
        with patch.object(process, '_emit_event'), \
             patch.object(task1, 'execute_async', new_callable=AsyncMock, return_value=task1_output), \
             patch.object(task2, 'execute_async', new_callable=AsyncMock, return_value=task2_output):
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            assert len(result.tasks_output) == 2
            
            # Check that context was set on task2 (valid zero index)
            assert hasattr(task2, '_context_outputs')
            assert len(task2._context_outputs) == 1
            assert task2._context_outputs[0] == task1_output
    
    @pytest.mark.asyncio
    async def test_non_task_output_with_number(self):
        """Test non-TaskOutput with number."""
        process = SequentialProcess()
        
        # Mock agents
        agents = [Mock()]
        agents[0].role = "TestAgent"
        
        # Mock task
        task = Mock()
        task.description = "Task 1"
        task.agent = None
        task.agent_role = None
        task.context = None
        
        tasks = [task]
        
        # Mock task execution returning number
        with patch.object(process, '_emit_event'), \
             patch.object(task, 'execute_async', new_callable=AsyncMock, return_value=42):
            
            result = await process.execute(agents, tasks)
            
            # Should succeed
            assert result.success
            assert len(result.tasks_output) == 1
            
            # Check that number was wrapped in TaskOutput
            assert isinstance(result.tasks_output[0], TaskOutput)
            assert result.tasks_output[0].raw == "42"
            assert result.tasks_output[0].task == task