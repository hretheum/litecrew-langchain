#!/usr/bin/env python3
"""
Simple log analysis dashboard for LiteCrewAI
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import argparse


class LogDashboard:
    """Simple terminal-based log dashboard"""

    def __init__(self, log_dir="/opt/litecrewai/logs"):
        self.log_dir = Path(log_dir)

    def parse_json_logs(self, log_file, hours=24):
        """Parse JSON logs from the last N hours"""
        logs = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        log_path = self.log_dir / log_file
        if not log_path.exists():
            return logs
            
        with open(log_path, "r") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_time = datetime.fromisoformat(
                        log_entry["timestamp"].replace("Z", "+00:00")
                    )
                    if log_time > cutoff_time:
                        logs.append(log_entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
                    
        return logs

    def print_header(self, title):
        """Print section header"""
        print(f"\n{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}\n")

    def show_error_summary(self, hours=24):
        """Show error summary"""
        self.print_header(f"ERROR SUMMARY (Last {hours} hours)")
        
        errors = self.parse_json_logs("error.log", hours)
        if not errors:
            print("No errors found! 🎉")
            return
            
        # Group by level
        levels = Counter(e.get("level", "UNKNOWN") for e in errors)
        print("Errors by Level:")
        for level, count in levels.most_common():
            print(f"  {level:10} {count:5} errors")
            
        # Group by module
        print("\nTop Error Sources:")
        modules = Counter(e.get("module", "unknown") for e in errors)
        for module, count in modules.most_common(5):
            print(f"  {module:20} {count:5} errors")
            
        # Recent errors
        print("\nMost Recent Errors:")
        for error in errors[-5:]:
            timestamp = error.get("timestamp", "")
            message = error.get("message", "")[:50]
            print(f"  [{timestamp}] {message}...")

    def show_performance_metrics(self, hours=24):
        """Show performance metrics"""
        self.print_header(f"PERFORMANCE METRICS (Last {hours} hours)")
        
        app_logs = self.parse_json_logs("app.log", hours)
        api_logs = self.parse_json_logs("api.log", hours)
        
        # Extract durations
        durations = []
        for log in app_logs + api_logs:
            extra = log.get("extra_fields", {})
            if "duration_seconds" in extra:
                durations.append(extra["duration_seconds"])
                
        if not durations:
            print("No performance data available")
            return
            
        durations.sort()
        
        print(f"Total Requests: {len(durations)}")
        print(f"Average Response Time: {sum(durations)/len(durations):.3f}s")
        print(f"Median Response Time: {durations[len(durations)//2]:.3f}s")
        print(f"95th Percentile: {durations[int(len(durations)*0.95)]:.3f}s")
        print(f"99th Percentile: {durations[int(len(durations)*0.99)]:.3f}s")
        
        # Request rate
        if app_logs:
            time_span = (
                datetime.fromisoformat(app_logs[-1]["timestamp"].replace("Z", "+00:00")) -
                datetime.fromisoformat(app_logs[0]["timestamp"].replace("Z", "+00:00"))
            ).total_seconds() / 3600
            if time_span > 0:
                print(f"\nRequest Rate: {len(app_logs)/time_span:.1f} req/hour")

    def show_llm_usage(self, hours=24):
        """Show LLM usage statistics"""
        self.print_header(f"LLM USAGE STATS (Last {hours} hours)")
        
        llm_logs = self.parse_json_logs("llm.log", hours)
        if not llm_logs:
            print("No LLM usage data available")
            return
            
        # Token usage
        total_tokens = 0
        model_usage = defaultdict(lambda: {"count": 0, "tokens": 0})
        
        for log in llm_logs:
            extra = log.get("extra_fields", {})
            model = extra.get("model", "unknown")
            tokens = extra.get("total_tokens", 0)
            
            total_tokens += tokens
            model_usage[model]["count"] += 1
            model_usage[model]["tokens"] += tokens
            
        print(f"Total Tokens Used: {total_tokens:,}")
        print("\nUsage by Model:")
        for model, stats in sorted(model_usage.items()):
            print(f"  {model:20} {stats['count']:5} calls, {stats['tokens']:8,} tokens")
            
        # Estimated costs
        print("\nEstimated Costs:")
        print("  (Based on typical pricing - adjust as needed)")
        cost_estimate = total_tokens * 0.00002  # Example rate
        print(f"  Total: ${cost_estimate:.2f}")

    def show_system_health(self):
        """Show overall system health"""
        self.print_header("SYSTEM HEALTH CHECK")
        
        # Check if logs are being written
        log_files = ["app.log", "api.log", "llm.log", "error.log"]
        
        print("Log File Status:")
        for log_file in log_files:
            log_path = self.log_dir / log_file
            if log_path.exists():
                # Get last modified time
                mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
                age = datetime.now() - mtime
                size_mb = log_path.stat().st_size / 1024 / 1024
                
                status = "✓" if age.total_seconds() < 3600 else "⚠"
                print(f"  {status} {log_file:15} Size: {size_mb:6.1f}MB, Last update: {age.total_seconds()/60:.0f}m ago")
            else:
                print(f"  ✗ {log_file:15} NOT FOUND")
                
        # Check for critical errors in last hour
        recent_errors = self.parse_json_logs("error.log", 1)
        critical_errors = [e for e in recent_errors if e.get("level") in ["ERROR", "CRITICAL"]]
        
        print(f"\nCritical Errors (Last Hour): {len(critical_errors)}")
        if critical_errors:
            print("  ⚠️  ATTENTION: Critical errors detected!")

    def run(self, hours=24):
        """Run the dashboard"""
        print("\n" + "="*60)
        print(f"{'LITECREWAI LOG DASHBOARD':^60}")
        print(f"{'Generated at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^60}")
        print("="*60)
        
        self.show_system_health()
        self.show_error_summary(hours)
        self.show_performance_metrics(hours)
        self.show_llm_usage(hours)
        
        print("\n" + "="*60)
        print(f"{'END OF REPORT':^60}")
        print("="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LiteCrewAI Log Dashboard")
    parser.add_argument(
        "--hours", 
        type=int, 
        default=24,
        help="Number of hours to analyze (default: 24)"
    )
    parser.add_argument(
        "--log-dir",
        default="/opt/litecrewai/logs",
        help="Log directory path"
    )
    
    args = parser.parse_args()
    
    dashboard = LogDashboard(args.log_dir)
    dashboard.run(args.hours)