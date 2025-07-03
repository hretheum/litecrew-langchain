"""
Pytest configuration and fixtures for LiteCrew tests.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load test environment
load_dotenv(".env.test", override=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_environment():
    """Ensure test environment variables are set."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Use test DB
    yield
    # Cleanup if needed


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    from unittest.mock import Mock
    
    mock = Mock()
    mock.invoke.return_value = "Mocked LLM response"
    mock.ainvoke.return_value = "Mocked async LLM response"
    return mock


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for tests."""
    return {
        "role": "Test Analyst",
        "goal": "Analyze test data",
        "backstory": "Expert in testing and analysis",
        "verbose": False,
        "allow_delegation": False,
    }


@pytest.fixture
def sample_task_config():
    """Sample task configuration for tests."""
    return {
        "description": "Analyze the test results",
        "expected_output": "A detailed analysis report",
        "async_execution": False,
    }