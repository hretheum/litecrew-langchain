"""
LiteTask - Task management for multi-agent systems
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskOutput(BaseModel):
    """Output from task execution."""

    raw: str = Field(description="Raw output from the agent")
    task_id: Optional[str] = None
    agent_role: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def __str__(self) -> str:
        return self.raw


class LiteTask(BaseModel):
    """
    A task that can be executed by an agent.

    Compatible with CrewAI Task API but simplified.
    """

    description: str = Field(description="Description of the task")
    agent: Optional[Any] = Field(
        default=None, description="Agent assigned to execute this task"
    )
    context: Optional[List["LiteTask"]] = Field(
        default=None, description="Tasks whose outputs will be used as context"
    )
    expected_output: str = Field(default="", description="Expected output description")
    tools: List[Any] = Field(
        default_factory=list, description="Tools available for this task"
    )
    output: Optional[TaskOutput] = Field(
        default=None, description="Task execution output"
    )

    # Additional fields for compatibility
    async_execution: bool = Field(
        default=False, description="Execute task asynchronously"
    )
    callback: Optional[Any] = Field(
        default=None, description="Callback function after execution"
    )

    class Config:
        arbitrary_types_allowed = True

    def execute(self, crew_context: Optional[Dict] = None) -> TaskOutput:
        """
        Execute the task using the assigned agent.

        Args:
            crew_context: Optional context from the crew

        Returns:
            TaskOutput containing the result
        """
        if not self.agent:
            raise ValueError("No agent assigned to execute this task")

        # Build context from dependent tasks
        context_str = self._build_context()

        # Add crew context if provided
        if crew_context:
            context_str = (
                f"{crew_context}\n\n{context_str}" if context_str else str(crew_context)
            )

        # Execute task through agent
        try:
            result = self.agent.execute(self.description, context_str)

            # Create output
            self.output = TaskOutput(
                raw=result,
                task_id=str(id(self)),
                agent_role=self.agent.role if hasattr(self.agent, "role") else None,
            )

            # Call callback if provided
            if self.callback:
                self.callback(self.output)

            return self.output

        except Exception as e:
            # Create error output
            self.output = TaskOutput(
                raw=f"Task execution failed: {str(e)}",
                task_id=str(id(self)),
                agent_role=self.agent.role if hasattr(self.agent, "role") else None,
            )
            raise

    def _build_context(self) -> str:
        """Build context string from dependent tasks."""
        if not self.context:
            return ""

        context_parts = []
        for task in self.context:
            if task.output:
                context_parts.append(
                    f"Output from {task.agent.role if task.agent else 'previous task'}:\n{task.output.raw}"
                )

        return "\n\n".join(context_parts)

    def __str__(self) -> str:
        return f"Task: {self.description[:50]}..."


# Alias for CrewAI compatibility
Task = LiteTask
