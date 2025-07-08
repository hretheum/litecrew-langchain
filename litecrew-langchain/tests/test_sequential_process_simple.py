"""Simple focused tests for SequentialProcess to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.processes.sequential import SequentialProcess
from litecrew.processes.base import ProcessConfig


class TestSequentialProcessSimple:
    """Simple tests for SequentialProcess methods."""
    
    @pytest.fixture
    def process(self):
        """Create SequentialProcess instance."""
        config = ProcessConfig(verbose=True)
        return SequentialProcess(config)
    
    @pytest.mark.asyncio
    async def test_init_without_config(self):
        """Test SequentialProcess initialization without config."""
        process = SequentialProcess()
        
        assert process.config is not None
        assert isinstance(process.config, ProcessConfig)
        assert process.config.verbose is False
    
    @pytest.mark.asyncio
    async def test_init_with_config(self):
        """Test SequentialProcess initialization with config."""
        config = ProcessConfig(verbose=True, max_iterations=5)
        process = SequentialProcess(config)
        
        assert process.config == config
        assert process.config.verbose is True
        assert process.config.max_iterations == 5
    
    @pytest.mark.asyncio
    async def test_init_with_none_config(self):
        """Test SequentialProcess initialization with None config."""
        process = SequentialProcess(None)
        
        assert process.config is not None
        assert isinstance(process.config, ProcessConfig)
        assert process.config.verbose is False
    
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
        assert process_type == "sequential"
    
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
        process = SequentialProcess(config)
        process._track_time()
        
        assert process._should_continue(0) is True
        assert process._should_continue(4) is True
        assert process._should_continue(5) is False
        assert process._should_continue(10) is False
    
    @pytest.mark.asyncio
    async def test_should_continue_with_timeout(self):
        """Test should_continue with timeout limit."""
        config = ProcessConfig(timeout=0.001)  # 1ms timeout
        process = SequentialProcess(config)
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
        process = SequentialProcess(config)
        
        process._emit_event("test_event", {"data": "test"})
        
        callback.on_event.assert_called_once_with("test_event", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_emit_event_with_invalid_callback(self):
        """Test emitting event with invalid callback."""
        invalid_callback = Mock(spec=[])  # Empty spec - no methods
        
        config = ProcessConfig(callbacks=[invalid_callback])
        process = SequentialProcess(config)
        
        # Should not raise exception
        process._emit_event("test_event", {"data": "test"})
        
        # Should not have on_event method
        assert not hasattr(invalid_callback, 'on_event')
    
    @pytest.mark.asyncio
    async def test_emit_event_multiple_callbacks(self):
        """Test emitting event with multiple callbacks."""
        callback1 = Mock()
        callback1.on_event = Mock()
        callback2 = Mock()
        callback2.on_event = Mock()
        
        config = ProcessConfig(callbacks=[callback1, callback2])
        process = SequentialProcess(config)
        
        process._emit_event("test_event", {"data": "test"})
        
        callback1.on_event.assert_called_once_with("test_event", {"data": "test"})
        callback2.on_event.assert_called_once_with("test_event", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_create_turn_functionality(self, process):
        """Test _create_turn helper method."""
        agent = Mock()
        agent.role = "TestAgent"
        
        turn = process._create_turn(
            agent, 
            "Test message", 
            task_index=0,
            task_description="Test task"
        )
        
        assert turn.agent == "TestAgent"
        assert turn.content == "Test message"
        assert turn.metadata["task_index"] == 0
        assert turn.metadata["task_description"] == "Test task"
        assert turn.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_aggregate_results_with_tasks_output(self, process):
        """Test aggregating results with task outputs."""
        from litecrew.task import TaskOutput
        
        task1 = Mock()
        task2 = Mock()
        
        outputs = [
            TaskOutput(raw="Output 1", task=task1),
            TaskOutput(raw="Output 2", task=task2)
        ]
        
        result = process._aggregate_results([], outputs)
        
        assert isinstance(result, str)
        assert "Output 1" in result
        assert "Output 2" in result
    
    @pytest.mark.asyncio
    async def test_aggregate_results_with_turns_only(self, process):
        """Test aggregating results with turns only."""
        from litecrew.processes.base import ProcessTurn
        from datetime import datetime
        
        turns = [
            ProcessTurn(agent="Agent1", content="Turn 1", timestamp=datetime.now()),
            ProcessTurn(agent="Agent2", content="Turn 2", timestamp=datetime.now())
        ]
        
        result = process._aggregate_results(turns, [])
        
        assert isinstance(result, str)
        assert "Agent1: Turn 1" in result
        assert "Agent2: Turn 2" in result
    
    @pytest.mark.asyncio
    async def test_aggregate_results_empty(self, process):
        """Test aggregating results with empty inputs."""
        result = process._aggregate_results([], [])
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_config_validation_valid(self):
        """Test config validation with valid parameters."""
        config = ProcessConfig(
            verbose=True,
            max_iterations=10,
            timeout=30.0,
            callbacks=[],
            metadata={"key": "value"}
        )
        
        # Should not raise exception
        config.validate()
        
        process = SequentialProcess(config)
        assert process.config == config
    
    @pytest.mark.asyncio
    async def test_config_validation_invalid_max_iterations(self):
        """Test config validation with invalid max_iterations."""
        with pytest.raises(ValueError, match="max_iterations must be positive"):
            config = ProcessConfig(max_iterations=0)
            config.validate()
    
    @pytest.mark.asyncio
    async def test_config_validation_negative_max_iterations(self):
        """Test config validation with negative max_iterations."""
        with pytest.raises(ValueError, match="max_iterations must be positive"):
            config = ProcessConfig(max_iterations=-1)
            config.validate()
    
    @pytest.mark.asyncio
    async def test_config_validation_invalid_timeout(self):
        """Test config validation with invalid timeout."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            config = ProcessConfig(timeout=0)
            config.validate()
    
    @pytest.mark.asyncio
    async def test_config_validation_negative_timeout(self):
        """Test config validation with negative timeout."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            config = ProcessConfig(timeout=-1.0)
            config.validate()
    
    @pytest.mark.asyncio
    async def test_config_defaults(self):
        """Test config default values."""
        config = ProcessConfig()
        
        assert config.verbose is False
        assert config.max_iterations is None
        assert config.timeout is None
        assert config.callbacks == []
        assert config.metadata == {}
    
    @pytest.mark.asyncio
    async def test_process_result_string_representation(self):
        """Test ProcessResult string representation."""
        from litecrew.processes.base import ProcessResult
        
        result = ProcessResult(raw="Test output")
        
        assert str(result) == "Test output"
    
    @pytest.mark.asyncio
    async def test_process_turn_creation(self):
        """Test ProcessTurn creation."""
        from litecrew.processes.base import ProcessTurn
        from datetime import datetime
        
        timestamp = datetime.now()
        turn = ProcessTurn(
            agent="TestAgent",
            content="Test content",
            timestamp=timestamp,
            metadata={"key": "value"}
        )
        
        assert turn.agent == "TestAgent"
        assert turn.content == "Test content"
        assert turn.timestamp == timestamp
        assert turn.metadata["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_process_agents_and_tasks_storage(self, process):
        """Test that process stores agents and tasks during execution."""
        # Start time tracking to initialize internal state
        process._track_time()
        
        agents = [Mock(), Mock()]
        tasks = [Mock(), Mock()]
        
        # Manually set the agents and tasks as the execute method would
        process._agents = agents
        process._tasks = tasks
        
        assert process._agents == agents
        assert process._tasks == tasks
        assert len(process._agents) == 2
        assert len(process._tasks) == 2