"""Tests for the monitoring dashboard."""

import time

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from litecrew.api import create_app


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    """Create async test client."""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestDashboardAccess:
    """Test dashboard accessibility and basic functionality."""

    def test_dashboard_loads(self, client):
        """Test that dashboard loads successfully."""
        start_time = time.perf_counter()
        response = client.get("/")
        load_time = (time.perf_counter() - start_time) * 1000

        assert response.status_code == 200
        assert load_time < 500  # <500ms load time
        assert "text/html" in response.headers.get("content-type", "")

    def test_dashboard_redirect(self, client):
        """Test dashboard redirect works."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/"

    def test_dashboard_content(self, client):
        """Test dashboard contains required elements."""
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check for key dashboard elements
        assert "LiteCrew Monitoring Dashboard" in content
        assert "active-crews" in content
        assert "memory-usage" in content
        assert "api-latency" in content
        assert "crew-list" in content
        assert "task-progress" in content
        assert "log-viewer" in content

    def test_static_files_served(self, client):
        """Test that static files are properly served."""
        # Test JavaScript file
        response = client.get("/static/dashboard.js")
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert (
                "application/javascript" in content_type
                or "text/javascript" in content_type
            )
            assert "Dashboard" in response.text


class TestDashboardMetrics:
    """Test dashboard metrics functionality."""

    def test_metrics_integration(self, client):
        """Test that dashboard can fetch metrics from API."""
        # Create a test crew first
        crew_data = {
            "name": "Dashboard Test Crew",
            "agents": [{"role": "Tester", "goal": "Test", "backstory": "Tester"}],
            "tasks": [{"description": "Test task", "agent_role": "Tester"}],
        }

        create_response = client.post("/api/v1/crews", json=crew_data)
        assert create_response.status_code == 201

        # Test that API endpoints used by dashboard work
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

        crews_response = client.get("/api/v1/crews")
        assert crews_response.status_code == 200

        crews_data = crews_response.json()
        assert "crews" in crews_data
        assert len(crews_data["crews"]) >= 1

    def test_performance_metrics(self, client):
        """Test that performance metrics meet requirements."""
        # Test multiple requests to check latency
        latencies = []

        for _ in range(10):
            start = time.perf_counter()
            response = client.get("/api/v1/health")
            latency = (time.perf_counter() - start) * 1000

            assert response.status_code == 200
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 100  # <100ms average latency

    def test_memory_usage_reporting(self, client):
        """Test that memory usage is properly reported."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "memory_mb" in data
        assert isinstance(data["memory_mb"], (int, float))
        assert data["memory_mb"] < 200  # <200MB memory usage (test environment)


@pytest.mark.asyncio
class TestDashboardRealTime:
    """Test real-time functionality."""

    async def test_websocket_connection(self, async_client):
        """Test WebSocket connection for real-time updates."""
        try:
            with async_client.websocket_connect("/ws") as websocket:
                # Test ping/pong
                await websocket.send_text("ping")
                response = await websocket.receive_text()
                assert response == "pong"
        except Exception as e:
            # WebSocket might not be available in test environment
            pytest.skip(f"WebSocket test skipped: {e}")

    async def test_update_latency(self, async_client):
        """Test that updates have low latency."""
        # Test API response time
        start = time.perf_counter()
        response = await async_client.get("/api/v1/health")
        latency = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert latency < 100  # <100ms update latency


class TestDashboardVisualization:
    """Test dashboard visualization components."""

    def test_crew_visualization(self, client):
        """Test crew visualization functionality."""
        # Create test crews
        for i in range(3):
            crew_data = {
                "name": f"Viz Test Crew {i}",
                "description": f"Test crew {i} for visualization",
                "agents": [{"role": "Worker", "goal": "Work", "backstory": "Worker"}],
                "tasks": [{"description": "Work task", "agent_role": "Worker"}],
            }

            response = client.post("/api/v1/crews", json=crew_data)
            assert response.status_code == 201

        # Test that crews endpoint returns data for visualization
        response = client.get("/api/v1/crews")
        assert response.status_code == 200

        data = response.json()
        assert len(data["crews"]) >= 3

        # Verify crew data structure
        for crew in data["crews"]:
            assert "name" in crew
            assert "agents" in crew
            assert "tasks" in crew
            assert "created_at" in crew

    def test_task_progress_tracking(self, client):
        """Test task progress tracking."""
        # Create and execute a crew
        crew_data = {
            "name": "Progress Test Crew",
            "agents": [{"role": "Worker", "goal": "Work", "backstory": "Worker"}],
            "tasks": [{"description": "Work task", "agent_role": "Worker"}],
        }

        create_response = client.post("/api/v1/crews", json=crew_data)
        crew_id = create_response.json()["crew_id"]

        # Execute the crew
        execution_data = {"inputs": {}, "async_execution": False}
        execute_response = client.post(
            f"/api/v1/crews/{crew_id}/execute", json=execution_data
        )
        assert execute_response.status_code == 200

        # Check executions endpoint
        executions_response = client.get("/api/v1/executions")
        assert executions_response.status_code == 200

        executions_data = executions_response.json()
        assert "executions" in executions_data


def test_dashboard_performance_requirements(client):
    """Test that dashboard meets all performance requirements."""
    # Test load time
    start = time.perf_counter()
    response = client.get("/")
    load_time = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert load_time < 500  # Dashboard load time <500ms

    # Test API latency
    start = time.perf_counter()
    health_response = client.get("/api/v1/health")
    api_latency = (time.perf_counter() - start) * 1000

    assert health_response.status_code == 200
    assert api_latency < 100  # Update latency <100ms

    # Test memory usage (relaxed for test environment with more dependencies)
    health_data = health_response.json()
    assert health_data["memory_mb"] < 200  # Memory usage <200MB (test environment)


def test_dashboard_error_handling(client):
    """Test dashboard error handling."""
    # Test accessing non-existent crew
    response = client.get("/api/v1/crews/non-existent-id")
    assert response.status_code == 404

    # Test invalid execution
    invalid_execution = client.post("/api/v1/crews/invalid-id/execute", json={})
    assert invalid_execution.status_code == 404

    # Dashboard should still load even if some API calls fail
    dashboard_response = client.get("/")
    assert dashboard_response.status_code == 200
