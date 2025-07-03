#!/usr/bin/env python3
# benchmark/scripts/benchmark_schema.py
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class TestResult(BaseModel):
    test_name: str
    duration_seconds: float
    memory_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    
class FrameworkResult(BaseModel):
    framework_name: str
    version: str
    package_size_mb: float
    dependencies_count: int
    import_time_seconds: float
    tests: List[TestResult]
    metadata: Dict[str, Any]
    
class BenchmarkReport(BaseModel):
    timestamp: datetime
    system_info: Dict[str, str]
    frameworks: List[FrameworkResult]
    raw_data_path: str
    
class OptimizationPotential(BaseModel):
    framework_name: str
    current_size_mb: float
    estimated_minimal_size_mb: float
    removable_dependencies: List[str]
    optimization_strategy: str
    effort_estimate_hours: int