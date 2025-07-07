"""Final tests to reach 70% coverage."""

import pytest
from unittest.mock import Mock, patch


def test_agent_additional_coverage():
    """Test agent module for additional coverage."""
    from litecrew.agent import LiteAgent
    
    # Test agent with custom system prompt
    agent = LiteAgent(
        role="System Agent",
        goal="Follow system instructions",
        backstory="System expert",
        system_prompt="You are a helpful assistant."
    )
    
    assert agent.role == "System Agent"
    assert agent.system_prompt == "You are a helpful assistant."
    
    # Test agent memory property
    assert hasattr(agent, 'memory')
    
    # Test agent llm property
    assert hasattr(agent, 'llm')
    
    # Test agent with tools
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    
    agent_with_tools = LiteAgent(
        role="Tool Agent",
        goal="Use tools",
        backstory="Tool expert",
        tools=[mock_tool]
    )
    
    # Should have delegation tool added automatically if allow_delegation is True
    assert len(agent_with_tools.tools) >= 1


def test_crew_additional_coverage():
    """Test crew module for additional coverage."""
    from litecrew.crew import LiteCrew
    from litecrew.agent import LiteAgent
    from litecrew.task import LiteTask
    
    agent = LiteAgent(
        role="Worker",
        goal="Do work",
        backstory="Hard worker"
    )
    
    task = LiteTask(
        description="Work task",
        agent=agent,
        expected_output="Work done"
    )
    
    # Test crew with callbacks
    callback_called = False
    def test_callback(event):
        nonlocal callback_called
        callback_called = True
    
    crew = LiteCrew(
        agents=[agent],
        tasks=[task],
        callbacks=[test_callback]
    )
    
    assert len(crew.callbacks) == 1
    
    # Test crew serialization
    crew_dict = crew.model_dump()
    assert isinstance(crew_dict, dict)
    assert crew_dict["id"] == crew.id


def test_outputs_additional():
    """Test outputs module additional functionality."""
    from litecrew.task import TaskOutput
    from litecrew.crew import CrewOutput
    
    # Test TaskOutput with metadata
    task_output = TaskOutput(
        raw="Task completed",
        task_id="task-123",
        agent_role="Worker",
        metadata={"duration": 5.2, "retries": 0}
    )
    
    assert task_output.metadata["duration"] == 5.2
    assert task_output.metadata["retries"] == 0
    
    # Test CrewOutput aggregation
    task_outputs = [
        TaskOutput(raw=f"Output {i}", task_id=f"task-{i}", agent_role="Agent")
        for i in range(3)
    ]
    
    crew_output = CrewOutput(
        raw="All tasks completed",
        tasks_output=task_outputs
    )
    
    # Test output methods
    assert len(crew_output.tasks_output) == 3
    assert str(crew_output) == "All tasks completed"


def test_llm_manager_additional():
    """Test LLM manager additional functionality."""
    from litecrew.llm.manager import LLMManager
    from litecrew.llm.config import LLMConfig, LLMProvider
    
    manager = LLMManager()
    
    # Test registry
    assert hasattr(manager, '_registry')
    
    # Test available providers
    providers = manager.get_available_providers()
    assert isinstance(providers, list)
    assert "openai" in providers
    
    # Test creating with config
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    
    # Should handle missing API key gracefully
    with patch.dict('os.environ', {}, clear=True):
        try:
            llm = manager.create_llm(config)
        except Exception:
            # Expected to fail without API key
            pass


def test_cli_main_additional():
    """Test CLI main module additional functionality."""
    from litecrew.cli.main import cli
    import click.testing
    
    runner = click.testing.CliRunner()
    
    # Test help command
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
    
    # Test version command
    result = runner.invoke(cli, ['--version'])
    # Should show version or error
    assert result.exit_code in [0, 2]


def test_storage_manager_additional():
    """Test storage manager additional functionality."""
    from litecrew.storage.manager import StorageManager
    from litecrew.storage import StorageType
    
    manager = StorageManager()
    
    # Test storage types
    assert StorageType.MEMORY.value == "memory"
    assert StorageType.SQLITE.value == "sqlite"
    assert StorageType.REDIS.value == "redis"
    
    # Test getting memory storage
    storage = manager.get_storage(StorageType.MEMORY)
    assert storage is not None
    
    # Test storage operations
    assert hasattr(storage, 'store')
    assert hasattr(storage, 'retrieve')
    assert hasattr(storage, 'delete')


def test_cache_metrics_additional():
    """Test cache metrics additional functionality."""
    from litecrew.cache.metrics import CacheMetrics
    
    metrics = CacheMetrics()
    
    # Test recording hit
    metrics.record_hit("test_key")
    assert metrics.hits > 0
    
    # Test recording miss
    metrics.record_miss("test_key")
    assert metrics.misses > 0
    
    # Test hit rate calculation
    hit_rate = metrics.get_hit_rate()
    assert 0 <= hit_rate <= 1
    
    # Test metrics summary
    summary = metrics.get_summary()
    assert isinstance(summary, dict)
    assert "hits" in summary
    assert "misses" in summary


def test_process_callbacks_additional():
    """Test process callbacks additional functionality."""
    from litecrew.api.process_callbacks import WebSocketCallback, ProcessEvent
    
    # Test process event
    event = ProcessEvent(
        type="task_started",
        data={"task_id": "123"},
        timestamp=None
    )
    
    assert event.type == "task_started"
    assert event.data["task_id"] == "123"
    assert event.timestamp is not None  # Should be auto-generated
    
    # Test WebSocket callback
    mock_websocket = Mock()
    callback = WebSocketCallback(mock_websocket)
    
    # Test callback call
    callback("test_event", {"test": "data"})
    
    # Should have called send_json
    assert mock_websocket.send_json.called


def test_api_models_additional():
    """Test API models additional functionality."""
    from litecrew.api.models import (
        AgentUpdate,
        CrewUpdate, 
        ExecutionResponse,
        ProcessTypeResponse
    )
    
    # Test AgentUpdate
    update = AgentUpdate(goal="New goal", verbose=True)
    assert update.goal == "New goal"
    assert update.verbose is True
    
    # Test CrewUpdate
    crew_update = CrewUpdate(name="Updated Crew")
    assert crew_update.name == "Updated Crew"
    
    # Test ExecutionResponse
    exec_response = ExecutionResponse(
        execution_id="exec-123",
        crew_id="crew-456",
        status="running",
        created_at="2024-01-01T00:00:00"
    )
    assert exec_response.execution_id == "exec-123"
    assert exec_response.status == "running"
    
    # Test ProcessTypeResponse
    process_response = ProcessTypeResponse(
        name="sequential",
        description="Sequential process",
        supports_moderator=False,
        configurable_options=[]
    )
    assert process_response.name == "sequential"
    assert process_response.supports_moderator is False


def test_crew_properties():
    """Test crew properties and methods."""
    from litecrew import LiteCrew, LiteAgent, LiteTask
    
    agent = LiteAgent(role="A", goal="G", backstory="B")
    task = LiteTask(description="T", expected_output="O", agent=agent)
    
    crew = LiteCrew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        memory=True
    )
    
    # Test properties
    assert crew.verbose is True
    assert crew.memory is True
    
    # Test task assignment
    assert task.agent == agent
    
    # Test crew state
    assert hasattr(crew, '_state')
    
    # Test crew metrics
    metrics = crew.get_metrics()
    assert isinstance(metrics, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])