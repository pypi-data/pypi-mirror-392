"""
Backward-compatible shim. Use ontologia.actions.temporal.activities.
"""

from __future__ import annotations

from ontologia.actions.temporal.activities import run_registered_action

__all__ = ["run_registered_action"]
