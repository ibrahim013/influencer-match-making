from __future__ import annotations

import logging
import sys
from typing import Literal

import structlog

_CONFIGURED = False


def configure_logging(
    *,
    log_format: Literal["text", "json"] = "text",
    level: int = logging.INFO,
) -> None:
    """Configure root logging once; bridge stdlib logging to structlog when JSON."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=False)
    shared: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        structlog.configure(
            processors=shared
            + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processor=structlog.processors.JSONRenderer(),
        )
    else:
        structlog.configure(
            processors=shared
            + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processor=structlog.dev.ConsoleRenderer(colors=False),
        )

    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)
    _CONFIGURED = True
