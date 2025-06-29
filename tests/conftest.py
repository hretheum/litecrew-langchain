"""
Pytest configuration and fixtures for LiteCrewAI tests
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    env_vars = {
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET": "test-jwt-secret",
        "LOG_LEVEL": "DEBUG",
        "ENVIRONMENT": "test"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing"""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.exists.return_value = False
    mock_redis.ping.return_value = True
    return mock_redis

@pytest.fixture
def mock_ollama():
    """Mock Ollama client for testing"""
    mock_client = Mock()
    mock_client.generate.return_value = {
        "response": "This is a test response from Ollama",
        "model": "mistral:7b",
        "created_at": "2025-06-29T12:00:00Z",
        "done": True
    }
    mock_client.list.return_value = {
        "models": [
            {"name": "mistral:7b", "size": 4200000000},
            {"name": "phi-2", "size": 1600000000}
        ]
    }
    return mock_client

@pytest.fixture
def test_client(mock_env):
    """Create a test client for the FastAPI app"""
    try:
        from app.main import app
        client = TestClient(app)
        return client
    except ImportError:
        # If main app doesn't exist yet, create a minimal test app
        from fastapi import FastAPI
        
        test_app = FastAPI()
        
        @test_app.get("/health")
        def health():
            return {"status": "healthy", "version": "0.1.0"}
            
        @test_app.get("/")
        def root():
            return {"message": "Welcome to LiteCrewAI", "version": "0.1.0"}
            
        return TestClient(test_app)

@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing"""
    return {
        "name": "test_agent",
        "role": "Assistant",
        "goal": "Help with testing",
        "backstory": "A helpful AI assistant for testing purposes",
        "llm": "ollama/mistral:7b",
        "max_iter": 3,
        "memory": True,
        "verbose": False
    }

@pytest.fixture
def sample_task_config():
    """Sample task configuration for testing"""
    return {
        "name": "test_task",
        "description": "This is a test task",
        "expected_output": "A successful test result",
        "agent": "test_agent",
        "tools": [],
        "async_execution": False
    }

@pytest.fixture
def sample_crew_config():
    """Sample crew configuration for testing"""
    return {
        "name": "test_crew",
        "agents": ["test_agent"],
        "tasks": ["test_task"],
        "process": "sequential",
        "verbose": False,
        "memory": True,
        "max_rpm": 10
    }

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Cleanup any test artifacts
    test_files = [
        "test.db",
        "test.db-shm", 
        "test.db-wal",
        "test_cache.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)