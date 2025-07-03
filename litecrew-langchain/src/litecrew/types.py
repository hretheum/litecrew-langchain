"""
Type definitions for LiteCrew.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Literal
from dataclasses import dataclass, field
from datetime import datetime

from litecrew.base import PydanticCompatible


@dataclass
class AgentConfig(PydanticCompatible):
    """Configuration for LiteAgent."""
    
    role: str  # Agent's role description
    goal: str  # Agent's goal or objective
    backstory: str  # Agent's background story
    tools: List[Any] = field(default_factory=list)  # List of tools available to agent
    llm: Optional[Any] = None  # Language model instance
    max_iter: int = 15  # Maximum iterations for task execution
    max_rpm: Optional[int] = None  # Max requests per minute rate limit
    memory: bool = False  # Enable conversation memory
    verbose: bool = False  # Enable verbose output
    allow_delegation: bool = False  # Allow delegating tasks to other agents


@dataclass
class TaskConfig(PydanticCompatible):
    """Configuration for LiteTask."""
    
    description: str  # Task description
    expected_output: str  # Expected output format/description
    agent: Optional[Any] = None  # Assigned agent
    context: Optional[List[Any]] = None  # Context from other tasks
    tools: List[Any] = field(default_factory=list)  # Task-specific tools
    async_execution: bool = False  # Execute asynchronously
    output_file: Optional[str] = None  # File to save output
    output_json: Optional[type[PydanticCompatible]] = None  # Model for JSON output
    callback: Optional[Callable] = None  # Callback function after completion


@dataclass
class CrewConfig(PydanticCompatible):
    """Configuration for LiteCrew."""
    
    agents: List[Any]  # List of agents in the crew
    tasks: List[Any]  # List of tasks to execute
    process: Literal["sequential", "hierarchical"] = "sequential"  # Execution process type
    verbose: bool = False  # Enable verbose output
    memory: bool = False  # Enable crew-wide memory
    cache: bool = True  # Enable result caching
    max_rpm: Optional[int] = None  # Global rate limit
    share_crew: bool = False  # Share crew data for training


@dataclass
class TaskOutput(PydanticCompatible):
    """Output from task execution."""
    
    description: str  # Task description
    raw: str  # Raw output from LLM
    agent: str  # Agent who completed the task
    summary: Optional[str] = None  # Summary of the output
    pydantic: Optional[PydanticCompatible] = None  # Structured output if requested
    json_dict: Optional[Dict[str, Any]] = None  # JSON output as dict
    timestamp: datetime = field(default_factory=datetime.now)  # Completion timestamp


@dataclass
class CrewOutput(PydanticCompatible):
    """Output from crew execution."""
    
    raw: str  # Final raw output
    tasks_output: List[TaskOutput]  # All task outputs
    duration: float  # Total execution time in seconds
    token_usage: Dict[str, Any] = field(default_factory=dict)  # Token usage statistics