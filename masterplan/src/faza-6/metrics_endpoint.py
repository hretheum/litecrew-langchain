# api/metrics_endpoint.py
from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
import secrets
from typing import Optional

security = HTTPBasic()

def verify_metrics_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify metrics endpoint authentication"""
    correct_username = secrets.compare_digest(
        credentials.username, 
        os.getenv("METRICS_USERNAME", "admin")
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        os.getenv("METRICS_PASSWORD", "changeme")
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

@app.get("/metrics", dependencies=[Depends(verify_metrics_auth)])
async def prometheus_metrics(prefix: Optional[str] = None):
    """Expose Prometheus metrics"""
    
    # Get metrics from registry
    metrics = generate_latest(registry)