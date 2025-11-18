"""
Backward-compatible shim. Use ontologia.event_handlers.cache.
"""

from __future__ import annotations

from ontologia.event_handlers.cache import (
    CacheInvalidationHandler,
    CacheWarmupHandler,
    register_cache_invalidation_handlers,
)

__all__ = [
    "CacheInvalidationHandler",
    "CacheWarmupHandler",
    "register_cache_invalidation_handlers",
]
