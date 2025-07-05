"""
Crew state representation and management.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from litecrew.state.base import StateError


@dataclass
class CrewState:
    """Represents the complete state of a crew execution."""

    crew_id: str
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: str
    status: str = "initialized"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Execution state
    current_task_index: int = 0
    task_states: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Performance metrics
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_tokens: int = 0
    total_cost: float = 0.0

    def __post_init__(self) -> None:
        """Initialize task states."""
        if not self.task_states:
            self.task_states = [
                {
                    "status": "pending",
                    "output": None,
                    "error": None,
                    "start_time": None,
                    "end_time": None,
                    "attempts": 0,
                }
                for _ in self.tasks
            ]

    @classmethod
    def from_crew(
        cls,
        crew_id: str,
        agents: List[Any],
        tasks: List[Any],
        process: str = "sequential",
    ) -> "CrewState":
        """Create state from crew components."""
        # Convert agents to serializable format
        agent_data = []
        for agent in agents:
            agent_data.append(
                {
                    "role": agent.role,
                    "goal": agent.goal,
                    "backstory": agent.backstory,
                    "tools": len(agent.tools) if hasattr(agent, "tools") else 0,
                    "llm": (
                        agent.llm.__class__.__name__
                        if hasattr(agent, "llm")
                        else "Unknown"
                    ),
                }
            )

        # Convert tasks to serializable format
        task_data = []
        for task in tasks:
            task_data.append(
                {
                    "description": task.description,
                    "expected_output": getattr(task, "expected_output", None),
                    "agent_role": task.agent.role if hasattr(task, "agent") else None,
                    "context_indices": [
                        tasks.index(t) for t in (getattr(task, "context", []) or [])
                    ],
                }
            )

        return cls(crew_id=crew_id, agents=agent_data, tasks=task_data, process=process)

    def update_task_status(self, task_index: int, status: str) -> None:
        """Update status of a specific task."""
        if 0 <= task_index < len(self.task_states):
            self.task_states[task_index]["status"] = status
            self.task_states[task_index]["attempts"] += 1

            if (
                status == "in_progress"
                and self.task_states[task_index]["start_time"] is None
            ):
                self.task_states[task_index]["start_time"] = time.time()
            elif status in ["completed", "failed"]:
                self.task_states[task_index]["end_time"] = time.time()

            self.updated_at = time.time()

    def update_task_output(self, task_index: int, output: Any) -> None:
        """Update output of a specific task."""
        if 0 <= task_index < len(self.task_states):
            self.task_states[task_index]["output"] = output
            self.updated_at = time.time()

    def update_task_error(self, task_index: int, error: str) -> None:
        """Update error for a specific task."""
        if 0 <= task_index < len(self.task_states):
            self.task_states[task_index]["error"] = error
            self.task_states[task_index]["status"] = "failed"
            self.updated_at = time.time()

    def update_status(self, status: str) -> None:
        """Update crew execution status."""
        self.status = status
        self.updated_at = time.time()

        if status == "running" and self.start_time is None:
            self.start_time = time.time()
        elif status in ["completed", "failed"] and self.end_time is None:
            self.end_time = time.time()

    def update_context(self, key: str, value: Any) -> None:
        """Update execution context."""
        self.context[key] = value
        self.updated_at = time.time()

    def add_metrics(self, tokens: int = 0, cost: float = 0.0) -> None:
        """Add to performance metrics."""
        self.total_tokens += tokens
        self.total_cost += cost
        self.updated_at = time.time()

    def get_execution_time(self) -> Optional[float]:
        """Get total execution time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return None

    def get_completed_tasks(self) -> List[int]:
        """Get indices of completed tasks."""
        return [
            i
            for i, state in enumerate(self.task_states)
            if state["status"] == "completed"
        ]

    def get_failed_tasks(self) -> List[int]:
        """Get indices of failed tasks."""
        return [
            i for i, state in enumerate(self.task_states) if state["status"] == "failed"
        ]

    def validate(self) -> bool:
        """Validate state consistency."""
        if not self.crew_id:
            raise StateError("Crew ID is required")

        if not self.agents:
            raise StateError("At least one agent is required")

        if not self.tasks:
            raise StateError("At least one task is required")

        if self.process not in ["sequential", "hierarchical"]:
            raise StateError(f"Invalid process type: {self.process}")

        if len(self.task_states) != len(self.tasks):
            raise StateError("Task states count mismatch")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "crew_id": self.crew_id,
            "agents": self.agents,
            "tasks": self.tasks,
            "process": self.process,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_task_index": self.current_task_index,
            "task_states": self.task_states,
            "context": self.context,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrewState":
        """Create state from dictionary."""
        return cls(**data)
