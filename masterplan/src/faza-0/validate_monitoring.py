#!/usr/bin/env python3
"""
Validate monitoring system setup for LiteCrewAI
"""

import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_status(message, status):
    """Print status message with color"""
    color = GREEN if status == "PASS" else RED
    symbol = "✓" if status == "PASS" else "✗"
    print(f"{color}{symbol} {message}{NC}")


def check_metrics_database():
    """Check if metrics database exists"""
    db_path = Path("/opt/litecrewai/data/metrics.db")
    
    if db_path.exists():
        print_status("Metrics database exists", "PASS")
        
        # Check size
        size_mb = db_path.stat().st_size / 1024 / 1024
        print(f"  Database size: {size_mb:.2f} MB")
        
        # Check if writable
        try:
            db_path.touch()
            print_status("Database is writable", "PASS")
            return True
        except Exception:
            print_status("Database is writable", "FAIL")
            return False
    else:
        print_status("Metrics database exists", "FAIL")
        print(f"  Database will be created on first run")
        return True  # Not a critical failure


def check_metrics_collection():
    """Check if metrics are being collected"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, "/opt/litecrewai/app")
        
        from app.core.metrics_storage import MetricsStorage
        
        storage = MetricsStorage()
        
        # Record test metric
        test_value = 42.0
        storage.record_metric("test.validation", test_value)
        
        # Read it back
        metrics = storage.get_metrics("test.validation")
        
        if metrics and metrics[-1]["metric_value"] == test_value:
            print_status("Metrics storage working", "PASS")
            return True
        else:
            print_status("Metrics storage working", "FAIL")
            return False
            
    except Exception as e:
        print_status("Metrics storage working", "FAIL")
        print(f"  Error: {e}")
        return False


def check_health_endpoints(base_url="http://localhost:8000"):
    """Check if health endpoints are responding"""
    endpoints = [
        ("/health", "Basic health check"),
        ("/health/detailed", "Detailed health check"),
        ("/metrics", "Prometheus metrics"),
    ]
    
    all_pass = True
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_status(f"{description} ({endpoint})", "PASS")
            else:
                print_status(f"{description} ({endpoint})", "FAIL")
                print(f"  Status code: {response.status_code}")
                all_pass = False
        except requests.exceptions.ConnectionError:
            print_status(f"{description} ({endpoint})", "FAIL")
            print(f"  Could not connect to {base_url}")
            all_pass = False
        except Exception as e:
            print_status(f"{description} ({endpoint})", "FAIL")
            print(f"  Error: {e}")
            all_pass = False
    
    return all_pass


def check_dashboard(base_url="http://localhost:8000"):
    """Check if dashboard is accessible"""
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        if response.status_code == 200 and "LiteCrewAI" in response.text:
            print_status("Dashboard accessible", "PASS")
            
            # Check if htmx is loaded
            if "htmx.org" in response.text:
                print_status("Dashboard has htmx loaded", "PASS")
                return True
            else:
                print_status("Dashboard has htmx loaded", "FAIL")
                return False
        else:
            print_status("Dashboard accessible", "FAIL")
            print(f"  Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_status("Dashboard accessible", "FAIL")
        print(f"  Error: {e}")
        return False


def check_metrics_aggregation():
    """Check if metrics aggregation is set up"""
    # Check if aggregation script exists
    script_path = Path("/opt/litecrewai/scripts/aggregate_metrics.py")
    
    if script_path.exists():
        print_status("Aggregation script exists", "PASS")
        
        # Check if executable
        if os.access(script_path, os.X_OK):
            print_status("Aggregation script is executable", "PASS")
        else:
            print_status("Aggregation script is executable", "FAIL")
            print(f"  Fix with: chmod +x {script_path}")
            return False
            
        # Check systemd timer
        try:
            import subprocess
            result = subprocess.run(
                ["systemctl", "is-active", "litecrewai-metrics-aggregation.timer"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and "active" in result.stdout:
                print_status("Aggregation timer is active", "PASS")
                return True
            else:
                print_status("Aggregation timer is active", "FAIL")
                print("  Timer not running or not installed")
                return False
                
        except Exception:
            print_status("Aggregation timer check", "FAIL")
            print("  Could not check systemd timer")
            return False
    else:
        print_status("Aggregation script exists", "FAIL")
        return False


def check_alert_system():
    """Check if alert system is configured"""
    try:
        sys.path.insert(0, "/opt/litecrewai/app")
        
        from app.core.alerts import AlertManager
        from app.core.metrics_storage import MetricsStorage
        
        storage = MetricsStorage()
        alert_manager = AlertManager(storage)
        
        # Check if rules are loaded
        if len(alert_manager.rules) > 0:
            print_status(f"Alert rules loaded ({len(alert_manager.rules)} rules)", "PASS")
            
            # List rules
            print("  Alert rules:")
            for rule in alert_manager.rules:
                print(f"    - {rule.name} ({rule.severity})")
            
            return True
        else:
            print_status("Alert rules loaded", "FAIL")
            return False
            
    except Exception as e:
        print_status("Alert system check", "FAIL")
        print(f"  Error: {e}")
        return False


def check_cost_tracking():
    """Check if cost tracking is working"""
    try:
        sys.path.insert(0, "/opt/litecrewai/app")
        
        from app.core.metrics import cost_tracker
        
        # Simulate some usage
        cost_tracker.add_usage("openai", "gpt-3.5-turbo", 100, 50)
        
        if cost_tracker.total_cost > 0:
            print_status("Cost tracking functional", "PASS")
            print(f"  Total cost tracked: ${cost_tracker.total_cost:.4f}")
            return True
        else:
            print_status("Cost tracking functional", "FAIL")
            return False
            
    except Exception as e:
        print_status("Cost tracking check", "FAIL")
        print(f"  Error: {e}")
        return False


def main():
    """Run all validation checks"""
    print(f"\n{GREEN}=== LiteCrewAI Monitoring System Validation ==={NC}\n")
    
    checks = [
        ("Metrics Database", check_metrics_database),
        ("Metrics Collection", check_metrics_collection),
        ("Health Endpoints", check_health_endpoints),
        ("Dashboard", check_dashboard),
        ("Metrics Aggregation", check_metrics_aggregation),
        ("Alert System", check_alert_system),
        ("Cost Tracking", check_cost_tracking),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        results.append(check_func())
    
    # Summary
    print(f"\n{GREEN}=== Summary ==={NC}")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}All checks passed! ({passed}/{total}){NC}")
        return 0
    else:
        print(f"{RED}Some checks failed ({passed}/{total}){NC}")
        print("\nNote: Some checks may fail if the application is not running.")
        print("Start the app with: cd /opt/litecrewai && python -m app.main")
        return 1


if __name__ == "__main__":
    sys.exit(main())