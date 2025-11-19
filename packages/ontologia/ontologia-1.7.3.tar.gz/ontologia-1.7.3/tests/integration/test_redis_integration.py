"""
Redis Integration Tests
-----------------------

Integration tests for Redis cache operations using the CacheRepository
with RedisCacheBackend.

These tests validate that our Redis integration works correctly
with a real Redis instance for caching functionality.
"""

import time

import pytest

# Optional dependency guard
try:  # pragma: no cover
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore
    pytestmark = pytest.mark.skip(reason="Redis not available in this environment")

from ontologia.infrastructure.cache_repository import (
    CacheRepository,
    RedisCacheBackend,
    create_redis_cache_repository,
)


class TestRedisIntegration:
    """Test Redis cache repository integration."""

    def test_basic_crud_operations(self, redis_client, integration_test_config: dict):
        """Test basic Redis CRUD operations."""
        # Create cache repository with Redis backend
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Test basic set/get operations
        key = "test:basic:123"
        value = {"id": 123, "name": "Test Object", "data": "value"}

        # Set value
        result = cache_repo.set(key, value)
        assert result is True

        # Get value
        retrieved = cache_repo.get(key)
        assert retrieved is not None
        assert retrieved["id"] == 123
        assert retrieved["name"] == "Test Object"

        # Test delete
        result = cache_repo.delete(key)
        assert result is True

        # Verify deletion
        retrieved = cache_repo.get(key)
        assert retrieved is None

        # Test exists
        assert cache_repo.exists(key) is False

    def test_expiration_and_ttl(self, redis_client, integration_test_config: dict):
        """Test Redis key expiration and TTL functionality."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        key = "test:expiration"
        value = "expires_soon"

        # Set with short TTL
        result = cache_repo.set(key, value, ttl_seconds=2)  # 2 seconds
        assert result is True

        # Verify it exists
        assert cache_repo.exists(key) is True
        retrieved = cache_repo.get(key)
        assert retrieved == value

        # Check TTL
        ttl = cache_repo.backend.ttl(key)
        assert ttl > 0 and ttl <= 2

        # Wait for expiration
        time.sleep(3)

        # Verify it's expired
        assert cache_repo.exists(key) is False
        retrieved = cache_repo.get(key)
        assert retrieved is None

    def test_get_or_set_pattern(self, redis_client, integration_test_config: dict):
        """Test the get_or_set pattern."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        key = "test:get_or_set"
        expensive_value = {"computed": True, "data": [1, 2, 3, 4, 5]}

        # First call - should compute and set
        result = cache_repo.get_or_set(key, lambda: expensive_value, ttl_seconds=60)
        assert result == expensive_value

        # Verify it was set
        assert cache_repo.exists(key) is True

        # Second call - should return cached value
        result = cache_repo.get_or_set(
            key, lambda: {"should": "not", "be": "called"}  # This shouldn't execute
        )
        assert result == expensive_value

    def test_pattern_based_invalidation(self, redis_client, integration_test_config: dict):
        """Test pattern-based cache invalidation."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Set multiple keys with same pattern
        keys = [
            "user:123:profile",
            "user:123:preferences",
            "user:123:history",
            "user:456:profile",
            "user:456:preferences",
        ]

        for key in keys:
            cache_repo.set(key, {"data": f"value_for_{key}"})

        # Verify all keys exist
        for key in keys:
            assert cache_repo.exists(key) is True

        # Delete by pattern for user 123
        deleted_count = cache_repo.delete_by_pattern("user:123:*")
        assert deleted_count == 3

        # Verify user 123 keys are deleted
        assert cache_repo.exists("user:123:profile") is False
        assert cache_repo.exists("user:123:preferences") is False
        assert cache_repo.exists("user:123:history") is False

        # Verify user 456 keys still exist
        assert cache_repo.exists("user:456:profile") is True
        assert cache_repo.exists("user:456:preferences") is True

    def test_serialization_edge_cases(self, redis_client, integration_test_config: dict):
        """Test serialization of complex data types."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Test complex nested structure
        complex_value = {
            "nested": {
                "dict": {"key": "value"},
                "list": [1, 2, 3, {"inner": "dict"}],
                "tuple": (1, 2, 3),  # Will be converted to list
                "none": None,
                "bool": True,
                "int": 42,
                "float": 3.14159,
            },
            "string": "test string",
            "empty_dict": {},
            "empty_list": [],
        }

        key = "test:complex"
        result = cache_repo.set(key, complex_value)
        assert result is True

        retrieved = cache_repo.get(key)
        assert retrieved is not None
        assert retrieved["nested"]["dict"]["key"] == "value"
        assert retrieved["nested"]["list"][3]["inner"] == "dict"
        assert retrieved["nested"]["bool"] is True
        assert retrieved["nested"]["int"] == 42
        assert retrieved["nested"]["float"] == 3.14159
        assert retrieved["nested"]["none"] is None
        # Tuple becomes list during JSON serialization
        assert retrieved["nested"]["tuple"] == [1, 2, 3]

    def test_factory_functions(self, integration_test_config: dict):
        """Test cache repository factory functions."""
        # Test factory function
        cache_repo = create_redis_cache_repository(
            integration_test_config["redis"]["url"], default_ttl=600
        )

        assert isinstance(cache_repo, CacheRepository)
        assert isinstance(cache_repo.backend, RedisCacheBackend)

        # Test basic functionality
        key = "test:factory"
        value = {"factory": "test"}

        result = cache_repo.set(key, value)
        assert result is True

        retrieved = cache_repo.get(key)
        assert retrieved == value

    def test_error_handling(self, redis_client, integration_test_config: dict):
        """Test error handling in Redis operations."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Test operations on non-existent key
        assert cache_repo.get("non:existent:key") is None
        assert cache_repo.exists("non:existent:key") is False
        assert (
            cache_repo.delete("non:existent:key") is False
        )  # Delete returns False for non-existent key
        assert cache_repo.backend.ttl("non:existent:key") == -2  # -2 means key doesn't exist

        # Test get_or_set with function that raises exception
        def failing_function():
            raise ValueError("Test exception")

        with pytest.raises(ValueError):
            cache_repo.get_or_set("test:failing", failing_function)

        # Key should not be set after failed function
        assert cache_repo.exists("test:failing") is False

    def test_key_building_utilities(self, redis_client, integration_test_config: dict):
        """Test cache key building utilities."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Test key building methods
        user_key = cache_repo.build_key("user", str(123), "profile")  # type: ignore[arg-type]
        assert user_key == "user:123:profile"

        # Test with different separators
        custom_key = cache_repo.build_key("api", "v1", "users", str(456), separator="/")  # type: ignore[arg-type]
        assert custom_key == "api/v1/users/456"

        # Test key prefixing (manual for now)
        prefixed_key = cache_repo.build_key("myapp", "user", str(123))  # type: ignore[arg-type]
        assert prefixed_key == "myapp:user:123"

        # Use the built keys
        value = {"test": "key_building"}
        result = cache_repo.set(user_key, value)
        assert result is True

        retrieved = cache_repo.get(user_key)
        assert retrieved == value

    def test_performance_with_large_data(self, redis_client, integration_test_config: dict):
        """Test performance with larger data sets."""
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Create a large data structure
        large_data = {
            "items": [{"id": i, "data": f"item_{i}"} for i in range(1000)],
            "metadata": {
                "total": 1000,
                "page": 1,
                "per_page": 1000,
                "description": "Large dataset for performance testing",
            },
        }

        key = "test:large_data"

        # Time the set operation
        start_time = time.time()
        result = cache_repo.set(key, large_data)
        set_time = time.time() - start_time

        assert result is True
        assert set_time < 1.0  # Should complete within 1 second

        # Time the get operation
        start_time = time.time()
        retrieved = cache_repo.get(key)
        get_time = time.time() - start_time

        assert retrieved is not None
        assert len(retrieved["items"]) == 1000
        assert retrieved["metadata"]["total"] == 1000
        assert get_time < 0.5  # Should complete within 0.5 seconds

        # Verify data integrity
        assert retrieved["items"][500]["id"] == 500
        assert retrieved["items"][500]["data"] == "item_500"
