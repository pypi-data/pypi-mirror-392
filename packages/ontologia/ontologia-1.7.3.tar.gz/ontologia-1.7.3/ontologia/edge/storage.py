from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from ontologia_edge.entity_manager import EntitySnapshot
from ontologia_edge.journal import EntityEvent


class EntityStateStore(Protocol):
    async def load_snapshots(self) -> list[EntitySnapshot]: ...

    async def apply_event(self, event: EntityEvent) -> None: ...


class InMemoryEntityStateStore(EntityStateStore):
    def __init__(self) -> None:
        self._snapshots: dict[str, EntitySnapshot] = {}

    async def load_snapshots(self) -> list[EntitySnapshot]:
        return list(self._snapshots.values())

    async def apply_event(self, event: EntityEvent) -> None:
        if event.event_type in {"remove", "expire"}:
            self._snapshots.pop(event.entity_id, None)
            return
        snapshot = EntitySnapshot(
            entity_id=event.entity_id,
            object_type=event.object_type,
            provenance=event.provenance,
            expires_at=event.expires_at,
            components=event.components,
            updated_at=event.updated_at,
        )
        self._snapshots[event.entity_id] = snapshot


@dataclass(slots=True)
class SQLiteEntityStateStore(EntityStateStore):
    path: Path

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
        )

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    object_type TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    components TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_entities_updated_at
                ON entities(updated_at)
                """
            )
            conn.commit()

    async def load_snapshots(self) -> list[EntitySnapshot]:
        return await asyncio.to_thread(self._load_snapshots_sync)

    def _load_snapshots_sync(self) -> list[EntitySnapshot]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT entity_id, object_type, provenance, expires_at, updated_at, components FROM entities"
            )
            rows = cursor.fetchall()
        snapshots: list[EntitySnapshot] = []
        for entity_id, object_type, provenance, expires_at, updated_at, components_json in rows:
            components = json.loads(components_json)
            expires_dt = datetime.fromisoformat(expires_at)
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=UTC)
            else:
                expires_dt = expires_dt.astimezone(UTC)
            updated_dt = datetime.fromisoformat(updated_at)
            if updated_dt.tzinfo is None:
                updated_dt = updated_dt.replace(tzinfo=UTC)
            else:
                updated_dt = updated_dt.astimezone(UTC)
            snapshots.append(
                EntitySnapshot(
                    entity_id=entity_id,
                    object_type=object_type,
                    provenance=provenance,
                    expires_at=expires_dt,
                    components=components,
                    updated_at=updated_dt,
                )
            )
        return snapshots

    async def apply_event(self, event: EntityEvent) -> None:
        await asyncio.to_thread(self._apply_event_sync, event)

    def _apply_event_sync(self, event: EntityEvent) -> None:
        if event.event_type in {"remove", "expire"}:
            self._delete_entity(event.entity_id)
            return
        self._upsert_entity(event)

    def _upsert_entity(self, event: EntityEvent) -> None:
        payload = json.dumps(event.components)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entities (entity_id, object_type, provenance, expires_at, updated_at, components)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_id) DO UPDATE SET
                    object_type=excluded.object_type,
                    provenance=excluded.provenance,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at,
                    components=excluded.components
                """,
                (
                    event.entity_id,
                    event.object_type,
                    event.provenance,
                    event.expires_at.isoformat(),
                    event.updated_at.isoformat(),
                    payload,
                ),
            )
            conn.commit()

    def _delete_entity(self, entity_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM entities WHERE entity_id = ?", (entity_id,))
            conn.commit()


class RedisEntityStateStore(EntityStateStore):
    def __init__(self, url: str) -> None:
        try:
            import redis.asyncio as redis
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "Redis support requires the 'redis' package. Install it with 'pip install redis'."
            ) from exc

        self._client = redis.from_url(url, decode_responses=True)
        self._namespace = "ontologia:entities"

    async def load_snapshots(self) -> list[EntitySnapshot]:
        keys: list[str] = []
        cursor: str = "0"
        while True:
            cursor, batch = await self._client.scan(cursor=cursor, match=f"{self._namespace}:*")
            keys.extend(batch)
            if cursor == "0":
                break
        snapshots: list[EntitySnapshot] = []
        for key in keys:
            payload = await self._client.get(key)
            if not payload:
                continue
            data = json.loads(payload)
            expires_at = datetime.fromisoformat(data["expires_at"]).replace(tzinfo=UTC)
            updated_at = datetime.fromisoformat(data["updated_at"]).replace(tzinfo=UTC)
            snapshots.append(
                EntitySnapshot(
                    entity_id=data["entity_id"],
                    object_type=data["object_type"],
                    provenance=data["provenance"],
                    expires_at=expires_at,
                    components=data["components"],
                    updated_at=updated_at,
                )
            )
        return snapshots

    async def apply_event(self, event: EntityEvent) -> None:
        key = f"{self._namespace}:{event.entity_id}"
        if event.event_type in {"remove", "expire"}:
            await self._client.delete(key)
            return
        payload = json.dumps(
            {
                "entity_id": event.entity_id,
                "object_type": event.object_type,
                "provenance": event.provenance,
                "expires_at": event.expires_at.isoformat(),
                "updated_at": event.updated_at.isoformat(),
                "components": event.components,
            }
        )
        metadata = event.metadata or {}
        ttl_seconds = metadata.get("ttl_seconds")
        expiry = int(ttl_seconds) if isinstance(ttl_seconds, (int, float)) else None
        await self._client.set(key, payload, ex=expiry if expiry and expiry > 0 else None)


__all__ = [
    "EntityStateStore",
    "InMemoryEntityStateStore",
    "RedisEntityStateStore",
    "SQLiteEntityStateStore",
]
