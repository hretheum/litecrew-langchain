"""
LiteCrewAI Logging Configuration
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from datetime import timedelta
import uuid
from contextvars import ContextVar

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "/opt/litecrewai/logs",
    enable_console: bool = True,
) -> None:
    """Setup logging configuration with multiple log files"""

    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Clear existing handlers
    logging.root.handlers = []

    # Setup formatters
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Define log files
    log_files = {
        "app": log_path / "app.log",
        "api": log_path / "api.log",
        "llm": log_path / "llm.log",
        "error": log_path / "error.log",
    }

    # Create handlers for each log file
    handlers = []
    
    # Application log handler
    app_handler = logging.FileHandler(log_files["app"])
    app_handler.setFormatter(json_formatter)
    app_handler.setLevel(getattr(logging, log_level.upper()))
    handlers.append(app_handler)

    # Error log handler
    error_handler = logging.FileHandler(log_files["error"])
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
    handlers.append(error_handler)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        handlers.append(console_handler)

    # Configure root logger
    logging.basicConfig(level=getattr(logging, log_level.upper()), handlers=handlers)

    # Configure specific loggers with dedicated handlers
    # API logger
    api_logger = logging.getLogger("litecrewai.api")
    api_handler = logging.FileHandler(log_files["api"])
    api_handler.setFormatter(json_formatter)
    api_logger.addHandler(api_handler)
    api_logger.propagate = False

    # LLM logger
    llm_logger = logging.getLogger("litecrewai.llm")
    llm_handler = logging.FileHandler(log_files["llm"])
    llm_handler.setFormatter(json_formatter)
    llm_logger.addHandler(llm_handler)
    llm_logger.propagate = False

    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger with extra functionality"""
    logger = logging.getLogger(name)

    # Add method to include extra fields
    def log_with_extra(level: int, msg: str, **kwargs):
        extra_fields = kwargs.pop("extra_fields", {})
        record = logger.makeRecord(
            logger.name, level, "(unknown file)", 0, msg, (), None
        )
        record.extra_fields = extra_fields
        logger.handle(record)

    logger.log_with_extra = log_with_extra
    return logger


def generate_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())


# Performance logging utilities
class PerformanceLogger:
    """Context manager for performance logging"""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        self.logger.log_with_extra(
            logging.INFO,
            f"{self.operation} completed",
            extra_fields={
                "operation": self.operation,
                "duration_seconds": duration,
                "success": exc_type is None,
            },
        )


# Correlation ID tracking
class CorrelationIDManager:
    """Manage correlation IDs for request tracking"""

    def __init__(self):
        self.correlation_id_var: ContextVar[Optional[str]] = ContextVar(
            "correlation_id", default=None
        )

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        """Set correlation ID for current context"""
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        self.correlation_id_var.set(correlation_id)
        return correlation_id

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return self.correlation_id_var.get()

    def clear_correlation_id(self) -> None:
        """Clear correlation ID"""
        self.correlation_id_var.set(None)


# Global correlation ID manager
correlation_manager = CorrelationIDManager()


# Log analysis utilities
class LogAnalyzer:
    """Analyze logs for patterns and statistics"""

    def __init__(self, log_dir: str = "/opt/litecrewai/logs"):
        self.log_dir = Path(log_dir)

    def parse_json_logs(self, log_file: str, hours: int = 24) -> list[Dict]:
        """Parse JSON logs from the last N hours"""
        logs = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        log_path = self.log_dir / log_file
        if not log_path.exists():
            return logs
            
        with open(log_path, "r") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_time = datetime.fromisoformat(
                        log_entry["timestamp"].replace("Z", "+00:00")
                    )
                    if log_time > cutoff_time:
                        logs.append(log_entry)
                except (json.JSONDecodeError, KeyError):
                    continue
                    
        return logs

    def get_error_statistics(self, hours: int = 24) -> Dict:
        """Get error statistics from logs"""
        errors = self.parse_json_logs("error.log", hours)
        
        stats = {
            "total_errors": len(errors),
            "errors_by_level": {},
            "errors_by_module": {},
            "top_errors": [],
        }
        
        for error in errors:
            # Count by level
            level = error.get("level", "UNKNOWN")
            stats["errors_by_level"][level] = (
                stats["errors_by_level"].get(level, 0) + 1
            )
            
            # Count by module
            module = error.get("module", "unknown")
            stats["errors_by_module"][module] = (
                stats["errors_by_module"].get(module, 0) + 1
            )
            
        return stats

    def get_performance_metrics(self, hours: int = 24) -> Dict:
        """Get performance metrics from logs"""
        app_logs = self.parse_json_logs("app.log", hours)
        
        metrics = {
            "request_count": 0,
            "avg_duration": 0,
            "p95_duration": 0,
            "p99_duration": 0,
        }
        
        durations = []
        for log in app_logs:
            if "duration_seconds" in log.get("extra_fields", {}):
                durations.append(log["extra_fields"]["duration_seconds"])
                
        if durations:
            durations.sort()
            metrics["request_count"] = len(durations)
            metrics["avg_duration"] = sum(durations) / len(durations)
            metrics["p95_duration"] = durations[int(len(durations) * 0.95)]
            metrics["p99_duration"] = durations[int(len(durations) * 0.99)]
            
        return metrics
