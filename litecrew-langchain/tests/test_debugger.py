"""
Tests for Debugging Tools.
"""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.crew import Crew as LiteCrew
from litecrew.task import LiteTask, TaskOutput
from litecrew.debugging.debugger import (
    ExecutionProfiler,
    ExecutionReplayer,
    ExecutionTrace,
    ExecutionTracer,
    TraceEvent,
    TraceEventType,
    trace_execution,
)


class TestTraceEvent:
    """Test TraceEvent functionality."""
    
    def test_event_creation(self):
        """Test creating trace events."""
        event = TraceEvent(
            timestamp=time.time(),
            event_type=TraceEventType.AGENT_START,
            component="agent_researcher",
            data={"task": "Research topic"},
            duration=1.5
        )
        
        assert event.event_type == TraceEventType.AGENT_START
        assert event.component == "agent_researcher"
        assert event.data["task"] == "Research topic"
        assert event.duration == 1.5
    
    def test_event_serialization(self):
        """Test event to/from dict conversion."""
        original = TraceEvent(
            timestamp=1234567890.0,
            event_type=TraceEventType.LLM_CALL,
            component="llm_gpt4",
            data={"prompt": "Test prompt", "temperature": 0.7}
        )
        
        # Convert to dict and back
        event_dict = original.to_dict()
        restored = TraceEvent.from_dict(event_dict)
        
        assert restored.timestamp == original.timestamp
        assert restored.event_type == original.event_type
        assert restored.component == original.component
        assert restored.data == original.data


class TestExecutionTrace:
    """Test ExecutionTrace functionality."""
    
    def test_trace_creation(self):
        """Test creating execution traces."""
        trace = ExecutionTrace(
            trace_id="test-123",
            start_time=time.time()
        )
        
        # Add events
        for i in range(3):
            event = TraceEvent(
                timestamp=time.time() + i,
                event_type=TraceEventType.TASK_START,
                component=f"task_{i}"
            )
            trace.add_event(event)
        
        assert len(trace.events) == 3
        assert trace.get_duration() > 0
    
    def test_trace_timeline(self):
        """Test timeline generation."""
        start_time = time.time()
        trace = ExecutionTrace(
            trace_id="timeline-test",
            start_time=start_time
        )
        
        # Add events with different timestamps
        for i in range(3):
            event = TraceEvent(
                timestamp=start_time + i * 0.5,
                event_type=TraceEventType.AGENT_START,
                component=f"agent_{i}",
                duration=0.3
            )
            trace.add_event(event)
        
        timeline = trace.get_timeline()
        
        assert len(timeline) == 3
        assert timeline[0]["time"] < timeline[1]["time"]
        assert all("duration" in item for item in timeline)
    
    def test_trace_save_load(self, tmp_path):
        """Test saving and loading traces."""
        # Create trace with events
        trace = ExecutionTrace(
            trace_id="save-test",
            start_time=time.time(),
            metadata={"test": True}
        )
        
        for i in range(2):
            trace.add_event(TraceEvent(
                timestamp=time.time(),
                event_type=TraceEventType.TASK_END,
                component=f"task_{i}",
                data={"result": f"Result {i}"}
            ))
        
        # Save as JSON
        json_path = tmp_path / "trace.json"
        trace.save(json_path)
        
        # Load and verify
        loaded = ExecutionTrace.load(json_path)
        assert loaded.trace_id == trace.trace_id
        assert len(loaded.events) == len(trace.events)
        assert loaded.metadata == trace.metadata


class TestExecutionTracer:
    """Test ExecutionTracer functionality."""
    
    @pytest.fixture
    def tracer(self):
        """Create test tracer."""
        return ExecutionTracer(auto_save=False)
    
    @pytest.fixture
    def test_crew(self):
        """Create test crew."""
        agent = LiteAgent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
        task = LiteTask(
            description="Test task",
            agent=agent,
            expected_output="Test output"
        )
        return LiteCrew(
            name="Test Crew",
            agents=[agent],
            tasks=[task]
        )
    
    def test_trace_lifecycle(self, tracer):
        """Test trace start/end lifecycle."""
        # Start trace
        trace = tracer.start_trace("test-trace")
        assert trace is not None
        assert tracer.get_trace() == trace
        
        # Add some events
        tracer.trace_event(
            TraceEventType.CUSTOM,
            "test_component",
            {"message": "Test event"}
        )
        
        # End trace
        ended_trace = tracer.end_trace()
        assert ended_trace == trace
        assert tracer.get_trace() is None
        assert len(ended_trace.events) == 1
    
    def test_crew_tracing(self, tracer, test_crew):
        """Test crew execution tracing."""
        tracer.start_trace()
        
        # Trace crew execution
        tracer.trace_crew_start(test_crew)
        
        # Trace agent execution
        agent = test_crew.agents[0]
        task = test_crew.tasks[0]
        tracer.trace_agent_start(agent, task)
        
        # Mock task output
        output = TaskOutput(raw="Test result", task_id="1")
        tracer.trace_agent_end(agent, output)
        
        tracer.trace_crew_end(test_crew, "Final result")
        
        trace = tracer.end_trace()
        
        # Verify events
        event_types = [e.event_type for e in trace.events]
        assert TraceEventType.CREW_START in event_types
        assert TraceEventType.AGENT_START in event_types
        assert TraceEventType.AGENT_END in event_types
        assert TraceEventType.CREW_END in event_types
    
    def test_llm_tracing(self, tracer):
        """Test LLM call tracing."""
        tracer.start_trace()
        
        # Trace LLM call
        tracer.trace_llm_call(
            prompt="Test prompt",
            model="gpt-4",
            temperature=0.7,
            max_tokens=100
        )
        
        # Trace response
        tracer.trace_llm_response(
            response="Test response",
            tokens_used=50
        )
        
        trace = tracer.end_trace()
        
        # Find LLM events
        llm_events = [e for e in trace.events if "llm" in e.component]
        assert len(llm_events) == 2
        assert any(e.event_type == TraceEventType.LLM_CALL for e in llm_events)
        assert any(e.event_type == TraceEventType.LLM_RESPONSE for e in llm_events)
    
    def test_auto_save(self, tmp_path, test_crew):
        """Test automatic trace saving."""
        tracer = ExecutionTracer(
            auto_save=True,
            save_path=tmp_path
        )
        
        tracer.start_trace("auto-save-test")
        tracer.trace_crew_start(test_crew)
        tracer.trace_crew_end(test_crew, "Done")
        tracer.end_trace()
        
        # Check if file was saved
        trace_files = list(tmp_path.glob("trace_*.json"))
        assert len(trace_files) == 1
        
        # Load and verify
        loaded = ExecutionTrace.load(trace_files[0])
        assert loaded.trace_id == "auto-save-test"


class TestExecutionProfiler:
    """Test ExecutionProfiler functionality."""
    
    def test_profiling_lifecycle(self):
        """Test profiler start/stop."""
        profiler = ExecutionProfiler()
        
        # Start profiling
        profiler.start_profiling()
        
        # Record some metrics
        profiler.record_timing("agent_execution", 0.5)
        profiler.record_timing("agent_execution", 0.3)
        profiler.increment_counter("llm_calls", 5)
        
        # Stop and get results
        results = profiler.stop_profiling()
        
        assert "total_execution_time" in results
        assert "component_timings" in results
        assert "counters" in results
        assert "memory_snapshots" in results
        
        # Check timing stats
        agent_stats = results["component_timings"]["agent_execution"]
        assert agent_stats["count"] == 2
        assert agent_stats["total"] == 0.8
        assert agent_stats["average"] == 0.4
        
        # Check counters
        assert results["counters"]["llm_calls"] == 5
    
    def test_memory_snapshots(self):
        """Test memory snapshot tracking."""
        profiler = ExecutionProfiler()
        
        profiler.start_profiling()
        time.sleep(0.1)  # Let some time pass
        results = profiler.stop_profiling()
        
        snapshots = results["memory_snapshots"]
        assert len(snapshots) >= 2  # Start and end
        assert snapshots[0]["label"] == "start"
        assert snapshots[-1]["label"] == "end"
        assert all("rss_mb" in s for s in snapshots)


class TestExecutionReplayer:
    """Test ExecutionReplayer functionality."""
    
    @pytest.fixture
    def sample_trace(self):
        """Create sample trace for testing."""
        trace = ExecutionTrace(
            trace_id="replay-test",
            start_time=1000.0
        )
        
        # Add events with different timestamps
        events = [
            (1000.0, TraceEventType.CREW_START, "crew_test"),
            (1000.5, TraceEventType.AGENT_START, "agent_1"),
            (1001.0, TraceEventType.LLM_CALL, "llm_gpt4"),
            (1001.5, TraceEventType.AGENT_END, "agent_1"),
            (1002.0, TraceEventType.CREW_END, "crew_test")
        ]
        
        for timestamp, event_type, component in events:
            trace.add_event(TraceEvent(
                timestamp=timestamp,
                event_type=event_type,
                component=component,
                data={"test": True}
            ))
        
        trace.end_time = 1002.0
        return trace
    
    def test_replay_summary(self, sample_trace):
        """Test trace summary generation."""
        replayer = ExecutionReplayer(sample_trace)
        summary = replayer.get_summary()
        
        assert summary["trace_id"] == "replay-test"
        assert summary["duration"] == 2.0
        assert summary["total_events"] == 5
        
        # Check event counts
        assert summary["event_counts"]["crew_start"] == 1
        assert summary["event_counts"]["agent_start"] == 1
        assert summary["event_counts"]["llm_call"] == 1
    
    def test_find_events(self, sample_trace):
        """Test event finding functionality."""
        replayer = ExecutionReplayer(sample_trace)
        
        # Find by event type
        agent_events = replayer.find_events(event_type=TraceEventType.AGENT_START)
        assert len(agent_events) == 1
        assert agent_events[0].component == "agent_1"
        
        # Find by component
        llm_events = replayer.find_events(component="llm")
        assert len(llm_events) == 1
        
        # Find by time range
        early_events = replayer.find_events(time_range=(0, 1.0))
        assert len(early_events) == 3  # Events at 0, 0.5, 1.0
    
    def test_replay_execution(self, sample_trace):
        """Test replay execution with callback."""
        replayer = ExecutionReplayer(sample_trace)
        
        # Track replayed events
        replayed = []
        
        def callback(event):
            replayed.append(event.event_type)
        
        # Replay at high speed
        replayer.replay(speed=100.0, callback=callback)
        
        assert len(replayed) == 5
        assert replayed[0] == TraceEventType.CREW_START
        assert replayed[-1] == TraceEventType.CREW_END


class TestTraceContext:
    """Test trace_execution context manager."""
    
    def test_context_manager(self):
        """Test trace context manager."""
        tracer = ExecutionTracer()
        
        agent = LiteAgent(role="Test", goal="Test", backstory="Test")
        task = LiteTask(description="Test", agent=agent, expected_output="Test")
        crew = LiteCrew(name="Context Test", agents=[agent], tasks=[task])
        
        # Use context manager
        with trace_execution(tracer, crew) as t:
            assert t == tracer
            assert tracer.get_trace() is not None
            
            # Add custom event
            tracer.trace_event(
                TraceEventType.CUSTOM,
                "test",
                {"message": "Inside context"}
            )
        
        # After context, trace should be ended
        assert tracer.get_trace() is None
    
    def test_context_manager_with_error(self):
        """Test context manager error handling."""
        tracer = ExecutionTracer()
        crew = LiteCrew(name="Error Test", agents=[], tasks=[])
        
        # Use context manager with error
        with pytest.raises(ValueError):
            with trace_execution(tracer, crew):
                raise ValueError("Test error")
        
        # Trace should still be ended
        assert tracer.get_trace() is None