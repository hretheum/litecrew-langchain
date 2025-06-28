# validate_monitoring.py
import requests
import sqlite3
import time
import psutil

def test_metrics_collection():
    """Test metrics are being collected"""
    db_path = "/opt/litecrewai/data/metrics.db"
    
    # Wait for some metrics to be collected
    time.sleep(65)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if metrics exist
    cursor.execute("SELECT COUNT(*) FROM metrics WHERE timestamp > datetime('now', '-2 minutes')")
    count = cursor.fetchone()[0]
    assert count > 0, "No recent metrics found"
    
    # Check metric types
    cursor.execute("SELECT DISTINCT metric_name FROM metrics")
    metrics = [row[0] for row in cursor.fetchall()]
    
    required_metrics = ["cpu_usage", "memory_usage", "disk_usage", "api_requests"]
    for metric in required_metrics:
        assert metric in metrics, f"Missing metric: {metric}"
    
    conn.close()
    print("✅ Metrics collection validated")

def test_health_endpoints():
    """Test health check endpoints"""
    base_url = "http://localhost:8000"
    
    # Basic health
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # Detailed health
    response = requests.get(f"{base_url}/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "redis" in data
    assert "ollama" in data
    
    # Metrics endpoint
    response = requests.get(f"{base_url}/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text  # Prometheus format
    
    print("✅ Health endpoints validated")

def test_dashboard():
    """Test monitoring dashboard"""
    response = requests.get("http://localhost:8000/dashboard")
    assert response.status_code == 200
    
    # Check for key elements
    html = response.text
    assert "System Metrics" in html
    assert "API Performance" in html
    assert "Cost Tracking" in html
    
    # Test it loads fast
    start = time.time()
    response = requests.get("http://localhost:8000/dashboard")
    load_time = time.time() - start
    assert load_time < 1.0, f"Dashboard too slow: {load_time:.2f}s"
    
    print("✅ Dashboard validated")

def test_alerting():
    """Test alert system"""
    # Trigger test alert
    response = requests.post("http://localhost:8000/api/test-alert")
    assert response.status_code == 200
    
    # Check alert was logged
    with open("/opt/litecrewai/logs/alerts.log", "r") as f:
        content = f.read()
        assert "TEST_ALERT" in content
    
    print("✅ Alerting system validated")

if __name__ == "__main__":
    test_metrics_collection()
    test_health_endpoints()
    test_dashboard()
    test_alerting()
    print("✅ All monitoring checks passed!")