"""
Backward-compatible shim. Use ontologia.event_handlers.search.
"""

from __future__ import annotations

from ontologia.event_handlers.search import (
    SearchEventHandler,
    create_indexes_for_object_types,
    register_search_event_handlers,
)

__all__ = [
    "SearchEventHandler",
    "register_search_event_handlers",
    "create_indexes_for_object_types",
]
