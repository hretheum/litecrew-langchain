"""
LiteCrew - Lightweight multi-agent orchestration on LangChain

A CrewAI-compatible framework with 10x better performance.
"""

__version__ = "0.1.0"

from litecrew.agent import LiteAgent
from litecrew.crew import LiteCrew
from litecrew.task import LiteTask, TaskOutput

# CrewAI compatibility aliases
Agent = LiteAgent
Crew = LiteCrew
Task = LiteTask

__all__ = [
    "LiteAgent",
    "LiteCrew",
    "LiteTask",
    "TaskOutput",
    # Compatibility
    "Agent",
    "Crew",
    "Task",
]
