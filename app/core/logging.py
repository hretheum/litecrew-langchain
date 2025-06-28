"""
LiteCrewAI Logging Configuration
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
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
    log_file: str = "/var/log/litecrewai/app.log",
    enable_console: bool = True,
) -> None:
    """Setup logging configuration"""

    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Clear existing handlers
    logging.root.handlers = []

    # Setup formatters
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with JSON format
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    handlers = [file_handler]
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        handlers.append(console_handler)

    # Configure root logger
    logging.basicConfig(level=getattr(logging, log_level.upper()), handlers=handlers)

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
