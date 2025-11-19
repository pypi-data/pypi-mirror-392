"""
Backward-compatible shim. Use ontologia.actions.exceptions.
"""

from __future__ import annotations

from ontologia.actions.exceptions import ActionValidationError

__all__ = ["ActionValidationError"]
