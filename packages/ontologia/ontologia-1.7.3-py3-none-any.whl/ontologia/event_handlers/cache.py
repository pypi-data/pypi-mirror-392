"""
cache.py
--------
Event handlers for intelligent cache invalidation.

Handles cache invalidation based on domain events, ensuring that
cached data stays consistent with the underlying data changes.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia.domain.events import (
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
    ObjectTypeSynced,
    SubscribableEventBus,
)
from ontologia.infrastructure.cache_repository import CacheRepository
from ontologia.tracing import trace_operation

logger = logging.getLogger(__name__)
# Global registry to prevent duplicate registrations
_registered_buses: dict[int, CacheInvalidationHandler] = {}


class CacheInvalidationHandler:
    """
    Handles domain events for intelligent cache invalidation.

    This handler ensures that cache entries are invalidated when
    underlying data changes, maintaining cache consistency.
    """

    def __init__(self, cache_repo: CacheRepository) -> None:
        """
        Initialize cache invalidation handler.

        Args:
            cache_repo: Cache repository instance
        """
        self._cache_repo = cache_repo
        self._logger = logging.getLogger(__name__)
        # Counters for observability
        self._counters = {
            "upsert_invalidations": 0,
            "delete_invalidations": 0,
            "sync_invalidations": 0,
            "total_keys_invalidated": 0,
        }

    @trace_operation("cache_invalidation_upsert", event_type="ObjectInstanceUpserted")
    def handle_object_instance_upserted(self, event: ObjectInstanceUpserted) -> None:
        """
        Handle object upsert events by invalidating relevant cache entries.

        Args:
            event: ObjectInstanceUpserted event
        """
        object_type = event.object_type_api_name

        self._logger.info("Handling upsert invalidation for object_type=%s", object_type)

        try:
            # Invalidate query cache for this object type
            query_pattern = self._cache_repo.build_query_pattern(object_type)
            deleted_queries = self._cache_repo.delete_by_pattern(query_pattern)

            # Invalidate specific object cache entries
            object_pattern = self._cache_repo.build_object_type_pattern(object_type)
            deleted_objects = self._cache_repo.delete_by_pattern(object_pattern)

            total_deleted = deleted_queries + deleted_objects
            self._counters["upsert_invalidations"] += 1
            self._counters["total_keys_invalidated"] += total_deleted

            self._logger.info(
                "Invalidated cache on upsert: object_type=%s, query_keys=%d, object_keys=%d, total=%d",
                object_type,
                deleted_queries,
                deleted_objects,
                total_deleted,
            )
        except Exception:
            self._logger.warning(
                "Failed to invalidate cache on upsert for object_type=%s",
                object_type,
                exc_info=True,
            )

    def get_stats(self) -> dict[str, int]:
        """Return current invalidation statistics."""
        return dict(self._counters)

    @trace_operation("cache_invalidation_delete", event_type="ObjectInstanceDeleted")
    def handle_object_instance_deleted(self, event: ObjectInstanceDeleted) -> None:
        """
        Handle object deletion events by invalidating relevant cache entries.

        Args:
            event: ObjectInstanceDeleted event
        """
        object_type = event.object_type_api_name
        pk_value = str(event.primary_key_value)

        try:
            # Invalidate query cache for this object type
            query_pattern = self._cache_repo.build_query_pattern(object_type)
            deleted_queries = self._cache_repo.delete_by_pattern(query_pattern)

            # Invalidate specific object cache entries
            object_pattern = self._cache_repo.build_object_type_pattern(object_type)
            deleted_objects = self._cache_repo.delete_by_pattern(object_pattern)

            # Also invalidate any cache entries that might contain this specific object
            specific_patterns = [
                f"*:{object_type}:{pk_value}:*",
                f"*:{pk_value}:*",
                f"*:{object_type}:*:{pk_value}*",
            ]

            deleted_specific = 0
            for pattern in specific_patterns:
                deleted_specific += self._cache_repo.delete_by_pattern(pattern)

            total_deleted = deleted_queries + deleted_objects + deleted_specific

            if total_deleted > 0:
                self._logger.info(
                    f"Invalidated {total_deleted} cache entries for "
                    f"object type '{object_type}:{pk_value}' due to deletion event"
                )
            else:
                self._logger.debug(
                    f"No cache entries to invalidate for object type '{object_type}:{pk_value}'"
                )

        except Exception as e:
            self._logger.error(
                f"Error invalidating cache for object type '{object_type}:{pk_value}': {e}"
            )

    @trace_operation("cache_invalidation_sync", event_type="ObjectTypeSynced")
    def handle_object_type_synced(self, event: ObjectTypeSynced) -> None:
        """
        Handle object type sync events by invalidating all related cache entries.

        This is triggered when the OntologySyncService completes a synchronization,
        ensuring that all cached data for the affected object type is invalidated.

        Args:
            event: ObjectTypeSynced event
        """
        object_type = event.object_type_api_name
        records_processed = event.records_processed
        is_incremental = event.incremental

        try:
            # Invalidate all cache entries for this object type
            query_pattern = self._cache_repo.build_query_pattern(object_type)
            deleted_queries = self._cache_repo.delete_by_pattern(query_pattern)

            object_pattern = self._cache_repo.build_object_type_pattern(object_type)
            deleted_objects = self._cache_repo.delete_by_pattern(object_pattern)

            # Also invalidate any aggregation or analytics cache entries
            analytics_patterns = [
                f"analytics:{object_type}:*",
                f"aggregate:{object_type}:*",
                f"summary:{object_type}:*",
            ]

            deleted_analytics = 0
            for pattern in analytics_patterns:
                deleted_analytics += self._cache_repo.delete_by_pattern(pattern)

            total_deleted = deleted_queries + deleted_objects + deleted_analytics

            # Log different levels based on sync type and number of records
            if total_deleted > 0:
                if is_incremental:
                    self._logger.info(
                        f"Invalidated {total_deleted} cache entries for object type '{object_type}' "
                        f"after incremental sync ({records_processed} records processed)"
                    )
                else:
                    self._logger.info(
                        f"Invalidated {total_deleted} cache entries for object type '{object_type}' "
                        f"after full sync ({records_processed} records processed)"
                    )
            else:
                self._logger.debug(
                    f"No cache entries to invalidate for object type '{object_type}' after sync"
                )

        except Exception as e:
            self._logger.error(
                f"Error invalidating cache for synced object type '{object_type}': {e}"
            )

    async def invalidate_all_for_object_type(self, object_type: str) -> int:
        """
        Manually invalidate all cache entries for an object type.

        This can be called manually when needed, such as during
        manual data updates or maintenance operations.

        Args:
            object_type: Object type API name

        Returns:
            Number of cache entries invalidated
        """
        try:
            # Invalidate all patterns for this object type
            patterns = [
                self._cache_repo.build_query_pattern(object_type),
                self._cache_repo.build_object_type_pattern(object_type),
                f"analytics:{object_type}:*",
                f"aggregate:{object_type}:*",
                f"summary:{object_type}:*",
            ]

            total_deleted = 0
            for pattern in patterns:
                total_deleted += self._cache_repo.delete_by_pattern(pattern)

            self._logger.info(
                f"Manually invalidated {total_deleted} cache entries for object type '{object_type}'"
            )

            return total_deleted

        except Exception as e:
            self._logger.error(f"Error manually invalidating cache for '{object_type}': {e}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a custom pattern.

        Args:
            pattern: Cache pattern to match

        Returns:
            Number of cache entries invalidated
        """
        try:
            deleted_count = self._cache_repo.delete_by_pattern(pattern)
            self._logger.info(
                f"Invalidated {deleted_count} cache entries matching pattern '{pattern}'"
            )
            return deleted_count

        except Exception as e:
            self._logger.error(f"Error invalidating cache pattern '{pattern}': {e}")
            return 0


class CacheWarmupHandler:
    """
    Handles cache warmup operations for frequently accessed data.

    This handler can pre-populate cache with commonly accessed
    queries and data to improve performance.
    """

    def __init__(self, cache_repo: CacheRepository) -> None:
        """
        Initialize cache warmup handler.

        Args:
            cache_repo: Cache repository instance
        """
        self._cache_repo = cache_repo
        self._logger = logging.getLogger(__name__)

    def warmup_object_type_queries(
        self, object_type: str, common_queries: list[dict[str, Any]]
    ) -> int:
        """
        Warm up cache with common queries for an object type.

        Args:
            object_type: Object type API name
            common_queries: List of common query definitions

        Returns:
            Number of queries warmed up
        """
        warmed_up = 0

        for query_def in common_queries:
            try:
                # Build cache key
                cache_key = self._cache_repo.build_key(
                    "query", object_type, query_def.get("hash", "default")
                )

                # Check if already cached
                if self._cache_repo.exists(cache_key):
                    continue

                # This would typically execute the query and cache the result
                # For now, we'll just mark it as warmed up with a placeholder
                placeholder_result = {
                    "warmed_up": True,
                    "query_type": query_def.get("type", "search"),
                    "object_type": object_type,
                }

                self._cache_repo.set(
                    cache_key,
                    placeholder_result,
                    ttl_seconds=query_def.get("ttl", 1800),
                )

                warmed_up += 1

            except Exception as e:
                self._logger.error(f"Error warming up query for '{object_type}': {e}")

        if warmed_up > 0:
            self._logger.info(
                f"Warmed up {warmed_up} cache entries for object type '{object_type}'"
            )

        return warmed_up


def register_cache_invalidation_handlers(
    bus: SubscribableEventBus, cache_repo: CacheRepository
) -> CacheInvalidationHandler:
    """
    Register cache invalidation handlers with the event bus.

    Args:
        bus: Event bus to register handlers with
        cache_repo: Cache repository instance

    Returns:
        The registered CacheInvalidationHandler instance for metrics
    """
    # Registration requires an in-process, subscribable bus. Distributed
    # implementations should wire handlers out of process and skip this.

    key = id(bus)
    if key in _registered_buses:
        logger.warning("Cache handlers already registered for this bus, skipping")
        return _registered_buses[key]

    handler = CacheInvalidationHandler(cache_repo)

    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)
    bus.subscribe(ObjectTypeSynced, handler.handle_object_type_synced)

    _registered_buses[key] = handler
    logger.info("Cache invalidation handlers registered with event bus")

    # Register metrics from the actual instance
    from ontologia.bootstrap import register_handler_metrics_from_instances

    register_handler_metrics_from_instances(cache_handler=handler)

    return handler
