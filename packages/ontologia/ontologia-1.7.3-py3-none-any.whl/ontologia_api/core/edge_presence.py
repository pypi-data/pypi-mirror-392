from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any


class PresenceBackend:
    async def upsert(
        self, node_id: str, payload: dict[str, Any], *, ttl: int | None = None
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class _RedisPresence(PresenceBackend):
    def __init__(self, url: str) -> None:
        try:
            import redis.asyncio as redis  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Redis backend requires 'redis' package.") from exc
        self._client = redis.from_url(url, decode_responses=True)
        self._key = "ontologia:edge:presence"

    async def upsert(
        self, node_id: str, payload: dict[str, Any], *, ttl: int | None = None
    ) -> None:
        expiry = ttl if ttl and ttl > 0 else 120
        key = f"{self._key}:{node_id}"
        data = json.dumps(
            {"node_id": node_id, "payload": payload, "updated_at": datetime.now(UTC).isoformat()}
        )
        await self._client.set(key, data, ex=expiry)


class _NullPresence(PresenceBackend):
    async def upsert(
        self, node_id: str, payload: dict[str, Any], *, ttl: int | None = None
    ) -> None:
        return None


_presence_backend: PresenceBackend | None = None


def get_presence_backend() -> PresenceBackend:
    global _presence_backend
    if _presence_backend is not None:
        return _presence_backend
    url = os.getenv("REDIS_URL") or os.getenv("EDGE_REDIS_URL")
    if url:
        try:
            _presence_backend = _RedisPresence(url)
            return _presence_backend
        except Exception:
            # Fallback to null if redis not available
            _presence_backend = _NullPresence()
            return _presence_backend
    _presence_backend = _NullPresence()
    return _presence_backend


__all__ = ["get_presence_backend", "PresenceBackend"]
