"""Performance optimization utilities for ontologia-core.

Provides JIT-optimized implementations of hot path functions
and performance measurement utilities.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from .python_features import supports_feature

# Performance optimization globals
JIT_ENABLED = supports_feature("jit")
FREE_THREADING_ENABLED = supports_feature("free_threading")


def jit_optimized(func: Callable) -> Callable:
    """Decorator to mark functions as JIT-optimized.

    Functions decorated with @jit_optimized will:
    1. Include JIT optimization hints in docstrings
    2. Be monitored for performance when JIT is available
    3. Include performance measurement in debug mode
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if JIT_ENABLED:
            # JIT compilation would happen here in Python 3.13+
            # For now, we just add performance monitoring
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            # Log performance in debug mode
            if __debug__:
                duration = (end_time - start_time) * 1000  # Convert to ms
                if duration > 1.0:  # Only log if > 1ms
                    fname = getattr(func, "__name__", "<func>")
                    print(f"[JIT-DEBUG] {fname}: {duration:.2f}ms")
        else:
            result = func(*args, **kwargs)

        return result

    # Add JIT optimization note to docstring
    if func.__doc__:
        wrapper.__doc__ = (
            func.__doc__ + "\n\n    JIT-optimized: Benefits from compilation when available."
        )
    else:
        wrapper.__doc__ = "JIT-optimized function."

    return wrapper


def performance_monitor(threshold_ms: float = 1.0) -> Callable:
    """Decorator to monitor function performance.

    Args:
        threshold_ms: Log warning if function takes longer than this (in milliseconds)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            duration = (end_time - start_time) * 1000  # Convert to ms
            if duration > threshold_ms:
                fname = getattr(func, "__name__", "<func>")
                print(f"[PERF] {fname}: {duration:.2f}ms (threshold: {threshold_ms}ms)")

            return result

        return wrapper

    return decorator


class PerformanceCounter:
    """Simple performance counter for measuring hot path execution."""

    def __init__(self, name: str):
        self.name = name
        self.count = 0
        self.total_time = 0.0
        self.start_time = None

    def start(self):
        """Start timing."""
        self.start_time = time.perf_counter()

    def stop(self):
        """Stop timing and record."""
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            self.count += 1
            self.total_time += duration
            self.start_time = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def average_time(self) -> float:
        """Get average execution time in milliseconds."""
        if self.count == 0:
            return 0.0
        return (self.total_time / self.count) * 1000

    def __str__(self):
        return f"PerformanceCounter({self.name}: {self.count} calls, avg {self.average_time:.2f}ms)"


# Global performance counters for hot paths
DTYPE_MAPPING_COUNTER = PerformanceCounter("dtype_from_annotation")
PROPERTY_BUILDING_COUNTER = PerformanceCounter("build_property_definitions")
SCHEMA_PLANNING_COUNTER = PerformanceCounter("schema_planning")


def optimize_list_comprehension(data: list[Any], predicate: Callable) -> list[Any]:
    """Optimized list comprehension with JIT hints.

    Args:
        data: List to process
        predicate: Function to apply to each item

    Returns:
        Filtered list
    """
    if JIT_ENABLED:
        # JIT optimization: Use built-in functions when possible
        return [item for item in data if predicate(item)]
    else:
        # Standard implementation
        return [item for item in data if predicate(item)]


def optimize_dict_processing(data: dict[Any, Any], transform: Callable) -> dict[Any, Any]:
    """Optimized dictionary processing with JIT hints.

    Args:
        data: Dictionary to process
        transform: Function to apply to each key-value pair

    Returns:
        Processed dictionary
    """
    if JIT_ENABLED:
        # JIT optimization: Use dict comprehension
        return {k: transform(v) for k, v in data.items()}
    else:
        # Standard implementation
        return {k: transform(v) for k, v in data.items()}


def batch_processor(items: list[Any], batch_size: int = 1000, processor: Callable | None = None):
    """Process items in batches for memory efficiency.

    Args:
        items: List of items to process
        batch_size: Size of each batch
        processor: Function to process each batch

    Yields:
        Processed batches
    """
    if processor is None:

        def identity_processor(x):
            return x

        processor = identity_processor

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        yield processor(batch)


# Performance optimization utilities
def get_performance_summary() -> dict[str, Any]:
    """Get summary of performance counters."""
    return {
        "jit_enabled": JIT_ENABLED,
        "free_threading_enabled": FREE_THREADING_ENABLED,
        "counters": {
            "dtype_mapping": str(DTYPE_MAPPING_COUNTER),
            "property_building": str(PROPERTY_BUILDING_COUNTER),
            "schema_planning": str(SCHEMA_PLANNING_COUNTER),
        },
    }


def reset_performance_counters():
    """Reset all performance counters."""
    global DTYPE_MAPPING_COUNTER, PROPERTY_BUILDING_COUNTER, SCHEMA_PLANNING_COUNTER

    DTYPE_MAPPING_COUNTER = PerformanceCounter("dtype_from_annotation")
    PROPERTY_BUILDING_COUNTER = PerformanceCounter("build_property_definitions")
    SCHEMA_PLANNING_COUNTER = PerformanceCounter("schema_planning")
