"""
Structured logging utilities for the Rust Crate Pipeline.

Provides JSON-formatted structured logging with correlation IDs,
log levels, and standardized fields for better observability.
"""

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add execution ID if present
        if hasattr(record, "execution_id"):
            log_data["execution_id"] = record.execution_id

        # Add crate name if present
        if hasattr(record, "crate_name"):
            log_data["crate_name"] = record.crate_name

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, default=str)


class CorrelationFilter(logging.Filter):
    """Filter to add correlation ID to log records."""

    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__()
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record."""
        record.correlation_id = self.correlation_id
        return True


def setup_structured_logging(
    level: str = "INFO",
    format_type: str = "json",
    correlation_id: Optional[str] = None,
) -> logging.Logger:
    """
    Set up structured logging for the pipeline.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ('json' or 'text')
        correlation_id: Optional correlation ID for request tracing
        
    Returns:
        Configured root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Set formatter based on format type
    if format_type == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
        )

    console_handler.setFormatter(formatter)

    # Add correlation filter
    if correlation_id:
        correlation_filter = CorrelationFilter(correlation_id)
        console_handler.addFilter(correlation_filter)
    else:
        correlation_filter = CorrelationFilter()
        console_handler.addFilter(correlation_filter)

    root_logger.addHandler(console_handler)

    return root_logger


def get_logger(name: str, correlation_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with optional correlation ID.
    
    Args:
        name: Logger name (typically __name__)
        correlation_id: Optional correlation ID
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if correlation_id:
        # Add correlation filter to logger
        for handler in logger.handlers:
            if not any(
                isinstance(f, CorrelationFilter) for f in handler.filters
            ):
                handler.addFilter(CorrelationFilter(correlation_id))
    return logger


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    correlation_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    crate_name: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a message with structured context.
    
    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        correlation_id: Optional correlation ID
        execution_id: Optional execution ID
        crate_name: Optional crate name
        extra_fields: Optional extra fields to include
    """
    log_method = getattr(logger, level.lower(), logger.info)

    # Create a log record with extra attributes
    extra = {}
    if correlation_id:
        extra["correlation_id"] = correlation_id
    if execution_id:
        extra["execution_id"] = execution_id
    if crate_name:
        extra["crate_name"] = crate_name
    if extra_fields:
        extra["extra_fields"] = extra_fields

    log_method(message, extra=extra)

