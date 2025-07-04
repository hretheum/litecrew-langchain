"""API models and schemas."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class CrewCreate(BaseModel):
    """Model for creating a new crew."""
    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: Optional[str] = "sequential"


class CrewResponse(BaseModel):
    """Model for crew response."""
    crew_id: str
    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: str
    created_at: str
    updated_at: Optional[str] = None


class CrewUpdate(BaseModel):
    """Model for updating crew."""
    name: Optional[str] = None
    description: Optional[str] = None


class TaskSubmission(BaseModel):
    """Model for task submission."""
    description: str
    expected_output: Optional[str] = "Task result"
    priority: Optional[str] = "medium"


class ExecutionRequest(BaseModel):
    """Model for execution request."""
    inputs: Dict[str, Any] = {}
    async_execution: bool = False