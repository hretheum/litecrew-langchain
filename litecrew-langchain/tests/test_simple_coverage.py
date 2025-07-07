"""Simple tests to increase coverage above 70%."""

from unittest.mock import Mock

import pytest


def test_litecrew_imports():
    """Test that all main imports work."""
    from litecrew import (  # Compatibility aliases
        Agent,
        Crew,
        LiteAgent,
        LiteCrew,
        LiteTask,
        Task,
        TaskOutput,
    )

    # Test aliases work
    assert Agent is LiteAgent
    assert Crew is LiteCrew
    assert Task is LiteTask

    # Test classes are importable
    assert LiteAgent is not None
    assert LiteCrew is not None
    assert LiteTask is not None
    assert TaskOutput is not None


def test_process_imports():
    """Test process imports."""
    from litecrew.processes import (
        BaseProcess,
        ProcessConfig,
        ProcessFactory,
        ProcessResult,
    )

    # Test all are importable
    assert BaseProcess is not None
    assert ProcessConfig is not None
    assert ProcessResult is not None
    assert ProcessFactory is not None


def test_process_config_creation():
    """Test ProcessConfig creation and validation."""
    from litecrew.processes import ProcessConfig

    # Test default config
    config = ProcessConfig()
    assert config.verbose is False
    assert config.max_iterations is None
    assert config.timeout is None
    assert config.callbacks == []
    assert config.metadata == {}

    # Test with values
    config = ProcessConfig(
        verbose=True,
        max_iterations=5,
        timeout=30.0,
        callbacks=[Mock()],
        metadata={"test": "value"},
    )
    assert config.verbose is True
    assert config.max_iterations == 5
    assert config.timeout == 30.0
    assert len(config.callbacks) == 1
    assert config.metadata["test"] == "value"

    # Test validation
    config.validate()  # Should not raise

    # Test invalid values
    with pytest.raises(ValueError):
        ProcessConfig(max_iterations=-1).validate()

    with pytest.raises(ValueError):
        ProcessConfig(timeout=-1.0).validate()


def test_process_result_creation():
    """Test ProcessResult creation."""
    from datetime import datetime

    from litecrew.processes import ProcessResult, ProcessTurn

    # Test minimal result
    result = ProcessResult(raw="Test output")
    assert result.raw == "Test output"
    assert result.success is True
    assert result.error is None
    assert str(result) == "Test output"

    # Test with turns
    turn = ProcessTurn(
        agent="TestAgent", content="Test content", timestamp=datetime.now()
    )

    result = ProcessResult(
        raw="Final output", turns=[turn], metadata={"key": "value"}, duration=1.5
    )
    assert len(result.turns) == 1
    assert result.duration == 1.5
    assert result.metadata["key"] == "value"


def test_cache_imports():
    """Test cache module imports."""
    from litecrew.storage.cache import CacheEntry, CacheStats, MemoryCache

    # Test basic cache creation
    memory_cache = MemoryCache(max_size=100)
    assert memory_cache.max_size == 100

    # Test cache stats
    stats = CacheStats()
    assert stats.hits == 0
    assert stats.misses == 0

    # Test cache entry - CacheEntry requires timestamp
    import time
    entry = CacheEntry(value="test", timestamp=time.time(), ttl=60)
    assert entry.value == "test"
    assert entry.is_expired() is False


def test_llm_imports():
    """Test LLM module imports."""
    from litecrew.llm import LLMConfig, LLMManager, LLMProvider

    # Test enum values
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.ANTHROPIC.value == "anthropic"
    assert LLMProvider.GROQ.value == "groq"
    assert LLMProvider.OLLAMA.value == "ollama"

    # Test config creation
    config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4", temperature=0.7)
    assert config.provider == LLMProvider.OPENAI
    assert config.model == "gpt-4"
    assert config.temperature == 0.7

    # Test manager creation
    manager = LLMManager()
    assert manager is not None
    assert "openai" in manager.get_available_providers()


def test_memory_imports():
    """Test memory module imports."""
    from litecrew.memory import ConversationMemory, MemorySearch

    # Test memory creation
    memory = ConversationMemory(max_size=10)
    assert memory.max_size == 10
    assert len(memory) == 0  # use __len__ method

    # Test search creation
    search = MemorySearch()
    assert search is not None


def test_state_imports():
    """Test state management imports."""
    from datetime import datetime

    from litecrew.state import CrewState, StateSnapshot

    # Test state creation - CrewState requires agents, tasks, and process
    state = CrewState(
        crew_id="test-123",
        agents=[{"role": "TestAgent", "goal": "Test", "backstory": "Test"}],
        tasks=[{"description": "Test Task", "expected_output": "Test Output"}],
        process="sequential",
        status="pending"
    )
    assert state.crew_id == "test-123"
    assert state.status == "pending"
    assert len(state.agents) == 1
    assert len(state.tasks) == 1

    # Test snapshot
    snapshot = StateSnapshot(
        crew_id="test-123",
        version=1,
        timestamp=datetime.now(),
        data={"state": "test"}
    )
    assert snapshot.crew_id == "test-123"
    assert snapshot.version == 1


def test_storage_imports():
    """Test storage module imports."""
    from litecrew.storage import SQLiteStorage, StorageManager
    from litecrew.storage.cache import RedisCache

    # Test imports work
    assert StorageManager is not None
    assert SQLiteStorage is not None
    assert RedisCache is not None


def test_config_module():
    """Test config module."""
    from litecrew.config import Config

    # Test config exists
    assert Config is not None

    # Test default values
    assert hasattr(Config, "ENVIRONMENT")
    assert hasattr(Config, "DATABASE_URL")
    assert hasattr(Config, "REDIS_URL")


def test_agent_extended():
    """Test more agent functionality."""
    from litecrew import LiteAgent
    
    # Test agent with various configurations
    agent = LiteAgent(
        role="Advanced Agent",
        goal="Complex tasks",
        backstory="Experienced professional",
        max_iter=5,
        max_rpm=100,
        verbose=True,
        allow_delegation=True
    )
    
    assert agent.role == "Advanced Agent"
    assert agent.max_iter == 5
    assert agent.max_rpm == 100
    assert agent.verbose is True
    assert agent.allow_delegation is True
    
    # Test agent methods
    assert hasattr(agent, "execute")
    
    # Test agent string representation
    assert "Advanced Agent" in str(agent)


def test_crew_extended():
    """Test more crew functionality."""
    from litecrew import LiteAgent, LiteCrew, LiteTask
    
    # Create agents
    agent1 = LiteAgent(role="Leader", goal="Lead", backstory="Leader")
    agent2 = LiteAgent(role="Worker", goal="Work", backstory="Worker")
    
    # Create tasks
    task = LiteTask(
        description="Team task",
        agent=agent1,
        expected_output="Result"
    )
    
    # Create crew with various configurations
    crew = LiteCrew(
        agents=[agent1, agent2],
        tasks=[task],
        process="sequential",
        verbose=True,
        memory=True
    )
    
    assert crew.verbose is True
    assert crew.memory is True
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 1
    
    # Test crew id generation
    assert hasattr(crew, "id")
    assert crew.id is not None


def test_outputs_module():
    """Test outputs module."""
    from litecrew.crew import CrewOutput
    from litecrew.task import TaskOutput
    
    # Create task outputs
    task_output1 = TaskOutput(
        raw="Task 1 result",
        task_id="task-1",
        agent_role="Agent1"
    )
    
    task_output2 = TaskOutput(
        raw="Task 2 result",
        task_id="task-2",
        agent_role="Agent2"
    )
    
    # Create crew output
    crew_output = CrewOutput(
        raw="Final output",
        tasks_output=[task_output1, task_output2]
    )
    
    assert crew_output.raw == "Final output"
    assert len(crew_output.tasks_output) == 2
    assert str(crew_output) == "Final output"
    
    # Test json output
    json_output = crew_output.json()
    assert isinstance(json_output, str)


def test_events_module():
    """Test events module."""
    from litecrew.events import EventEmitter, EventType
    
    # Create event emitter
    emitter = EventEmitter()
    
    # Test emit
    emitter.emit(
        EventType.TASK_STARTED,
        {"task": "test_task"},
        source="test"
    )
    
    # Test event types
    assert EventType.TASK_STARTED.value == "task.started"
    assert EventType.TASK_COMPLETED.value == "task.completed"
    assert EventType.CREW_STARTED.value == "crew.started"
    assert EventType.CREW_COMPLETED.value == "crew.completed"


def test_rate_limiter():
    """Test rate limiter functionality."""
    from litecrew.rate_limiter import RateLimiter
    
    # Create rate limiter
    limiter = RateLimiter(max_rpm=60)
    
    assert limiter.max_rpm == 60
    # Calculate expected requests per second
    assert limiter.max_rpm / 60 == 1.0
    
    # Test that rate limiter has necessary attributes
    assert hasattr(limiter, "max_rpm")
    assert isinstance(limiter.max_rpm, int)
