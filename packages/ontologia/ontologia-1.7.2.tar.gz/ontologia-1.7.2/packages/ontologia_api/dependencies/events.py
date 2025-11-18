"""FastAPI dependency helpers for domain event bus wiring."""

from __future__ import annotations

from functools import lru_cache
from typing import cast

from ontologia.domain.events import DomainEventBus, InProcessEventBus, SubscribableEventBus
from ontologia.event_bus import get_event_bus
from ontologia.event_handlers.cache import register_cache_invalidation_handlers
from ontologia.event_handlers.search import register_search_event_handlers
from ontologia_api.core.settings import get_settings
from ontologia_api.event_handlers.graph import register_graph_event_handlers
from ontologia_api.repositories.cache_repository import (
    CacheRepository,
    create_redis_cache_repository,
)
from ontologia_api.repositories.elasticsearch_repository import ElasticsearchRepository


@lru_cache(maxsize=1)
def _shared_event_bus() -> DomainEventBus:
    bus = get_event_bus()
    if isinstance(bus, InProcessEventBus):
        s_bus = cast(SubscribableEventBus, bus)
        register_graph_event_handlers(bus)
        register_cache_invalidation_handlers(s_bus, _cache_repository())
        register_search_event_handlers(s_bus, _elasticsearch_repository())
    return bus


def get_domain_event_bus() -> DomainEventBus:
    """Return the application-level event bus instance."""

    return _shared_event_bus()


def reset_dependencies_caches() -> None:
    """Clear all dependency-level caches related to the event bus and settings.

    This is used by tests to ensure a clean state between runs. It clears:
    - Ontologia core event bus cache
    - FastAPI dependency singletons (event bus and repositories)
    - Application settings cache
    """
    # Clear ontologia core event-bus cache
    try:
        from ontologia.event_bus import reset_event_bus_cache as _reset_event_bus_cache

        _reset_event_bus_cache()
    except Exception:
        pass

    # Clear this module's singletons
    try:
        _shared_event_bus.cache_clear()
    except Exception:
        pass
    try:
        _cache_repository.cache_clear()
    except Exception:
        pass
    try:
        _elasticsearch_repository.cache_clear()
    except Exception:
        pass

    # Clear API settings cache
    try:
        from ontologia_api.core.settings import get_settings as _api_get_settings

        _api_get_settings.cache_clear()
    except Exception:
        pass


@lru_cache(maxsize=1)
def _cache_repository() -> CacheRepository:
    settings = get_settings()
    redis_url = settings.redis_url
    return create_redis_cache_repository(redis_url=redis_url)


@lru_cache(maxsize=1)
def _elasticsearch_repository() -> ElasticsearchRepository | None:
    settings = get_settings()
    if not settings.enable_search_indexing:
        return None
    return ElasticsearchRepository(hosts=settings.elasticsearch_hosts)


def get_elasticsearch_repository() -> ElasticsearchRepository | None:
    return _elasticsearch_repository()
