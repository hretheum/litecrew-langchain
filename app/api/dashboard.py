"""
Simple monitoring dashboard using FastAPI and htmx
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from typing import Optional
import json

from app.core.metrics_storage import MetricsStorage
from app.core.metrics import metrics_collector, cost_tracker
from app.core.logging import LogAnalyzer

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Initialize storage
metrics_storage = MetricsStorage()

# HTML template with htmx
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LiteCrewAI Dashboard</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }
        .label {
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
        }
        .status-healthy {
            color: #27ae60;
        }
        .status-warning {
            color: #f39c12;
        }
        .status-error {
            color: #e74c3c;
        }
        .chart {
            height: 200px;
            margin-top: 10px;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
            padding: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        th {
            background: #ecf0f1;
        }
        .refresh-info {
            text-align: right;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LiteCrewAI Monitoring Dashboard</h1>
            <div class="refresh-info">
                Auto-refresh every 5 seconds
                <span hx-get="/dashboard/refresh-time" hx-trigger="every 5s" hx-swap="innerHTML">
                    Last update: <span id="last-update">{{ current_time }}</span>
                </span>
            </div>
        </div>
        
        <div class="grid">
            <!-- System Health -->
            <div class="card" hx-get="/dashboard/system-health" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading system health...
            </div>
            
            <!-- Request Metrics -->
            <div class="card" hx-get="/dashboard/request-metrics" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading request metrics...
            </div>
            
            <!-- LLM Usage -->
            <div class="card" hx-get="/dashboard/llm-usage" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading LLM usage...
            </div>
            
            <!-- Cost Tracking -->
            <div class="card" hx-get="/dashboard/cost-tracking" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading cost data...
            </div>
            
            <!-- Active Alerts -->
            <div class="card" hx-get="/dashboard/alerts" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading alerts...
            </div>
            
            <!-- Recent Errors -->
            <div class="card" hx-get="/dashboard/recent-errors" hx-trigger="load, every 5s" hx-swap="innerHTML">
                Loading error log...
            </div>
        </div>
    </div>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return DASHBOARD_HTML.replace("{{ current_time }}", datetime.now().strftime("%H:%M:%S"))


@router.get("/refresh-time", response_class=HTMLResponse)
async def refresh_time():
    """Get current time for refresh indicator"""
    return f'Last update: <span id="last-update">{datetime.now().strftime("%H:%M:%S")}</span>'


@router.get("/system-health", response_class=HTMLResponse)
async def system_health():
    """System health widget"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Determine health status
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
            status = "warning"
        else:
            status = "healthy"
        
        html = f"""
        <h3>System Health</h3>
        <div class="metric status-{status}">
            {status.upper()}
        </div>
        <table>
            <tr>
                <td>CPU Usage</td>
                <td>{cpu_percent:.1f}%</td>
            </tr>
            <tr>
                <td>Memory Usage</td>
                <td>{memory.percent:.1f}% ({memory.used / 1024 / 1024 / 1024:.1f}GB / {memory.total / 1024 / 1024 / 1024:.1f}GB)</td>
            </tr>
            <tr>
                <td>Disk Usage</td>
                <td>{disk.percent:.1f}% ({disk.used / 1024 / 1024 / 1024:.1f}GB / {disk.total / 1024 / 1024 / 1024:.1f}GB)</td>
            </tr>
            <tr>
                <td>Uptime</td>
                <td>{(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).days} days</td>
            </tr>
        </table>
        """
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading system health: {str(e)}</div>'


@router.get("/request-metrics", response_class=HTMLResponse)
async def request_metrics():
    """Request metrics widget"""
    try:
        # Get metrics from last hour
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        metrics = metrics_storage.get_metrics(
            "http.request.duration_seconds",
            start_time=start_time,
            end_time=end_time,
            interval="5min"
        )
        
        total_requests = sum(m.get("count", 0) for m in metrics)
        avg_duration = sum(m.get("avg", 0) for m in metrics) / len(metrics) if metrics else 0
        
        html = f"""
        <h3>Request Metrics (1h)</h3>
        <div class="label">Total Requests</div>
        <div class="metric">{total_requests}</div>
        <div class="label">Average Response Time</div>
        <div class="metric">{avg_duration:.3f}s</div>
        <div class="chart">
            <small>Response time trend (5min buckets)</small>
            <!-- Simple ASCII chart -->
            <pre>{generate_ascii_chart(metrics)}</pre>
        </div>
        """
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading request metrics: {str(e)}</div>'


@router.get("/llm-usage", response_class=HTMLResponse)
async def llm_usage():
    """LLM usage widget"""
    try:
        # Get LLM metrics from last hour
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        prompt_metrics = metrics_storage.get_metrics(
            "llm.tokens.prompt",
            start_time=start_time,
            end_time=end_time
        )
        
        completion_metrics = metrics_storage.get_metrics(
            "llm.tokens.completion",
            start_time=start_time,
            end_time=end_time
        )
        
        total_prompt_tokens = sum(m.get("metric_value", 0) for m in prompt_metrics)
        total_completion_tokens = sum(m.get("metric_value", 0) for m in completion_metrics)
        
        html = f"""
        <h3>LLM Usage (1h)</h3>
        <table>
            <tr>
                <td>Prompt Tokens</td>
                <td>{total_prompt_tokens:,}</td>
            </tr>
            <tr>
                <td>Completion Tokens</td>
                <td>{total_completion_tokens:,}</td>
            </tr>
            <tr>
                <td>Total Tokens</td>
                <td>{total_prompt_tokens + total_completion_tokens:,}</td>
            </tr>
            <tr>
                <td>API Calls</td>
                <td>{len(prompt_metrics)}</td>
            </tr>
        </table>
        """
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading LLM usage: {str(e)}</div>'


@router.get("/cost-tracking", response_class=HTMLResponse)
async def cost_tracking():
    """Cost tracking widget"""
    try:
        html = f"""
        <h3>Cost Tracking</h3>
        <table>
            <tr>
                <td>Total Cost</td>
                <td>${cost_tracker.total_cost:.4f}</td>
            </tr>
            <tr>
                <td>Daily Estimate</td>
                <td>${cost_tracker.get_daily_cost():.2f}</td>
            </tr>
            <tr>
                <td>Monthly Estimate</td>
                <td>${cost_tracker.get_monthly_estimate():.2f}</td>
            </tr>
        </table>
        <small>Based on current usage patterns</small>
        """
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading cost data: {str(e)}</div>'


@router.get("/alerts", response_class=HTMLResponse) 
async def alerts():
    """Active alerts widget"""
    try:
        active_alerts = metrics_storage.get_active_alerts()
        
        if not active_alerts:
            html = """
            <h3>Active Alerts</h3>
            <div class="status-healthy">No active alerts 🎉</div>
            """
        else:
            html = "<h3>Active Alerts</h3><table>"
            for alert in active_alerts[:5]:  # Show max 5 alerts
                severity_class = {
                    "critical": "status-error",
                    "warning": "status-warning",
                    "info": "status-healthy"
                }.get(alert["severity"].lower(), "")
                
                html += f"""
                <tr>
                    <td class="{severity_class}">{alert["severity"]}</td>
                    <td>{alert["alert_name"]}</td>
                    <td>{alert["message"][:50]}...</td>
                </tr>
                """
            html += "</table>"
            
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading alerts: {str(e)}</div>'


@router.get("/recent-errors", response_class=HTMLResponse)
async def recent_errors():
    """Recent errors widget"""
    try:
        analyzer = LogAnalyzer()
        error_stats = analyzer.get_error_statistics(hours=1)
        
        html = f"""
        <h3>Recent Errors (1h)</h3>
        <div class="label">Total Errors</div>
        <div class="metric status-{'error' if error_stats['total_errors'] > 10 else 'healthy'}">
            {error_stats['total_errors']}
        </div>
        """
        
        if error_stats['errors_by_module']:
            html += "<table><tr><th>Module</th><th>Count</th></tr>"
            for module, count in list(error_stats['errors_by_module'].items())[:5]:
                html += f"<tr><td>{module}</td><td>{count}</td></tr>"
            html += "</table>"
            
        return html
    except Exception as e:
        return f'<div class="status-error">Error loading error log: {str(e)}</div>'


def generate_ascii_chart(metrics):
    """Generate simple ASCII chart for metrics"""
    if not metrics:
        return "No data"
    
    values = [m.get("avg", 0) for m in metrics]
    max_val = max(values) if values else 1
    
    # Normalize to 0-10 scale
    normalized = [int((v / max_val) * 10) for v in values]
    
    # Generate chart
    lines = []
    for i in range(10, -1, -1):
        line = ""
        for val in normalized:
            line += "█" if val >= i else " "
        lines.append(line)
    
    return "\n".join(lines)