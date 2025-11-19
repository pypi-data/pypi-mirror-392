"""
Backward-compatible shim. Use ontologia.actions.test_actions.
Importing this module ensures built-in actions are registered.
"""

from __future__ import annotations

# Register an alias executor used by integration tests
from typing import Any

from ontologia.actions.registry import register_action
from ontologia.actions.test_actions import log_message as _log_message


@register_action("system.log_message_test")
def _log_message_test(context: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    return _log_message(context, params)


__all__: list[str] = ["_log_message_test"]
