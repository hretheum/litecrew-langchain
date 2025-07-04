"""Simple health check router without psutil."""

from datetime import datetime
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
    timestamp: str
    memory_mb: float


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Simple health check endpoint."""
    health_data = {
        "status": "healthy",
        "version": "0.6.0",
        "environment": "production",
        "metrics": {
            "uptime": "N/A",
            "memory_usage": "N/A",
            "cpu_percent": "N/A",
            "active_crews": 0,
            "total_tasks": 0,
        },
        "timestamp": datetime.now().isoformat(),
        "memory_mb": 50,  # Estimated for test environment
    }
    
    return HealthStatus(**health_data)
