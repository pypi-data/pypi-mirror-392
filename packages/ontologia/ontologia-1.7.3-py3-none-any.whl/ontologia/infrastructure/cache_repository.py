"""
cache_repository.py
-------------------
Repository for distributed caching operations using Redis.

Provides a unified interface for caching operations with support for
different cache backends, TTL management, and pattern-based invalidation.
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

try:  # pragma: no cover - optional dependency
    import redis
except Exception:  # pragma: no cover - handled at runtime
    redis: Any = None


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: int = 3600) -> bool:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    def delete_by_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern. Returns number of deleted keys."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key. Returns -1 if no TTL, -2 if key doesn't exist."""
        pass


class RedisCacheBackend(CacheBackend):
    """Redis implementation of cache backend."""

    def __init__(self, redis_client: Any):
        """
        Initialize Redis cache backend.

        Args:
            redis_client: Redis client instance
        """
        self.client = redis_client
        self.logger = logging.getLogger(__name__)

    def ping(self) -> bool:
        """Check Redis connection."""
        try:
            return self.client.ping()
        except Exception as e:
            self.logger.error(f"Redis ping error: {e}")
            return False

    def get(self, key: str) -> Any | None:
        """Get value from Redis."""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            if isinstance(value, bytes):
                return value.decode("utf-8")
            return value
        except Exception as e:
            self.logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    def set(self, key: str, value: str, ttl_seconds: int = 3600) -> bool:
        """Set value in Redis with TTL."""
        try:
            self.client.setex(key, ttl_seconds, value)
            return True
        except Exception as e:
            self.logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            result = self.client.delete(key)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    def delete_by_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern using SCAN to avoid blocking."""
        try:
            deleted_count = 0
            for key in self.client.scan_iter(match=pattern):
                self.client.delete(key)
                deleted_count += 1
            return deleted_count
        except Exception as e:
            self.logger.error(f"Redis DELETE_BY_PATTERN error for pattern '{pattern}': {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            result = self.client.exists(key)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get remaining TTL for key."""
        try:
            ttl_value = self.client.ttl(key)
            return int(ttl_value)
        except Exception as e:
            self.logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend for development and testing."""

    def __init__(self):
        """Initialize memory cache backend."""
        self._cache: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def ping(self) -> bool:
        """Ping method to match RedisBackend interface."""
        return True

    def get(self, key: str) -> Any | None:
        """Get value from memory cache."""
        try:
            if key in self._cache:
                entry = self._cache[key]
                if entry.get("expires_at", 0) > 0:
                    import time

                    if time.time() > entry["expires_at"]:
                        del self._cache[key]
                        return None
                return entry["value"]
            return None
        except Exception as e:
            self.logger.error(f"Memory cache GET error for key '{key}': {e}")
            return None

    def set(self, key: str, value: str, ttl_seconds: int = 3600) -> bool:
        """Set value in memory cache with TTL."""
        try:
            import time

            expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else 0
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
            }
            return True
        except Exception as e:
            self.logger.error(f"Memory cache SET error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from memory cache."""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Memory cache DELETE error for key '{key}': {e}")
            return False

    def delete_by_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern from memory cache."""
        try:
            import fnmatch

            keys_to_delete: list[str] = []
            for key in list(self._cache.keys()):
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)
        except Exception as e:
            self.logger.error(f"Memory cache DELETE_BY_PATTERN error for pattern '{pattern}': {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        try:
            if key in self._cache:
                entry = self._cache[key]
                if entry.get("expires_at", 0) > 0:
                    import time

                    if time.time() > entry["expires_at"]:
                        del self._cache[key]
                        return False
                return True
            return False
        except Exception as e:
            self.logger.error(f"Memory cache EXISTS error for key '{key}': {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get remaining TTL for key."""
        try:
            if key in self._cache:
                entry = self._cache[key]
                if entry.get("expires_at", 0) > 0:
                    import time

                    remaining = entry["expires_at"] - time.time()
                    return max(0, int(remaining))
                return -1
            return -2
        except Exception as e:
            self.logger.error(f"Memory cache TTL error for key '{key}': {e}")
            return -2


class CacheRepository:
    """
    High-level repository for caching operations.

    Provides a unified interface for caching with support for
    serialization, compression, and intelligent invalidation.
    """

    def __init__(self, backend: CacheBackend, default_ttl: int = 3600):
        """
        Initialize cache repository.

        Args:
            backend: Cache backend implementation
            default_ttl: Default TTL in seconds
        """
        self.backend = backend
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)

    def get(self, key: str, *, deserialize: bool = True) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key
            deserialize: Whether to deserialize JSON value

        Returns:
            Cached value or None
        """
        try:
            value = self.backend.get(key)
            if value is None:
                return None

            if deserialize:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return value

        except Exception as e:
            self.logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
        serialize: bool = True,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: TTL in seconds (uses default if None)
            serialize: Whether to serialize value to JSON

        Returns:
            True if successful
        """
        try:
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl

            if serialize:
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)

            return self.backend.set(key, serialized_value, ttl)

        except Exception as e:
            self.logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            return self.backend.delete(key)
        except Exception as e:
            self.logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def delete_by_pattern(self, pattern: str) -> int:
        """
        Delete keys matching pattern.

        Args:
            pattern: Pattern to match (supports wildcards)

        Returns:
            Number of keys deleted
        """
        try:
            deleted_count = self.backend.delete_by_pattern(pattern)
            self.logger.info(f"Deleted {deleted_count} cache keys matching pattern '{pattern}'")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Cache delete_by_pattern error for pattern '{pattern}': {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            return self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    def get_or_set(
        self,
        key: str,
        value_func,
        *,
        ttl_seconds: int | None = None,
        serialize: bool = True,
    ) -> Any:
        """
        Get value from cache or set it if not exists.

        Args:
            key: Cache key
            value_func: Function to generate value if not cached
            ttl_seconds: TTL in seconds
            serialize: Whether to serialize value

        Returns:
            Cached or generated value
        """
        # Try to get from cache first
        cached_value = self.get(key, deserialize=serialize)
        if cached_value is not None:
            return cached_value

        # Generate new value
        try:
            new_value = value_func() if callable(value_func) else value_func

            # Cache the new value
            self.set(key, new_value, ttl_seconds=ttl_seconds, serialize=serialize)

            return new_value

        except Exception as e:
            self.logger.error(f"Error in get_or_set for key '{key}': {e}")
            raise

    def build_key(self, *parts: str, separator: str = ":") -> str:
        """
        Build cache key from parts.

        Args:
            *parts: Key parts
            separator: Separator between parts

        Returns:
            Complete cache key
        """
        return separator.join(str(part) for part in parts if part)

    def build_object_type_pattern(self, object_type: str) -> str:
        """
        Build pattern for invalidating all cache entries for an object type.

        Args:
            object_type: Object type API name

        Returns:
            Cache pattern
        """
        return f"*:{object_type}:*"

    def build_query_pattern(self, object_type: str) -> str:
        """
        Build pattern for invalidating query cache entries for an object type.

        Args:
            object_type: Object type API name

        Returns:
            Cache pattern
        """
        return f"query:{object_type}:*"

    def invalidate_object_type(self, object_type: str) -> int:
        """
        Invalidate all cache entries for an object type.

        Args:
            object_type: Object type API name

        Returns:
            Number of keys invalidated
        """
        pattern = self.build_object_type_pattern(object_type)
        return self.delete_by_pattern(pattern)

    def invalidate_queries(self, object_type: str) -> int:
        """
        Invalidate query cache entries for an object type.

        Args:
            object_type: Object type API name

        Returns:
            Number of keys invalidated
        """
        pattern = self.build_query_pattern(object_type)
        return self.delete_by_pattern(pattern)


# Factory functions for creating cache repositories


logger = logging.getLogger(__name__)


def create_cache_repository(
    backend: CacheBackend | None = None,
    default_ttl: int = 3600,
) -> CacheRepository:
    """
    Create cache repository with Redis as default backend.

    Args:
        backend: Cache backend instance (optional, defaults to Redis)
        default_ttl: Default TTL in seconds

    Returns:
        CacheRepository instance
    """
    if backend is not None:
        return CacheRepository(backend, default_ttl)

    # Try Redis backend first for production
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    if redis is None:
        logger.warning(
            "redis package is not installed; install the 'realtime' dependency group to enable Redis caching"
        )
        backend = MemoryCacheBackend()
    else:
        try:
            redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
            # Test connection with timeout
            redis_client.ping()
            backend = RedisCacheBackend(redis_client)
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.warning(
                f"Failed to connect to Redis at {redis_url}: {e}; falling back to memory cache"
            )
            backend = MemoryCacheBackend()

    return CacheRepository(backend, default_ttl)


def create_memory_cache_repository(default_ttl: int = 3600) -> CacheRepository:
    """
    Create memory-based cache repository for development/testing.

    Args:
        default_ttl: Default TTL in seconds

    Returns:
        CacheRepository instance
    """
    backend = MemoryCacheBackend()
    return CacheRepository(backend, default_ttl)


def create_redis_cache_repository(
    redis_url: str | None = "redis://localhost:6379",
    default_ttl: int = 3600,
) -> CacheRepository:
    """
    Create Redis-based cache repository.

    Args:
        redis_url: Redis connection URL
        default_ttl: Default TTL in seconds

    Returns:
        CacheRepository instance
    """
    if not redis_url:
        logger.warning("Redis URL not provided; using memory cache backend")
        return CacheRepository(MemoryCacheBackend(), default_ttl)

    if redis is None:
        logger.error(
            "redis package is not installed; install the 'realtime' dependency group to enable Redis"
        )
        return CacheRepository(MemoryCacheBackend(), default_ttl)

    try:
        redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
        # Fail fast if the connection string is invalid
        redis_client.ping()
    except Exception as e:  # pragma: no cover - requires external service
        logger.error("Failed to connect to Redis at %s: %s", redis_url, e)
        return CacheRepository(MemoryCacheBackend(), default_ttl)

    logger.info("Redis cache backend enabled for %s", redis_url)
    backend = RedisCacheBackend(redis_client)
    return CacheRepository(backend, default_ttl)
