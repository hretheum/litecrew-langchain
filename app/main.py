"""
LiteCrewAI Main Application
"""
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Import monitoring dashboard
from app.monitoring.dashboard import monitoring_app

# Create main app
app = FastAPI(
    title="LiteCrewAI",
    description="Lightweight AI Agent Orchestration Platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'litecrewai_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'litecrewai_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_AGENTS = Gauge(
    'litecrewai_active_agents',
    'Number of active agents'
)

ACTIVE_TASKS = Gauge(
    'litecrewai_active_tasks', 
    'Number of active tasks'
)

INFO_METRIC = Gauge(
    'litecrewai_info',
    'LiteCrewAI information',
    ['version', 'environment']
)

# Set info metric
INFO_METRIC.labels(version="0.1.0", environment=os.getenv("ENVIRONMENT", "development")).set(1)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect metrics"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LiteCrewAI",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "uptime": "unknown"  # Would calculate actual uptime
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint"""
    # Mock health checks - in real implementation these would check actual services
    components = {
        "database": {"status": "healthy", "response_time": 0.012},
        "redis": {"status": "healthy", "response_time": 0.003},
        "ollama": {"status": "healthy", "response_time": 0.150},
        "file_system": {"status": "healthy", "disk_usage": 45.2}
    }
    
    # Mock system metrics
    system = {
        "cpu_usage": 23.5,
        "memory_usage": 67.8,
        "disk_usage": 45.2,
        "load_average": [0.5, 0.8, 0.9]
    }
    
    # Mock cost tracking
    costs = {
        "total_requests": 1247,
        "llm_tokens_used": 45782,
        "estimated_cost_usd": 2.34
    }
    
    # Determine overall status
    unhealthy_components = [name for name, info in components.items() if info["status"] != "healthy"]
    overall_status = "degraded" if unhealthy_components else "healthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "components": components,
        "system": system,
        "costs": costs,
        "version": "0.1.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 error handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500 error handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Mount monitoring dashboard
app.mount("/monitoring", monitoring_app)

# API routes (placeholders for future implementation)
@app.get("/api/agents")
async def list_agents():
    """List all agents"""
    # Mock response
    return {
        "agents": [
            {"id": "agent_1", "name": "Research Assistant", "status": "active"},
            {"id": "agent_2", "name": "Writer", "status": "idle"},
            {"id": "agent_3", "name": "Reviewer", "status": "busy"}
        ]
    }

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    # Mock response
    return {
        "tasks": [
            {"id": "task_1", "name": "Research AI trends", "status": "completed", "agent": "agent_1"},
            {"id": "task_2", "name": "Write summary", "status": "in_progress", "agent": "agent_2"},
            {"id": "task_3", "name": "Review document", "status": "pending", "agent": None}
        ]
    }

@app.get("/api/crews")
async def list_crews():
    """List all crews"""
    # Mock response
    return {
        "crews": [
            {"id": "crew_1", "name": "Content Creation Crew", "agents": 3, "status": "active"},
            {"id": "crew_2", "name": "Data Analysis Crew", "agents": 2, "status": "idle"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)