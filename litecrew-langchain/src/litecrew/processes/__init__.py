"""LiteCrew Process Types - Multi-Process Engine"""

from .base import BaseProcess, ProcessConfig, ProcessResult, ProcessTurn

# Import process types to trigger registration
from .conversational import ConversationalProcess
from .debate import DebateProcess
from .factory import ProcessFactory
from .hierarchical import HierarchicalProcess
from .panel import PanelProcess
from .prompts import ProcessPrompts, enhance_agent_for_process
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
