from __future__ import annotations

import os
import time


class _TokenBucket:
    def __init__(self, capacity: int, refill_per_sec: float) -> None:
        self.capacity = max(1, capacity)
        self.refill = max(0.01, refill_per_sec)
        self.tokens = float(capacity)
        self.updated_at = time.time()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.updated_at
        self.updated_at = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class _MemoryLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, _TokenBucket] = {}

    def allow(self, key: str, capacity: int, per_seconds: int) -> bool:
        refill = capacity / max(1, per_seconds)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _TokenBucket(capacity, refill)
            self._buckets[key] = bucket
        return bucket.allow(1.0)


class _RedisLimiter:
    def __init__(self, url: str) -> None:
        try:
            import redis.asyncio as redis  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError("Redis required for rate limiter") from exc
        self._r = redis.from_url(url, decode_responses=True)

    async def allow(self, key: str, capacity: int, per_seconds: int) -> bool:
        # Sliding window counter with TTL
        window = max(1, per_seconds)
        now = int(time.time())
        bucket_key = f"ontologia:edge:rl:{key}:{now // window}"
        count = await self._r.incr(bucket_key)
        if count == 1:
            await self._r.expire(bucket_key, window + 1)
        return count <= capacity


_limiter: _MemoryLimiter | _RedisLimiter | None = None


def _get_limits(prefix: str, default_capacity: int, default_window: int) -> tuple[int, int]:
    cap = int(os.getenv(f"EDGE_RL_{prefix}_CAP", str(default_capacity)))
    win = int(os.getenv(f"EDGE_RL_{prefix}_WIN", str(default_window)))
    return cap, win


def limiter_backend() -> _MemoryLimiter | _RedisLimiter:
    global _limiter
    if _limiter is not None:
        return _limiter
    url = os.getenv("REDIS_URL") or os.getenv("EDGE_REDIS_URL")
    if url:
        try:
            _limiter = _RedisLimiter(url)
            return _limiter
        except Exception:
            pass
    _limiter = _MemoryLimiter()
    return _limiter


async def rate_limit(key: str, *, prefix: str, default_capacity: int, default_window: int) -> bool:
    cap, win = _get_limits(prefix, default_capacity, default_window)
    backend = limiter_backend()
    if isinstance(backend, _RedisLimiter):
        return await backend.allow(key, cap, win)
    return backend.allow(key, cap, win)
