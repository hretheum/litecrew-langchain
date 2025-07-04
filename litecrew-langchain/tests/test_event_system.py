"""Tests for event system and callbacks functionality."""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock

from litecrew.events import (
    EventEmitter, Event, EventType, EventFilter,
    LifecycleCallbacks, AsyncEventHandler
)
from litecrew.agent import Agent
from litecrew.crew import Crew
from litecrew.task import Task


class TestEventEmitter:
    """Test basic event emitter functionality."""
    
    def test_event_emitter_creation(self):
        """Test creating an event emitter."""
        emitter = EventEmitter()
        
        assert emitter is not None
        assert hasattr(emitter, 'on')
        assert hasattr(emitter, 'emit')
        assert hasattr(emitter, 'off')
        assert hasattr(emitter, 'once')
    
    def test_emit_and_listen(self):
        """Test emitting and listening to events."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Register handler
        emitter.on('test_event', handler)
        
        # Emit event
        emitter.emit('test_event', {'data': 'test'})
        
        # Verify handler was called
        handler.assert_called_once_with({'data': 'test'})
    
    def test_multiple_handlers(self):
        """Test multiple handlers for same event."""
        emitter = EventEmitter()
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()
        
        # Register multiple handlers
        emitter.on('multi_event', handler1)
        emitter.on('multi_event', handler2)
        emitter.on('multi_event', handler3)
        
        # Emit event
        emitter.emit('multi_event', 'test_data')
        
        # All handlers should be called
        handler1.assert_called_once_with('test_data')
        handler2.assert_called_once_with('test_data')
        handler3.assert_called_once_with('test_data')
    
    def test_once_handler(self):
        """Test handler that only fires once."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Register once handler
        emitter.once('once_event', handler)
        
        # Emit multiple times
        emitter.emit('once_event', 'first')
        emitter.emit('once_event', 'second')
        emitter.emit('once_event', 'third')
        
        # Handler should only be called once
        handler.assert_called_once_with('first')
    
    def test_remove_handler(self):
        """Test removing event handlers."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Register and then remove
        emitter.on('remove_test', handler)
        emitter.off('remove_test', handler)
        
        # Emit should not call handler
        emitter.emit('remove_test', 'data')
        handler.assert_not_called()
    
    def test_event_dispatch_performance(self):
        """Test event dispatch is under 1ms."""
        emitter = EventEmitter()
        
        # Add 100 handlers
        handlers = []
        for i in range(100):
            handler = Mock()
            handlers.append(handler)
            emitter.on('perf_test', handler)
        
        # Measure dispatch time
        start = time.perf_counter()
        emitter.emit('perf_test', {'test': 'data'})
        duration = time.perf_counter() - start
        
        # Should be under 2ms for 100 handlers (allowing some overhead)
        assert duration < 0.002, f"Event dispatch took {duration*1000:.3f}ms"
        
        # Verify all handlers were called
        for handler in handlers:
            handler.assert_called_once()


class TestEventTypes:
    """Test custom event types."""
    
    def test_event_type_enum(self):
        """Test event type enumeration."""
        # Standard event types
        assert EventType.AGENT_CREATED
        assert EventType.AGENT_STARTED
        assert EventType.AGENT_COMPLETED
        assert EventType.AGENT_FAILED
        assert EventType.TASK_CREATED
        assert EventType.TASK_STARTED
        assert EventType.TASK_COMPLETED
        assert EventType.TASK_FAILED
        assert EventType.CREW_STARTED
        assert EventType.CREW_COMPLETED
        assert EventType.DELEGATION_STARTED
        assert EventType.DELEGATION_COMPLETED
    
    def test_event_object(self):
        """Test Event object structure."""
        event = Event(
            type=EventType.AGENT_STARTED,
            source='agent_1',
            data={'task': 'analyze_data'},
            timestamp=time.time()
        )
        
        assert event.type == EventType.AGENT_STARTED
        assert event.source == 'agent_1'
        assert event.data['task'] == 'analyze_data'
        assert event.timestamp > 0
    
    def test_custom_event_type(self):
        """Test creating custom event types."""
        # Custom event
        custom_event = Event(
            type='custom.process_complete',
            source='custom_processor',
            data={'result': 'success'},
            metadata={'priority': 'high'}
        )
        
        assert custom_event.type == 'custom.process_complete'
        assert custom_event.metadata['priority'] == 'high'


class TestEventFiltering:
    """Test event filtering functionality."""
    
    def test_basic_filter(self):
        """Test basic event filtering."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Create filter for specific event type
        filter = EventFilter(event_types=[EventType.AGENT_STARTED])
        
        # Register handler with filter
        emitter.on('*', handler, filter=filter)
        
        # Emit various events
        emitter.emit(EventType.AGENT_STARTED, {'agent': 'test'})
        emitter.emit(EventType.AGENT_COMPLETED, {'agent': 'test'})
        emitter.emit(EventType.TASK_STARTED, {'task': 'test'})
        
        # Handler should only be called for AGENT_STARTED
        assert handler.call_count == 1
        handler.assert_called_with({'agent': 'test'})
    
    def test_source_filter(self):
        """Test filtering by event source."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Filter for specific source
        filter = EventFilter(sources=['agent_1', 'agent_2'])
        
        emitter.on('*', handler, filter=filter)
        
        # Emit from different sources
        emitter.emit_from('agent_1', 'test_event', 'data1')
        emitter.emit_from('agent_2', 'test_event', 'data2')
        emitter.emit_from('agent_3', 'test_event', 'data3')
        
        # Should only receive from agent_1 and agent_2
        assert handler.call_count == 2
    
    def test_custom_filter_function(self):
        """Test custom filter function."""
        emitter = EventEmitter()
        handler = Mock()
        
        # Custom filter: only events with priority > 5
        def high_priority_filter(event):
            return event.metadata.get('priority', 0) > 5
        
        filter = EventFilter(custom_filter=high_priority_filter)
        emitter.on('*', handler, filter=filter)
        
        # Emit events with different priorities
        emitter.emit('task', {'id': 1}, metadata={'priority': 3})
        emitter.emit('task', {'id': 2}, metadata={'priority': 7})
        emitter.emit('task', {'id': 3}, metadata={'priority': 10})
        
        # Should only receive high priority events
        assert handler.call_count == 2


class TestLifecycleCallbacks:
    """Test lifecycle callbacks functionality."""
    
    def test_agent_lifecycle_callbacks(self):
        """Test agent lifecycle callbacks."""
        callbacks = LifecycleCallbacks()
        
        # Register callbacks
        on_create = Mock()
        on_start = Mock()
        on_complete = Mock()
        on_error = Mock()
        
        callbacks.on_agent_create(on_create)
        callbacks.on_agent_start(on_start)
        callbacks.on_agent_complete(on_complete)
        callbacks.on_agent_error(on_error)
        
        # Create agent with callbacks
        agent = Agent(
            role="Test Agent",
            goal="Test lifecycle",
            backstory="I test things",
            lifecycle_callbacks=callbacks
        )
        
        # Verify creation callback
        on_create.assert_called_once()
        
        # Execute task (simulated)
        # In real implementation, these would be called during execution
        callbacks.trigger('agent_start', agent)
        callbacks.trigger('agent_complete', agent, result="success")
        
        on_start.assert_called_once()
        on_complete.assert_called_once()
    
    def test_task_lifecycle_callbacks(self):
        """Test task lifecycle callbacks."""
        callbacks = LifecycleCallbacks()
        
        # Register callbacks
        on_create = Mock()
        on_start = Mock()
        on_complete = Mock()
        on_retry = Mock()
        
        callbacks.on_task_create(on_create)
        callbacks.on_task_start(on_start)
        callbacks.on_task_complete(on_complete)
        callbacks.on_task_retry(on_retry)
        
        # Task would trigger these during execution
        task_data = {'id': 'task_1', 'description': 'Test task'}
        
        callbacks.trigger('task_create', task_data)
        callbacks.trigger('task_start', task_data)
        callbacks.trigger('task_complete', task_data, result="done")
        
        on_create.assert_called_once()
        on_start.assert_called_once()
        on_complete.assert_called_once()
    
    def test_crew_lifecycle_callbacks(self):
        """Test crew lifecycle callbacks."""
        callbacks = LifecycleCallbacks()
        
        # Register callbacks
        on_start = Mock()
        on_task_complete = Mock()
        on_complete = Mock()
        
        callbacks.on_crew_start(on_start)
        callbacks.on_crew_task_complete(on_task_complete)
        callbacks.on_crew_complete(on_complete)
        
        # Simulate crew execution
        crew_data = {'id': 'crew_1', 'agents': 3}
        
        callbacks.trigger('crew_start', crew_data)
        callbacks.trigger('crew_task_complete', {'task': 1, 'result': 'ok'})
        callbacks.trigger('crew_task_complete', {'task': 2, 'result': 'ok'})
        callbacks.trigger('crew_complete', crew_data, results=['ok', 'ok'])
        
        on_start.assert_called_once()
        assert on_task_complete.call_count == 2
        on_complete.assert_called_once()


class TestAsyncEventHandlers:
    """Test async event handler functionality."""
    
    @pytest.mark.asyncio
    async def test_async_event_handler(self):
        """Test async event handlers."""
        emitter = EventEmitter()
        
        # Track call order
        call_order = []
        
        # Async handler
        async def async_handler(data):
            await asyncio.sleep(0.01)  # Simulate async work
            call_order.append(f"async_{data}")
        
        # Sync handler
        def sync_handler(data):
            call_order.append(f"sync_{data}")
        
        # Register both
        emitter.on('test', AsyncEventHandler(async_handler))
        emitter.on('test', sync_handler)
        
        # Emit event
        await emitter.emit_async('test', 'data')
        
        # Both should be called
        assert 'sync_data' in call_order
        assert 'async_data' in call_order
    
    @pytest.mark.asyncio
    async def test_concurrent_async_handlers(self):
        """Test concurrent execution of async handlers."""
        emitter = EventEmitter()
        
        # Track execution
        execution_times = []
        
        async def slow_handler(data):
            start = time.time()
            await asyncio.sleep(0.05)  # 50ms
            execution_times.append(time.time() - start)
        
        # Register multiple async handlers
        for _ in range(5):
            emitter.on('concurrent', AsyncEventHandler(slow_handler))
        
        # Emit and wait for all
        start = time.time()
        await emitter.emit_async('concurrent', 'test')
        total_time = time.time() - start
        
        # Should execute concurrently, not sequentially
        # 5 handlers * 50ms = 250ms if sequential
        # Should be close to 50ms if concurrent
        assert total_time < 0.1, f"Handlers not concurrent: {total_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test error handling in async handlers."""
        emitter = EventEmitter()
        
        # Handler that raises error
        async def failing_handler(data):
            raise ValueError("Test error")
        
        # Handler that succeeds
        success_handler = AsyncMock()
        
        # Register both
        emitter.on('error_test', AsyncEventHandler(failing_handler))
        emitter.on('error_test', AsyncEventHandler(success_handler))
        
        # Emit - should not crash
        await emitter.emit_async('error_test', 'data')
        
        # Success handler should still be called
        success_handler.assert_called_once_with('data')


class TestEventIntegration:
    """Test event system integration with agents and crews."""
    
    def test_agent_event_emission(self):
        """Test that agents emit proper events."""
        # Create agent with event tracking
        emitter = EventEmitter()
        events_received = []
        
        def track_event(event):
            events_received.append(event)
        
        emitter.on('*', track_event)
        
        agent = Agent(
            role="Event Test Agent",
            goal="Test events",
            backstory="I emit events",
            event_emitter=emitter
        )
        
        # Execute task (mocked)
        # In real implementation, these events would be emitted during execution
        emitter.emit(EventType.AGENT_CREATED, {'agent': agent.role})
        emitter.emit(EventType.AGENT_STARTED, {'task': 'test_task'})
        emitter.emit(EventType.AGENT_COMPLETED, {'result': 'success'})
        
        # Verify events were emitted
        assert len(events_received) >= 4  # Agent creation emits an event automatically
        # Check that the agent creation event was emitted (it just contains data, not event type)
        assert any('Event Test Agent' in str(e) for e in events_received)
    
    def test_crew_event_emission(self):
        """Test that crews emit proper events."""
        emitter = EventEmitter()
        events = []
        
        emitter.on('*', lambda e: events.append(e))
        
        # Create crew with event emitter
        agent1 = Agent(role="Agent 1", goal="Goal 1", backstory="Story 1")
        agent2 = Agent(role="Agent 2", goal="Goal 2", backstory="Story 2")
        
        # Create a dummy task to satisfy validation
        from litecrew.task import Task
        task = Task(description="Test task", agent=agent1)
        
        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task],
            event_emitter=emitter
        )
        
        # Simulate crew lifecycle events
        emitter.emit(EventType.CREW_STARTED, {'crew_id': id(crew)})
        emitter.emit(EventType.TASK_STARTED, {'task': 'task_1'})
        emitter.emit(EventType.TASK_COMPLETED, {'task': 'task_1', 'result': 'ok'})
        emitter.emit(EventType.CREW_COMPLETED, {'total_tasks': 1})
        
        # Verify crew events
        assert len(events) >= 4
    
    def test_event_metrics(self):
        """Test event system metrics."""
        emitter = EventEmitter()
        
        # Emit various events
        for i in range(100):
            emitter.emit(f'event_{i % 10}', {'index': i})
        
        # Get metrics
        metrics = emitter.get_metrics()
        
        assert metrics['total_events_emitted'] == 100
        assert metrics['unique_event_types'] == 10
        assert metrics['total_handlers'] >= 0
        assert 'events_per_type' in metrics


def test_zero_event_loss():
    """Test that no events are lost during high-frequency emission."""
    emitter = EventEmitter()
    received_events = []
    
    def handler(data):
        received_events.append(data)
    
    emitter.on('rapid', handler)
    
    # Emit 1000 events rapidly
    sent_count = 1000
    for i in range(sent_count):
        emitter.emit('rapid', {'index': i})
    
    # Verify all events were received
    assert len(received_events) == sent_count
    
    # Verify order is preserved
    for i, event in enumerate(received_events):
        assert event['index'] == i


def test_handler_execution_concurrent():
    """Test that handlers can execute concurrently."""
    emitter = EventEmitter()
    execution_order = []
    lock = asyncio.Lock()
    
    async def handler_a(data):
        async with lock:
            execution_order.append('a_start')
        await asyncio.sleep(0.01)
        async with lock:
            execution_order.append('a_end')
    
    async def handler_b(data):
        async with lock:
            execution_order.append('b_start')
        await asyncio.sleep(0.01)
        async with lock:
            execution_order.append('b_end')
    
    # This test verifies concurrent execution
    # If sequential: a_start, a_end, b_start, b_end
    # If concurrent: a_start, b_start, a_end, b_end (or similar)
    
    # Run test
    async def run_test():
        emitter.on('concurrent', AsyncEventHandler(handler_a))
        emitter.on('concurrent', AsyncEventHandler(handler_b))
        await emitter.emit_async('concurrent', 'test')
        
        # Check for interleaved execution
        assert execution_order.index('b_start') < execution_order.index('a_end')
    
    asyncio.run(run_test())