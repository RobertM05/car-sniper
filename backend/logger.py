"""
Shared structured JSON-line logger for motorbit.
Replaces bare print() calls with machine-readable JSON log lines.

Usage:
    from backend.logger import get_logger
    log = get_logger(__name__)
    log.info("Scraping started", extra={"make": "BMW", "model": "X5"})
"""

import logging
import json
import sys
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Include any extra fields passed via log.info(..., extra={...})
        for attr in dir(record):
            if attr.startswith("_"):
                continue
            if attr in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            value = getattr(record, attr, None)
            if value is not None and not callable(value):
                payload[attr] = value

        if record.exc_info and record.exc_info[1]:
            payload["exception"] = str(record.exc_info[1])

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes JSON lines to stderr (production-safe)."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        level = os.environ.get("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level, logging.INFO))

    return logger


# Convenience: a root logger for the whole package
log = get_logger("motorbit")
