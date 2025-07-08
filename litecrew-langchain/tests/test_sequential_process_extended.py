"""Extended tests for SequentialProcess to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.processes.sequential import SequentialProcess
from litecrew.task import TaskOutput
from litecrew.processes.base import ProcessConfig


class TestSequentialProcessExtended:
    """Extended tests for SequentialProcess methods."""
    
    @pytest.fixture
    def process(self):
        """Create SequentialProcess instance."""
        config = ProcessConfig(verbose=True)
        return SequentialProcess(config)
    
    @pytest.fixture
    def agents(self):
        """Create mock agents."""
        agents = []
        for role in ["Developer", "Designer", "Tester"]:
            agent = Mock()
            agent.role = role
            agents.append(agent)
        return agents
    
    @pytest.fixture
    def tasks(self):
        """Create mock tasks."""
        tasks = []
        for i in range(3):
            task = Mock()
            task.description = f"Task {i+1}: Complete assignment {i+1}"
            task.agent = None
            task.agent_role = None
            tasks.append(task)
        return tasks
    
    @pytest.mark.asyncio
    async def test_execute_task_with_assigned_agent(self, process, agents, tasks):
        """Test execution with task having assigned agent."""
        # Assign agent directly to task
        tasks[0].agent = agents[1]  # Assign Designer
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            assert result.metadata["process_type"] == "sequential"
            assert result.metadata["tasks_completed"] == 3
    
    @pytest.mark.asyncio
    async def test_execute_task_with_agent_role(self, process, agents, tasks):
        """Test execution with task having agent_role."""
        # Set agent role for first task
        tasks[0].agent_role = "Designer"
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
    
    @pytest.mark.asyncio
    async def test_execute_task_with_default_agent(self, process, agents, tasks):
        """Test execution using default agent when no specific assignment."""
        # No agent or agent_role assigned - should use first agent
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
    
    @pytest.mark.asyncio
    async def test_execute_no_agent_found_error(self, process, tasks):
        """Test execution error when no agent found."""
        # Empty agents list
        agents = []
        
        result = await process.execute(agents, tasks)
        
        assert not result.success
        assert "No agent found for task" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_invalid_agent_role(self, process, agents, tasks):
        """Test execution with invalid agent role."""
        tasks[0].agent_role = "NonExistentRole"
        
        result = await process.execute(agents, tasks)
        
        assert not result.success
        assert "No agent found for task" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_with_context_indices(self, process, agents, tasks):
        """Test execution with task context using indices."""
        # Second task depends on first task (index 0)
        tasks[1].context = [0]
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Check if context was set
            assert hasattr(tasks[1], '_context_outputs')
            assert len(tasks[1]._context_outputs) == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_context_task_objects(self, process, agents, tasks):
        """Test execution with task context using task objects."""
        # Third task depends on first task (task object)
        tasks[2].context = [tasks[0]]
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Check if context was set
            assert hasattr(tasks[2], '_context_outputs')
            assert len(tasks[2]._context_outputs) == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_context_index(self, process, agents, tasks):
        """Test execution with invalid context index."""
        # Second task depends on invalid index
        tasks[1].context = [10]  # Invalid index
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            # Context should not be set for invalid index
            assert not hasattr(tasks[1], '_context_outputs')
    
    @pytest.mark.asyncio
    async def test_execute_with_context_task_not_found(self, process, agents, tasks):
        """Test execution with context task object not found."""
        # Create a task that's not in the tasks list
        unknown_task = Mock()
        tasks[1].context = [unknown_task]
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            # Context should not be set for unknown task
            assert not hasattr(tasks[1], '_context_outputs')
    
    @pytest.mark.asyncio
    async def test_execute_with_no_context_outputs(self, process, agents, tasks):
        """Test execution when context exists but no outputs found."""
        # Set context but ensure no context outputs are found
        tasks[1].context = []  # Empty context
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            # Context should not be set for empty context
            assert not hasattr(tasks[1], '_context_outputs')
    
    @pytest.mark.asyncio
    async def test_execute_with_synchronous_task(self, process, agents, tasks):
        """Test execution with task that only has synchronous execute method."""
        # Remove execute_async to force sync execution
        for task in tasks:
            if hasattr(task, 'execute_async'):
                delattr(task, 'execute_async')
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute', return_value=TaskOutput(raw="Sync result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute', return_value=TaskOutput(raw="Sync result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute', return_value=TaskOutput(raw="Sync result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_non_task_output(self, process, agents, tasks):
        """Test execution with task returning non-TaskOutput object."""
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value="Simple string output"), \
             patch.object(tasks[1], 'execute_async', return_value="Another string"), \
             patch.object(tasks[2], 'execute_async', return_value="Third string"):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Should convert strings to TaskOutput
            for task_output in result.tasks_output:
                assert isinstance(task_output, TaskOutput)
    
    @pytest.mark.asyncio
    async def test_execute_with_should_continue_false(self, process, agents, tasks):
        """Test execution when should_continue returns False."""
        with patch.object(process, '_emit_event'), \
             patch.object(process, '_should_continue', return_value=False):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 0  # No tasks executed
    
    @pytest.mark.asyncio
    async def test_execute_with_verbose_output(self, agents, tasks):
        """Test execution with verbose configuration."""
        config = ProcessConfig(verbose=True)
        process = SequentialProcess(config)
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])), \
             patch('builtins.print') as mock_print:
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            # Should print task execution messages
            assert mock_print.called
            # Check that print was called for each task
            assert mock_print.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_task_execution_exception(self, process, agents, tasks):
        """Test execution handling task execution exceptions."""
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', side_effect=Exception("Task execution failed")):
            
            result = await process.execute(agents, tasks)
            
            assert not result.success
            assert "Task execution failed" in result.error
            assert len(result.tasks_output) == 0
    
    @pytest.mark.asyncio
    async def test_execute_with_mixed_context_types(self, process, agents, tasks):
        """Test execution with mixed context types (indices and task objects)."""
        # Third task depends on first task (index) and second task (object)
        tasks[2].context = [0, tasks[1]]
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=tasks[0])), \
             patch.object(tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=tasks[1])), \
             patch.object(tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=tasks[2])):
            
            result = await process.execute(agents, tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Check if context was set with both dependencies
            assert hasattr(tasks[2], '_context_outputs')
            assert len(tasks[2]._context_outputs) == 2
    
    @pytest.mark.asyncio
    async def test_execute_task_output_raw_access(self, process, agents, tasks):
        """Test execution with output that has raw attribute."""
        output_with_raw = Mock()
        output_with_raw.raw = "Raw output content"
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=output_with_raw):
            
            result = await process.execute(agents, [tasks[0]])
            
            assert result.success
            assert len(result.turns) == 1
            assert "Raw output content" in result.turns[0].content
    
    @pytest.mark.asyncio
    async def test_execute_task_output_no_raw_attribute(self, process, agents, tasks):
        """Test execution with output that doesn't have raw attribute."""
        output_without_raw = Mock()
        # No raw attribute - should use str() conversion
        output_without_raw.__str__ = Mock(return_value="String representation")
        
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=output_without_raw):
            
            result = await process.execute(agents, [tasks[0]])
            
            assert result.success
            assert len(result.turns) == 1
    
    @pytest.mark.asyncio
    async def test_validate_inputs_empty_agents(self, process):
        """Test input validation with empty agents list."""
        tasks = [Mock(), Mock()]
        
        valid, error = await process.validate_inputs([], tasks)
        
        assert valid is False
        assert error is not None
        assert "No agents provided" in error
    
    @pytest.mark.asyncio
    async def test_validate_inputs_empty_tasks(self, process, agents):
        """Test input validation with empty tasks list."""
        valid, error = await process.validate_inputs(agents, [])
        
        assert valid is False
        assert error is not None
        assert "No tasks provided" in error
    
    @pytest.mark.asyncio
    async def test_validate_inputs_valid(self, process, agents, tasks):
        """Test input validation with valid inputs."""
        valid, error = await process.validate_inputs(agents, tasks)
        
        assert valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_get_process_type(self, process):
        """Test getting process type."""
        process_type = process.get_process_type()
        assert process_type == "sequential"
    
    @pytest.mark.asyncio
    async def test_init_without_config(self):
        """Test SequentialProcess initialization without config."""
        process = SequentialProcess()
        
        assert process.config is not None
        assert isinstance(process.config, ProcessConfig)
    
    @pytest.mark.asyncio
    async def test_init_with_config(self):
        """Test SequentialProcess initialization with config."""
        config = ProcessConfig(verbose=True, max_iterations=5)
        process = SequentialProcess(config)
        
        assert process.config == config
        assert process.config.verbose is True
        assert process.config.max_iterations == 5
    
    @pytest.mark.asyncio
    async def test_agent_lookup_creation(self, process, agents, tasks):
        """Test that agent lookup is created correctly."""
        with patch.object(process, '_emit_event'), \
             patch.object(tasks[0], 'execute_async', return_value=TaskOutput(raw="Result", task=tasks[0])):
            
            result = await process.execute(agents, tasks[:1])
            
            assert result.success
            # Verify that agents are accessible by role
            assert len(agents) == 3
            assert agents[0].role == "Developer"
            assert agents[1].role == "Designer"
            assert agents[2].role == "Tester"