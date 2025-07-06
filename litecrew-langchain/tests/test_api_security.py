"""
Tests for API security features
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["LITECREW_API_KEYS"] = "test-key-123,test-key-456"
os.environ["ENVIRONMENT"] = "test"
os.environ["SESSION_SECRET"] = "test-secret"

from litecrew.api import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Valid auth headers."""
    return {"X-API-Key": "test-key-123"}


class TestAPIAuthentication:
    """Test API authentication."""

    def test_health_endpoint_no_auth_required(self, client):
        """Health endpoint should work without auth."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_crews_endpoint_requires_auth(self, client):
        """Crews endpoint should require authentication."""
        response = client.get("/api/v1/crews")
        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"
        assert response.headers.get("WWW-Authenticate") == "ApiKey"

    def test_invalid_api_key_rejected(self, client):
        """Invalid API key should be rejected."""
        response = client.get("/api/v1/crews", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid API key"

    def test_valid_api_key_accepted(self, client, auth_headers):
        """Valid API key should be accepted."""
        response = client.get("/api/v1/crews", headers=auth_headers)
        assert response.status_code == 200
        assert "crews" in response.json()

    def test_create_crew_requires_auth(self, client):
        """Creating crew should require auth."""
        crew_data = {
            "name": "Test Crew",
            "description": "Test",
            "agents": [{"role": "test", "goal": "test", "backstory": "test"}],
            "tasks": [
                {"description": "test", "agent_role": "test", "expected_output": "test"}
            ],
        }
        response = client.post("/api/v1/crews", json=crew_data)
        assert response.status_code == 401

    def test_create_crew_with_auth(self, client, auth_headers):
        """Creating crew with auth should work."""
        crew_data = {
            "name": "Test Crew",
            "description": "Test",
            "agents": [{"role": "test", "goal": "test", "backstory": "test"}],
            "tasks": [
                {"description": "test", "agent_role": "test", "expected_output": "test"}
            ],
        }
        response = client.post("/api/v1/crews", json=crew_data, headers=auth_headers)
        assert response.status_code == 201
        assert "crew_id" in response.json()


class TestRateLimiting:
    """Test rate limiting."""

    def test_rate_limit_headers_present(self, client, auth_headers):
        """Rate limit headers should be present."""
        response = client.get("/api/v1/crews", headers=auth_headers)
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_authenticated_higher_rate_limit(self, client, auth_headers):
        """Authenticated users should have higher rate limit."""
        response = client.get("/api/v1/crews", headers=auth_headers)
        limit = int(response.headers["X-RateLimit-Limit"])
        assert limit >= 600  # 600 requests per minute for authenticated


class TestSecurityHeaders:
    """Test security headers."""

    def test_security_headers_present(self, client):
        """Security headers should be present."""
        response = client.get("/api/v1/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert (
            response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        )

    def test_process_time_header(self, client):
        """Process time header should be present."""
        response = client.get("/api/v1/health")
        assert "X-Process-Time" in response.headers


class TestExcludedPaths:
    """Test excluded paths."""

    def test_docs_no_auth_required(self, client):
        """Docs should not require auth."""
        response = client.get("/docs")
        # FastAPI returns HTML for docs
        assert response.status_code == 200

    def test_openapi_no_auth_required(self, client):
        """OpenAPI spec should not require auth."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

    def test_root_no_auth_required(self, client):
        """Root path should not require auth."""
        with patch.dict(os.environ, {"REQUIRE_DASHBOARD_AUTH": "false"}):
            app = create_app()
            test_client = TestClient(app)
            response = test_client.get("/")
            assert response.status_code == 200
