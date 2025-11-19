"""
Backward-compatible shim. Use ontologia.event_handlers.graph.
Provides compatibility for tests that monkeypatch `api.event_handlers.graph.get_kuzu_repo`.
"""

from __future__ import annotations

import ontologia.event_handlers.graph as _core_graph
from ontologia.domain.events import (
    DomainEventBus,
    InProcessEventBus,
    LinkCreated,
    LinkDeleted,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
)

# Import a shim-level provider that tests can monkeypatch via this module namespace
from ontologia_api.repositories.kuzudb_repository import get_kuzu_repo  # noqa: F401


class GraphEventHandler(_core_graph.GraphEventHandler):
    def __init__(self) -> None:
        # Use the shim-level symbol so tests can monkeypatch api.event_handlers.graph.get_kuzu_repo
        self._kuzu_repo = get_kuzu_repo()


def register_graph_event_handlers(bus: DomainEventBus) -> None:
    if not isinstance(bus, InProcessEventBus):
        return
    handler = GraphEventHandler()
    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)
    bus.subscribe(LinkCreated, handler.handle_link_created)
    bus.subscribe(LinkDeleted, handler.handle_link_deleted)


__all__ = [
    "GraphEventHandler",
    "register_graph_event_handlers",
    "get_kuzu_repo",
]
