"""Base Process Abstract Class for LiteCrew Multi-Process Engine"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from litecrew.agent import LiteAgent
from litecrew.task import LiteTask, TaskOutput


@dataclass
class ProcessConfig:
    """Configuration for process execution"""
    verbose: bool = False
    max_iterations: Optional[int] = None
    timeout: Optional[float] = None
    callbacks: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        if self.max_iterations is not None and self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout must be positive")


@dataclass
class ProcessTurn:
    """Represents a single turn in a process"""
    agent: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessResult:
    """Result of process execution"""
    raw: str
    turns: List[ProcessTurn] = field(default_factory=list)
    tasks_output: List[TaskOutput] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    duration: float = 0.0
    
    def __str__(self) -> str:
        return self.raw


class BaseProcess(ABC):
    """Abstract base class for all process types"""
    
    def __init__(self, config: Optional[ProcessConfig] = None):
        self.config = config or ProcessConfig()
        self.config.validate()
        self._start_time: Optional[float] = None
        self._agents: List[LiteAgent] = []
        self._tasks: List[LiteTask] = []
        
    @abstractmethod
    async def execute(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask],
        inputs: Optional[Dict[str, Any]] = None
    ) -> ProcessResult:
        """Execute the process with given agents and tasks"""
        self._track_time()  # Start tracking time here
        raise NotImplementedError("Subclasses must implement execute")
    
    def _track_time(self) -> None:
        """Start time tracking"""
        self._start_time = time.perf_counter()
        
    def _get_duration(self) -> float:
        """Get execution duration"""
        if self._start_time is None:
            return 0.0
        return time.perf_counter() - self._start_time
    
    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit event to callbacks"""
        for callback in self.config.callbacks:
            if hasattr(callback, 'on_event'):
                callback.on_event(event_type, data)
                
    def _should_continue(self, iteration: int) -> bool:
        """Check if process should continue"""
        if self.config.max_iterations and iteration >= self.config.max_iterations:
            return False
        if self.config.timeout and self._get_duration() > self.config.timeout:
            return False
        return True
    
    def _create_turn(self, agent: LiteAgent, content: str, **metadata) -> ProcessTurn:
        """Create a process turn"""
        return ProcessTurn(
            agent=agent.role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
    
    def _aggregate_results(self, turns: List[ProcessTurn], tasks_output: List[TaskOutput]) -> str:
        """Aggregate results into final output"""
        if tasks_output:
            return "\n\n".join(str(output.raw) for output in tasks_output)
        elif turns:
            return "\n\n".join(f"{turn.agent}: {turn.content}" for turn in turns)
        return ""
    
    async def validate_inputs(
        self, 
        agents: List[LiteAgent], 
        tasks: List[LiteTask]
    ) -> Tuple[bool, Optional[str]]:
        """Validate inputs before execution"""
        if not agents:
            return False, "No agents provided"
        if not tasks:
            return False, "No tasks provided"
        return True, None
    
    def get_process_type(self) -> str:
        """Get the process type name"""
        return self.__class__.__name__.replace("Process", "").lower()