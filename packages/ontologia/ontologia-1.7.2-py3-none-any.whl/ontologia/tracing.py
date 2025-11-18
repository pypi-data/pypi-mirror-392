"""OpenTelemetry tracing utilities for ontologia-core."""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

# Import OpenTelemetry components only when available
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class Tracer:
    """Simple tracer wrapper that works with or without OpenTelemetry."""

    def __init__(self, service_name: str = "ontologia-core"):
        self.service_name = service_name
        if OPENTELEMETRY_AVAILABLE:
            self._tracer = trace.get_tracer(service_name)
        else:
            self._tracer = None

    @contextmanager
    def start_as_current_span(self, name: str, **attributes: Any) -> Generator[None, None, None]:
        """Start a span with the given name and attributes."""
        if OPENTELEMETRY_AVAILABLE and self._tracer:
            with self._tracer.start_as_current_span(name) as span:
                if attributes:
                    span.set_attributes(attributes)
                yield
        else:
            # Fallback: just log and time the operation
            start_time = perf_counter()
            logger.debug("Starting span: %s", name)
            try:
                yield
            finally:
                duration = perf_counter() - start_time
                logger.debug("Completed span: %s in %.3fs", name, duration)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the current span."""
        if OPENTELEMETRY_AVAILABLE:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute(key, value)

    def set_status(self, status_code: str, description: str | None = None) -> None:
        """Set the status on the current span."""
        if OPENTELEMETRY_AVAILABLE:
            current_span = trace.get_current_span()
            if current_span:
                status = StatusCode.OK if status_code == "OK" else StatusCode.ERROR
                current_span.set_status(Status(status, description))

    def record_exception(self, exception: Exception) -> None:
        """Record an exception on the current span."""
        if OPENTELEMETRY_AVAILABLE:
            current_span = trace.get_current_span()
            if current_span:
                current_span.record_exception(exception)


# Default tracer instance
default_tracer = Tracer()


def trace_operation(operation_name: str, **attributes: Any):
    """Decorator to trace an operation."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with default_tracer.start_as_current_span(operation_name, **attributes):
                try:
                    result = func(*args, **kwargs)
                    default_tracer.set_status("OK")
                    return result
                except Exception as e:
                    default_tracer.record_exception(e)
                    default_tracer.set_status("ERROR", str(e))
                    raise

        return wrapper

    return decorator


@contextmanager
def trace_span(name: str, **attributes: Any) -> Generator[None, None, None]:
    """Context manager to trace a span."""
    with default_tracer.start_as_current_span(name, **attributes):
        try:
            yield
            default_tracer.set_status("OK")
        except Exception as e:
            default_tracer.record_exception(e)
            default_tracer.set_status("ERROR", str(e))
            raise


def is_tracing_enabled() -> bool:
    """Check if OpenTelemetry tracing is available and enabled."""
    return OPENTELEMETRY_AVAILABLE


__all__ = [
    "Tracer",
    "default_tracer",
    "is_tracing_enabled",
    "trace_operation",
    "trace_span",
]
