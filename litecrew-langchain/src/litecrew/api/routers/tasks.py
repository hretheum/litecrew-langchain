"""Task management API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..storage import APIStorage

router = APIRouter()
storage = APIStorage()


@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get task execution status."""
    task_info = await storage.get_task(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_info


@router.get("/tasks")
async def list_tasks() -> Dict[str, Any]:
    """List all tasks."""
    tasks = await storage.list_tasks()
    return {"tasks": tasks}
