"""Simple focused tests for HierarchicalProcess methods."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from litecrew.processes.hierarchical import HierarchicalProcess
from litecrew.task import TaskOutput
from litecrew.processes.base import ProcessConfig


class TestHierarchicalProcessSimple:
    """Simple tests for HierarchicalProcess methods."""
    
    @pytest.fixture
    def process(self):
        """Create HierarchicalProcess instance."""
        config = ProcessConfig(verbose=True)
        return HierarchicalProcess(config)
    
    @pytest.mark.asyncio
    async def test_manager_analyze_tasks(self, process):
        """Test manager task analysis method."""
        tasks = [Mock(), Mock(), Mock()]
        for i, task in enumerate(tasks):
            task.description = f"Task {i+1}"
        
        result = await process._manager_analyze_tasks(tasks)
        
        assert isinstance(result, str)
        assert "Task analysis complete" in result
        assert "Ready to delegate" in result
    
    @pytest.mark.asyncio
    async def test_manager_delegate_task_with_agent_role(self, process):
        """Test manager delegation with specific agent role."""
        task = Mock()
        task.agent_role = "Developer"
        
        worker_agents = [Mock(), Mock(), Mock()]
        worker_agents[0].role = "Developer"
        worker_agents[1].role = "Designer"
        worker_agents[2].role = "Tester"
        
        agent_lookup = {agent.role: agent for agent in worker_agents}
        process._tasks = [task]
        
        result = await process._manager_delegate_task(task, worker_agents, agent_lookup)
        
        assert result == worker_agents[0]
        assert result.role == "Developer"
    
    @pytest.mark.asyncio
    async def test_manager_delegate_task_without_agent_role(self, process):
        """Test manager delegation without specific agent role."""
        task = Mock()
        task.agent_role = None
        
        worker_agents = [Mock(), Mock(), Mock()]
        worker_agents[0].role = "Developer"
        worker_agents[1].role = "Designer"
        worker_agents[2].role = "Tester"
        
        agent_lookup = {agent.role: agent for agent in worker_agents}
        process._tasks = [task, Mock(), Mock()]  # 3 tasks for round-robin
        
        result = await process._manager_delegate_task(task, worker_agents, agent_lookup)
        
        assert result in worker_agents
        assert result == worker_agents[0]  # First task goes to first agent
    
    @pytest.mark.asyncio
    async def test_manager_delegate_task_nonexistent_agent_role(self, process):
        """Test manager delegation with non-existent agent role."""
        task = Mock()
        task.agent_role = "NonExistent"
        
        worker_agents = [Mock(), Mock()]
        worker_agents[0].role = "Developer"
        worker_agents[1].role = "Designer"
        
        agent_lookup = {agent.role: agent for agent in worker_agents}
        process._tasks = [task]
        
        result = await process._manager_delegate_task(task, worker_agents, agent_lookup)
        
        assert result in worker_agents
        assert result == worker_agents[0]  # Falls back to round-robin
    
    @pytest.mark.asyncio
    async def test_manager_delegate_task_round_robin(self, process):
        """Test manager delegation uses round-robin selection."""
        tasks = [Mock(), Mock(), Mock()]
        for i, task in enumerate(tasks):
            task.agent_role = None
        
        worker_agents = [Mock(), Mock()]
        worker_agents[0].role = "Developer"
        worker_agents[1].role = "Designer"
        
        agent_lookup = {agent.role: agent for agent in worker_agents}
        process._tasks = tasks
        
        # First task should go to first agent
        result1 = await process._manager_delegate_task(tasks[0], worker_agents, agent_lookup)
        assert result1 == worker_agents[0]
        
        # Second task should go to second agent
        result2 = await process._manager_delegate_task(tasks[1], worker_agents, agent_lookup)
        assert result2 == worker_agents[1]
        
        # Third task should go back to first agent
        result3 = await process._manager_delegate_task(tasks[2], worker_agents, agent_lookup)
        assert result3 == worker_agents[0]
    
    @pytest.mark.asyncio
    async def test_manager_review_output(self, process):
        """Test manager output review."""
        task = Mock()
        task.description = "Test task"
        
        output = TaskOutput(raw="Test output", task=task)
        
        worker = Mock()
        worker.role = "Developer"
        
        result = await process._manager_review_output(task, output, worker)
        
        assert isinstance(result, str)
        assert "Developer" in result
        assert "work" in result
        assert "meets requirements" in result
    
    @pytest.mark.asyncio
    async def test_manager_review_output_different_workers(self, process):
        """Test manager review for different workers."""
        task = Mock()
        output = TaskOutput(raw="Test output", task=task)
        
        workers = [Mock(), Mock(), Mock()]
        workers[0].role = "Developer"
        workers[1].role = "Designer"
        workers[2].role = "Tester"
        
        for worker in workers:
            result = await process._manager_review_output(task, output, worker)
            assert worker.role in result
            assert "meets requirements" in result
    
    @pytest.mark.asyncio
    async def test_manager_summarize_results_empty(self, process):
        """Test manager summarization with empty results."""
        result = await process._manager_summarize_results([])
        
        assert isinstance(result, str)
        assert "No tasks were completed" in result
    
    @pytest.mark.asyncio
    async def test_manager_summarize_results_single_task(self, process):
        """Test manager summarization with single task."""
        task = Mock()
        output = TaskOutput(raw="Single task result", task=task)
        
        result = await process._manager_summarize_results([output])
        
        assert isinstance(result, str)
        assert "Team successfully completed" in result
        assert "1. Single task result" in result
    
    @pytest.mark.asyncio
    async def test_manager_summarize_results_multiple_tasks(self, process):
        """Test manager summarization with multiple tasks."""
        tasks = [Mock(), Mock(), Mock()]
        outputs = [
            TaskOutput(raw="First task result", task=tasks[0]),
            TaskOutput(raw="Second task result", task=tasks[1]),
            TaskOutput(raw="Third task result", task=tasks[2])
        ]
        
        result = await process._manager_summarize_results(outputs)
        
        assert isinstance(result, str)
        assert "Team successfully completed" in result
        assert "1. First task result" in result
        assert "2. Second task result" in result
        assert "3. Third task result" in result
    
    @pytest.mark.asyncio
    async def test_manager_summarize_results_long_output(self, process):
        """Test manager summarization with long output (truncation)."""
        task = Mock()
        long_output = "This is a very long output that should be truncated because it exceeds the character limit set in the summarization method for display purposes and testing truncation functionality."
        output = TaskOutput(raw=long_output, task=task)
        
        result = await process._manager_summarize_results([output])
        
        assert isinstance(result, str)
        assert "Team successfully completed" in result
        # Should contain truncated version
        assert "1. " in result
        assert "..." in result
    
    @pytest.mark.asyncio
    async def test_init_with_config(self):
        """Test HierarchicalProcess initialization with config."""
        config = ProcessConfig(verbose=True, max_iterations=10)
        process = HierarchicalProcess(config)
        
        assert process.config == config
        assert process.config.verbose is True
        assert process.config.max_iterations == 10
        assert process.manager_agent is None
    
    @pytest.mark.asyncio
    async def test_init_without_config(self):
        """Test HierarchicalProcess initialization without config."""
        process = HierarchicalProcess()
        
        assert process.config is not None
        assert isinstance(process.config, ProcessConfig)
        assert process.config.verbose is False
        assert process.manager_agent is None
    
    @pytest.mark.asyncio
    async def test_init_with_none_config(self):
        """Test HierarchicalProcess initialization with None config."""
        process = HierarchicalProcess(None)
        
        assert process.config is not None
        assert isinstance(process.config, ProcessConfig)
        assert process.config.verbose is False
        assert process.manager_agent is None
    
    @pytest.mark.asyncio
    async def test_validate_inputs_empty_agents(self, process):
        """Test input validation with empty agents list."""
        tasks = [Mock(), Mock()]
        
        valid, error = await process.validate_inputs([], tasks)
        
        assert valid is False
        assert error is not None
        assert "No agents provided" in error
    
    @pytest.mark.asyncio
    async def test_validate_inputs_empty_tasks(self, process):
        """Test input validation with empty tasks list."""
        agents = [Mock(), Mock()]
        
        valid, error = await process.validate_inputs(agents, [])
        
        assert valid is False
        assert error is not None
        assert "No tasks provided" in error
    
    @pytest.mark.asyncio
    async def test_validate_inputs_valid(self, process):
        """Test input validation with valid inputs."""
        agents = [Mock(), Mock()]
        tasks = [Mock(), Mock()]
        
        valid, error = await process.validate_inputs(agents, tasks)
        
        assert valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_validate_inputs_single_agent_single_task(self, process):
        """Test input validation with single agent and task."""
        agents = [Mock()]
        tasks = [Mock()]
        
        valid, error = await process.validate_inputs(agents, tasks)
        
        assert valid is True
        assert error is None
    
    @pytest.mark.asyncio
    async def test_get_process_type(self, process):
        """Test getting process type."""
        process_type = process.get_process_type()
        assert process_type == "hierarchical"
    
    @pytest.mark.asyncio
    async def test_track_time_and_duration(self, process):
        """Test time tracking functionality."""
        # Initially duration should be 0
        assert process._get_duration() == 0.0
        
        # After tracking starts, duration should be available
        process._track_time()
        import time
        time.sleep(0.01)  # Small delay
        
        duration = process._get_duration()
        assert duration > 0.0
        assert duration < 1.0  # Should be very small
    
    @pytest.mark.asyncio
    async def test_should_continue_no_limits(self, process):
        """Test should_continue with no limits."""
        process._track_time()
        
        assert process._should_continue(0) is True
        assert process._should_continue(100) is True
        assert process._should_continue(1000) is True
    
    @pytest.mark.asyncio
    async def test_should_continue_with_max_iterations(self):
        """Test should_continue with max iterations limit."""
        config = ProcessConfig(max_iterations=5)
        process = HierarchicalProcess(config)
        process._track_time()
        
        assert process._should_continue(0) is True
        assert process._should_continue(4) is True
        assert process._should_continue(5) is False
        assert process._should_continue(10) is False
    
    @pytest.mark.asyncio
    async def test_should_continue_with_timeout(self):
        """Test should_continue with timeout limit."""
        config = ProcessConfig(timeout=0.001)  # 1ms timeout
        process = HierarchicalProcess(config)
        process._track_time()
        
        import time
        time.sleep(0.002)  # Wait longer than timeout
        
        assert process._should_continue(0) is False
    
    @pytest.mark.asyncio
    async def test_emit_event_no_callbacks(self, process):
        """Test emitting event with no callbacks."""
        # Should not raise any exception
        process._emit_event("test_event", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_emit_event_with_callbacks(self):
        """Test emitting event with callbacks."""
        callback = Mock()
        callback.on_event = Mock()
        
        config = ProcessConfig(callbacks=[callback])
        process = HierarchicalProcess(config)
        
        process._emit_event("test_event", {"data": "test"})
        
        callback.on_event.assert_called_once_with("test_event", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_emit_event_with_invalid_callback(self):
        """Test emitting event with invalid callback."""
        invalid_callback = Mock(spec=[])  # Empty spec - no methods
        
        config = ProcessConfig(callbacks=[invalid_callback])
        process = HierarchicalProcess(config)
        
        # Should not raise exception
        process._emit_event("test_event", {"data": "test"})
        
        # Should not have on_event method
        assert not hasattr(invalid_callback, 'on_event')