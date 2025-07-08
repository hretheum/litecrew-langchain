"""Tests for template analytics module."""

import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest

from litecrew.api.template_analytics import TemplateAnalytics, get_analytics


class TestTemplateAnalytics:
    """Test template analytics functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def analytics(self, temp_dir):
        """Create analytics instance with temp storage."""
        return TemplateAnalytics(storage_path=temp_dir)

    def test_init_creates_directory(self, temp_dir):
        """Test that initialization creates storage directory."""
        analytics = TemplateAnalytics(storage_path=temp_dir)
        assert os.path.exists(temp_dir)
        assert analytics.storage_path == temp_dir

    def test_init_with_default_path(self):
        """Test initialization with default path."""
        analytics = TemplateAnalytics()
        assert analytics.storage_path.endswith(".litecrew/analytics")

    def test_load_empty_usage_data(self, analytics):
        """Test loading when no data exists."""
        assert analytics.usage_data == {"usage_events": [], "aggregated": {}}

    def test_load_existing_usage_data(self, temp_dir):
        """Test loading existing usage data."""
        # Create existing data
        usage_file = os.path.join(temp_dir, "template_usage.json")
        test_data = {
            "usage_events": [{"template": "test", "timestamp": "2024-01-01"}],
            "aggregated": {"test": 1},
        }
        with open(usage_file, "w") as f:
            json.dump(test_data, f)

        # Load it
        analytics = TemplateAnalytics(storage_path=temp_dir)
        assert analytics.usage_data == test_data

    def test_load_corrupted_data(self, temp_dir):
        """Test loading corrupted data falls back to empty."""
        # Create corrupted file
        usage_file = os.path.join(temp_dir, "template_usage.json")
        with open(usage_file, "w") as f:
            f.write("not valid json")

        # Should fall back to empty
        analytics = TemplateAnalytics(storage_path=temp_dir)
        assert analytics.usage_data == {"usage_events": [], "aggregated": {}}

    def test_save_usage_data(self, analytics):
        """Test saving usage data."""
        analytics.usage_data = {
            "usage_events": [{"test": "event"}],
            "aggregated": {"count": 1},
        }
        analytics.save_usage_data()

        # Verify saved
        with open(analytics.usage_file, "r") as f:
            saved_data = json.load(f)
        assert saved_data == analytics.usage_data

    def test_track_template_usage_basic(self, analytics):
        """Test basic template usage tracking."""
        analytics.track_template_usage(
            template_name="research_team", success=True, execution_time=5.2
        )

        # Check event was added
        assert len(analytics.usage_data["usage_events"]) == 1
        event = analytics.usage_data["usage_events"][0]
        assert event["template_name"] == "research_team"
        assert event["success"] is True
        assert event["execution_time"] == 5.2
        assert "timestamp" in event

    def test_track_template_usage_with_metadata(self, analytics):
        """Test tracking with full metadata."""
        analytics.track_template_usage(
            template_name="research_team",
            scenario_id="scenario_1",
            user_id="user123",
            success=False,
            execution_time=10.5,
            metadata={"error": "timeout", "retries": 3},
        )

        event = analytics.usage_data["usage_events"][0]
        assert event["scenario_id"] == "scenario_1"
        assert event["user_id"] == "user123"
        assert event["success"] is False
        assert event["metadata"]["error"] == "timeout"
        assert event["metadata"]["retries"] == 3

    def test_get_usage_stats(self, analytics):
        """Test getting usage statistics."""
        # Add some usage data
        for i in range(5):
            analytics.track_template_usage("template_a", success=True)
        for i in range(3):
            analytics.track_template_usage("template_b", success=i < 2)

        stats = analytics.get_usage_stats()
        assert stats["total_usage"] == 8
        assert stats["unique_templates"] == 2
        assert stats["success_rate"] == 7 / 8
        assert stats["template_counts"]["template_a"] == 5
        assert stats["template_counts"]["template_b"] == 3

    def test_get_usage_stats_empty(self, analytics):
        """Test getting stats with no data."""
        stats = analytics.get_usage_stats()
        assert stats["total_usage"] == 0
        assert stats["unique_templates"] == 0
        assert stats["success_rate"] == 0
        assert stats["template_counts"] == {}

    def test_get_template_stats(self, analytics):
        """Test getting stats for specific template."""
        # Add usage data
        analytics.track_template_usage(
            "research_team", success=True, execution_time=5.0
        )
        analytics.track_template_usage(
            "research_team", success=True, execution_time=7.0
        )
        analytics.track_template_usage(
            "research_team", success=False, execution_time=10.0
        )
        analytics.track_template_usage("other_team", success=True)

        stats = analytics.get_template_stats("research_team")
        assert stats["total_usage"] == 3
        assert stats["success_rate"] == round((2 / 3) * 100, 1)  # 66.7%
        assert stats["avg_execution_time"] == round((5.0 + 7.0 + 10.0) / 3, 2)
        assert "recent_usage_count" in stats

    def test_get_template_stats_nonexistent(self, analytics):
        """Test getting stats for nonexistent template."""
        stats = analytics.get_template_stats("nonexistent")
        assert stats["total_usage"] == 0
        assert stats["template_name"] == "nonexistent"

    def test_get_popular_templates(self, analytics):
        """Test getting popular templates."""
        # Add usage data
        for _ in range(10):
            analytics.track_template_usage("popular")
        for _ in range(5):
            analytics.track_template_usage("medium")
        for _ in range(2):
            analytics.track_template_usage("rare")

        popular = analytics.get_popular_templates(limit=2)
        assert len(popular) == 2
        assert popular[0]["template_name"] == "popular"
        assert popular[0]["usage_count"] == 10
        assert popular[1]["template_name"] == "medium"
        assert popular[1]["usage_count"] == 5

    def test_get_recent_usage(self, analytics):
        """Test getting recent usage."""
        # Add some events
        for i in range(5):
            analytics.track_template_usage(f"template_{i}")

        recent = analytics.get_recent_usage(limit=3)
        assert len(recent) == 3
        # Should be in reverse chronological order
        assert recent[0]["template_name"] == "template_4"

    def test_cleanup_old_events(self, analytics):
        """Test cleanup of old events."""
        # Add old event manually
        old_event = {
            "template_name": "old",
            "timestamp": (datetime.now() - timedelta(days=40)).isoformat(),
            "success": True,
            "execution_time": None,
            "scenario_id": None,
            "error": None,
        }
        recent_event = {
            "template_name": "recent",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "execution_time": None,
            "scenario_id": None,
            "error": None,
        }
        analytics.usage_data["usage_events"] = [old_event, recent_event]

        # Clean up events older than 30 days
        analytics.cleanup_old_events(days=30)

        assert len(analytics.usage_data["usage_events"]) == 1
        assert analytics.usage_data["usage_events"][0]["template_name"] == "recent"

    def test_export_analytics_report(self, analytics, temp_dir):
        """Test exporting analytics report."""
        # Add some data
        analytics.track_template_usage("template_a", success=True)
        analytics.track_template_usage("template_b", success=False)

        # Export report as JSON
        report = analytics.export_analytics_report(format="json")

        assert isinstance(report, dict)
        assert "generated_at" in report
        assert "summary" in report
        assert "popular_templates" in report
        assert report["summary"]["total_usage"] == 2
        
        # Test markdown export
        markdown_report = analytics.export_analytics_report(format="markdown")
        assert isinstance(markdown_report, str)
        assert "# Template Analytics Report" in markdown_report

    def test_get_analytics_singleton(self):
        """Test get_analytics returns singleton."""
        analytics1 = get_analytics()
        analytics2 = get_analytics()
        assert analytics1 is analytics2

    def test_track_scenario_usage(self, analytics):
        """Test tracking scenario-specific usage."""
        analytics.track_template_usage(
            template_name="research_team", scenario_id="deep_research", success=True
        )
        analytics.track_template_usage(
            template_name="research_team", scenario_id="quick_research", success=True
        )

        # Should track both separately
        events = analytics.usage_data["usage_events"]
        assert len(events) == 2
        assert events[0]["scenario_id"] == "deep_research"
        assert events[1]["scenario_id"] == "quick_research"
