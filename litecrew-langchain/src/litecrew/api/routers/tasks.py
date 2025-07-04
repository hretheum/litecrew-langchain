"""Task management API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..storage import get_storage

router = APIRouter()


@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get task execution status."""
    storage = get_storage()
    task_info = await storage.get_task(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_info


@router.get("/tasks")
async def list_tasks() -> Dict[str, Any]:
    """List all tasks."""
    storage = get_storage()
    tasks = await storage.list_tasks()
    return {"tasks": tasks}
