"""Simple authentication placeholder for non-OAuth deployment."""

from typing import Optional

from fastapi import APIRouter, Request

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login_placeholder():
    """Placeholder for Google OAuth login."""
    return {
        "message": "Google OAuth not configured",
        "info": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to enable",
    }


@router.get("/google/callback")
async def google_callback_placeholder():
    """Placeholder for Google OAuth callback."""
    return {"message": "Google OAuth not configured"}


@router.get("/logout")
async def logout_placeholder():
    """Placeholder for logout."""
    return {"message": "Logout endpoint"}


@router.get("/me")
async def get_current_user_placeholder():
    """Placeholder for current user info."""
    return {"message": "Authentication not configured"}


async def verify_dashboard_auth(request: Request) -> Optional[dict]:
    """Placeholder dashboard auth verification - always returns None."""
    return None
