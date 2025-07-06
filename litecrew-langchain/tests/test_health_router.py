"""Tests for health router endpoints."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from litecrew.api.routers.health import router


@pytest.fixture
def client():
    """Create test client."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "memory_mb" in data
    assert "uptime" in data

    # Verify values
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

    # Check timestamp format
    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    assert isinstance(timestamp, datetime)

    # Check memory is reasonable
    assert isinstance(data["memory_mb"], (int, float))
    assert data["memory_mb"] > 0

    # Check uptime is reasonable
    assert isinstance(data["uptime"], (int, float))
    assert data["uptime"] > 0


def test_health_check_response_structure(client):
    """Test health check response structure consistency."""
    response1 = client.get("/health")
    response2 = client.get("/health")

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # Same fields in both responses
    assert set(data1.keys()) == set(data2.keys())

    # Status and version should be the same
    assert data1["status"] == data2["status"]
    assert data1["version"] == data2["version"]

    # Memory and uptime might differ slightly
    assert data1["memory_mb"] > 0
    assert data2["memory_mb"] > 0
    assert data1["uptime"] <= data2["uptime"]  # Uptime should increase
