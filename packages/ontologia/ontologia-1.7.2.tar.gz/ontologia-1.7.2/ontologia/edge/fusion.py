from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from ontologia_edge.entity_manager import EntitySnapshot
from ontologia_edge.journal import EntityEvent

from ontologia.domain.events import DomainEvent, DomainEventBus, NullEventBus

from .storage import EntityStateStore


@dataclass(slots=True)
class SensorDetection:
    sensor_id: str
    object_type: str
    ttl: timedelta
    components: dict[str, dict[str, object]] = field(default_factory=dict)
    entity_hint: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    event_type: str = "upsert"


@dataclass(slots=True, kw_only=True, frozen=True)
class RuntimeEntityUpserted(DomainEvent):
    entity_id: str
    object_type_api_name: str
    provenance: str
    payload: dict[str, dict[str, object]]
    metadata: dict[str, object]


EntityResolver = Callable[[SensorDetection], str]


class SensorFusionEngine:
    def __init__(
        self,
        store: EntityStateStore,
        *,
        bus: DomainEventBus | None = None,
        resolver: EntityResolver | None = None,
    ) -> None:
        self._store = store
        self._bus = bus or NullEventBus()
        self._resolver = resolver or self._default_resolver
        self._sequence = itertools.count(1)
        self._snapshots: dict[str, EntitySnapshot] = {}

    async def load(self) -> None:
        snapshots = await self._store.load_snapshots()
        self._snapshots = {item.entity_id: item for item in snapshots}

    async def ingest(self, detection: SensorDetection) -> EntityEvent:
        entity_id = self._resolver(detection)
        now = datetime.now(UTC)
        expires_at = now + detection.ttl
        event = EntityEvent(
            sequence=next(self._sequence),
            event_type=detection.event_type,
            entity_id=entity_id,
            object_type=detection.object_type,
            provenance=detection.sensor_id,
            components=detection.components,
            expires_at=expires_at,
            updated_at=now,
            metadata={**detection.metadata, "ttl_seconds": detection.ttl.total_seconds()},
        )

        await self._store.apply_event(event)
        await self._publish(event)
        if event.event_type in {"remove", "expire"}:
            self._snapshots.pop(entity_id, None)
        else:
            self._snapshots[entity_id] = EntitySnapshot(
                entity_id=entity_id,
                object_type=event.object_type,
                provenance=event.provenance,
                expires_at=event.expires_at,
                components=event.components,
                updated_at=event.updated_at,
            )
        return event

    async def _publish(self, event: EntityEvent) -> None:
        if isinstance(self._bus, NullEventBus):
            return
        domain_event = RuntimeEntityUpserted(
            entity_id=event.entity_id,
            object_type_api_name=event.object_type,
            provenance=event.provenance,
            payload=event.components,
            metadata=event.metadata,
        )
        self._bus.publish(domain_event)

    def _default_resolver(self, detection: SensorDetection) -> str:
        if detection.entity_hint:
            return detection.entity_hint
        if "entity_id" in detection.metadata:
            value = detection.metadata["entity_id"]
            if isinstance(value, str) and value:
                return value
        identity = detection.components.get("identity")
        if identity and isinstance(identity.get("id"), str):
            return identity["id"]
        return f"{detection.sensor_id}:{uuid4().hex}"


__all__ = [
    "RuntimeEntityUpserted",
    "SensorDetection",
    "SensorFusionEngine",
]
