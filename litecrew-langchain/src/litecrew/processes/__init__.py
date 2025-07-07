"""LiteCrew Process Types - Multi-Process Engine"""

from .base import BaseProcess, ProcessConfig, ProcessResult, ProcessTurn
from .factory import ProcessFactory
from .sequential import SequentialProcess
from .hierarchical import HierarchicalProcess
from .conversational import ConversationalProcess
from .debate import DebateProcess
from .panel import PanelProcess
from .prompts import ProcessPrompts, enhance_agent_for_process

__all__ = [
    "BaseProcess",
    "ProcessConfig", 
    "ProcessResult",
    "ProcessTurn",
    "ProcessFactory",
    "SequentialProcess",
    "HierarchicalProcess",
    "ConversationalProcess",
    "DebateProcess",
    "PanelProcess",
    "ProcessPrompts",
    "enhance_agent_for_process",
]