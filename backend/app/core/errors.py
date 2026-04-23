from __future__ import annotations

import functools
import logging
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class ToolError(RuntimeError):
    """Raised when an external tool (Pinecone, OpenAI, etc.) fails after retries."""


class GuardrailError(RuntimeError):
    """Raised when outbound validation cannot be satisfied."""


def with_tool_retry(
    *,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...],
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Async retry wrapper for external I/O (Pinecone, OpenAI HTTP, etc.)."""

    def decorator(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            @retry(
                reraise=True,
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=0.5, max=8),
                retry=retry_if_exception_type(exceptions),
                before_sleep=lambda rs: logger.warning(
                    "Retrying %s after attempt %s: %s",
                    fn.__name__,
                    rs.attempt_number,
                    rs.outcome.exception(),
                ),
            )
            async def _inner() -> R:
                return await fn(*args, **kwargs)

            try:
                return await _inner()
            except Exception as e:
                raise ToolError(f"{fn.__name__} failed: {e}") from e

        return wrapper

    return decorator


def log_exception(context: str, exc: BaseException, **extra: Any) -> None:
    logger.exception("%s: %s", context, exc, extra=extra)
