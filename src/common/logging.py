"""Structured logging configuration"""

import sys
import structlog
from structlog.processors import JSONRenderer, TimeStamper
from typing import Optional


def configure_logging(
    level: str = "INFO",
    json_output: bool = True
) -> None:
    """Configure structured logging"""
    
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        TimeStamper(fmt="iso"),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_output:
        processors.append(JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a logger instance"""
    return structlog.get_logger(name)


# Default logger
logger = get_logger()