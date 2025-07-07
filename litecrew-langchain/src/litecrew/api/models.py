"""API models and schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CrewCreate(BaseModel):
    """Model for creating a new crew."""

    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: Optional[str] = "sequential"
    process_config: Optional[Dict[str, Any]] = None


class CrewResponse(BaseModel):
    """Model for crew response."""

    crew_id: str
    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    process: str
    process_config: Optional[Dict[str, Any]] = None
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


class ProcessType(BaseModel):
    """Information about a process type."""
    
    name: str
    description: str
    supports_moderator: bool = False
    configurable_options: List[str] = []
    example_config: Dict[str, Any] = {}


class ProcessSwitch(BaseModel):
    """Model for switching process type."""
    
    process_type: str
    process_config: Optional[Dict[str, Any]] = None


class AgentTypeInfo(BaseModel):
    """Information about an agent type."""
    
    name: str
    description: str
    configurable_options: List[str]
    default_config: Dict[str, Any]
    personality: Optional[Dict[str, Any]] = None


class AgentCreate(BaseModel):
    """Model for creating an agent."""
    
    role: str
    goal: str
    backstory: str
    tools: Optional[List[str]] = None
    memory: bool = True
    verbose: bool = False
    max_iter: int = 5
    # Agent type fields
    type: Optional[str] = None
    type_config: Optional[Dict[str, Any]] = None
    # Other optional fields
    llm_provider: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    max_rpm: Optional[int] = None
    streaming: bool = False


class AgentResponse(BaseModel):
    """Model for agent response."""
    
    agent_id: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    memory: bool
    verbose: bool
    max_iter: int
    type: Optional[str] = None
    type_config: Optional[Dict[str, Any]] = None
    type_info: Optional[AgentTypeInfo] = None
    created_at: str
    metrics: Optional[Dict[str, Any]] = None
