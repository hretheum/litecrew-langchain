# validate_logging.py
import json
import os
import logging
import subprocess
from datetime import datetime

def test_log_structure():
    """Test log files structure"""
    log_files = [
        "/opt/litecrewai/logs/app.log",
        "/opt/litecrewai/logs/api.log", 
        "/opt/litecrewai/logs/llm.log",
        "/opt/litecrewai/logs/error.log"
    ]
    
    for log_file in log_files:
        # Create log directory if not exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Test writing
        logger = logging.getLogger(os.path.basename(log_file))
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        # Write test log
        test_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test log entry",
            "correlation_id": "test-123"
        }
        logger.info(json.dumps(test_entry))
        
        # Verify it's readable as JSON
        with open(log_file, 'r') as f:
            last_line = f.readlines()[-1]
            parsed = json.loads(last_line)
            assert parsed["correlation_id"] == "test-123"
    
    print("✅ Log structure validated")

def test_logrotate():
    """Test logrotate configuration"""
    config_path = "/etc/logrotate.d/litecrewai"
    assert os.path.exists(config_path), "Logrotate config not found"
    
    # Test configuration
    result = subprocess.run(["logrotate", "-d", config_path], capture_output=True, text=True)
    assert result.returncode == 0, f"Logrotate config invalid: {result.stderr}"
    
    print("✅ Logrotate configuration validated")

def test_log_dashboard():
    """Test log analysis dashboard"""
    dashboard_script = "/opt/litecrewai/scripts/log_dashboard.py"
    assert os.path.exists(dashboard_script), "Dashboard script not found"
    
    # Run dashboard in test mode
    result = subprocess.run([
        "/opt/litecrewai/venv/bin/python",
        dashboard_script,
        "--test"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Dashboard failed: {result.stderr}"
    assert "Error Rate:" in result.stdout
    assert "Performance:" in result.stdout
    
    print("✅ Log dashboard validated")

if __name__ == "__main__":
    test_log_structure()
    test_logrotate()
    test_log_dashboard()
    print("✅ All logging checks passed!")