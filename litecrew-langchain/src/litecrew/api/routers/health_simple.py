"""Simple health check router without psutil."""

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str
    metrics: Dict[str, Any]


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Simple health check endpoint."""
    return HealthStatus(
        status="healthy",
        version="0.6.0",
        environment="production",
        metrics={
            "uptime": "N/A",
            "memory_usage": "N/A",
            "cpu_percent": "N/A",
            "active_crews": 0,
            "total_tasks": 0,
        },
    )
