"""LiteCrew API module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from .routers import crews, tasks, executions
from .routers import health_simple as health
from .websocket import websocket_router
from fastapi.staticfiles import StaticFiles
import os


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="LiteCrew API",
        description="Lightweight CrewAI-compatible orchestration API",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(crews.router, prefix="/api/v1", tags=["crews"])
    app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
    app.include_router(executions.router, prefix="/api/v1", tags=["executions"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(websocket_router, tags=["websockets"])

    # Mount static files for dashboard
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def dashboard():
        """Serve the monitoring dashboard."""
        from fastapi.responses import FileResponse

        dashboard_path = os.path.join(static_dir, "index.html")
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path)
        return {"message": "LiteCrew API", "docs": "/docs"}

    @app.get("/dashboard")
    async def dashboard_redirect():
        """Redirect to dashboard."""
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/")

    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        """Add response time header."""
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    return app
