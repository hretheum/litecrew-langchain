"""Extended tests for HierarchicalProcess to improve coverage."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from litecrew.processes.hierarchical import HierarchicalProcess
from litecrew.task import TaskOutput


class TestHierarchicalProcessExtended:
    """Extended tests for HierarchicalProcess."""
    
    @pytest.fixture
    def manager_agent(self):
        """Create a mock manager agent."""
        agent = Mock()
        agent.role = "Project Manager"
        agent.goal = "Coordinate team tasks"
        agent.backstory = "Experienced project manager"
        return agent
        
    @pytest.fixture
    def worker_agents(self):
        """Create mock worker agents."""
        agents = []
        for role in ["Developer", "Designer", "Tester"]:
            agent = Mock()
            agent.role = role
            agent.goal = f"Complete {role.lower()} tasks"
            agent.backstory = f"Expert {role.lower()}"
            agents.append(agent)
        return agents
        
    @pytest.fixture
    def test_tasks(self):
        """Create test tasks."""
        tasks = []
        for i in range(3):
            task = Mock()
            task.description = f"Task {i+1}: Complete assignment {i+1}"
            task.expected_output = f"Result {i+1}"
            task.agent = None
            tasks.append(task)
        return tasks
        
    @pytest.fixture
    def process(self):
        """Create HierarchicalProcess instance."""
        config = Mock()
        config.verbose = True
        config.max_execution_time = 300
        return HierarchicalProcess(config)
        
    @pytest.mark.asyncio
    async def test_execute_with_specific_agent_role(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution with task having specific agent role."""
        # Set specific agent role for first task
        test_tasks[0].agent_role = "Developer"
        
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', return_value=TaskOutput(raw="Developer result", task=test_tasks[0])), \
             patch.object(test_tasks[1], 'execute_async', return_value=TaskOutput(raw="Designer result", task=test_tasks[1])), \
             patch.object(test_tasks[2], 'execute_async', return_value=TaskOutput(raw="Tester result", task=test_tasks[2])):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            assert result.metadata["process_type"] == "hierarchical"
            assert result.metadata["manager"] == "Project Manager"
            assert "Developer" in result.metadata["workers"]
            
    @pytest.mark.asyncio
    async def test_execute_with_task_context(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution with task context dependencies."""
        # Set context for second task
        test_tasks[1].context = [0]  # Depends on first task
        
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', return_value=TaskOutput(raw="First result", task=test_tasks[0])), \
             patch.object(test_tasks[1], 'execute_async', return_value=TaskOutput(raw="Second result", task=test_tasks[1])), \
             patch.object(test_tasks[2], 'execute_async', return_value=TaskOutput(raw="Third result", task=test_tasks[2])):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Second task should have context from first task
            assert hasattr(test_tasks[1], '_context_outputs')
            
    @pytest.mark.asyncio
    async def test_execute_with_invalid_context(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution with invalid context indices."""
        # Set invalid context
        test_tasks[1].context = [10]  # Invalid index
        
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', return_value=TaskOutput(raw="First result", task=test_tasks[0])), \
             patch.object(test_tasks[1], 'execute_async', return_value=TaskOutput(raw="Second result", task=test_tasks[1])), \
             patch.object(test_tasks[2], 'execute_async', return_value=TaskOutput(raw="Third result", task=test_tasks[2])):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            # Should not set context for invalid indices
            assert not hasattr(test_tasks[1], '_context_outputs')
            
    @pytest.mark.asyncio
    async def test_execute_with_task_execution_exception(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution handling task execution exceptions."""
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', side_effect=Exception("Task execution failed")):
            
            result = await process.execute(agents, test_tasks)
            
            assert not result.success
            assert "Task execution failed" in result.error
            assert len(result.tasks_output) == 0
            
    @pytest.mark.asyncio
    async def test_execute_with_non_task_output(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution with task returning non-TaskOutput object."""
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', return_value="Simple string output"), \
             patch.object(test_tasks[1], 'execute_async', return_value="Another string"), \
             patch.object(test_tasks[2], 'execute_async', return_value="Third string"):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            # Should convert strings to TaskOutput
            for task_output in result.tasks_output:
                assert isinstance(task_output, TaskOutput)
                
    @pytest.mark.asyncio
    async def test_execute_with_should_continue_false(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution when should_continue returns False."""
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(process, '_should_continue', return_value=False):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            assert len(result.tasks_output) == 0  # No tasks executed
            
    @pytest.mark.asyncio
    async def test_execute_with_synchronous_task(self, process, manager_agent, worker_agents, test_tasks):
        """Test execution with task that only has synchronous execute method."""
        agents = [manager_agent] + worker_agents
        
        # Remove async method to force sync execution
        for task in test_tasks:
            if hasattr(task, 'execute_async'):
                delattr(task, 'execute_async')
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute', return_value=TaskOutput(raw="Sync result 1", task=test_tasks[0])), \
             patch.object(test_tasks[1], 'execute', return_value=TaskOutput(raw="Sync result 2", task=test_tasks[1])), \
             patch.object(test_tasks[2], 'execute', return_value=TaskOutput(raw="Sync result 3", task=test_tasks[2])):
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            assert len(result.tasks_output) == 3
            
    @pytest.mark.asyncio
    async def test_manager_analyze_tasks(self, process, test_tasks):
        """Test manager task analysis."""
        analysis = await process._manager_analyze_tasks(test_tasks)
        
        assert isinstance(analysis, str)
        assert "Task analysis complete" in analysis
        
    @pytest.mark.asyncio
    async def test_manager_delegate_task_with_agent_role(self, process, manager_agent, worker_agents, test_tasks):
        """Test manager delegation with specific agent role."""
        process._tasks = test_tasks
        test_tasks[0].agent_role = "Developer"
        
        agent_lookup = {agent.role: agent for agent in [manager_agent] + worker_agents}
        
        delegated = await process._manager_delegate_task(
            test_tasks[0], worker_agents, agent_lookup
        )
        
        assert delegated.role == "Developer"
        
    @pytest.mark.asyncio
    async def test_manager_delegate_task_without_agent_role(self, process, manager_agent, worker_agents, test_tasks):
        """Test manager delegation without specific agent role."""
        process._tasks = test_tasks
        
        agent_lookup = {agent.role: agent for agent in [manager_agent] + worker_agents}
        
        delegated = await process._manager_delegate_task(
            test_tasks[0], worker_agents, agent_lookup
        )
        
        # Should use round-robin selection
        assert delegated in worker_agents
        
    @pytest.mark.asyncio
    async def test_manager_delegate_task_invalid_agent_role(self, process, manager_agent, worker_agents, test_tasks):
        """Test manager delegation with invalid agent role."""
        process._tasks = test_tasks
        test_tasks[0].agent_role = "NonExistentRole"
        
        agent_lookup = {agent.role: agent for agent in [manager_agent] + worker_agents}
        
        delegated = await process._manager_delegate_task(
            test_tasks[0], worker_agents, agent_lookup
        )
        
        # Should fall back to round-robin
        assert delegated in worker_agents
        
    @pytest.mark.asyncio
    async def test_manager_review_output(self, process, manager_agent, worker_agents, test_tasks):
        """Test manager output review."""
        output = TaskOutput(raw="Test output", task=test_tasks[0])
        
        review = await process._manager_review_output(
            test_tasks[0], output, worker_agents[0]
        )
        
        assert isinstance(review, str)
        assert worker_agents[0].role in review
        assert "meets requirements" in review
        
    @pytest.mark.asyncio
    async def test_manager_summarize_results_empty(self, process):
        """Test manager summarization with empty results."""
        summary = await process._manager_summarize_results([])
        
        assert isinstance(summary, str)
        assert "No tasks were completed" in summary
        
    @pytest.mark.asyncio
    async def test_manager_summarize_results_with_outputs(self, process, test_tasks):
        """Test manager summarization with task outputs."""
        outputs = [
            TaskOutput(raw="First result with long content that should be truncated", task=test_tasks[0]),
            TaskOutput(raw="Second result", task=test_tasks[1])
        ]
        
        summary = await process._manager_summarize_results(outputs)
        
        assert isinstance(summary, str)
        assert "Team successfully completed" in summary
        assert "First result with long content that should be truncated" in summary
        assert "Second result" in summary
        
    @pytest.mark.asyncio
    async def test_validate_inputs_valid(self, process, manager_agent, worker_agents, test_tasks):
        """Test input validation with valid inputs."""
        agents = [manager_agent] + worker_agents
        
        valid, error = await process.validate_inputs(agents, test_tasks)
        
        assert valid
        assert error is None
        
    @pytest.mark.asyncio
    async def test_validate_inputs_invalid(self, process):
        """Test input validation with invalid inputs."""
        # Empty agents list
        valid, error = await process.validate_inputs([], [])
        
        assert not valid
        assert error is not None
        
    @pytest.mark.asyncio
    async def test_init_with_config(self):
        """Test HierarchicalProcess initialization with config."""
        config = Mock()
        config.verbose = True
        
        process = HierarchicalProcess(config)
        
        assert process.config == config
        assert process.manager_agent is None
        
    @pytest.mark.asyncio
    async def test_init_without_config(self):
        """Test HierarchicalProcess initialization without config."""
        process = HierarchicalProcess()
        
        assert process.config is not None  # Default config is created
        assert process.manager_agent is None
        
    @pytest.mark.asyncio
    async def test_create_turn_helper(self, process, manager_agent):
        """Test _create_turn helper method."""
        process.manager_agent = manager_agent
        
        turn = process._create_turn(
            manager_agent, 
            "Test message", 
            phase="test", 
            task_index=0
        )
        
        assert turn.agent == manager_agent.role
        assert turn.content == "Test message"
        assert turn.metadata["phase"] == "test"
        assert turn.metadata["task_index"] == 0
        assert turn.timestamp is not None
        
    @pytest.mark.asyncio
    async def test_execute_with_verbose_config(self, manager_agent, worker_agents, test_tasks):
        """Test execution with verbose configuration."""
        config = Mock()
        config.verbose = True
        config.max_execution_time = 300
        
        process = HierarchicalProcess(config)
        agents = [manager_agent] + worker_agents
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', return_value=TaskOutput(raw="Result 1", task=test_tasks[0])), \
             patch.object(test_tasks[1], 'execute_async', return_value=TaskOutput(raw="Result 2", task=test_tasks[1])), \
             patch.object(test_tasks[2], 'execute_async', return_value=TaskOutput(raw="Result 3", task=test_tasks[2])), \
             patch('builtins.print') as mock_print:
            
            result = await process.execute(agents, test_tasks)
            
            assert result.success
            # Should print delegation messages
            assert mock_print.called
            
    @pytest.mark.asyncio
    async def test_execute_with_agent_restoration(self, process, manager_agent, worker_agents, test_tasks):
        """Test that original agent is restored even on exception."""
        agents = [manager_agent] + worker_agents
        
        # Set original agent
        original_agent = Mock()
        test_tasks[0].agent = original_agent
        
        with patch.object(process, '_emit_event'), \
             patch.object(test_tasks[0], 'execute_async', side_effect=Exception("Task failed")):
            
            result = await process.execute(agents, test_tasks)
            
            # Should restore original agent even on exception
            assert test_tasks[0].agent == original_agent
            assert not result.success