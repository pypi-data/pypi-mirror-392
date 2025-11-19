"""Application-level domain event handlers."""

from __future__ import annotations

from .cache import register_cache_invalidation_handlers
from .embedding import register_embedding_event_handlers
from .graph import register_graph_event_handlers
from .search import register_search_event_handlers

__all__ = [
    "register_cache_invalidation_handlers",
    "register_embedding_event_handlers",
    "register_graph_event_handlers",
    "register_search_event_handlers",
]
