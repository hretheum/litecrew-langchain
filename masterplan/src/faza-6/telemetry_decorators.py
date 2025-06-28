# telemetry/decorators.py
from functools import wraps
from typing import Callable, Any
import time
import asyncio
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Metrics
task_duration = meter.create_histogram(
    name="litecrewai.task.duration",
    description="Task execution duration",
    unit="ms"
)

task_counter = meter.create_counter(
    name="litecrewai.task.count",
    description="Number of tasks executed"
)

llm_tokens = meter.create_counter(
    name="litecrewai.llm.tokens",
    description="LLM tokens used"
)

def traced(span_name: str = None):
    """Decorator for tracing async functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add common attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Extract known entities
                if "agent_id" in kwargs:
                    span.set_attribute("agent.id", kwargs["agent_id"])
                if "task_id" in kwargs:
                    span.set_attribute("task.id", kwargs["task_id"])
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(
                        Status(StatusCode.ERROR, str(e))
                    )
                    span.record_exception(e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function.name", func.__name__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(
                        Status(StatusCode.ERROR, str(e))
                    )
                    span.record_exception(e)
                    raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def metered(metric_name: str = None):
    """Decorator for collecting metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            labels = {}
            
            # Extract labels
            if "agent_id" in kwargs:
                labels["agent_id"] = kwargs["agent_id"]
            if hasattr(args[0], "__class__"):
                labels["class"] = args[0].__class__.__name__
            
            try:
                result = await func(*args, **kwargs)
                labels["status"] = "success"
                return result
            except Exception as e:
                labels["status"] = "error"
                labels["error_type"] = type(e).__name__
                raise
            finally:
                duration = (time.time() - start_time) * 1000
                task_duration.record(duration, labels)
                task_counter.add(1, labels)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            # Similar sync implementation
            pass
    
    return decorator