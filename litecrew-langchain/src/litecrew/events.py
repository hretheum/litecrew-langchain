"""Event system and callbacks for LiteCrew."""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from functools import wraps


logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standard event types for the system."""
    
    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_DELEGATED = "task.delegated"
    
    # Crew events
    CREW_STARTED = "crew.started"
    CREW_COMPLETED = "crew.completed"
    CREW_FAILED = "crew.failed"
    
    # Delegation events
    DELEGATION_STARTED = "delegation.started"
    DELEGATION_COMPLETED = "delegation.completed"
    
    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"
    MEMORY_CLEARED = "memory.cleared"
    
    # LLM events
    LLM_STARTED = "llm.started"
    LLM_COMPLETED = "llm.completed"
    LLM_FAILED = "llm.failed"
    LLM_STREAMING = "llm.streaming"


@dataclass
class Event:
    """Event object containing event data."""
    
    type: Union[EventType, str]
    data: Any
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class EventFilter:
    """Filter for event handlers."""
    
    event_types: Optional[List[Union[EventType, str]]] = None
    sources: Optional[List[str]] = None
    custom_filter: Optional[Callable[[Event], bool]] = None
    
    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria."""
        # Check event type
        if self.event_types:
            event_type = event.type.value if isinstance(event.type, EventType) else event.type
            type_match = any(
                event_type == (t.value if isinstance(t, EventType) else t)
                for t in self.event_types
            )
            if not type_match:
                return False
        
        # Check source
        if self.sources and event.source not in self.sources:
            return False
        
        # Apply custom filter
        if self.custom_filter and not self.custom_filter(event):
            return False
        
        return True


class AsyncEventHandler:
    """Wrapper for async event handlers."""
    
    def __init__(self, handler: Callable):
        self.handler = handler
        self.is_async = asyncio.iscoroutinefunction(handler)
    
    async def __call__(self, *args, **kwargs):
        """Call the handler, converting to async if needed."""
        if self.is_async:
            return await self.handler(*args, **kwargs)
        else:
            # Run sync handler in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.handler, *args, **kwargs)


class EventEmitter:
    """Event emitter for publishing and subscribing to events."""
    
    def __init__(self):
        self._handlers: Dict[str, List[tuple[Callable, Optional[EventFilter]]]] = defaultdict(list)
        self._once_handlers: Set[tuple[str, Callable]] = set()
        self._metrics = {
            "total_events_emitted": 0,
            "events_per_type": defaultdict(int),
            "total_handlers": 0,
            "errors": 0
        }
    
    def on(self, event_type: Union[EventType, str], handler: Callable, 
           filter: Optional[EventFilter] = None) -> None:
        """Register an event handler."""
        event_key = self._get_event_key(event_type)
        self._handlers[event_key].append((handler, filter))
        self._metrics["total_handlers"] += 1
    
    def once(self, event_type: Union[EventType, str], handler: Callable) -> None:
        """Register a handler that only fires once."""
        event_key = self._get_event_key(event_type)
        
        @wraps(handler)
        def once_wrapper(*args, **kwargs):
            # Remove handler after first call
            self.off(event_type, once_wrapper)
            return handler(*args, **kwargs)
        
        self.on(event_type, once_wrapper)
        self._once_handlers.add((event_key, once_wrapper))
    
    def off(self, event_type: Union[EventType, str], handler: Callable) -> None:
        """Remove an event handler."""
        event_key = self._get_event_key(event_type)
        self._handlers[event_key] = [
            (h, f) for h, f in self._handlers[event_key] 
            if h != handler
        ]
        self._metrics["total_handlers"] = max(0, self._metrics["total_handlers"] - 1)
    
    def emit(self, event_type: Union[EventType, str], data: Any = None, 
             source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event synchronously."""
        event = self._create_event(event_type, data, source, metadata)
        self._emit_event(event)
    
    def emit_from(self, source: str, event_type: Union[EventType, str], 
                  data: Any = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event from a specific source."""
        self.emit(event_type, data, source=source, metadata=metadata)
    
    async def emit_async(self, event_type: Union[EventType, str], data: Any = None,
                        source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event asynchronously."""
        event = self._create_event(event_type, data, source, metadata)
        await self._emit_event_async(event)
    
    def _create_event(self, event_type: Union[EventType, str], data: Any,
                     source: Optional[str], metadata: Optional[Dict[str, Any]]) -> Event:
        """Create an event object."""
        return Event(
            type=event_type,
            data=data,
            source=source,
            metadata=metadata or {}
        )
    
    def _get_event_key(self, event_type: Union[EventType, str]) -> str:
        """Get string key for event type."""
        if isinstance(event_type, EventType):
            return event_type.value
        return event_type
    
    def _emit_event(self, event: Event) -> None:
        """Emit event to all matching handlers synchronously."""
        event_key = self._get_event_key(event.type)
        
        # Update metrics
        self._metrics["total_events_emitted"] += 1
        self._metrics["events_per_type"][event_key] += 1
        
        # Get handlers for specific event and wildcard
        handlers = self._handlers.get(event_key, []) + self._handlers.get('*', [])
        
        for handler, filter in handlers:
            try:
                # Check filter
                if filter and not filter.matches(event):
                    continue
                
                # Call handler
                if isinstance(handler, AsyncEventHandler):
                    # Run async handler in new task
                    asyncio.create_task(self._call_async_handler(handler, event.data))
                else:
                    handler(event.data)
                    
            except Exception as e:
                self._metrics["errors"] += 1
                logger.error(f"Error in event handler for {event_key}: {e}")
    
    async def _emit_event_async(self, event: Event) -> None:
        """Emit event to all matching handlers asynchronously."""
        event_key = self._get_event_key(event.type)
        
        # Update metrics
        self._metrics["total_events_emitted"] += 1
        self._metrics["events_per_type"][event_key] += 1
        
        # Get handlers
        handlers = self._handlers.get(event_key, []) + self._handlers.get('*', [])
        
        # Create tasks for all handlers
        tasks = []
        for handler, filter in handlers:
            try:
                # Check filter
                if filter and not filter.matches(event):
                    continue
                
                # Create task for handler
                if isinstance(handler, AsyncEventHandler):
                    tasks.append(self._call_async_handler(handler, event.data))
                else:
                    # Wrap sync handler
                    tasks.append(self._call_sync_handler_async(handler, event.data))
                    
            except Exception as e:
                self._metrics["errors"] += 1
                logger.error(f"Error preparing handler for {event_key}: {e}")
        
        # Execute all handlers concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_async_handler(self, handler: AsyncEventHandler, data: Any) -> None:
        """Call an async handler with error handling."""
        try:
            await handler(data)
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Error in async event handler: {e}")
    
    async def _call_sync_handler_async(self, handler: Callable, data: Any) -> None:
        """Call a sync handler in an executor."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler, data)
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Error in sync event handler: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event system metrics."""
        return {
            "total_events_emitted": self._metrics["total_events_emitted"],
            "unique_event_types": len(self._metrics["events_per_type"]),
            "events_per_type": dict(self._metrics["events_per_type"]),
            "total_handlers": self._metrics["total_handlers"],
            "errors": self._metrics["errors"]
        }


class LifecycleCallbacks:
    """Manager for lifecycle callbacks."""
    
    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
    
    # Agent callbacks
    def on_agent_create(self, callback: Callable) -> None:
        """Register callback for agent creation."""
        self._callbacks['agent_create'].append(callback)
    
    def on_agent_start(self, callback: Callable) -> None:
        """Register callback for agent start."""
        self._callbacks['agent_start'].append(callback)
    
    def on_agent_complete(self, callback: Callable) -> None:
        """Register callback for agent completion."""
        self._callbacks['agent_complete'].append(callback)
    
    def on_agent_error(self, callback: Callable) -> None:
        """Register callback for agent error."""
        self._callbacks['agent_error'].append(callback)
    
    # Task callbacks
    def on_task_create(self, callback: Callable) -> None:
        """Register callback for task creation."""
        self._callbacks['task_create'].append(callback)
    
    def on_task_start(self, callback: Callable) -> None:
        """Register callback for task start."""
        self._callbacks['task_start'].append(callback)
    
    def on_task_complete(self, callback: Callable) -> None:
        """Register callback for task completion."""
        self._callbacks['task_complete'].append(callback)
    
    def on_task_retry(self, callback: Callable) -> None:
        """Register callback for task retry."""
        self._callbacks['task_retry'].append(callback)
    
    # Crew callbacks
    def on_crew_start(self, callback: Callable) -> None:
        """Register callback for crew start."""
        self._callbacks['crew_start'].append(callback)
    
    def on_crew_task_complete(self, callback: Callable) -> None:
        """Register callback for crew task completion."""
        self._callbacks['crew_task_complete'].append(callback)
    
    def on_crew_complete(self, callback: Callable) -> None:
        """Register callback for crew completion."""
        self._callbacks['crew_complete'].append(callback)
    
    def trigger(self, event: str, *args, **kwargs) -> None:
        """Trigger callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in lifecycle callback {event}: {e}")
    
    async def trigger_async(self, event: str, *args, **kwargs) -> None:
        """Trigger callbacks asynchronously."""
        tasks = []
        for callback in self._callbacks.get(event, []):
            if asyncio.iscoroutinefunction(callback):
                tasks.append(callback(*args, **kwargs))
            else:
                # Run sync callback in executor
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, callback, *args, **kwargs))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Global event emitter instance (optional, for convenience)
global_emitter = EventEmitter()


def emit_event(event_type: Union[EventType, str], data: Any = None, **kwargs) -> None:
    """Convenience function to emit events globally."""
    global_emitter.emit(event_type, data, **kwargs)


async def emit_event_async(event_type: Union[EventType, str], data: Any = None, **kwargs) -> None:
    """Convenience function to emit events globally (async)."""
    await global_emitter.emit_async(event_type, data, **kwargs)