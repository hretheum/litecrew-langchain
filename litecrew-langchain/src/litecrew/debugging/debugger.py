"""
Debugging Tools for LiteCrew.

Provides execution tracing, profiling, and replay capabilities.
"""

import json
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Tuple

from litecrew.agent import Agent as LiteAgent
from litecrew.crew import Crew as LiteCrew
from litecrew.task import LiteTask, TaskOutput


class TraceEventType(Enum):
    """Types of trace events."""
    CREW_START = "crew_start"
    CREW_END = "crew_end"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TASK_START = "task_start"
    TASK_END = "task_end"
    LLM_CALL = "llm_call"
    LLM_RESPONSE = "llm_response"
    MEMORY_ACCESS = "memory_access"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass
class TraceEvent:
    """A single trace event."""
    
    timestamp: float
    event_type: TraceEventType
    component: str  # Component name (agent, task, etc.)
    data: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "component": self.component,
            "data": self.data,
            "duration": self.duration,
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TraceEvent":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            event_type=TraceEventType(data["event_type"]),
            component=data["component"],
            data=data.get("data", {}),
            duration=data.get("duration"),
            parent_id=data.get("parent_id")
        )


@dataclass
class ExecutionTrace:
    """Complete execution trace."""
    
    trace_id: str
    start_time: float
    end_time: Optional[float] = None
    events: List[TraceEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: TraceEvent) -> None:
        """Add an event to the trace."""
        self.events.append(event)
    
    def get_duration(self) -> float:
        """Get total execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def get_event_tree(self) -> Dict[str, Any]:
        """Build hierarchical event tree."""
        tree = {"root": {"children": []}}
        event_map = {}
        
        for event in self.events:
            event_dict = event.to_dict()
            event_dict["children"] = []
            event_id = f"{event.component}_{event.timestamp}"
            event_map[event_id] = event_dict
            
            if event.parent_id:
                parent = event_map.get(event.parent_id, tree["root"])
                parent["children"].append(event_dict)
            else:
                tree["root"]["children"].append(event_dict)
        
        return tree
    
    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get events in timeline format."""
        timeline = []
        
        for event in sorted(self.events, key=lambda e: e.timestamp):
            timeline.append({
                "time": event.timestamp - self.start_time,
                "type": event.event_type.value,
                "component": event.component,
                "duration": event.duration,
                "data": event.data
            })
        
        return timeline
    
    def save(self, filepath: Union[str, Path]) -> None:
        """Save trace to file."""
        filepath = Path(filepath)
        
        data = {
            "trace_id": self.trace_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "events": [e.to_dict() for e in self.events],
            "metadata": self.metadata
        }
        
        if filepath.suffix == ".json":
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        else:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "ExecutionTrace":
        """Load trace from file."""
        filepath = Path(filepath)
        
        if filepath.suffix == ".json":
            with open(filepath, "r") as f:
                data = json.load(f)
        else:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
        
        trace = cls(
            trace_id=data["trace_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            metadata=data.get("metadata", {})
        )
        
        for event_data in data["events"]:
            trace.add_event(TraceEvent.from_dict(event_data))
        
        return trace


class ExecutionTracer:
    """Traces crew execution for debugging."""
    
    def __init__(
        self,
        trace_llm_calls: bool = True,
        trace_memory: bool = True,
        trace_tools: bool = True,
        auto_save: bool = False,
        save_path: Optional[Path] = None
    ):
        """Initialize execution tracer.
        
        Args:
            trace_llm_calls: Trace LLM API calls
            trace_memory: Trace memory operations
            trace_tools: Trace tool usage
            auto_save: Automatically save traces
            save_path: Path for auto-saving traces
        """
        self.trace_llm_calls = trace_llm_calls
        self.trace_memory = trace_memory
        self.trace_tools = trace_tools
        self.auto_save = auto_save
        self.save_path = save_path or Path("traces")
        
        self._active_trace: Optional[ExecutionTrace] = None
        self._component_stack: List[str] = []
    
    def start_trace(self, trace_id: Optional[str] = None) -> ExecutionTrace:
        """Start a new execution trace."""
        import uuid
        
        trace_id = trace_id or str(uuid.uuid4())
        self._active_trace = ExecutionTrace(
            trace_id=trace_id,
            start_time=time.time(),
            metadata={
                "created_at": datetime.now().isoformat(),
                "tracer_config": {
                    "trace_llm_calls": self.trace_llm_calls,
                    "trace_memory": self.trace_memory,
                    "trace_tools": self.trace_tools
                }
            }
        )
        
        return self._active_trace
    
    def end_trace(self) -> Optional[ExecutionTrace]:
        """End the current trace."""
        if not self._active_trace:
            return None
        
        self._active_trace.end_time = time.time()
        
        if self.auto_save:
            self._save_trace()
        
        trace = self._active_trace
        self._active_trace = None
        self._component_stack.clear()
        
        return trace
    
    def trace_event(
        self,
        event_type: TraceEventType,
        component: str,
        data: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None
    ) -> None:
        """Trace a single event."""
        if not self._active_trace:
            return
        
        event = TraceEvent(
            timestamp=time.time(),
            event_type=event_type,
            component=component,
            data=data or {},
            duration=duration,
            parent_id=self._component_stack[-1] if self._component_stack else None
        )
        
        self._active_trace.add_event(event)
    
    def trace_crew_start(self, crew: LiteCrew) -> None:
        """Trace crew execution start."""
        self.trace_event(
            TraceEventType.CREW_START,
            f"crew_{crew.name or 'unnamed'}",
            {
                "num_agents": len(crew.agents),
                "num_tasks": len(crew.tasks),
                "process": crew.process.value if crew.process else "sequential"
            }
        )
        self._component_stack.append(f"crew_{crew.name or 'unnamed'}")
    
    def trace_crew_end(self, crew: LiteCrew, result: Any) -> None:
        """Trace crew execution end."""
        if self._component_stack:
            self._component_stack.pop()
        
        self.trace_event(
            TraceEventType.CREW_END,
            f"crew_{crew.name or 'unnamed'}",
            {"result": str(result)[:1000]}  # Truncate large results
        )
    
    def trace_agent_start(self, agent: LiteAgent, task: LiteTask) -> None:
        """Trace agent task execution start."""
        component = f"agent_{agent.role}"
        self.trace_event(
            TraceEventType.AGENT_START,
            component,
            {
                "task": task.description,
                "expected_output": task.expected_output
            }
        )
        self._component_stack.append(component)
    
    def trace_agent_end(self, agent: LiteAgent, result: TaskOutput) -> None:
        """Trace agent task execution end."""
        if self._component_stack:
            self._component_stack.pop()
        
        self.trace_event(
            TraceEventType.AGENT_END,
            f"agent_{agent.role}",
            {"result": result.raw if result else None}
        )
    
    def trace_llm_call(self, prompt: str, model: str, **kwargs) -> None:
        """Trace LLM API call."""
        if not self.trace_llm_calls:
            return
        
        self.trace_event(
            TraceEventType.LLM_CALL,
            f"llm_{model}",
            {
                "prompt": prompt[:500],  # Truncate long prompts
                "model": model,
                "parameters": kwargs
            }
        )
    
    def trace_llm_response(self, response: str, tokens_used: int = 0) -> None:
        """Trace LLM response."""
        if not self.trace_llm_calls:
            return
        
        self.trace_event(
            TraceEventType.LLM_RESPONSE,
            "llm_response",
            {
                "response": response[:500],  # Truncate long responses
                "tokens_used": tokens_used
            }
        )
    
    def get_trace(self) -> Optional[ExecutionTrace]:
        """Get the current active trace."""
        return self._active_trace
    
    def _save_trace(self) -> None:
        """Save the current trace."""
        if not self._active_trace:
            return
        
        self.save_path.mkdir(exist_ok=True)
        filename = f"trace_{self._active_trace.trace_id}_{int(time.time())}.json"
        filepath = self.save_path / filename
        
        self._active_trace.save(filepath)


class ExecutionProfiler:
    """Profile crew execution performance."""
    
    def __init__(self):
        """Initialize profiler."""
        self._timings: Dict[str, List[float]] = {}
        self._counters: Dict[str, int] = {}
        self._memory_snapshots: List[Dict[str, Any]] = []
        self._start_time: Optional[float] = None
    
    def start_profiling(self) -> None:
        """Start profiling."""
        self._start_time = time.perf_counter()
        self._timings.clear()
        self._counters.clear()
        self._memory_snapshots.clear()
        
        # Take initial memory snapshot
        self._take_memory_snapshot("start")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """Stop profiling and return results."""
        if not self._start_time:
            return {}
        
        total_time = time.perf_counter() - self._start_time
        
        # Take final memory snapshot
        self._take_memory_snapshot("end")
        
        # Calculate statistics
        timing_stats = {}
        for component, times in self._timings.items():
            timing_stats[component] = {
                "count": len(times),
                "total": sum(times),
                "average": sum(times) / len(times) if times else 0,
                "min": min(times) if times else 0,
                "max": max(times) if times else 0
            }
        
        return {
            "total_execution_time": total_time,
            "component_timings": timing_stats,
            "counters": self._counters,
            "memory_snapshots": self._memory_snapshots
        }
    
    def record_timing(self, component: str, duration: float) -> None:
        """Record a timing measurement."""
        if component not in self._timings:
            self._timings[component] = []
        self._timings[component].append(duration)
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        if name not in self._counters:
            self._counters[name] = 0
        self._counters[name] += value
    
    def _take_memory_snapshot(self, label: str) -> None:
        """Take a memory usage snapshot."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        snapshot = {
            "label": label,
            "timestamp": time.time(),
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "cpu_percent": process.cpu_percent()
        }
        
        self._memory_snapshots.append(snapshot)


class ExecutionReplayer:
    """Replay crew executions from traces."""
    
    def __init__(self, trace: ExecutionTrace):
        """Initialize replayer with a trace.
        
        Args:
            trace: Execution trace to replay
        """
        self.trace = trace
        self._current_index = 0
    
    def replay(
        self,
        speed: float = 1.0,
        callback: Optional[callable] = None,
        filter_types: Optional[Set[TraceEventType]] = None
    ) -> None:
        """Replay the execution.
        
        Args:
            speed: Replay speed multiplier (1.0 = real-time)
            callback: Function to call for each event
            filter_types: Event types to include (None = all)
        """
        if not self.trace.events:
            return
        
        start_time = time.time()
        trace_start = self.trace.events[0].timestamp
        
        for event in self.trace.events:
            # Filter events if requested
            if filter_types and event.event_type not in filter_types:
                continue
            
            # Calculate when this event should occur in replay
            event_offset = event.timestamp - trace_start
            replay_time = start_time + (event_offset / speed)
            
            # Wait until it's time for this event
            wait_time = replay_time - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
            
            # Process event
            if callback:
                callback(event)
            else:
                self._default_callback(event)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get trace summary statistics."""
        event_counts = {}
        component_times = {}
        
        for event in self.trace.events:
            # Count events by type
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Track component execution times
            if event.duration:
                if event.component not in component_times:
                    component_times[event.component] = []
                component_times[event.component].append(event.duration)
        
        # Calculate component statistics
        component_stats = {}
        for component, times in component_times.items():
            component_stats[component] = {
                "total_time": sum(times),
                "avg_time": sum(times) / len(times) if times else 0,
                "executions": len(times)
            }
        
        return {
            "trace_id": self.trace.trace_id,
            "duration": self.trace.get_duration(),
            "total_events": len(self.trace.events),
            "event_counts": event_counts,
            "component_stats": component_stats,
            "metadata": self.trace.metadata
        }
    
    def find_events(
        self,
        event_type: Optional[TraceEventType] = None,
        component: Optional[str] = None,
        time_range: Optional[Tuple[float, float]] = None
    ) -> List[TraceEvent]:
        """Find events matching criteria."""
        results = []
        
        for event in self.trace.events:
            # Check event type
            if event_type and event.event_type != event_type:
                continue
            
            # Check component
            if component and component not in event.component:
                continue
            
            # Check time range
            if time_range:
                event_time = event.timestamp - self.trace.start_time
                if event_time < time_range[0] or event_time > time_range[1]:
                    continue
            
            results.append(event)
        
        return results
    
    def _default_callback(self, event: TraceEvent) -> None:
        """Default event callback for replay."""
        timestamp = event.timestamp - self.trace.start_time
        print(f"[{timestamp:.3f}s] {event.event_type.value}: {event.component}")
        
        if event.data:
            for key, value in event.data.items():
                print(f"  {key}: {str(value)[:100]}")


# Context manager for easy tracing
class trace_execution:
    """Context manager for tracing crew execution."""
    
    def __init__(self, tracer: ExecutionTracer, crew: LiteCrew):
        """Initialize trace context.
        
        Args:
            tracer: Execution tracer
            crew: Crew to trace
        """
        self.tracer = tracer
        self.crew = crew
    
    def __enter__(self):
        """Start tracing."""
        self.tracer.start_trace()
        self.tracer.trace_crew_start(self.crew)
        return self.tracer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracing."""
        if exc_type:
            self.tracer.trace_event(
                TraceEventType.ERROR,
                "error",
                {
                    "type": exc_type.__name__,
                    "message": str(exc_val)
                }
            )
        
        self.tracer.trace_crew_end(self.crew, None)
        self.tracer.end_trace()