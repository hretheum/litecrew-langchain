"""Tests for LiteCrew Multi-Process Engine"""

import asyncio
import time
from unittest.mock import Mock, patch
import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput
from litecrew.processes import (
    BaseProcess, 
    ProcessConfig, 
    ProcessResult,
    ProcessFactory,
    SequentialProcess,
    HierarchicalProcess
)


class TestProcessConfig:
    """Test ProcessConfig validation"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ProcessConfig()
        assert config.verbose is False
        assert config.max_iterations is None
        assert config.timeout is None
        assert config.callbacks == []
        assert config.metadata == {}
        
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = ProcessConfig(max_iterations=10, timeout=30.0)
        config.validate()  # Should not raise
        
        # Invalid max_iterations
        with pytest.raises(ValueError, match="max_iterations must be positive"):
            config = ProcessConfig(max_iterations=0)
            config.validate()
            
        # Invalid timeout
        with pytest.raises(ValueError, match="timeout must be positive"):
            config = ProcessConfig(timeout=-1)
            config.validate()


class TestProcessFactory:
    """Test ProcessFactory functionality"""
    
    def test_register_and_create(self):
        """Test registering and creating process types"""
        # Clear registry for clean test
        ProcessFactory.clear_registry()
        
        # Register test process
        class TestProcess(BaseProcess):
            async def execute(self, agents, tasks, inputs=None):
                return ProcessResult(raw="test")
                
        ProcessFactory.register("test", TestProcess)
        
        # Create instance
        process = ProcessFactory.create("test")
        assert isinstance(process, TestProcess)
        
    def test_create_with_config(self):
        """Test creating process with configuration"""
        ProcessFactory.clear_registry()
        
        class ConfigurableProcess(BaseProcess):
            def __init__(self, config=None):
                super().__init__(config)
                self.custom_value = None
                
            @classmethod
            def from_config(cls, base_config, specific_config):
                instance = cls(base_config)
                instance.custom_value = specific_config.get('custom_value')
                return instance
                
            async def execute(self, agents, tasks, inputs=None):
                return ProcessResult(raw=f"custom: {self.custom_value}")
                
        ProcessFactory.register("configurable", ConfigurableProcess)
        
        # Create with config
        process = ProcessFactory.create(
            "configurable",
            {"verbose": True, "custom_value": "test123"}
        )
        assert process.config.verbose is True
        assert process.custom_value == "test123"
        
    def test_unknown_process_type(self):
        """Test error for unknown process type"""
        with pytest.raises(ValueError, match="Unknown process type"):
            ProcessFactory.create("nonexistent")
            
    def test_list_types(self):
        """Test listing available process types"""
        ProcessFactory.clear_registry()
        ProcessFactory.register("type1", SequentialProcess)
        ProcessFactory.register("type2", HierarchicalProcess)
        
        types = ProcessFactory.list_types()
        assert "type1" in types
        assert "type2" in types


class TestBaseProcess:
    """Test BaseProcess functionality"""
    
    class SimpleProcess(BaseProcess):
        """Simple test process"""
        async def execute(self, agents, tasks, inputs=None):
            self._track_time()  # Start time tracking
            turns = []
            for agent in agents:
                turn = self._create_turn(agent, f"Hello from {agent.role}")
                turns.append(turn)
            # Add small delay to ensure duration > 0
            await asyncio.sleep(0.001)
            return ProcessResult(
                raw=self._aggregate_results(turns, []),
                turns=turns,
                duration=self._get_duration()
            )
    
    @pytest.mark.asyncio
    async def test_time_tracking(self):
        """Test execution time tracking"""
        process = self.SimpleProcess()
        agent = LiteAgent(role="Test", goal="Test", backstory="Test")
        
        result = await process.execute([agent], [])
        
        assert result.duration > 0
        assert result.duration < 1.0  # Should be very fast
        
    @pytest.mark.asyncio
    async def test_input_validation(self):
        """Test input validation"""
        process = self.SimpleProcess()
        
        # No agents
        valid, error = await process.validate_inputs([], [LiteTask(description="test")])
        assert not valid
        assert "No agents" in error
        
        # No tasks
        valid, error = await process.validate_inputs([LiteAgent(role="Test", goal="Test", backstory="Test")], [])
        assert not valid
        assert "No tasks" in error
        
    def test_process_type_name(self):
        """Test getting process type name"""
        process = self.SimpleProcess()
        assert process.get_process_type() == "simple"
        
    @pytest.mark.asyncio
    async def test_max_iterations(self):
        """Test max iterations limit"""
        process = self.SimpleProcess(ProcessConfig(max_iterations=2))
        
        # Simulate checking iterations
        assert process._should_continue(0) is True
        assert process._should_continue(1) is True
        assert process._should_continue(2) is False
        
    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test timeout functionality"""
        process = self.SimpleProcess(ProcessConfig(timeout=0.1))
        process._track_time()
        
        # Initially should continue
        assert process._should_continue(0) is True
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        assert process._should_continue(0) is False
        
    def test_event_emission(self):
        """Test event emission to callbacks"""
        callback = Mock()
        callback.on_event = Mock()
        
        process = self.SimpleProcess(ProcessConfig(callbacks=[callback]))
        process._emit_event("test_event", {"data": "test"})
        
        callback.on_event.assert_called_once_with("test_event", {"data": "test"})


class TestSequentialProcess:
    """Test SequentialProcess execution"""
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test basic sequential task execution"""
        # Setup agents and tasks
        agent1 = LiteAgent(role="Researcher", goal="Research", backstory="Expert")
        agent2 = LiteAgent(role="Writer", goal="Write", backstory="Author")
        
        task1 = LiteTask(description="Research topic", agent=agent1)
        task2 = LiteTask(description="Write article", agent=agent2)
        
        # Mock agent execution instead of task.execute
        agent1.execute = Mock(return_value="Research complete")
        agent2.execute = Mock(return_value="Article written")
        
        # Execute process
        process = SequentialProcess()
        result = await process.execute([agent1, agent2], [task1, task2])
        
        # Verify results
        assert result.success is True
        assert len(result.tasks_output) == 2
        assert result.tasks_output[0].raw == "Research complete"
        assert result.tasks_output[1].raw == "Article written"
        assert len(result.turns) == 2
        
    @pytest.mark.asyncio
    async def test_sequential_with_context(self):
        """Test sequential execution with task context"""
        agent = LiteAgent(role="Worker", goal="Work", backstory="Expert")
        
        task1 = LiteTask(description="Task 1", agent=agent)
        task2 = LiteTask(description="Task 2", agent=agent)
        
        # Mock execution
        agent.execute = Mock(side_effect=["Output 1", "Output 2"])
        
        process = SequentialProcess()
        result = await process.execute([agent], [task1, task2])
        
        # Verify execution
        assert result.success is True
        assert len(result.tasks_output) == 2
        # Check context was preserved
        assert result.tasks_output[0].raw == "Output 1"
        assert result.tasks_output[1].raw == "Output 2"


class TestHierarchicalProcess:
    """Test HierarchicalProcess execution"""
    
    @pytest.mark.asyncio
    async def test_hierarchical_execution(self):
        """Test hierarchical process with manager"""
        # Setup agents
        manager = LiteAgent(role="Manager", goal="Manage", backstory="Leader")
        worker1 = LiteAgent(role="Developer", goal="Code", backstory="Coder")
        worker2 = LiteAgent(role="Tester", goal="Test", backstory="QA")
        
        # Setup tasks
        task1 = LiteTask(description="Implement feature", agent_role="Developer")
        task2 = LiteTask(description="Test feature", agent_role="Tester")
        
        # Mock execution - workers do the actual execution
        worker1.execute = Mock(return_value="Feature implemented")
        worker2.execute = Mock(return_value="Tests passed")
        
        # Execute
        process = HierarchicalProcess()
        result = await process.execute([manager, worker1, worker2], [task1, task2])
        
        # Verify
        assert result.success is True
        assert len(result.tasks_output) == 2
        assert "manager" in result.metadata
        assert result.metadata["manager"] == "Manager"
        assert set(result.metadata["workers"]) == {"Developer", "Tester"}
        
        # Check turns include manager activities
        manager_turns = [t for t in result.turns if t.agent == "Manager"]
        assert len(manager_turns) >= 3  # analysis, delegations, review, summary
        
    @pytest.mark.asyncio
    async def test_hierarchical_fallback_to_sequential(self):
        """Test hierarchical falls back to sequential with no workers"""
        manager = LiteAgent(role="Manager", goal="Do all", backstory="Solo")
        task = LiteTask(description="Do everything", agent=manager)
        
        # Mock manager execution
        manager.execute = Mock(return_value="Done")
        
        process = HierarchicalProcess()
        result = await process.execute([manager], [task])
        
        # Should work like sequential
        assert result.success is True
        assert len(result.tasks_output) == 1


class TestProcessPerformance:
    """Test performance metrics"""
    
    def test_process_instantiation_time(self):
        """Test process instantiation is fast"""
        start = time.perf_counter()
        
        for _ in range(100):
            process = SequentialProcess()
            
        duration = time.perf_counter() - start
        avg_time = duration / 100 * 1000  # Convert to ms
        
        assert avg_time < 10  # Should be less than 10ms
        
    def test_process_memory_overhead(self):
        """Test process memory overhead is low"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure baseline
        baseline = process.memory_info().rss
        
        # Create many processes
        processes = []
        for _ in range(100):
            p = SequentialProcess(ProcessConfig(verbose=True))
            processes.append(p)
            
        # Measure after
        after = process.memory_info().rss
        
        # Calculate overhead per process
        overhead_mb = (after - baseline) / (1024 * 1024) / 100
        
        assert overhead_mb < 1  # Less than 1MB per process
        
    @pytest.mark.asyncio
    async def test_process_switching_time(self):
        """Test process switching is fast"""
        from litecrew.crew import LiteCrew
        
        agents = [LiteAgent(role=f"Agent{i}", goal="Work", backstory="Pro") for i in range(3)]
        tasks = [LiteTask(description=f"Task {i}") for i in range(3)]
        
        crew = LiteCrew(agents=agents, tasks=tasks, process="sequential")
        
        # Measure switching time
        start = time.perf_counter()
        crew.switch_process("hierarchical", {"manager_rounds": 2})
        duration = (time.perf_counter() - start) * 1000  # ms
        
        assert duration < 5  # Should be less than 5ms
        assert crew.process == "hierarchical"
        assert crew.process_config["manager_rounds"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])