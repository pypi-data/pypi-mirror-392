from __future__ import annotations

import logging

from ontologia.config import use_graph_writes_enabled
from ontologia.domain.events import (
    LinkCreated,
    LinkDeleted,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
    SubscribableEventBus,
)
from ontologia.infrastructure.persistence.kuzu import KuzuDBRepository, get_kuzu_repo

logger = logging.getLogger(__name__)
# Global registry to prevent duplicate registrations
_registered_buses: dict[int, GraphEventHandler] = {}


class GraphEventHandler:
    def __init__(self, graph_repo: KuzuDBRepository | None = None) -> None:
        # Allow explicit repo injection or lazy resolution
        self._kuzu_repo = graph_repo or get_kuzu_repo()

    def handle_object_instance_upserted(self, event: ObjectInstanceUpserted) -> None:
        if not self._should_write():
            return
        if not event.primary_key_field:
            return
        props = dict(event.payload or {})
        set_parts: list[str] = []
        for key, value in props.items():
            if value is None:
                continue
            literal = self._kuzu_literal(value)
            set_parts.append(f"o.`{key}` = {literal}")
        if not set_parts:
            return
        pk_literal = self._kuzu_literal(event.primary_key_value)
        label = event.object_type_api_name
        pk_field = event.primary_key_field
        # Use MERGE for idempotent upsert
        merge_query = (
            f"MERGE (o:`{label}` {{`{pk_field}`: {pk_literal}}}) " f"SET {', '.join(set_parts)}"
        )
        self._execute(merge_query)

    def handle_object_instance_deleted(self, event: ObjectInstanceDeleted) -> None:
        if not self._should_write():
            return
        if not event.primary_key_field:
            return
        pk_literal = self._kuzu_literal(event.primary_key_value)
        label = event.object_type_api_name
        pk_field = event.primary_key_field
        query = f"MATCH (o:`{label}`) WHERE o.`{pk_field}` = {pk_literal} DELETE o"
        self._execute(query)

    def handle_link_created(self, event: LinkCreated) -> None:
        if not self._should_write():
            return
        if not event.from_primary_key_field or not event.to_primary_key_field:
            return
        from_literal = self._kuzu_literal(event.from_pk)
        to_literal = self._kuzu_literal(event.to_pk)
        props = event.properties or {}
        allowed_names = event.property_names or tuple(props.keys())
        set_parts = [
            f"{self._rel_property_ref(name)} = {self._kuzu_literal(props[name])}"
            for name in allowed_names
            if name in props and props[name] is not None
        ]
        cypher = (
            f"MATCH (a:`{event.from_object_type}` {{`{event.from_primary_key_field}`: {from_literal}}}) "
            f"MATCH (b:`{event.to_object_type}` {{`{event.to_primary_key_field}`: {to_literal}}}) "
            f"CREATE (a)-[r:`{event.link_type_api_name}`]->(b)"
        )
        if set_parts:
            cypher += f" SET {', '.join(set_parts)}"
        self._execute(cypher)

    def handle_link_deleted(self, event: LinkDeleted) -> None:
        if not self._should_write():
            return
        if not event.from_primary_key_field or not event.to_primary_key_field:
            return
        from_literal = self._kuzu_literal(event.from_pk)
        to_literal = self._kuzu_literal(event.to_pk)
        query = (
            f"MATCH (a:`{event.from_object_type}`)-[r:`{event.link_type_api_name}`]->"
            f"(b:`{event.to_object_type}`) WHERE a.`{event.from_primary_key_field}` = {from_literal} "
            f"AND b.`{event.to_primary_key_field}` = {to_literal} DELETE r"
        )
        self._execute(query)

    def _should_write(self) -> bool:
        if not use_graph_writes_enabled():
            return False
        try:
            return bool(self._kuzu_repo and self._kuzu_repo.is_available())
        except Exception:
            return False

    def _execute(self, query: str) -> None:
        if not query:
            return
        try:
            self._kuzu_repo.execute(query)  # type: ignore[union-attr]
        except Exception:
            logger.debug("graph sync query failed: %s", query, exc_info=True)

    @staticmethod
    def _kuzu_literal(value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int | float):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    @staticmethod
    def _rel_property_ref(name: str) -> str:
        if not name:
            return "r"
        if name.isidentifier():
            return f"r.{name}"
        escaped = name.replace("`", "``")
        return f"r.`{escaped}`"


def register_graph_event_handlers(
    bus: SubscribableEventBus, graph_repo: KuzuDBRepository
) -> GraphEventHandler:
    """
    Register graph event handlers with the event bus.

    Args:
        bus: Event bus to register handlers with
        graph_repo: Graph repository instance

    Returns:
        The registered GraphEventHandler instance for metrics
    """
    # Registration requires an in-process, subscribable bus. Distributed
    # implementations should wire handlers out of process and skip this.

    key = id(bus)
    if key in _registered_buses:
        logger.warning("Graph handlers already registered for this bus, skipping")
        return _registered_buses[key]

    handler = GraphEventHandler(graph_repo)

    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)
    bus.subscribe(LinkCreated, handler.handle_link_created)
    bus.subscribe(LinkDeleted, handler.handle_link_deleted)

    _registered_buses[key] = handler
    logger.info("Graph event handlers registered with event bus")

    # Register metrics from the actual instance
    from ontologia.bootstrap import register_handler_metrics_from_instances

    register_handler_metrics_from_instances(graph_handler=handler)

    return handler
