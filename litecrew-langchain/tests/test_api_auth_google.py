"""Tests for Google OAuth module to improve coverage."""

import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

try:
    import jwt
except ImportError:
    # If PyJWT is not installed, skip this test file
    import pytest
    pytest.skip("PyJWT not installed, skipping Google OAuth tests", allow_module_level=True)
import pytest
from fastapi import Request
from fastapi.testclient import TestClient

# Import after setting env vars
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["ALLOWED_EMAIL_DOMAINS"] = "example.com,test.com"
os.environ["ALLOWED_EMAILS"] = "admin@special.com"

from litecrew.api.auth.google import (
    TokenData,
    google_callback,
    is_email_allowed,
    router,
    verify_dashboard_auth,
)


@pytest.fixture
def client():
    """Create test client with Google OAuth router."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestGoogleOAuth:
    """Test Google OAuth functionality."""

    def test_token_data_model(self):
        """Test TokenData model."""
        token_data = TokenData(
            email="test@example.com",
            name="Test User",
            picture="https://example.com/pic.jpg",
            exp=datetime.utcnow() + timedelta(hours=1),
        )
        assert token_data.email == "test@example.com"
        assert token_data.name == "Test User"
        assert token_data.picture == "https://example.com/pic.jpg"

    def test_is_email_allowed_no_restrictions(self):
        """Test email allowed when no restrictions."""
        with patch.dict(
            os.environ, {"ALLOWED_EMAIL_DOMAINS": "", "ALLOWED_EMAILS": ""}
        ):
            assert is_email_allowed("any@email.com") is True

    def test_is_email_allowed_specific_email(self):
        """Test specific allowed email."""
        assert is_email_allowed("admin@special.com") is True

    def test_is_email_allowed_domain(self):
        """Test allowed domain."""
        assert is_email_allowed("user@example.com") is True
        assert is_email_allowed("user@test.com") is True

    def test_is_email_allowed_rejected(self):
        """Test rejected email."""
        assert is_email_allowed("user@notallowed.com") is False

    def test_google_login_redirect(self, client):
        """Test Google login redirect."""
        # Mock session
        with patch("litecrew.api.auth.google.secrets.token_urlsafe") as mock_token:
            mock_token.return_value = "test-state"
            response = client.get("/auth/google/login")

        assert response.status_code == 200
        assert "accounts.google.com" in response.text

    def test_google_login_no_client_id(self, client):
        """Test Google login without client ID."""
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": ""}):
            response = client.get("/auth/google/login")
        assert response.status_code == 500
        assert "Google OAuth not configured" in response.json()["detail"]

    @patch("litecrew.api.auth.google.httpx.AsyncClient")
    async def test_google_callback_success(self, mock_httpx, client):
        """Test successful Google callback."""
        # Mock httpx responses
        mock_client = MagicMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client

        # Mock token response
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test-access-token"}
        token_response.raise_for_status = MagicMock()

        # Mock user info response
        user_response = MagicMock()
        user_response.json.return_value = {
            "email": "user@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }
        user_response.raise_for_status = MagicMock()

        mock_client.post.return_value = token_response
        mock_client.get.return_value = user_response

        # Mock request with session
        request = MagicMock(spec=Request)
        request.session = {"oauth_state": "test-state"}

        # Call callback
        from litecrew.api.auth.google import google_callback

        response = await google_callback(request, code="test-code", state="test-state")

        assert response.status_code == 302  # Redirect
        assert "auth_token" in response.headers["set-cookie"]

    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.get("/auth/logout")
        assert response.status_code == 302  # Redirect
        # Check cookie deletion in headers
        assert any(
            "auth_token" in h and "Max-Age=0" in h
            for h in response.headers.getlist("set-cookie")
        )

    def test_get_current_user_authenticated(self, client):
        """Test getting current user when authenticated."""
        # Create valid JWT token
        token_data = {
            "email": "user@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(token_data, "test-jwt-secret", algorithm="HS256")

        response = client.get("/auth/me", cookies={"auth_token": token})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["name"] == "Test User"

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token."""
        # Create expired JWT token
        token_data = {
            "email": "user@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
        }
        token = jwt.encode(token_data, "test-jwt-secret", algorithm="HS256")

        response = client.get("/auth/me", cookies={"auth_token": token})
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get("/auth/me", cookies={"auth_token": "invalid-token"})
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_verify_dashboard_auth_valid(self):
        """Test dashboard auth verification with valid token."""
        # Create valid JWT token
        token_data = {
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(token_data, "test-jwt-secret", algorithm="HS256")

        request = MagicMock(spec=Request)
        request.cookies = {"auth_token": token}

        result = await verify_dashboard_auth(request)
        assert result is not None
        assert result["email"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_verify_dashboard_auth_no_token(self):
        """Test dashboard auth verification without token."""
        request = MagicMock(spec=Request)
        request.cookies = {}

        result = await verify_dashboard_auth(request)
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_dashboard_auth_invalid_token(self):
        """Test dashboard auth verification with invalid token."""
        request = MagicMock(spec=Request)
        request.cookies = {"auth_token": "invalid-token"}

        result = await verify_dashboard_auth(request)
        assert result is None

    @pytest.mark.asyncio
    async def test_google_callback_invalid_state(self):
        """Test Google callback with invalid state."""
        request = MagicMock(spec=Request)
        request.session = {"oauth_state": "different-state"}

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await google_callback(request, code="test-code", state="test-state")
        assert exc_info.value.status_code == 400
        assert "Invalid state parameter" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_google_callback_email_not_allowed(self):
        """Test Google callback with non-allowed email."""
        # Mock httpx responses
        with patch("litecrew.api.auth.google.httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_httpx.return_value.__aenter__.return_value = mock_client

            # Mock responses
            token_response = MagicMock()
            token_response.json.return_value = {"access_token": "test-token"}
            token_response.raise_for_status = MagicMock()

            user_response = MagicMock()
            user_response.json.return_value = {"email": "user@notallowed.com"}
            user_response.raise_for_status = MagicMock()

            mock_client.post.return_value = token_response
            mock_client.get.return_value = user_response

            request = MagicMock(spec=Request)
            request.session = {"oauth_state": "test-state"}

            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                await google_callback(request, code="test-code", state="test-state")
            assert exc_info.value.status_code == 403
            assert "Email not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_google_callback_auth_error(self):
        """Test Google callback with auth error."""
        with patch("litecrew.api.auth.google.httpx.AsyncClient") as mock_httpx:
            # Make httpx raise an error
            mock_httpx.return_value.__aenter__.side_effect = Exception("Network error")

            request = MagicMock(spec=Request)
            request.session = {"oauth_state": "test-state"}

            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                await google_callback(request, code="test-code", state="test-state")
            assert exc_info.value.status_code == 500
            assert "Failed to authenticate with Google" in exc_info.value.detail
