"""
Type definitions for LiteCrew.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AgentConfig(BaseModel):
    """Configuration for LiteAgent."""
    
    role: str = Field(..., description="Agent's role description")
    goal: str = Field(..., description="Agent's goal or objective")
    backstory: str = Field(..., description="Agent's background story")
    tools: List[Any] = Field(default_factory=list, description="List of tools available to agent")
    llm: Optional[Any] = Field(None, description="Language model instance")
    max_iter: int = Field(15, description="Maximum iterations for task execution")
    max_rpm: Optional[int] = Field(None, description="Max requests per minute rate limit")
    memory: bool = Field(False, description="Enable conversation memory")
    verbose: bool = Field(False, description="Enable verbose output")
    allow_delegation: bool = Field(False, description="Allow delegating tasks to other agents")
    
    class Config:
        arbitrary_types_allowed = True


class TaskConfig(BaseModel):
    """Configuration for LiteTask."""
    
    description: str = Field(..., description="Task description")
    expected_output: str = Field(..., description="Expected output format/description")
    agent: Optional[Any] = Field(None, description="Assigned agent")
    context: Optional[List[Any]] = Field(None, description="Context from other tasks")
    tools: List[Any] = Field(default_factory=list, description="Task-specific tools")
    async_execution: bool = Field(False, description="Execute asynchronously")
    output_file: Optional[str] = Field(None, description="File to save output")
    output_json: Optional[type[BaseModel]] = Field(None, description="Pydantic model for JSON output")
    callback: Optional[Callable] = Field(None, description="Callback function after completion")
    
    class Config:
        arbitrary_types_allowed = True


class CrewConfig(BaseModel):
    """Configuration for LiteCrew."""
    
    agents: List[Any] = Field(..., description="List of agents in the crew")
    tasks: List[Any] = Field(..., description="List of tasks to execute")
    process: Literal["sequential", "hierarchical"] = Field("sequential", description="Execution process type")
    verbose: bool = Field(False, description="Enable verbose output")
    memory: bool = Field(False, description="Enable crew-wide memory")
    cache: bool = Field(True, description="Enable result caching")
    max_rpm: Optional[int] = Field(None, description="Global rate limit")
    share_crew: bool = Field(False, description="Share crew data for training")
    
    class Config:
        arbitrary_types_allowed = True


class TaskOutput(BaseModel):
    """Output from task execution."""
    
    description: str = Field(..., description="Task description")
    summary: Optional[str] = Field(None, description="Summary of the output")
    raw: str = Field(..., description="Raw output from LLM")
    pydantic: Optional[BaseModel] = Field(None, description="Structured output if requested")
    json_dict: Optional[Dict[str, Any]] = Field(None, description="JSON output as dict")
    agent: str = Field(..., description="Agent who completed the task")
    timestamp: datetime = Field(default_factory=datetime.now, description="Completion timestamp")
    
    class Config:
        arbitrary_types_allowed = True


class CrewOutput(BaseModel):
    """Output from crew execution."""
    
    raw: str = Field(..., description="Final raw output")
    tasks_output: List[TaskOutput] = Field(..., description="All task outputs")
    token_usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage statistics")
    duration: float = Field(..., description="Total execution time in seconds")
    
    class Config:
        arbitrary_types_allowed = True