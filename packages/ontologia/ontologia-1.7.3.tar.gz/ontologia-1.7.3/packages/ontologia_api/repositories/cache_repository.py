"""
Backward-compatible shim. Use ontologia.infrastructure.cache_repository.
"""

from __future__ import annotations

from ontologia.infrastructure.cache_repository import CacheRepository, create_redis_cache_repository

__all__ = ["CacheRepository", "create_redis_cache_repository"]
