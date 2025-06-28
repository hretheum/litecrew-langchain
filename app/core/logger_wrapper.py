"""
Logger wrapper for easy usage in LiteCrewAI
"""

from app.core.logging import get_logger, PerformanceLogger, correlation_manager
from typing import Optional


class LiteCrewAILogger:
    """Convenient logger wrapper with domain-specific methods"""

    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.api_logger = get_logger(f"litecrewai.api.{name}")
        self.llm_logger = get_logger(f"litecrewai.llm.{name}")

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """Log API request with structured data"""
        self.api_logger.info(
            f"API Request: {method} {path} - {status_code}",
            extra={
                "extra_fields": {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_seconds": duration,
                    "user_id": user_id,
                    "correlation_id": correlation_manager.get_correlation_id(),
                    **kwargs
                }
            }
        )

    def log_llm_call(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration: float,
        cost: float,
        **kwargs
    ):
        """Log LLM API call with metrics"""
        total_tokens = prompt_tokens + completion_tokens
        
        self.llm_logger.info(
            f"LLM Call: {provider}/{model} - {total_tokens} tokens",
            extra={
                "extra_fields": {
                    "provider": provider,
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "duration_seconds": duration,
                    "cost_usd": cost,
                    "correlation_id": correlation_manager.get_correlation_id(),
                    **kwargs
                }
            }
        )

    def log_agent_task(
        self,
        agent_name: str,
        task_type: str,
        status: str,
        duration: float,
        **kwargs
    ):
        """Log agent task execution"""
        self.logger.info(
            f"Agent Task: {agent_name} - {task_type} - {status}",
            extra={
                "extra_fields": {
                    "agent_name": agent_name,
                    "task_type": task_type,
                    "status": status,
                    "duration_seconds": duration,
                    "correlation_id": correlation_manager.get_correlation_id(),
                    **kwargs
                }
            }
        )

    def log_error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error with structured data"""
        extra_fields = {
            "correlation_id": correlation_manager.get_correlation_id(),
            **kwargs
        }
        
        if exception:
            self.logger.error(
                message,
                exc_info=exception,
                extra={"extra_fields": extra_fields}
            )
        else:
            self.logger.error(message, extra={"extra_fields": extra_fields})

    def performance(self, operation: str) -> PerformanceLogger:
        """Create performance logging context manager"""
        return PerformanceLogger(self.logger, operation)


# Example usage
if __name__ == "__main__":
    # Initialize logger
    logger = LiteCrewAILogger("example_module")
    
    # Set correlation ID for request tracking
    correlation_manager.set_correlation_id("req-123-456")
    
    # Log API request
    logger.log_api_request(
        method="POST",
        path="/api/v1/agents",
        status_code=201,
        duration=0.123,
        user_id="user-789"
    )
    
    # Log with performance tracking
    with logger.performance("database_query"):
        # Simulate some work
        import time
        time.sleep(0.1)
    
    # Log LLM call
    logger.log_llm_call(
        provider="openai",
        model="gpt-3.5-turbo",
        prompt_tokens=150,
        completion_tokens=75,
        duration=1.234,
        cost=0.0045
    )
    
    # Log agent task
    logger.log_agent_task(
        agent_name="ResearchAgent",
        task_type="web_search",
        status="completed",
        duration=2.5,
        results_count=10
    )
    
    # Log error
    try:
        raise ValueError("Example error")
    except ValueError as e:
        logger.log_error("Something went wrong", exception=e, context="example_context")