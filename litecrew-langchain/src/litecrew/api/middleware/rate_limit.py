"""Rate limiting middleware to prevent API abuse."""

import time
from collections import defaultdict
from typing import Dict

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        authenticated_multiplier: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.authenticated_multiplier = authenticated_multiplier
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (API key or IP)."""
        # Prefer API key if available
        if hasattr(request.state, "api_key"):
            return f"api:{request.state.api_key}"

        # Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client = request.client
        if client:
            return f"ip:{client.host}"

        return "ip:unknown"

    def _get_limit(self, client_id: str) -> int:
        """Get rate limit for client."""
        if client_id.startswith("api:"):
            return self.requests_per_minute * self.authenticated_multiplier
        return self.requests_per_minute

    def _clean_old_requests(self, request_times: list, current_time: float) -> list:
        """Remove requests older than 1 minute."""
        cutoff = current_time - 60
        return [t for t in request_times if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        # Skip rate limiting for static files and docs
        if request.url.path.startswith(("/static", "/docs", "/openapi.json")):
            return await call_next(request)

        client_id = self._get_client_id(request)
        current_time = time.time()

        # Clean old requests
        self.requests[client_id] = self._clean_old_requests(
            self.requests[client_id], current_time
        )

        # Check rate limit
        limit = self._get_limit(client_id)
        request_count = len(self.requests[client_id])

        if request_count >= limit:
            # Check burst allowance
            recent_requests = [
                t
                for t in self.requests[client_id]
                if t > current_time - 10  # Last 10 seconds
            ]
            if len(recent_requests) >= self.burst_size:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + 60)),
                    },
                )

        # Record request
        self.requests[client_id].append(current_time)

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit - len(self.requests[client_id]))
        )
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

        return response


# Alternative: Using slowapi (more feature-rich)
def setup_slowapi_limiter():
    """Setup slowapi rate limiter (requires: pip install slowapi)."""
    try:
        from slowapi import Limiter
        from slowapi.util import get_remote_address

        # Create limiter with custom key function
        def get_rate_limit_key(request: Request) -> str:
            # Use API key if available
            if hasattr(request.state, "api_key"):
                return request.state.api_key
            # Otherwise use IP
            return get_remote_address(request)

        limiter = Limiter(key_func=get_rate_limit_key)

        return limiter
    except ImportError:
        # Fallback to simple middleware if slowapi not installed
        return None
