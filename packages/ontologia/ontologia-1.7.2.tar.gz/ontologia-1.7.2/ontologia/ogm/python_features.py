"""Feature detection and gating for modern Python capabilities.

Provides centralized feature detection for JIT, free-threading, and other
Python version-specific optimizations. Includes environment toggles for opt-in
experimental features.
"""

from __future__ import annotations

import os
import sys
from typing import Final, Literal

# Environment variable names
_ONTOLOGIA_EXPERIMENTAL_JIT: Final = "ONTOLOGIA_EXPERIMENTAL_JIT"
_ONTOLOGIA_EXPERIMENTAL_FREE_THREADING: Final = "ONTOLOGIA_EXPERIMENTAL_FREE_THREADING"

# Feature constants
FeatureName = Literal["jit", "free_threading", "match", "walrus", "positional_only_params"]

# Feature availability cache
_FEATURE_CACHE: dict[FeatureName, bool] = {}


def _parse_env_flag(env_var: str, default: bool = False) -> bool:
    """Parse environment variable as boolean flag."""
    val = os.getenv(env_var, "").strip().lower()
    if not val:
        return default
    return val in {"1", "true", "yes", "on", "enabled"}


def supports_feature(feature: FeatureName) -> bool:
    """Check if a Python feature is available and enabled.

    Args:
        feature: Name of the feature to check.

    Returns:
        True if the feature is available and enabled via environment toggle.
    """
    if feature in _FEATURE_CACHE:
        return _FEATURE_CACHE[feature]

    result: bool
    if feature == "jit":
        # Python 3.13+ experimental JIT
        # Note: JIT requires -X jit command-line flag or PYTHONJIT=1
        is_available = sys.version_info >= (3, 13)
        experimental_enabled = _parse_env_flag(_ONTOLOGIA_EXPERIMENTAL_JIT, default=False)
        result = is_available and experimental_enabled
    elif feature == "free_threading":
        # Python 3.13+ free-threading (no GIL) builds
        is_available = (
            sys.version_info >= (3, 13)
            and hasattr(sys, "_is_gil_enabled")
            and not sys._is_gil_enabled()
        )
        experimental_enabled = _parse_env_flag(
            _ONTOLOGIA_EXPERIMENTAL_FREE_THREADING, default=False
        )
        result = is_available and experimental_enabled
    elif feature == "match":
        # Structural pattern matching (Python 3.10+)
        result = sys.version_info >= (3, 10)
    elif feature == "walrus":
        # Assignment expressions (Python 3.8+)
        result = sys.version_info >= (3, 8)
    elif feature == "positional_only_params":
        # Positional-only parameters (Python 3.8+)
        result = sys.version_info >= (3, 8)
    else:
        raise ValueError(f"Unknown feature: {feature}")

    _FEATURE_CACHE[feature] = result
    return result


def get_feature_summary() -> dict[FeatureName, dict[str, bool | str]]:
    """Get a summary of all detected features and their status."""
    summary: dict[FeatureName, dict[str, bool | str]] = {}
    for feature in ["jit", "free_threading", "match", "walrus", "positional_only_params"]:
        available = supports_feature(feature)
        env_var = {
            "jit": _ONTOLOGIA_EXPERIMENTAL_JIT,
            "free_threading": _ONTOLOGIA_EXPERIMENTAL_FREE_THREADING,
        }.get(feature)
        env_val = os.getenv(env_var, "") if env_var else ""
        summary[feature] = {
            "available": available,
            "python_version_min": {
                "jit": "3.13",
                "free_threading": "3.13",
                "match": "3.10",
                "walrus": "3.8",
                "positional_only_params": "3.8",
            }[feature],
            "env_var": env_var or "",
            "env_value": env_val,
        }
    return summary


def require_feature(feature: FeatureName) -> None:
    """Raise RuntimeError if feature is not available.

    Useful for early validation at module import time.

    Args:
        feature: Name of the required feature.

    Raises:
        RuntimeError: If the feature is not available.
    """
    if not supports_feature(feature):
        min_version = {
            "jit": "3.13",
            "free_threading": "3.13",
            "match": "3.10",
            "walrus": "3.8",
            "positional_only_params": "3.8",
        }[feature]
        env_hint = ""
        if feature in {"jit", "free_threading"}:
            env_var = {
                "jit": _ONTOLOGIA_EXPERIMENTAL_JIT,
                "free_threading": _ONTOLOGIA_EXPERIMENTAL_FREE_THREADING,
            }[feature]
            env_hint = f" Set {env_var}=1 to enable."
        raise RuntimeError(f"Feature '{feature}' requires Python {min_version}+{env_hint}")


# Decorators for conditional optimization
def conditional_jit(func):
    """Apply JIT optimization if available (placeholder for future @torch.compile-style)."""
    if supports_feature("jit"):
        # Future: replace with actual JIT decorator when available
        # For now, just return the function unchanged
        return func
    return func


def experimental(feature: FeatureName):
    """Decorator to mark functions as experimental and require feature."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            require_feature(feature)
            return func(*args, **kwargs)

        wrapper._experimental_feature = feature  # type: ignore[attr-defined]
        wrapper.__doc__ = (func.__doc__ or "") + f"\n\nExperimental: Requires feature '{feature}'."
        return wrapper

    return decorator
