from __future__ import annotations

import os
import time


class DedupBackend:
    async def is_new(
        self, msg_id: str, *, node_id: str | None, ttl: int | None
    ) -> bool:  # pragma: no cover - interface
        raise NotImplementedError


class _RedisDedup(DedupBackend):
    def __init__(self, url: str) -> None:
        try:
            import redis.asyncio as redis  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Redis backend requires 'redis' package.") from exc
        self._client = redis.from_url(url, decode_responses=True)
        self._key = "ontologia:edge:dedup"

    async def is_new(self, msg_id: str, *, node_id: str | None, ttl: int | None) -> bool:
        expiry = int(ttl) if ttl and ttl > 0 else 60
        key = f"{self._key}:{msg_id}"
        # SETNX then EXPIRE
        was_set = await self._client.setnx(key, node_id or "")
        if was_set:
            await self._client.expire(key, expiry)
            return True
        return False


class _NullDedup(DedupBackend):
    def __init__(self) -> None:
        self._seen: dict[str, float] = {}

    async def is_new(self, msg_id: str, *, node_id: str | None, ttl: int | None) -> bool:
        now = time.time()
        expiry = now + (ttl if ttl and ttl > 0 else 60)
        # cleanup
        for k, v in list(self._seen.items()):
            if v <= now:
                del self._seen[k]
        if msg_id in self._seen:
            return False
        self._seen[msg_id] = expiry
        return True


_backend: DedupBackend | None = None


def get_dedup_backend() -> DedupBackend:
    global _backend
    if _backend is not None:
        return _backend
    url = os.getenv("REDIS_URL") or os.getenv("EDGE_REDIS_URL")
    if url:
        try:
            _backend = _RedisDedup(url)
            return _backend
        except Exception:
            _backend = _NullDedup()
            return _backend
    _backend = _NullDedup()
    return _backend


__all__ = ["get_dedup_backend", "DedupBackend"]
