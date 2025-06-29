"""
LiteCrewAI Monitoring Dashboard
Simple monitoring dashboard using FastAPI and HTMX
"""
import os
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Create monitoring app
monitoring_app = FastAPI(title="LiteCrewAI Monitoring", version="0.1.0")

# Templates and static files
templates = Jinja2Templates(directory="app/monitoring/templates")

class SystemMetrics(BaseModel):
    """System metrics model"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float

class ApplicationMetrics(BaseModel):
    """Application metrics model"""
    timestamp: datetime
    active_agents: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    requests_per_minute: int
    average_response_time: float

class MonitoringService:
    """Core monitoring service"""
    
    def __init__(self, metrics_file: str = "/tmp/litecrewai_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_history: List[Dict] = []
        self.load_metrics()
    
    def load_metrics(self):
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics_history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.metrics_history = []
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, default=str)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_total_mb=memory.total / (1024 * 1024),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_total_gb=disk.total / (1024 * 1024 * 1024)
        )
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect current application metrics"""
        # Mock application metrics - in real implementation,
        # these would come from the actual application
        return ApplicationMetrics(
            timestamp=datetime.now(),
            active_agents=self._get_active_agents(),
            active_tasks=self._get_active_tasks(),
            completed_tasks=self._get_completed_tasks(),
            failed_tasks=self._get_failed_tasks(),
            requests_per_minute=self._get_requests_per_minute(),
            average_response_time=self._get_average_response_time()
        )
    
    def _get_active_agents(self) -> int:
        """Get number of active agents"""
        # Mock implementation
        return len([p for p in psutil.process_iter() if 'litecrewai' in p.name()])
    
    def _get_active_tasks(self) -> int:
        """Get number of active tasks"""
        # Mock implementation - would query task queue
        return 3
    
    def _get_completed_tasks(self) -> int:
        """Get number of completed tasks"""
        # Mock implementation - would query database
        return 47
    
    def _get_failed_tasks(self) -> int:
        """Get number of failed tasks"""
        # Mock implementation - would query database
        return 2
    
    def _get_requests_per_minute(self) -> int:
        """Get requests per minute"""
        # Mock implementation - would calculate from request logs
        return 15
    
    def _get_average_response_time(self) -> float:
        """Get average response time in seconds"""
        # Mock implementation - would calculate from response logs
        return 0.85
    
    def record_metrics(self):
        """Record current metrics"""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        
        metrics_entry = {
            "timestamp": datetime.now().isoformat(),
            "system": system_metrics.dict(),
            "application": app_metrics.dict()
        }
        
        self.metrics_history.append(metrics_entry)
        self.save_metrics()
    
    def get_latest_metrics(self) -> Dict:
        """Get latest metrics"""
        if not self.metrics_history:
            self.record_metrics()
        
        return self.metrics_history[-1] if self.metrics_history else {}
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = []
        for entry in self.metrics_history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff_time:
                    filtered_metrics.append(entry)
            except (ValueError, KeyError):
                continue
        
        return filtered_metrics
    
    def get_health_status(self) -> Dict:
        """Get overall health status"""
        latest = self.get_latest_metrics()
        
        if not latest:
            return {"status": "unknown", "message": "No metrics available"}
        
        system = latest.get("system", {})
        app = latest.get("application", {})
        
        # Determine health based on thresholds
        issues = []
        
        if system.get("cpu_percent", 0) > 80:
            issues.append("High CPU usage")
        
        if system.get("memory_percent", 0) > 85:
            issues.append("High memory usage")
        
        if system.get("disk_percent", 0) > 90:
            issues.append("Low disk space")
        
        if app.get("failed_tasks", 0) > app.get("completed_tasks", 1) * 0.1:
            issues.append("High task failure rate")
        
        if app.get("average_response_time", 0) > 5.0:
            issues.append("Slow response times")
        
        if not issues:
            return {"status": "healthy", "message": "All systems operational"}
        elif len(issues) <= 2:
            return {"status": "degraded", "message": f"Issues: {', '.join(issues)}"}
        else:
            return {"status": "unhealthy", "message": f"Multiple issues: {', '.join(issues)}"}

# Global monitoring service instance
monitoring_service = MonitoringService()

@monitoring_app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "LiteCrewAI Monitoring Dashboard"
    })

@monitoring_app.get("/api/health")
async def get_health():
    """Health check endpoint"""
    health = monitoring_service.get_health_status()
    return JSONResponse(content=health)

@monitoring_app.get("/api/metrics/latest")
async def get_latest_metrics():
    """Get latest metrics"""
    metrics = monitoring_service.get_latest_metrics()
    return JSONResponse(content=metrics)

@monitoring_app.get("/api/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get metrics history"""
    if hours < 1 or hours > 168:  # Max 1 week
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")
    
    history = monitoring_service.get_metrics_history(hours)
    return JSONResponse(content=history)

@monitoring_app.post("/api/metrics/record")
async def record_current_metrics():
    """Record current metrics"""
    monitoring_service.record_metrics()
    return JSONResponse(content={"status": "recorded", "timestamp": datetime.now().isoformat()})

@monitoring_app.get("/api/system/info")
async def get_system_info():
    """Get system information"""
    return JSONResponse(content={
        "hostname": os.uname().nodename,
        "platform": os.uname().sysname,
        "architecture": os.uname().machine,
        "python_version": os.sys.version,
        "uptime": time.time() - psutil.boot_time(),
        "cpu_count": psutil.cpu_count(),
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
    })

@monitoring_app.get("/api/alerts")
async def get_alerts():
    """Get current alerts"""
    health = monitoring_service.get_health_status()
    latest_metrics = monitoring_service.get_latest_metrics()
    
    alerts = []
    
    if health["status"] != "healthy":
        alerts.append({
            "severity": "warning" if health["status"] == "degraded" else "critical",
            "message": health["message"],
            "timestamp": datetime.now().isoformat(),
            "category": "system"
        })
    
    # Add specific alerts based on metrics
    if latest_metrics:
        system = latest_metrics.get("system", {})
        
        if system.get("memory_percent", 0) > 90:
            alerts.append({
                "severity": "critical",
                "message": f"Memory usage critical: {system['memory_percent']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "category": "memory"
            })
        
        if system.get("disk_percent", 0) > 95:
            alerts.append({
                "severity": "critical",
                "message": f"Disk space critical: {system['disk_percent']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "category": "disk"
            })
    
    return JSONResponse(content=alerts)

# Auto-record metrics every minute (this would be better as a background task)
import threading

def metrics_collector():
    """Background metrics collection"""
    while True:
        try:
            monitoring_service.record_metrics()
            time.sleep(60)  # Record every minute
        except Exception as e:
            print(f"Error in metrics collection: {e}")
            time.sleep(60)

# Start background metrics collection
metrics_thread = threading.Thread(target=metrics_collector, daemon=True)
metrics_thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(monitoring_app, host="0.0.0.0", port=8001)