"""Targeted tests for specific coverage gaps."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

def test_api_templates_basic():
    """Test basic API templates functionality."""
    from litecrew.api.templates import ProcessTemplate
    
    # Test template initialization
    template = ProcessTemplate(
        name="test_template",
        description="Test template",
        process_type="sequential"
    )
    assert template.name == "test_template"
    assert template.description == "Test template"
    assert template.process_type == "sequential"
    
    # Test basic methods
    config = template.get_process_config()
    assert isinstance(config, dict)
    
    defaults = template.get_default_inputs()
    assert isinstance(defaults, dict)
    
    # Test estimated_time if it exists
    if hasattr(template, 'estimated_time'):
        time_estimate = template.estimated_time()
        assert isinstance(time_estimate, int)


def test_llm_manager_basic():
    """Test basic LLM manager functionality."""
    from litecrew.llm.manager import LLMManager
    
    # Test initialization
    manager = LLMManager()
    assert manager is not None
    
    # Test get_available_providers
    providers = manager.get_available_providers()
    assert isinstance(providers, list)
    assert len(providers) > 0
    
    # Test metrics property
    metrics = manager._metrics
    assert isinstance(metrics, dict)
    assert "provider_switches" in metrics
    assert "total_creations" in metrics


def test_api_routers_basic():
    """Test basic API routers functionality."""
    from litecrew.api.routers.agents import router as agents_router
    from litecrew.api.routers.tasks import router as tasks_router
    
    # Test routers exist
    assert agents_router is not None
    assert tasks_router is not None
    
    # Test routers have routes
    assert len(agents_router.routes) > 0
    assert len(tasks_router.routes) > 0


def test_crew_basic_coverage():
    """Test basic crew functionality to boost coverage."""
    from litecrew.crew import LiteCrew
    from litecrew import LiteAgent, LiteTask
    
    # Test crew initialization
    agent = LiteAgent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory"
    )
    
    task = LiteTask(
        description="Test task",
        expected_output="Test output"
    )
    
    crew = LiteCrew(
        agents=[agent],
        tasks=[task]
    )
    
    assert crew is not None
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
    
    # Test basic methods exist
    assert hasattr(crew, 'kickoff')
    
    # Test usage metrics property
    if hasattr(crew, 'usage_metrics'):
        metrics = crew.usage_metrics
        assert isinstance(metrics, dict)


def test_memory_basic():
    """Test basic memory functionality."""
    from litecrew.memory.conversation import ConversationMemory
    
    # Test initialization
    memory = ConversationMemory()
    assert memory is not None
    
    # Test basic operations
    memory.add_turn("user", "Hello")
    memory.add_turn("assistant", "Hi!")
    
    turns = memory.get_turns()
    assert len(turns) == 2
    
    # Test clear
    memory.clear()
    turns = memory.get_turns()
    assert len(turns) == 0


