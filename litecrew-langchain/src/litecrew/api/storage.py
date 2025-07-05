"""API storage layer."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional


class APIStorage:
    """In-memory storage for API data."""

    def __init__(self) -> None:
        self._crews: Dict[str, Dict[str, Any]] = {}
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._executions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def store_crew(self, crew_id: str, crew_info: Dict[str, Any]) -> None:
        """Store crew information."""
        async with self._lock:
            # Remove crew_instance before storing (not serializable)
            crew_data = {k: v for k, v in crew_info.items() if k != "crew_instance"}
            self._crews[crew_id] = crew_data
            # Keep the instance separately
            self._crews[crew_id]["_instance"] = crew_info.get("crew_instance")

    async def get_crew(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """Get crew information."""
        async with self._lock:
            crew_data = self._crews.get(crew_id)
            if crew_data:
                # Add crew_instance back
                result = crew_data.copy()
                if "_instance" in result:
                    result["crew_instance"] = result.pop("_instance")
                return result
            return None

    async def list_crews(self) -> List[Dict[str, Any]]:
        """List all crews."""
        async with self._lock:
            crews = []
            for crew_data in self._crews.values():
                crew_copy = {k: v for k, v in crew_data.items() if k != "_instance"}
                crews.append(crew_copy)
            return crews

    async def delete_crew(self, crew_id: str) -> None:
        """Delete crew."""
        async with self._lock:
            self._crews.pop(crew_id, None)

    async def store_task(self, task_id: str, task_info: Dict[str, Any]) -> None:
        """Store task information."""
        async with self._lock:
            self._tasks[task_id] = task_info

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task information."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks."""
        async with self._lock:
            return list(self._tasks.values())

    async def store_execution(self, execution_id: str, execution_info: Dict[str, Any]) -> None:
        """Store execution information."""
        async with self._lock:
            self._executions[execution_id] = execution_info

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution information."""
        async with self._lock:
            execution = self._executions.get(execution_id)
            if execution:
                # Add duration if completed
                if execution.get("status") == "completed":
                    created_at = datetime.fromisoformat(execution["created_at"])
                    duration = (datetime.utcnow() - created_at).total_seconds()
                    execution["duration"] = duration
            return execution

    async def list_executions(self) -> List[Dict[str, Any]]:
        """List all executions."""
        async with self._lock:
            executions = []
            for execution in self._executions.values():
                if execution.get("status") == "completed":
                    created_at = datetime.fromisoformat(execution["created_at"])
                    duration = (datetime.utcnow() - created_at).total_seconds()
                    execution["duration"] = duration
                executions.append(execution)
            return executions

    async def get_crew_executions(self, crew_id: str) -> List[Dict[str, Any]]:
        """Get executions for a specific crew."""
        async with self._lock:
            executions = []
            for execution in self._executions.values():
                if execution.get("crew_id") == crew_id:
                    if execution.get("status") == "completed":
                        created_at = datetime.fromisoformat(execution["created_at"])
                        duration = (datetime.utcnow() - created_at).total_seconds()
                        execution["duration"] = duration
                    executions.append(execution)
            return executions

    async def execute_crew_async(
        self, execution_id: str, crew: Any, execution_data: Dict[str, Any]
    ) -> None:
        """Execute crew asynchronously."""
        try:
            result = await crew.kickoff_async(execution_data.get("inputs", {}))

            async with self._lock:
                if execution_id in self._executions:
                    self._executions[execution_id]["status"] = "completed"
                    self._executions[execution_id]["result"] = result
                    self._executions[execution_id][
                        "completed_at"
                    ] = datetime.utcnow().isoformat()

        except Exception as e:
            async with self._lock:
                if execution_id in self._executions:
                    self._executions[execution_id]["status"] = "failed"
                    self._executions[execution_id]["error"] = str(e)
                    self._executions[execution_id][
                        "completed_at"
                    ] = datetime.utcnow().isoformat()


# Global storage instance
_storage_instance = None


def get_storage() -> APIStorage:
    """Get global storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = APIStorage()
    return _storage_instance
