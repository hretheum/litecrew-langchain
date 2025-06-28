"""
LiteCrewAI Main Application
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
import time
import os
from typing import Dict, Any

from app.core.logging import (
    setup_logging,
    get_logger,
    generate_request_id,
    request_id_var,
)
from app.core.metrics import metrics_collector, cost_tracker
from app.core.metrics_storage import MetricsStorage
from prometheus_client import CONTENT_TYPE_LATEST

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "/logs/app.log"),
)

logger = get_logger(__name__)

# Initialize metrics storage
metrics_storage = MetricsStorage()
metrics_collector.storage = metrics_storage
metrics_collector.cost_tracker = cost_tracker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LiteCrewAI application...")

    # Initialize components here
    # await init_database()
    # await init_redis()

    yield

    # Shutdown
    logger.info("Shutting down LiteCrewAI application...")
    # await cleanup_resources()


# Create FastAPI app
app = FastAPI(
    title="LiteCrewAI",
    description="Lightweight AI Agent Orchestration Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to context"""
    request_id = request.headers.get("X-Request-ID", generate_request_id())
    request_id_var.set(request_id)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Add request ID to response
    response.headers["X-Request-ID"] = request_id

    # Track metrics
    metrics_collector.track_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration,
    )

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "request_id": request_id,
        },
    )

    return response


# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time(), "version": "0.1.0"}


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component status"""

    # Check components
    components = {
        "api": "healthy",
        "database": "healthy",  # TODO: Implement actual checks
        "redis": "healthy",
        "ollama": "healthy",
    }

    # System metrics
    import psutil

    return {
        "status": (
            "healthy"
            if all(v == "healthy" for v in components.values())
            else "degraded"
        ),
        "timestamp": time.time(),
        "version": "0.1.0",
        "components": components,
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        },
        "costs": {
            "total_usd": round(cost_tracker.total_cost, 4),
            "daily_estimate_usd": round(cost_tracker.get_daily_cost(), 2),
            "monthly_estimate_usd": round(cost_tracker.get_monthly_estimate(), 2),
        },
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=metrics_collector.get_metrics(), media_type=CONTENT_TYPE_LATEST
    )


# Import and include dashboard
from app.api.dashboard import router as dashboard_router
app.include_router(dashboard_router)

# API routes will be added here
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LiteCrewAI",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "dashboard": "/dashboard",
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404, content={"error": "Not found", "path": request.url.path}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
