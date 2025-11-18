"""
redis.py
--------
Redis connection management and configuration.

Provides centralized Redis client management with support for
connection pooling, retry logic, and graceful fallbacks.
"""

from __future__ import annotations

import logging
from typing import Any

# Note: This is a mock implementation for now.
# In production, you would install and use redis-py:
# pip install redis
# import redis.asyncio as redis
# import redis

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Any | None = None


class RedisConfig:
    """Configuration for Redis connection."""

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        max_connections: int = 10,
        *,
        retry_on_timeout: bool = True,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        health_check_interval: int = 30,
    ):
        """
        Initialize Redis configuration.

        Args:
            url: Redis connection URL
            max_connections: Maximum connection pool size
            retry_on_timeout: Whether to retry on timeout
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            health_check_interval: Health check interval in seconds
        """
        self.url = url
        self.max_connections = max_connections
        self.retry_on_timeout = retry_on_timeout
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.health_check_interval = health_check_interval


def get_redis_client(config: RedisConfig | None = None, *, force_new: bool = False) -> Any:
    """
    Get Redis client instance.

    Args:
        config: Redis configuration
        force_new: Whether to create a new client instance

    Returns:
        Redis client instance (mock for development)
    """
    global _redis_client

    if _redis_client is None or force_new:
        if config is None:
            config = RedisConfig()

        try:
            # In production, create real Redis client:
            # _redis_client = redis.from_url(
            #     config.url,
            #     max_connections=config.max_connections,
            #     retry_on_timeout=config.retry_on_timeout,
            #     socket_timeout=config.socket_timeout,
            #     socket_connect_timeout=config.socket_connect_timeout,
            #     health_check_interval=config.health_check_interval,
            # )

            # Mock client for development
            _redis_client = MockRedisClient(config.url)

            logger.info(f"Redis client created: {config.url}")

        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            # Return mock client as fallback
            _redis_client = MockRedisClient(config.url)
            logger.warning("Using mock Redis client due to connection failure")

    return _redis_client


async def test_redis_connection(redis_client: Any) -> bool:
    """
    Test Redis connection.

    Args:
        redis_client: Redis client instance

    Returns:
        True if connection is successful
    """
    try:
        # In production:
        # await redis_client.ping()
        # return True

        # Mock implementation
        if hasattr(redis_client, "ping"):
            result = await redis_client.ping()
            return result
        return True

    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        return False


def close_redis_connection() -> None:
    """Close Redis connection."""
    global _redis_client

    if _redis_client:
        try:
            # In production:
            # await _redis_client.close()

            logger.info("Redis connection closed")

        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        finally:
            _redis_client = None


class MockRedisClient:
    """Mock Redis client for development and testing."""

    def __init__(self, url: str):
        """
        Initialize mock Redis client.

        Args:
            url: Redis URL (for logging purposes)
        """
        self.url = url
        self._data: dict[str, bytes] = {}
        self.logger = logging.getLogger(__name__)

    async def ping(self) -> bool:
        """Mock ping operation."""
        return True

    async def get(self, key: str) -> bytes | None:
        """Mock get operation."""
        return self._data.get(key.encode())

    async def setex(self, key: str, seconds: int, value: str) -> bool:
        """Mock set with expiration."""
        self._data[key.encode()] = value.encode()
        return True

    async def delete(self, key: str) -> int:
        """Mock delete operation."""
        key_bytes = key.encode()
        if key_bytes in self._data:
            del self._data[key_bytes]
            return 1
        return 0

    async def exists(self, key: str) -> int:
        """Mock exists operation."""
        return 1 if key.encode() in self._data else 0

    async def ttl(self, key: str) -> int:
        """Mock TTL operation."""
        return -1 if key.encode() in self._data else -2

    async def scan_iter(self, match: str = "*", count: int = 10) -> list[str]:
        """Mock scan_iter operation."""
        import fnmatch

        # pattern unused; match is used directly below
        keys = []
        for key in self._data.keys():
            key_str = key.decode()
            if fnmatch.fnmatch(key_str, match):
                keys.append(key_str)
                if len(keys) >= count:
                    break
        return keys

    async def close(self) -> None:
        """Mock close operation."""
        self._data.clear()
        self.logger.info("Mock Redis client closed")


def create_redis_config_from_env() -> RedisConfig:
    """
    Create Redis configuration from environment variables.

    Returns:
        RedisConfig instance
    """
    import os

    return RedisConfig(
        url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        retry_on_timeout=os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
        socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
        socket_connect_timeout=float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0")),
        health_check_interval=int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30")),
    )


# Health check utilities


async def check_redis_health(redis_client: Any) -> dict[str, Any]:
    """
    Check Redis health status.

    Args:
        redis_client: Redis client instance

    Returns:
        Health status dictionary
    """
    try:
        start_time = __import__("time").time()

        # Test basic connectivity
        ping_result = await test_redis_connection(redis_client)

        # Test basic operations
        test_key = "health_check_test"
        await redis_client.setex(test_key, 1, "test_value")
        get_result = await redis_client.get(test_key)
        await redis_client.delete(test_key)

        response_time = (__import__("time").time() - start_time) * 1000

        return {
            "status": "healthy" if ping_result and get_result else "unhealthy",
            "ping": ping_result,
            "basic_operations": get_result is not None,
            "response_time_ms": round(response_time, 2),
            "url": getattr(redis_client, "url", "unknown"),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "url": getattr(redis_client, "url", "unknown"),
        }


def get_redis_info(redis_client: Any) -> dict[str, Any]:
    """
    Get Redis server information.

    Args:
        redis_client: Redis client instance

    Returns:
        Redis info dictionary
    """
    try:
        # In production:
        # info = await redis_client.info()
        # return {
        #     "version": info.get("redis_version"),
        #     "used_memory": info.get("used_memory_human"),
        #     "connected_clients": info.get("connected_clients"),
        #     "uptime_in_seconds": info.get("uptime_in_seconds")
        # }

        # Mock implementation
        return {
            "version": "mock-7.0.0",
            "used_memory": "1MB",
            "connected_clients": 1,
            "uptime_in_seconds": 3600,
            "url": getattr(redis_client, "url", "unknown"),
            "note": "Mock Redis client for development",
        }

    except Exception as e:
        return {"error": str(e), "url": getattr(redis_client, "url", "unknown")}
