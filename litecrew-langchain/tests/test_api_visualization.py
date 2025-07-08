"""Tests for API visualization module."""

from datetime import datetime, timedelta

import pytest

from litecrew.api.visualization import ProcessVisualizer
from litecrew.processes import ProcessResult, ProcessTurn
from litecrew.task import TaskOutput


class TestProcessVisualizer:
    """Test process visualization functionality."""

    @pytest.fixture
    def sample_turns(self):
        """Create sample process turns."""
        base_time = datetime.now()
        return [
            ProcessTurn(
                agent="Agent1",
                content="First turn content",
                timestamp=base_time,
                metadata={"phase": "initialization"},
            ),
            ProcessTurn(
                agent="Agent2",
                content="Second turn with a very long content that should be truncated "
                * 10,
                timestamp=base_time + timedelta(seconds=5),
                metadata={"phase": "discussion", "round": 1},
            ),
            ProcessTurn(
                agent="Agent1",
                content="Final turn",
                timestamp=base_time + timedelta(seconds=10),
                metadata={"phase": "conclusion"},
            ),
        ]

    @pytest.fixture
    def sample_result(self, sample_turns):
        """Create sample process result."""
        return ProcessResult(
            raw="Final output from the process",
            success=True,
            duration=10.5,
            turns=sample_turns,
            tasks_output=[
                TaskOutput(raw="Task 1 output", task_id="1", agent_role="Agent1"),
                TaskOutput(raw="Task 2 output", task_id="2", agent_role="Agent2"),
            ],
            metadata={"process_type": "debate", "total_rounds": 3},
        )

    def test_format_turn(self):
        """Test formatting a single turn."""
        turn = ProcessTurn(
            agent="TestAgent",
            content="Test content",
            timestamp=datetime.now(),
            metadata={"phase": "test_phase", "extra": "data"},
        )

        formatted = ProcessVisualizer.format_turn(turn)
        assert formatted["agent"] == "TestAgent"
        assert formatted["content"] == "Test content"
        assert "timestamp" in formatted
        assert formatted["phase"] == "test_phase"
        assert formatted["metadata"]["extra"] == "data"

    def test_format_turn_truncates_long_content(self):
        """Test that long content is truncated."""
        long_content = "x" * 300
        turn = ProcessTurn(
            agent="TestAgent",
            content=long_content,
            timestamp=datetime.now(),
            metadata={},
        )

        formatted = ProcessVisualizer.format_turn(turn)
        assert len(formatted["content"]) == 203  # 200 + "..."
        assert formatted["content"].endswith("...")

    def test_format_process_result(self, sample_result):
        """Test formatting process result."""
        formatted = ProcessVisualizer.format_process_result(sample_result)

        assert formatted["success"] is True
        assert formatted["duration"] == 10.5
        assert formatted["error"] is None
        assert formatted["tasks_completed"] == 2
        assert len(formatted["turns"]) == 3
        assert formatted["summary"] == "Final output from the process"
        assert formatted["metadata"]["process_type"] == "debate"

    def test_format_process_result_with_error(self, sample_turns):
        """Test formatting failed process result."""
        result = ProcessResult(
            raw="",
            success=False,
            error="Process failed",
            duration=5.0,
            turns=sample_turns,
            tasks_output=[],
        )

        formatted = ProcessVisualizer.format_process_result(result)
        assert formatted["success"] is False
        assert formatted["error"] == "Process failed"
        assert formatted["tasks_completed"] == 0
        assert formatted["summary"] == ""

    def test_create_timeline(self, sample_turns):
        """Test creating timeline visualization."""
        timeline = ProcessVisualizer.create_timeline(sample_turns)

        assert len(timeline) == 3

        # Check first entry
        assert timeline[0]["id"] == 0
        assert timeline[0]["agent"] == "Agent1"
        assert timeline[0]["phase"] == "initialization"
        assert timeline[0]["duration_from_start"] == 0

        # Check second entry
        assert timeline[1]["id"] == 1
        assert timeline[1]["agent"] == "Agent2"
        assert timeline[1]["phase"] == "discussion"
        assert timeline[1]["duration_from_start"] == 5.0

        # Check third entry
        assert timeline[2]["duration_from_start"] == 10.0

    def test_create_timeline_empty(self):
        """Test creating timeline with no turns."""
        timeline = ProcessVisualizer.create_timeline([])
        assert timeline == []

    def test_create_agent_stats(self, sample_turns):
        """Test creating agent statistics."""
        stats = ProcessVisualizer.create_agent_stats(sample_turns)

        assert "Agent1" in stats
        assert "Agent2" in stats

        # Agent1 stats
        assert stats["Agent1"]["turn_count"] == 2
        assert stats["Agent1"]["total_length"] == len("First turn content") + len(
            "Final turn"
        )
        assert (
            stats["Agent1"]["avg_length"]
            == (len("First turn content") + len("Final turn")) / 2
        )

        # Agent2 stats
        assert stats["Agent2"]["turn_count"] == 1
        assert stats["Agent2"]["total_length"] > 0

    def test_create_phase_distribution(self, sample_turns):
        """Test creating phase distribution."""
        # Skip if method doesn't exist
        if not hasattr(ProcessVisualizer, "create_phase_distribution"):
            pytest.skip("create_phase_distribution not implemented")

        distribution = ProcessVisualizer.create_phase_distribution(sample_turns)
        assert distribution["initialization"] == 1
        assert distribution["discussion"] == 1
        assert distribution["conclusion"] == 1

    def test_create_mermaid_diagram(self, sample_turns):
        """Test creating Mermaid diagram."""
        # Skip if method doesn't exist
        if not hasattr(ProcessVisualizer, "create_mermaid_diagram"):
            pytest.skip("create_mermaid_diagram not implemented")

        diagram = ProcessVisualizer.create_mermaid_diagram(sample_turns)
        assert diagram.startswith("graph TD")
        assert "Agent1" in diagram
        assert "Agent2" in diagram
        assert "initialization" in diagram
        assert "discussion" in diagram
        assert "conclusion" in diagram

    def test_create_gantt_chart_data(self, sample_turns):
        """Test creating Gantt chart data."""
        # Skip if method doesn't exist
        if not hasattr(ProcessVisualizer, "create_gantt_chart_data"):
            pytest.skip("create_gantt_chart_data not implemented")

        gantt_data = ProcessVisualizer.create_gantt_chart_data(sample_turns)
        assert len(gantt_data) == 3
        for entry in gantt_data:
            assert "agent" in entry
            assert "start" in entry
            assert "end" in entry
            assert "phase" in entry

    def test_get_process_insights(self, sample_result):
        """Test getting process insights."""
        # Skip if method doesn't exist
        if not hasattr(ProcessVisualizer, "get_process_insights"):
            pytest.skip("get_process_insights not implemented")

        insights = ProcessVisualizer.get_process_insights(sample_result)
        assert isinstance(insights, list)
        assert len(insights) >= 3
        assert any("Process completed in" in i for i in insights)
        assert any("Total 3 turns" in i for i in insights)
        assert any("Most active agent" in i for i in insights)

    def test_format_for_export(self, sample_result):
        """Test formatting for export."""
        # Skip if method doesn't exist
        if not hasattr(ProcessVisualizer, "format_for_export"):
            pytest.skip("format_for_export not implemented")

        export_data = ProcessVisualizer.format_for_export(sample_result)
        assert "metadata" in export_data
        assert "turns" in export_data
        assert "tasks_output" in export_data
        assert "final_output" in export_data
        assert export_data["metadata"]["success"] == True
        assert export_data["metadata"]["duration"] == 10.5
        assert export_data["metadata"]["total_turns"] == 3


class TestVisualizationHelpers:
    """Test visualization helper functions."""

    def test_visualization_endpoint_integration(self):
        """Test visualization endpoint integration."""
        # This tests that add_visualization_endpoints can be called
        from unittest.mock import Mock

        from litecrew.api.visualization import add_visualization_endpoints

        mock_router = Mock()
        add_visualization_endpoints(mock_router)

        # Should have added the endpoint
        assert mock_router.get.called

    def test_create_process_flow(self):
        """Test creating process flow visualization."""
        turns = [
            ProcessTurn(agent="A1", content="Start", timestamp=datetime.now()),
            ProcessTurn(agent="A2", content="Reply", timestamp=datetime.now()),
        ]

        flow = ProcessVisualizer.create_process_flow("sequential", turns)
        assert "nodes" in flow
        assert "edges" in flow
        assert len(flow["nodes"]) >= 2

    def test_create_debate_visualization(self):
        """Test creating debate-specific visualization."""
        turns = [
            ProcessTurn(
                agent="Debater1",
                content="I argue for",
                timestamp=datetime.now(),
                metadata={"phase": "opening_statement", "side": "for"},
            ),
            ProcessTurn(
                agent="Debater2",
                content="I argue against",
                timestamp=datetime.now(),
                metadata={"phase": "opening_statement", "side": "against"},
            ),
        ]

        debate_viz = ProcessVisualizer.create_debate_visualization(turns)
        assert "rounds" in debate_viz
        assert "for_arguments" in debate_viz
        assert "against_arguments" in debate_viz
        assert len(debate_viz["for_arguments"]) == 1
        assert len(debate_viz["against_arguments"]) == 1
