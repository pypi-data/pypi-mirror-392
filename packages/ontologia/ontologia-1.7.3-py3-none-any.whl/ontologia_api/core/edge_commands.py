from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import time
from typing import Any


@dataclass(slots=True)
class EnqueuedCommand:
    id: str
    node_id: str
    target: str
    action: str
    payload: dict[str, Any]
    timestamp: float


class CommandQueue:
    async def enqueue(
        self, cmd: EnqueuedCommand, *, ttl: int | None = None
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def pull(
        self, node_id: str, *, max_items: int = 10
    ) -> list[EnqueuedCommand]:  # pragma: no cover - interface
        raise NotImplementedError

    async def pull_blocking(
        self, node_id: str, *, timeout: int = 0, max_items: int = 10
    ) -> list[EnqueuedCommand]:
        # Default: poll using pull()
        if timeout <= 0:
            return await self.pull(node_id, max_items=max_items)
        import asyncio

        end = time() + timeout
        while time() < end:
            items = await self.pull(node_id, max_items=max_items)
            if items:
                return items
            await asyncio.sleep(0.5)
        return []


class _RedisCommandQueue(CommandQueue):
    def __init__(self, url: str) -> None:
        try:
            import redis.asyncio as redis  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Redis backend requires 'redis' package.") from exc
        self._client = redis.from_url(url, decode_responses=True)
        self._prefix = "ontologia:edge:cmd"

    def _key(self, node_id: str) -> str:
        return f"{self._prefix}:{node_id}"

    async def enqueue(self, cmd: EnqueuedCommand, *, ttl: int | None = None) -> None:
        key = self._key(cmd.node_id)
        payload = json.dumps(cmd.__dict__, ensure_ascii=False)
        # Push to the right (FIFO)
        await self._client.rpush(key, payload)
        # Set TTL on the list key if provided
        if ttl and ttl > 0:
            await self._client.expire(key, ttl)

    async def pull(self, node_id: str, *, max_items: int = 10) -> list[EnqueuedCommand]:
        key = self._key(node_id)
        # Get up to N items via LRANGE then trim
        items = await self._client.lrange(key, 0, max_items - 1)
        if not items:
            return []
        await self._client.ltrim(key, len(items), -1)
        result: list[EnqueuedCommand] = []
        for raw in items:
            try:
                data = json.loads(raw)
                result.append(EnqueuedCommand(**data))
            except Exception:
                continue
        return result

    async def pull_blocking(
        self, node_id: str, *, timeout: int = 0, max_items: int = 10
    ) -> list[EnqueuedCommand]:
        if timeout <= 0:
            return await self.pull(node_id, max_items=max_items)
        key = self._key(node_id)
        result: list[EnqueuedCommand] = []
        remaining = max_items
        deadline = time() + timeout
        while remaining > 0 and time() < deadline:
            # BLPOP returns [key, value] or None on timeout
            item = await self._client.blpop(key, timeout=max(1, int(deadline - time())))
            if not item:
                break
            _, raw = item
            try:
                data = json.loads(raw)
                result.append(EnqueuedCommand(**data))
                remaining -= 1
            except Exception:
                continue
        return result


class _InMemoryCommandQueue(CommandQueue):
    def __init__(self) -> None:
        self._queues: dict[str, list[EnqueuedCommand]] = {}

    async def enqueue(self, cmd: EnqueuedCommand, *, ttl: int | None = None) -> None:
        self._queues.setdefault(cmd.node_id, []).append(cmd)

    async def pull(self, node_id: str, *, max_items: int = 10) -> list[EnqueuedCommand]:
        queue = self._queues.get(node_id) or []
        if not queue:
            return []
        items = queue[:max_items]
        self._queues[node_id] = queue[max_items:]
        return items


_queue: CommandQueue | None = None


def get_command_queue() -> CommandQueue:
    global _queue
    if _queue is not None:
        return _queue
    url = os.getenv("REDIS_URL") or os.getenv("EDGE_REDIS_URL")
    if url:
        try:
            _queue = _RedisCommandQueue(url)
            return _queue
        except Exception:
            _queue = _InMemoryCommandQueue()
            return _queue
    _queue = _InMemoryCommandQueue()
    return _queue


def new_command_id() -> str:
    # Use timestamp-based simple id; can be replaced with ULID
    return hex(int(time() * 1_000_000))[2:]


__all__ = [
    "EnqueuedCommand",
    "get_command_queue",
    "new_command_id",
]
