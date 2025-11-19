"""
search.py
--------
Event handlers for maintaining Elasticsearch search indexes.

Handles indexing and deletion of objects in Elasticsearch based on
domain events, ensuring the search index stays synchronized with
the primary data store.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia.config import load_config
from ontologia.domain.events import (
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
    SubscribableEventBus,
)
from ontologia.infrastructure.elasticsearch_repository import ElasticsearchRepository
from ontologia.tracing import trace_operation

logger = logging.getLogger(__name__)
# Global registry to prevent duplicate registrations
_registered_buses: dict[int, SearchEventHandler] = {}


class SearchEventHandler:
    """
    Handles domain events for maintaining Elasticsearch search indexes.

    This handler ensures that object instances are indexed in Elasticsearch
    when they are created or updated, and removed from the index when deleted.
    """

    def __init__(self, elasticsearch_repo: ElasticsearchRepository | None = None) -> None:
        """
        Initialize the search event handler.

        Args:
            elasticsearch_repo: Elasticsearch repository instance
        """
        self._elasticsearch = elasticsearch_repo
        self._config = load_config()
        self._logger = logging.getLogger(__name__)
        # Counters for observability
        self._counters = {
            "index_operations": 0,
            "delete_operations": 0,
            "failed_operations": 0,
            "skipped_operations": 0,
        }

    def _should_index(self) -> bool:
        """
        Check if indexing should be performed based on configuration.

        Returns:
            True if indexing is enabled and Elasticsearch is available
        """
        if not self._elasticsearch:
            return False

        # Check if search features are enabled in configuration
        if hasattr(self._config.features, "enable_search_indexing"):
            return self._config.features.enable_search_indexing

        # Default to enabled for development
        return True

    @trace_operation("search_index_upsert", event_type="ObjectInstanceUpserted")
    def handle_object_instance_upserted(self, event: ObjectInstanceUpserted) -> None:
        """
        Handle object instance upsert events by updating Elasticsearch index.

        Args:
            event: ObjectInstanceUpserted event
        """
        object_type = event.object_type_api_name
        pk_value = str(event.primary_key_value)

        if not self._should_index():
            self._counters["skipped_operations"] += 1
            self._logger.debug(
                "Search indexing disabled, skipping upsert for object_type=%s, pk=%s",
                object_type,
                pk_value,
            )
            return

        if not self._elasticsearch:
            self._counters["failed_operations"] += 1
            self._logger.warning(
                "Elasticsearch repository not available, skipping indexing for object_type=%s, pk=%s",
                object_type,
                pk_value,
            )
            return

        try:
            # Prepare document for indexing
            document = self._prepare_index_document(event)
            if not document:
                self._counters["skipped_operations"] += 1
                self._logger.debug(
                    "No document to index for object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
                return

            # Index the document
            success = self._elasticsearch.index_object(document)

            if success:
                self._counters["index_operations"] += 1
                self._logger.info(
                    "Indexed object in Elasticsearch: object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
            else:
                self._counters["failed_operations"] += 1
                self._logger.warning(
                    "Failed to index object in Elasticsearch: object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
        except Exception:
            self._counters["failed_operations"] += 1
            self._logger.error(
                "Error indexing object in Elasticsearch: object_type=%s, pk=%s",
                object_type,
                pk_value,
                exc_info=True,
            )

    def get_stats(self) -> dict[str, int]:
        """Return current search indexing statistics."""
        return dict(self._counters)

    @trace_operation("search_index_delete", event_type="ObjectInstanceDeleted")
    def handle_object_instance_deleted(self, event: ObjectInstanceDeleted) -> None:
        """
        Handle object instance deletion events by removing from Elasticsearch.

        Args:
            event: ObjectInstanceDeleted event
        """
        if not self._should_index():
            self._logger.debug("Search indexing disabled, skipping delete handler")
            return

        if not self._elasticsearch:
            self._logger.warning("Elasticsearch repository not available, skipping deletion")
            return

        try:
            # Delete from index
            success = self._elasticsearch.delete_object(
                object_type=event.object_type_api_name, pk_value=str(event.primary_key_value)
            )

            if success:
                self._logger.info(
                    f"Deleted object {event.object_type_api_name}:{event.primary_key_value} from Elasticsearch"
                )
            else:
                self._logger.warning(
                    f"Failed to delete object {event.object_type_api_name}:{event.primary_key_value} from Elasticsearch"
                )

        except Exception as e:
            self._logger.error(
                f"Error deleting object {event.object_type_api_name}:{event.primary_key_value} from Elasticsearch: {e}"
            )

    def _prepare_index_document(self, event: ObjectInstanceUpserted) -> dict[str, Any] | None:
        """
        Prepare document for Elasticsearch indexing.

        Args:
            event: ObjectInstanceUpserted event

        Returns:
            Document dictionary ready for indexing, or None if preparation fails
        """
        if not event.primary_key_value:
            self._logger.warning(
                f"Object missing primary key value, skipping indexing: {event.object_type_api_name}"
            )
            return None

        # Build the document structure
        document = {
            "objectTypeApiName": event.object_type_api_name,
            "pkValue": str(event.primary_key_value),
        }

        # Add properties if available
        if event.payload:
            # Merge properties into the document
            document.update(event.payload)

        return document

    def create_index_if_not_exists(
        self, object_type_api_name: str, properties: dict[str, Any]
    ) -> bool:
        """
        Create Elasticsearch index for an object type if it doesn't exist.

        Args:
            object_type_api_name: API name of the object type
            properties: Dictionary of property definitions

        Returns:
            True if index was created or already exists
        """
        if not self._should_index():
            return False

        if not self._elasticsearch:
            self._logger.warning("Elasticsearch repository not available")
            return False

        try:
            success = self._elasticsearch.create_index(object_type_api_name, properties)
            if success:
                self._logger.info(f"Created Elasticsearch index for {object_type_api_name}")
            return success

        except Exception as e:
            self._logger.error(
                f"Failed to create Elasticsearch index for {object_type_api_name}: {e}"
            )
            return False


def register_search_event_handlers(
    bus: SubscribableEventBus, elasticsearch_repo: ElasticsearchRepository | None = None
) -> SearchEventHandler:
    """
    Register search event handlers with the event bus.

    Args:
        bus: Event bus to register handlers with
        elasticsearch_repo: Elasticsearch repository instance

    Returns:
        The registered SearchEventHandler instance for metrics
    """
    # Registration requires an in-process, subscribable bus. Distributed
    # implementations should wire handlers out of process and skip this.

    key = id(bus)
    if key in _registered_buses:
        logger.warning("Search handlers already registered for this bus, skipping")
        return _registered_buses[key]

    handler = SearchEventHandler(elasticsearch_repo)

    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)

    _registered_buses[key] = handler
    logger.info("Search event handlers registered with event bus")

    # Register metrics from the actual instance
    from ontologia.bootstrap import register_handler_metrics_from_instances

    register_handler_metrics_from_instances(search_handler=handler)

    return handler


def create_indexes_for_object_types(
    elasticsearch_repo: ElasticsearchRepository, object_types: list[dict[str, Any]]
) -> None:
    """
    Create Elasticsearch indexes for a list of object types.

    This utility function can be called during application startup
    to ensure indexes exist for all known object types.

    Args:
        elasticsearch_repo: Elasticsearch repository instance
        object_types: List of object type definitions
    """
    if not elasticsearch_repo:
        logger.warning("Elasticsearch repository not available, skipping index creation")
        return

    handler = SearchEventHandler(elasticsearch_repo)

    for obj_type in object_types:
        api_name = obj_type.get("api_name")
        properties = obj_type.get("properties", {})

        if api_name and properties:
            handler.create_index_if_not_exists(api_name, properties)
