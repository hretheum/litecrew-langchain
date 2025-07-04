"""Execution management API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..storage import APIStorage

router = APIRouter()
storage = APIStorage()


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get execution results."""
    execution_info = await storage.get_execution(execution_id)
    if not execution_info:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution_info


@router.get("/executions")
async def list_executions() -> Dict[str, Any]:
    """List all executions."""
    executions = await storage.list_executions()
    return {"executions": executions}