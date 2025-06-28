#!/usr/bin/env python3
"""
Validate logging system setup for LiteCrewAI
"""

import os
import sys
import json
import time
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


def check_log_directory():
    """Check if log directory exists with proper permissions"""
    log_dir = Path("/opt/litecrewai/logs")
    
    if not log_dir.exists():
        print_status("Log directory exists", "FAIL")
        print(f"  Create with: sudo mkdir -p {log_dir}")
        return False
    
    print_status("Log directory exists", "PASS")
    
    # Check permissions
    stat_info = log_dir.stat()
    if oct(stat_info.st_mode)[-3:] == "755":
        print_status("Log directory permissions (755)", "PASS")
    else:
        print_status("Log directory permissions", "FAIL")
        print(f"  Fix with: sudo chmod 755 {log_dir}")
        return False
    
    return True


def check_log_files():
    """Check if log files are being created"""
    log_dir = Path("/opt/litecrewai/logs")
    expected_files = ["app.log", "api.log", "llm.log", "error.log"]
    
    all_exist = True
    for log_file in expected_files:
        log_path = log_dir / log_file
        if log_path.exists():
            print_status(f"Log file {log_file} exists", "PASS")
        else:
            print_status(f"Log file {log_file} exists", "FAIL")
            all_exist = False
    
    return all_exist


def check_json_format():
    """Check if logs are in proper JSON format"""
    log_path = Path("/opt/litecrewai/logs/app.log")
    
    if not log_path.exists():
        print_status("JSON format validation", "FAIL")
        print("  No app.log file to validate")
        return False
    
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if not lines:
                print_status("JSON format validation", "FAIL")
                print("  Log file is empty")
                return False
            
            # Check last few lines
            valid_json = True
            for line in lines[-5:]:
                try:
                    log_entry = json.loads(line.strip())
                    # Check required fields
                    required_fields = ["timestamp", "level", "logger", "message"]
                    for field in required_fields:
                        if field not in log_entry:
                            valid_json = False
                            break
                except json.JSONDecodeError:
                    valid_json = False
                    break
            
            if valid_json:
                print_status("JSON format validation", "PASS")
                return True
            else:
                print_status("JSON format validation", "FAIL")
                print("  Logs are not in valid JSON format")
                return False
                
    except Exception as e:
        print_status("JSON format validation", "FAIL")
        print(f"  Error reading log file: {e}")
        return False


def check_logrotate():
    """Check if logrotate is configured"""
    logrotate_config = Path("/etc/logrotate.d/litecrewai")
    
    if logrotate_config.exists():
        print_status("Logrotate configuration exists", "PASS")
        
        # Check configuration content
        with open(logrotate_config, "r") as f:
            content = f.read()
            
        required_settings = ["daily", "rotate 30", "compress", "maxsize 100M"]
        all_present = all(setting in content for setting in required_settings)
        
        if all_present:
            print_status("Logrotate settings correct", "PASS")
            return True
        else:
            print_status("Logrotate settings correct", "FAIL")
            print("  Missing required settings")
            return False
    else:
        print_status("Logrotate configuration exists", "FAIL")
        print("  Run: sudo /opt/litecrewai/scripts/setup_logrotate.sh")
        return False


def check_logging_functionality():
    """Test actual logging functionality"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, "/opt/litecrewai/app")
        
        from app.core.logging import setup_logging, get_logger
        from app.core.logger_wrapper import LiteCrewAILogger
        
        # Setup logging
        setup_logging(log_dir="/opt/litecrewai/logs")
        
        # Test logging
        logger = LiteCrewAILogger("validation_test")
        
        # Log test message
        test_id = f"test-{int(time.time())}"
        logger.logger.info(f"Validation test message {test_id}")
        
        # Give it a moment to write
        time.sleep(0.1)
        
        # Check if message was written
        log_path = Path("/opt/litecrewai/logs/app.log")
        with open(log_path, "r") as f:
            content = f.read()
            if test_id in content:
                print_status("Logging functionality test", "PASS")
                return True
            else:
                print_status("Logging functionality test", "FAIL")
                print("  Test message not found in logs")
                return False
                
    except ImportError:
        print_status("Logging functionality test", "FAIL")
        print("  Could not import logging modules")
        return False
    except Exception as e:
        print_status("Logging functionality test", "FAIL")
        print(f"  Error during test: {e}")
        return False


def check_dashboard():
    """Check if log dashboard script exists and is executable"""
    dashboard_path = Path("/opt/litecrewai/scripts/log_dashboard.py")
    
    if dashboard_path.exists():
        print_status("Log dashboard script exists", "PASS")
        
        # Check if executable
        if os.access(dashboard_path, os.X_OK):
            print_status("Log dashboard is executable", "PASS")
            return True
        else:
            print_status("Log dashboard is executable", "FAIL")
            print(f"  Fix with: chmod +x {dashboard_path}")
            return False
    else:
        print_status("Log dashboard script exists", "FAIL")
        return False


def main():
    """Run all validation checks"""
    print(f"\n{GREEN}=== LiteCrewAI Logging System Validation ==={NC}\n")
    
    checks = [
        ("Log Directory", check_log_directory),
        ("Log Files", check_log_files),
        ("JSON Format", check_json_format),
        ("Logrotate", check_logrotate),
        ("Logging Functionality", check_logging_functionality),
        ("Dashboard", check_dashboard),
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
        return 1


if __name__ == "__main__":
    sys.exit(main())