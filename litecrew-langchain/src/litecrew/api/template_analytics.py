"""Template usage analytics and metrics."""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class TemplateAnalytics:
    """Track and analyze template usage patterns."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize analytics storage."""
        self.storage_path = storage_path or os.path.join(
            os.path.expanduser("~"), ".litecrew", "analytics"
        )
        os.makedirs(self.storage_path, exist_ok=True)
        self.usage_file = os.path.join(self.storage_path, "template_usage.json")
        self.load_usage_data()

    def load_usage_data(self) -> None:
        """Load usage data from storage."""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, "r") as f:
                    self.usage_data = json.load(f)
            except Exception:
                self.usage_data = {"usage_events": [], "aggregated": {}}
        else:
            self.usage_data = {"usage_events": [], "aggregated": {}}

    def save_usage_data(self) -> None:
        """Save usage data to storage."""
        try:
            with open(self.usage_file, "w") as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save analytics: {e}")

    def track_template_usage(
        self,
        template_name: str,
        scenario_id: Optional[str] = None,
        user_id: Optional[str] = None,
        success: bool = True,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track template usage event.

        Args:
            template_name: Name of the template used
            scenario_id: ID of specific scenario if used
            user_id: User identifier (optional)
            success: Whether the usage was successful
            execution_time: Time taken to execute
            metadata: Additional metadata
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "template_name": template_name,
            "scenario_id": scenario_id,
            "user_id": user_id,
            "success": success,
            "execution_time": execution_time,
            "metadata": metadata or {},
        }

        self.usage_data["usage_events"].append(event)
        self._update_aggregated_stats()
        self.save_usage_data()

    def _update_aggregated_stats(self) -> None:
        """Update aggregated statistics."""
        events = self.usage_data["usage_events"]

        # Template usage counts
        template_counts = Counter(event["template_name"] for event in events)

        # Success rates
        success_rates = {}
        for template in template_counts:
            template_events = [e for e in events if e["template_name"] == template]
            successes = sum(1 for e in template_events if e["success"])
            success_rates[template] = (successes / len(template_events)) * 100

        # Average execution times
        avg_execution_times = {}
        for template in template_counts:
            template_events = [
                e
                for e in events
                if e["template_name"] == template and e["execution_time"] is not None
            ]
            if template_events:
                avg_time = sum(e["execution_time"] for e in template_events) / len(
                    template_events
                )
                avg_execution_times[template] = avg_time

        # Recent usage (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = [
            e for e in events if datetime.fromisoformat(e["timestamp"]) > week_ago
        ]
        recent_counts = Counter(event["template_name"] for event in recent_events)

        self.usage_data["aggregated"] = {
            "total_usage": template_counts,
            "success_rates": success_rates,
            "avg_execution_times": avg_execution_times,
            "recent_usage": recent_counts,
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular templates by usage count."""
        aggregated = self.usage_data.get("aggregated", {})
        total_usage = aggregated.get("total_usage", {})
        success_rates = aggregated.get("success_rates", {})
        avg_times = aggregated.get("avg_execution_times", {})

        popular = []
        for template, count in total_usage.most_common(limit):
            popular.append(
                {
                    "template_name": template,
                    "usage_count": count,
                    "success_rate": round(success_rates.get(template, 0), 1),
                    "avg_execution_time": (
                        round(avg_times.get(template, 0), 2)
                        if avg_times.get(template)
                        else None
                    ),
                }
            )

        return popular

    def get_template_stats(self, template_name: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific template."""
        events = [
            e
            for e in self.usage_data["usage_events"]
            if e["template_name"] == template_name
        ]

        if not events:
            return {"template_name": template_name, "total_usage": 0}

        # Basic stats
        total_usage = len(events)
        successes = sum(1 for e in events if e["success"])
        success_rate = (successes / total_usage) * 100

        # Execution times
        execution_times = [
            e["execution_time"] for e in events if e["execution_time"] is not None
        ]
        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else None
        )

        # Usage over time (last 30 days, grouped by day)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_events = [
            e
            for e in events
            if datetime.fromisoformat(e["timestamp"]) > thirty_days_ago
        ]

        daily_usage = defaultdict(int)
        for event in recent_events:
            date = datetime.fromisoformat(event["timestamp"]).date().isoformat()
            daily_usage[date] += 1

        # Scenario usage (if applicable)
        scenario_usage = Counter(e["scenario_id"] for e in events if e["scenario_id"])

        return {
            "template_name": template_name,
            "total_usage": total_usage,
            "success_rate": round(success_rate, 1),
            "avg_execution_time": (
                round(avg_execution_time, 2) if avg_execution_time else None
            ),
            "daily_usage_last_30_days": dict(daily_usage),
            "scenario_usage": dict(scenario_usage),
            "recent_usage_count": len(recent_events),
        }

    def get_usage_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get usage trends over specified number of days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_events = [
            e
            for e in self.usage_data["usage_events"]
            if datetime.fromisoformat(e["timestamp"]) > cutoff_date
        ]

        # Group by day
        daily_success = defaultdict(int)
        daily_total = defaultdict(int)

        for event in recent_events:
            date = datetime.fromisoformat(event["timestamp"]).date().isoformat()
            daily_total[date] += 1
            if event["success"]:
                daily_success[date] += 1

        # Calculate daily success rates
        daily_success_rates = {}
        for date in daily_total:
            daily_success_rates[date] = (daily_success[date] / daily_total[date]) * 100

        # Template trends
        template_trends = defaultdict(lambda: defaultdict(int))
        for event in recent_events:
            date = datetime.fromisoformat(event["timestamp"]).date().isoformat()
            template_trends[event["template_name"]][date] += 1

        return {
            "period_days": days,
            "total_usage": len(recent_events),
            "daily_usage": dict(daily_total),
            "daily_success_rates": daily_success_rates,
            "template_trends": {k: dict(v) for k, v in template_trends.items()},
            "unique_templates_used": len(
                set(e["template_name"] for e in recent_events)
            ),
        }

    def generate_insights(self) -> List[str]:
        """Generate insights based on usage patterns."""
        insights = []

        aggregated = self.usage_data.get("aggregated", {})
        total_usage = aggregated.get("total_usage", {})
        success_rates = aggregated.get("success_rates", {})
        recent_usage = aggregated.get("recent_usage", {})

        if not total_usage:
            return ["No usage data available yet."]

        # Most popular template
        most_popular = max(total_usage, key=total_usage.get)
        insights.append(
            f"Most popular template: '{most_popular}' with {total_usage[most_popular]} uses"
        )

        # Highest success rate
        if success_rates:
            best_success = max(success_rates, key=success_rates.get)
            rate = success_rates[best_success]
            insights.append(
                f"Highest success rate: '{best_success}' with {rate:.1f}% success"
            )

        # Recent trend
        if recent_usage:
            trending = max(recent_usage, key=recent_usage.get)
            insights.append(
                f"Trending this week: '{trending}' with {recent_usage[trending]} recent uses"
            )

        # Template diversity
        total_templates = len(total_usage)
        total_uses = sum(total_usage.values())
        avg_uses_per_template = (
            total_uses / total_templates if total_templates > 0 else 0
        )
        insights.append(
            f"Template diversity: {total_templates} different templates used, averaging {avg_uses_per_template:.1f} uses each"
        )

        # Success rate insights
        if success_rates:
            avg_success_rate = sum(success_rates.values()) / len(success_rates)
            insights.append(f"Overall success rate: {avg_success_rate:.1f}%")

            low_success_templates = [
                t for t, rate in success_rates.items() if rate < 80
            ]
            if low_success_templates:
                insights.append(
                    f"Templates with low success rates: {', '.join(low_success_templates)}"
                )

        return insights


# Global instance
_analytics_instance: Optional[TemplateAnalytics] = None


def get_analytics() -> TemplateAnalytics:
    """Get the global analytics instance."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = TemplateAnalytics()
    return _analytics_instance
