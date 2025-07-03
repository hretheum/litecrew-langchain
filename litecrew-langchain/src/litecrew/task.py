"""
LiteTask - Task management for multi-agent systems
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from datetime import datetime

from litecrew.base import PydanticCompatible


@dataclass
class TaskOutput(PydanticCompatible):
    """Output from task execution."""
    raw: str  # Raw output from the agent
    task_id: Optional[str] = None
    agent_role: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return self.raw


@dataclass
class LiteTask(PydanticCompatible):
    """
    A task that can be executed by an agent.
    
    Compatible with CrewAI Task API but simplified.
    
    Attributes:
        description: Description of the task
        agent: Agent assigned to execute this task
        context: Tasks whose outputs will be used as context
        expected_output: Expected output description
        tools: Tools available for this task
        output: Task execution output
        async_execution: Execute task asynchronously
        callback: Callback function after execution
    """
    description: str
    agent: Optional[Any] = None
    context: Optional[List['LiteTask']] = None
    expected_output: str = ""
    tools: List[Any] = field(default_factory=list)
    output: Optional[TaskOutput] = None
    
    # Additional fields for compatibility
    async_execution: bool = False
    callback: Optional[Any] = None
    
    def __post_init__(self):
        """Validate task configuration."""
        # Validate description
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        
        # Ensure description is stripped
        self.description = self.description.strip()
        
        # Validate expected_output if provided
        if self.expected_output:
            self.expected_output = self.expected_output.strip()
    
    def execute(self, crew_context: Optional[Dict] = None, shared_context=None) -> TaskOutput:
        """
        Execute the task using the assigned agent.
        
        Args:
            crew_context: Optional context from the crew
            shared_context: Optional shared context store
            
        Returns:
            TaskOutput containing the result
        """
        if not self.agent:
            raise ValueError("No agent assigned to execute this task")
            
        # Build context from dependent tasks
        context_str = self._build_context()
        
        # Add crew context if provided
        if crew_context:
            context_str = f"{crew_context}\n\n{context_str}" if context_str else str(crew_context)
        
        # Add shared context if provided
        if shared_context:
            # Get relevant context from shared store
            relevant_context = shared_context.get_relevant_context(self.description, max_items=5)
            if relevant_context:
                context_str = f"{context_str}\n\n--- Shared Context ---\n{relevant_context}" if context_str else f"--- Shared Context ---\n{relevant_context}"
            
            # Get agent-specific context
            if hasattr(self.agent, 'role'):
                agent_context = shared_context.get_agent_context(self.agent.role, max_items=3)
                if agent_context:
                    context_str = f"{context_str}\n\n--- Agent History ---\n{agent_context}" if context_str else f"--- Agent History ---\n{agent_context}"
            
        # Execute task through agent
        try:
            result = self.agent.execute(self.description, context_str)
            
            # Create output
            self.output = TaskOutput(
                raw=result,
                task_id=str(id(self)),
                agent_role=str(self.agent.role) if hasattr(self.agent, 'role') else None
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
                agent_role=str(self.agent.role) if hasattr(self.agent, 'role') else None
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