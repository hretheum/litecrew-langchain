"""Basic health check tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test basic health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"

def test_detailed_health_check():
    """Test detailed health endpoint"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "components" in data
    assert "system" in data
    assert "costs" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to LiteCrewAI"
    assert data["version"] == "0.1.0"

def test_404_handler():
    """Test 404 error handling"""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Not found"
    assert data["path"] == "/nonexistent"

def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "litecrewai_info" in response.text
    assert "litecrewai_requests_total" in response.text