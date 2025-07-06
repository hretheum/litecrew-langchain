"""Google OAuth integration for dashboard authentication."""

import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
)
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Allowed email domains (optional)
ALLOWED_DOMAINS = os.getenv("ALLOWED_EMAIL_DOMAINS", "").split(",")
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenData(BaseModel):
    """JWT token data."""

    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    exp: datetime


@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:
    """Redirect to Google OAuth login."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    # Build Google OAuth URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str, state: str) -> RedirectResponse:
    """Handle Google OAuth callback."""
    # Verify state
    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    # Exchange code for token
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_response.raise_for_status()
            user_info = user_response.json()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate with Google: {str(e)}",
        )

    # Check if user is allowed
    email = user_info.get("email", "")
    if not is_email_allowed(email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not authorized to access this application",
        )

    # Create JWT token
    token_data = {
        "email": email,
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }

    jwt_token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Set cookie and redirect to dashboard
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="auth_token",
        value=jwt_token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="lax",
        max_age=JWT_EXPIRATION_HOURS * 3600,
    )

    return response


@router.get("/logout")
async def logout() -> RedirectResponse:
    """Logout user by clearing auth cookie."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("auth_token")
    return response


@router.get("/me")
async def get_current_user(request: Request) -> Dict[str, Optional[str]]:
    """Get current authenticated user info."""
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "email": payload.get("email"),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def is_email_allowed(email: str) -> bool:
    """Check if email is allowed to access the application."""
    # If no restrictions, allow all
    if not ALLOWED_DOMAINS and not ALLOWED_EMAILS:
        return True

    # Check specific emails
    if email in ALLOWED_EMAILS:
        return True

    # Check domains
    domain = email.split("@")[-1]
    if domain in ALLOWED_DOMAINS:
        return True

    return False


async def verify_dashboard_auth(request: Request) -> Optional[Dict[str, Any]]:
    """Verify dashboard authentication via JWT cookie."""
    token = request.cookies.get("auth_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return dict(payload)  # Explicitly convert to dict
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
