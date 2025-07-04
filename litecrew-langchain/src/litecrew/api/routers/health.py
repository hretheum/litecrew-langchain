"""Health check API endpoints."""

import time
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "uptime": time.time(),
    }
