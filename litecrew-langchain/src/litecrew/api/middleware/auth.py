"""Authentication middleware for API key validation."""

import os
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys for protected endpoints."""
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/openapi.json",
            "/api/v1/health",
            "/dashboard",
            "/static",
            "/auth",  # OAuth endpoints
        ]
        # Handle root path separately to avoid matching all paths
        self.excluded_exact_paths = {"/"}  # Only exact match for root
        # Load valid API keys from environment
        self.valid_api_keys = set(
            key.strip() 
            for key in os.getenv("LITECREW_API_KEYS", "").split(",") 
            if key.strip()
        )
        
    async def dispatch(self, request: Request, call_next):
        """Check API key for protected endpoints."""
        # Check if path is excluded
        path = request.url.path
        print(f"Auth middleware - Path: {path}")
        
        # Check exact match first
        if path in self.excluded_exact_paths:
            print(f"Path {path} is excluded from auth (exact match)")
            return await call_next(request)
            
        # Then check prefix matches
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            print(f"Path {path} is excluded from auth (prefix match)")
            return await call_next(request)
            
        # Check API key header
        api_key = request.headers.get("X-API-Key")
        print(f"API Key present: {bool(api_key)}")
        print(f"Valid API keys configured: {bool(self.valid_api_keys)}")
        print(f"Valid API keys: {self.valid_api_keys}")
        
        if not api_key:
            # Return JSON response directly instead of raising exception
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key required"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
            
        if api_key not in self.valid_api_keys:
            # Return JSON response directly instead of raising exception
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API key"},
            )
            
        # Add user context to request state
        request.state.api_key = api_key
        
        return await call_next(request)


# FastAPI dependency for optional API key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Get API key from header."""
    return api_key


async def require_api_key(api_key: Optional[str] = None) -> str:
    """Require valid API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    valid_keys = set(
        key.strip() 
        for key in os.getenv("LITECREW_API_KEYS", "").split(",") 
        if key.strip()
    )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return api_key