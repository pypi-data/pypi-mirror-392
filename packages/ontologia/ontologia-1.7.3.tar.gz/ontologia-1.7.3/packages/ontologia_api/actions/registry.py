"""
Backward-compatible shim. Use ontologia.actions.registry.
"""

from __future__ import annotations

from ontologia.actions.registry import ACTION_REGISTRY, register_action

__all__ = ["ACTION_REGISTRY", "register_action"]
