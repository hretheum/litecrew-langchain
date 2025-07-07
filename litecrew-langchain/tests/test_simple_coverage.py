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
    from litecrew.cache import CacheEntry, CacheStats, MemoryCache

    # Test basic cache creation
    memory_cache = MemoryCache(max_size=100)
    assert memory_cache.max_size == 100

    # Test cache stats
    stats = CacheStats()
    assert stats.hits == 0
    assert stats.misses == 0

    # Test cache entry
    entry = CacheEntry(value="test", ttl=60)
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
    assert LLMProvider.OPENAI in manager.available_providers()


def test_memory_imports():
    """Test memory module imports."""
    from litecrew.memory import ConversationMemory, MemorySearch

    # Test memory creation
    memory = ConversationMemory(max_turns=10)
    assert memory.max_turns == 10
    assert len(memory.turns) == 0

    # Test search creation
    search = MemorySearch(memory)
    assert search.memory == memory


def test_state_imports():
    """Test state management imports."""
    from datetime import datetime

    from litecrew.state import CrewState, StateSnapshot

    # Test state creation
    state = CrewState(crew_id="test-123", status="pending")
    assert state.crew_id == "test-123"
    assert state.status == "pending"

    # Test snapshot
    snapshot = StateSnapshot(
        state_id="snap-1", crew_state=state, timestamp=datetime.now()
    )
    assert snapshot.state_id == "snap-1"
    assert snapshot.crew_state == state


def test_storage_imports():
    """Test storage module imports."""
    from litecrew.storage import RedisCache, SQLiteStorage, StorageManager

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
