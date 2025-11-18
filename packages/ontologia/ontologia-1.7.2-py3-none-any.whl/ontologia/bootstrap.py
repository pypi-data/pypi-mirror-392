"""Bootstrap utilities for ontologia-core.

Provides helpers to initialize the core with default actions,
event handlers, and infrastructure components.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia.actions import ACTION_REGISTRY
from ontologia.application.actions_service import ActionsService
from ontologia.domain.events import (
    DomainEventBus,
    InProcessEventBus,
    SubscribableEventBus,
)
from ontologia.event_bus import get_event_bus
from ontologia.event_handlers import (
    register_cache_invalidation_handlers,
    register_embedding_event_handlers,
    register_graph_event_handlers,
    register_search_event_handlers,
)
from ontologia.event_handlers.cache import CacheInvalidationHandler
from ontologia.event_handlers.embedding import EmbeddingEventHandler
from ontologia.event_handlers.graph import GraphEventHandler
from ontologia.event_handlers.search import SearchEventHandler
from ontologia.infrastructure.cache_repository import (
    CacheRepository,
    create_memory_cache_repository,
)
from ontologia.infrastructure.elasticsearch_repository import ElasticsearchRepository
from ontologia.infrastructure.persistence.kuzu import get_kuzu_repo
from ontologia.infrastructure.persistence.sql import SQLMetamodelRepository
from ontologia.infrastructure.vector_store_factory import create_vector_repository
from ontologia.metrics import get_core_metrics, register_handler_metrics

logger = logging.getLogger(__name__)

# Global storage for handler instances (for metrics access)
_HANDLER_INSTANCES: dict[str, Any] = {}

# Import built-in actions to ensure registration


def bootstrap_core(
    sql_repo: SQLMetamodelRepository,
    *,
    enable_cache: bool = True,
    enable_search: bool = True,
    enable_graph: bool = True,
    enable_embeddings: bool = True,
    cache_repo: CacheRepository | None = None,
    elasticsearch_repo: ElasticsearchRepository | None = None,
    graph_repo: Any | None = None,  # Type from kuzu module
    vector_repo: Any | None = None,  # VectorRepository type
    event_bus: DomainEventBus | None = None,
) -> tuple[DomainEventBus, dict[str, Any]]:
    """
    Bootstrap the ontologia core with all required components.

    Args:
        sql_repo: SQLModel repository for persistence
        enable_cache: Whether to enable cache invalidation handlers
        enable_search: Whether to enable search event handlers
        enable_graph: Whether to enable graph event handlers
        enable_embeddings: Whether to enable vector embedding handlers
        cache_repo: Optional cache repository (created if None)
        elasticsearch_repo: Optional Elasticsearch repository
        graph_repo: Optional graph repository
        vector_repo: Optional vector repository (created if None)
        event_bus: Optional event bus (created if None)

    Returns:
        Tuple of (event_bus, handler_instances) where handler_instances contains
        the registered handlers for metrics collection
    """
    # Create event bus
    if event_bus is None:
        event_bus = get_event_bus()

    # Initialize metrics
    metrics = get_core_metrics()
    if hasattr(metrics, "initialize"):
        try:
            metrics.initialize()  # type: ignore[attr-defined]
        except Exception:
            pass

    handler_instances = {}

    is_in_process_bus = isinstance(event_bus, InProcessEventBus)
    if not is_in_process_bus:
        logger.info(
            "Skipping handler registration for bus type %s",
            type(event_bus).__name__,
        )

    # Type narrow: we know event_bus is SubscribableEventBus when is_in_process_bus is True
    subscribable_bus: SubscribableEventBus = event_bus  # type: ignore[assignment]

    # Register cache handlers
    if enable_cache and is_in_process_bus:
        if cache_repo is None:
            cache_repo = create_memory_cache_repository()
        cache_handler = register_cache_invalidation_handlers(
            subscribable_bus,
            cache_repo,
        )
        handler_instances["cache"] = cache_handler

    # Register search handlers
    if enable_search and is_in_process_bus:
        search_handler = register_search_event_handlers(
            subscribable_bus,
            elasticsearch_repo,
        )
        handler_instances["search"] = search_handler

    # Register graph handlers
    if enable_graph and is_in_process_bus:
        if graph_repo is None:
            raise ValueError("Graph repository required when enable_graph=True")
        graph_handler = register_graph_event_handlers(
            subscribable_bus,
            graph_repo,
        )
        handler_instances["graph"] = graph_handler

    # Register embedding handlers
    if enable_embeddings and is_in_process_bus:
        if vector_repo is None:
            vector_repo = create_vector_repository()
        if vector_repo is not None:
            embedding_handler = register_embedding_event_handlers(
                subscribable_bus,
                vector_repo,
            )
            handler_instances["embeddings"] = embedding_handler
        else:
            logger.warning("Vector embeddings enabled but no repository available")

    # Store handler instances globally for metrics access
    global _HANDLER_INSTANCES
    _HANDLER_INSTANCES = handler_instances

    logger.info("Ontologia core bootstrapped successfully")
    return event_bus, handler_instances


def get_action_stats() -> dict[str, Any]:
    """Return statistics about registered actions."""
    return {
        "total_actions": len(ACTION_REGISTRY),
        "action_keys": sorted(ACTION_REGISTRY.keys()),
    }


def get_handler_instances() -> dict[str, Any]:
    """Return the registered handler instances for metrics access."""
    return _HANDLER_INSTANCES.copy()


def create_actions_service(session: Any, **kwargs: Any) -> ActionsService:
    """Create an ActionsService with default configuration.

    Args:
        session: SQLModel Session instance
        **kwargs: Additional arguments passed to ActionsService

    Returns:
        Configured ActionsService instance
    """
    return ActionsService(session, **kwargs)


def list_available_infrastructure() -> dict[str, bool]:
    """Check availability of optional infrastructure components."""
    infra = {
        "kuzu": False,
        "cache": True,  # Memory backend always available
        "elasticsearch": False,
    }

    # Check Kùzu availability
    try:
        repo = get_kuzu_repo()
        infra["kuzu"] = repo is not None
    except Exception:
        infra["kuzu"] = False

    # Check Elasticsearch availability (mock always available)
    try:
        ElasticsearchRepository()
        infra["elasticsearch"] = True  # Mock counts as available
    except Exception:
        infra["elasticsearch"] = False

    return infra


def get_core_metrics_summary() -> dict[str, Any]:
    """Get aggregated metrics from all core components."""
    metrics = get_core_metrics()

    # Note: Real-time metrics should be registered during handler subscription
    # This function now returns current state without creating temporary instances
    return metrics.get_summary_metrics()


def register_handler_metrics_from_instances(
    cache_handler: CacheInvalidationHandler | None = None,
    search_handler: SearchEventHandler | None = None,
    graph_handler: GraphEventHandler | None = None,
    embedding_handler: EmbeddingEventHandler | None = None,
) -> None:
    """Register metrics from actual handler instances."""
    if cache_handler:
        register_handler_metrics("cache", getattr(cache_handler, "get_stats", lambda: {})())
    if search_handler:
        register_handler_metrics("search", getattr(search_handler, "get_stats", lambda: {})())
    if graph_handler:
        register_handler_metrics("graph", getattr(graph_handler, "get_stats", lambda: {})())
    if embedding_handler:
        register_handler_metrics(
            "embeddings", getattr(embedding_handler, "get_stats", lambda: {})()
        )
