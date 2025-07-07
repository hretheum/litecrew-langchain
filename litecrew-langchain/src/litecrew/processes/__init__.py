"""LiteCrew Process Types - Multi-Process Engine"""

from .base import BaseProcess, ProcessConfig, ProcessResult, ProcessTurn
from .factory import ProcessFactory
from .prompts import ProcessPrompts, enhance_agent_for_process

# Import process types to trigger registration
from .conversational import ConversationalProcess
from .debate import DebateProcess
from .hierarchical import HierarchicalProcess
from .panel import PanelProcess
from .sequential import SequentialProcess

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
