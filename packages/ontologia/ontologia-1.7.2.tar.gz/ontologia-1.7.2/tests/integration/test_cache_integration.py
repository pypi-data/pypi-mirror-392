"""
Integration tests for cache repository.

These tests validate that our cache integration works correctly
with a real Redis instance for distributed caching.
"""

import time

import pytest

from ontologia.infrastructure.cache_repository import (
    CacheRepository,
    RedisCacheBackend,
    create_cache_repository,
    create_redis_cache_repository,
)


class TestCacheIntegration:
    """Test cache repository integration with Redis."""

    def test_basic_cache_operations(self, redis_client, integration_test_config: dict):
        """Test basic cache set/get/delete operations."""
        # Create cache repository with Redis backend
        redis_backend = RedisCacheBackend(redis_client)
        cache_repo = CacheRepository(redis_backend, default_ttl=300)

        # Test set and get with serialization
        key = "test:object:123"
        value = {
            "id": 123,
            "name": "Test Object",
            "type": "test_type",
            "properties": {"key": "value"},
            "created_at": "2024-01-01T00:00:00Z",
        }

        # Set value
        result = cache_repo.set(key, value)
        assert result is True

        # Get value
        retrieved = cache_repo.get(key)
        assert retrieved is not None
        assert retrieved["id"] == 123
        assert retrieved["name"] == "Test Object"
        assert retrieved["properties"]["key"] == "value"

        # Test delete
        result = cache_repo.delete(key)
        assert result is True

        # Verify deletion
        retrieved = cache_repo.get(key)
        assert retrieved is None

    def test_ttl_and_expiration(self, integration_test_config: dict):
        """Test cache TTL and expiration functionality."""
        cache_repo = create_redis_cache_repository(
            integration_test_config["redis"]["url"], default_ttl=300
        )

        key = "test:expiration"
        value = {"data": "expires_soon"}

        # Set with custom TTL
        result = cache_repo.set(key, value, ttl_seconds=2)
        assert result is True

        # Verify key exists
        assert cache_repo.exists(key) is True

        # Check TTL
        ttl = cache_repo.backend.ttl(key)
        assert 1 <= ttl <= 2  # Should be 1 or 2 seconds

        # Wait for expiration
        time.sleep(3)

        # Verify key expired
        assert cache_repo.exists(key) is False
        assert cache_repo.get(key) is None

    def test_get_or_set_pattern(self, integration_test_config: dict):
        """Test the get_or_set caching pattern."""
        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        key = "test:get_or_set"

        # First call should execute function and cache result
        call_count = 0

        def expensive_operation():
            nonlocal call_count
            call_count += 1
            return {"result": f"computed_{call_count}", "timestamp": time.time()}

        # First call - should execute function
        result1 = cache_repo.get_or_set(key, expensive_operation)
        assert result1["result"] == "computed_1"
        assert call_count == 1

        # Second call - should use cached value
        result2 = cache_repo.get_or_set(key, expensive_operation)
        assert result2["result"] == "computed_1"  # Same result as first call
        assert call_count == 1  # Function not called again

        # Verify same timestamp (cached value)
        assert result1["timestamp"] == result2["timestamp"]

    def test_pattern_based_invalidation(self, integration_test_config: dict):
        """Test cache invalidation using patterns."""
        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        object_type = "test_object"

        # Create multiple cache keys for the same object type
        keys = [
            f"object:{object_type}:123",
            f"object:{object_type}:456",
            f"query:{object_type}:list",
            f"query:{object_type}:search:term",
            "other:unrelated:key",
        ]

        # Set values for all keys
        for key in keys:
            cache_repo.set(key, {"data": f"value_for_{key}"})

        # Verify all keys exist
        for key in keys:
            assert cache_repo.exists(key) is True

        # Invalidate object type patterns
        deleted_count = cache_repo.invalidate_object_type(object_type)
        assert deleted_count == 2  # Should delete object:* keys

        # Verify object keys are deleted but others remain
        assert cache_repo.exists(f"object:{object_type}:123") is False
        assert cache_repo.exists(f"object:{object_type}:456") is False
        assert cache_repo.exists(f"query:{object_type}:list") is True
        assert cache_repo.exists("other:unrelated:key") is True

        # Invalidate query patterns
        deleted_count = cache_repo.invalidate_queries(object_type)
        assert deleted_count == 2  # Should delete query:* keys

        # Verify query keys are deleted
        assert cache_repo.exists(f"query:{object_type}:list") is False
        assert cache_repo.exists(f"query:{object_type}:search:term") is False
        assert cache_repo.exists("other:unrelated:key") is True

    def test_key_building_utilities(self, integration_test_config: dict):
        """Test cache key building utilities."""
        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        # Test basic key building
        key = cache_repo.build_key("object", "test_type", "123")
        assert key == "object:test_type:123"

        # Test custom separator
        key = cache_repo.build_key("object", "test_type", "123", separator="_")
        assert key == "object_test_type_123"

        # Test empty parts are filtered out
        key = cache_repo.build_key("object", "", "test_type", "123", None)  # type: ignore[arg-type]
        assert key == "object:test_type:123"

        # Test object type pattern building
        pattern = cache_repo.build_object_type_pattern("test_type")
        assert pattern == "*:test_type:*"

        # Test query pattern building
        pattern = cache_repo.build_query_pattern("test_type")
        assert pattern == "query:test_type:*"

    def test_serialization_edge_cases(self, integration_test_config: dict):
        """Test serialization of complex data types."""
        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        # Test complex nested structure
        complex_value = {
            "id": 123,
            "name": "Test",
            "nested": {
                "array": [1, 2, 3, {"nested": "value"}],
                "dict": {"key": "value", "number": 42.5},
                "boolean": True,
                "null": None,
            },
            "unicode": "测试 🚀",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        key = "test:complex"

        # Set complex value
        result = cache_repo.set(key, complex_value)
        assert result is True

        # Get and verify
        retrieved = cache_repo.get(key)
        assert retrieved is not None
        assert retrieved["id"] == 123
        assert retrieved["nested"]["array"][3]["nested"] == "value"
        assert retrieved["unicode"] == "测试 🚀"
        assert retrieved["nested"]["null"] is None

        # Test non-serialized storage
        raw_key = "test:raw"
        raw_value = "simple_string_value"

        result = cache_repo.set(raw_key, raw_value, serialize=False)
        assert result is True

        retrieved = cache_repo.get(raw_key, deserialize=False)
        assert retrieved == raw_value

    def test_cache_factory_functions(self, integration_test_config: dict):
        """Test cache repository factory functions."""
        # Test create_redis_cache_repository
        redis_repo = create_redis_cache_repository(
            integration_test_config["redis"]["url"], default_ttl=600
        )
        assert isinstance(redis_repo, CacheRepository)
        assert redis_repo.default_ttl == 600

        # Test basic operation
        result = redis_repo.set("factory:test", {"value": "test"})
        assert result is True

        retrieved = redis_repo.get("factory:test")
        assert retrieved is not None
        assert retrieved["value"] == "test"  # type: ignore[index]

        # Test create_cache_repository with explicit Redis URL
        explicit_repo = create_cache_repository(default_ttl=1200)
        assert isinstance(explicit_repo, CacheRepository)
        assert explicit_repo.default_ttl == 1200

    def test_error_handling_and_resilience(self, integration_test_config: dict):
        """Test error handling and resilience patterns."""
        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        # Test get_or_set with function that raises exception
        def failing_function():
            raise ValueError("Simulated error")

        key = "test:error"

        # Should propagate the exception
        with pytest.raises(ValueError, match="Simulated error"):
            cache_repo.get_or_set(key, failing_function)

        # Verify no value was cached
        assert cache_repo.get(key) is None

        # Test with non-callable value
        static_value = {"data": "static"}
        result = cache_repo.get_or_set(key, static_value)
        assert result == static_value
        assert cache_repo.get(key) == static_value
