"""LiteCrew API module with security enhancements."""

import os
import time
from typing import Any, Callable, cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# Import auth based on configuration
if os.getenv("GOOGLE_CLIENT_ID"):
    from .auth.google import router as auth_router
    from .auth.google import verify_dashboard_auth
else:
    from .auth.simple import router as auth_router
    from .auth.simple import verify_dashboard_auth
from .middleware.auth import APIKeyMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .routers import agents, crews, executions, processes, tasks, templates
from .routers import health_simple as health
from .websocket import websocket_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application with security."""
    app = FastAPI(
        title="LiteCrew API",
        description="Lightweight CrewAI-compatible orchestration API",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # CORS middleware with restrictions (add first, execute last)
    allowed_origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            allowed_origins if os.getenv("ENVIRONMENT") == "production" else ["*"]
        ),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Session middleware (required for OAuth)
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET", os.urandom(32).hex()),
        same_site="lax",
        https_only=os.getenv("ENVIRONMENT") == "production",
    )

    # Rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,
        burst_size=10,
        authenticated_multiplier=10,
    )

    # API Key authentication middleware (add last, execute first)
    app.add_middleware(APIKeyMiddleware)

    # Trusted host middleware (prevent host header attacks)
    if os.getenv("ENVIRONMENT") == "production":
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "152.42.139.18").split(",")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(
        request: Request, call_next: Callable[..., Any]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return cast(Response, response)

    # Include routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
    app.include_router(crews.router, prefix="/api/v1", tags=["crews"])
    app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
    app.include_router(executions.router, prefix="/api/v1", tags=["executions"])
    app.include_router(processes.router, prefix="/api/v1", tags=["processes"])
    app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(websocket_router, tags=["websockets"])

    # Mount static files for dashboard
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def dashboard(request: Request) -> Any:
        """Serve the monitoring dashboard (requires Google auth)."""
        # Check if user is authenticated
        user = await verify_dashboard_auth(request)

        if not user and os.getenv("REQUIRE_DASHBOARD_AUTH", "true").lower() == "true":
            # Redirect to Google login
            return JSONResponse(
                content={
                    "message": "Authentication required",
                    "login_url": "/auth/google/login",
                },
                status_code=401,
            )

        # Try enhanced dashboard first, fall back to basic
        enhanced_path = os.path.join(static_dir, "enhanced-dashboard.html")
        basic_path = os.path.join(static_dir, "index.html")
        
        if os.path.exists(enhanced_path):
            return FileResponse(enhanced_path)
        elif os.path.exists(basic_path):
            return FileResponse(basic_path)
        return {"message": "LiteCrew API", "docs": "/docs"}

    @app.get("/dashboard")
    async def dashboard_redirect(request: Request) -> Any:
        """Redirect to dashboard."""
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/")

    @app.middleware("http")
    async def add_process_time_header(request: Any, call_next: Any) -> Any:
        """Add response time header."""
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    @app.on_event("startup")
    async def startup_event() -> None:
        """Log security configuration on startup."""
        print("🔒 Security Configuration:")
        print(
            f"  - API Keys: {'Configured' if os.getenv('LITECREW_API_KEYS') else 'Not configured'}"
        )
        print(
            f"  - Google OAuth: {'Configured' if os.getenv('GOOGLE_CLIENT_ID') else 'Not configured'}"
        )
        print(
            f"  - Dashboard Auth: {'Required' if os.getenv('REQUIRE_DASHBOARD_AUTH', 'true').lower() == 'true' else 'Disabled'}"
        )
        print(
            f"  - CORS Origins: {allowed_origins if os.getenv('ENVIRONMENT') == 'production' else 'All (*)'}"
        )
        print(f"  - Environment: {os.getenv('ENVIRONMENT', 'development')}")

    return app


# Create app instance for uvicorn
app = create_app()

__all__ = ["create_app", "app"]
