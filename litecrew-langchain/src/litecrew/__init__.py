"""
LiteCrew - Lightweight multi-agent orchestration on LangChain

A CrewAI-compatible framework with 10x better performance.
"""

__version__ = "0.1.0"

# CrewAI compatibility aliases
from litecrew.agent import Agent
from litecrew.agent import Agent as LiteAgent
from litecrew.crew import LiteCrew
from litecrew.task import LiteTask, TaskOutput

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
