"""Execution management API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..storage import get_storage

router = APIRouter()


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get execution results."""
    storage = get_storage()
    execution_info = await storage.get_execution(execution_id)
    if not execution_info:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution_info


@router.get("/executions")
async def list_executions() -> Dict[str, Any]:
    """List all executions."""
    storage = get_storage()
    executions = await storage.list_executions()
    return {"executions": executions}
