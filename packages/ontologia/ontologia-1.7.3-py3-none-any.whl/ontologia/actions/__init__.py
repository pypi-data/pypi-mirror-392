"""Actions framework for the Ontologia core.

Provides registration and execution of business actions with optional
Temporal workflow support.
"""

from __future__ import annotations

from .exceptions import ActionValidationError
from .registry import ACTION_REGISTRY, register_action

__all__ = ["ACTION_REGISTRY", "ActionValidationError", "register_action"]
