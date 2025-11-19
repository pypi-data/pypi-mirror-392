"""
Structured logging configuration for the web scraping module.
"""

import logging
import os
import sys
from typing import Any

import structlog


def setup_logging() -> None:
    """Configure structured logging for the application."""

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            _group_extra_attributes,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set log level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, log_level, logging.INFO),
    )


def _group_extra_attributes(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Group all non-reserved fields under 'attrs' and ensure consistent field ordering."""
    # Reserved fields that should stay at top level in specific order
    reserved_fields = {
        "timestamp",
        "level",
        "logger",
        "message",
        # Keep exception info top-level
        "exc_info",
        "stack_info",
        "exception",
        # Prevent nesting attrs into attrs
        "attrs",
        "_record",
        "_from_structlog",
    }

    # Create ordered result with consistent field ordering
    ordered_result = {}

    # Add fields in specific order
    field_order = [
        "timestamp",
        "level",
        "logger",
        "message",
    ]

    for field in field_order:
        if field in event_dict:
            ordered_result[field] = event_dict[field]

    # Collect non-reserved keys for attrs
    attrs = {k: v for k, v in event_dict.items() if k not in reserved_fields}

    # Add attrs if not empty
    if attrs:
        ordered_result["attrs"] = attrs

    # Add exception info at the end if present
    if "exception" in event_dict:
        ordered_result["exception"] = event_dict["exception"]

    return ordered_result


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with the given name."""
    return structlog.get_logger(name)
