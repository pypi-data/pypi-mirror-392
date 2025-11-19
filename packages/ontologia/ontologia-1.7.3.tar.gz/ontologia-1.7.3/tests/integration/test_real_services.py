"""
Integration tests with real services (Elasticsearch, Redis, DuckDB).

These tests validate that our infrastructure repositories work correctly
with actual service instances, not just mocks.
"""

import subprocess
import time
from unittest.mock import patch

import pytest

# Optional heavy deps; skip module when unavailable
try:  # pragma: no cover
    import redis  # type: ignore
    import requests  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore
    requests = None  # type: ignore
    pytestmark = pytest.mark.skip(reason="Integration deps (redis/requests) not available")

from ontologia.application.settings import get_settings
from ontologia.domain.metamodels.instances.object_instance import ObjectInstance
from ontologia.infrastructure.cache_repository import (
    create_redis_cache_repository,
)
from ontologia.infrastructure.elasticsearch_repository import ElasticsearchRepository
from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository


@pytest.fixture(scope="session")
def docker_services():
    """Start Docker services for integration testing."""
    # Start services
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Wait for services to be ready
    max_wait = 120  # 2 minutes
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            # Check Elasticsearch
            es_response = requests.get("http://localhost:9200/_cluster/health", timeout=5)
            if es_response.status_code == 200:
                es_health = es_response.json()
                if es_health.get("status") in ["yellow", "green"]:
                    # Check Redis
                    r = redis.Redis(host="localhost", port=6380, decode_responses=True)
                    if r.ping():
                        yield True
                        break
        except Exception:
            pass

        time.sleep(2)
    else:
        pytest.fail("Services failed to start within timeout period")

    # Cleanup
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
        capture_output=True,
        text=True,
    )


@pytest.fixture
def elasticsearch_repo(docker_services):
    """Create Elasticsearch repository for testing."""
    if not docker_services:
        pytest.skip("Docker services not available")

    # Override settings for test
    with patch.dict(
        get_settings().model_dump(),
        {
            "elasticsearch_host": "http://localhost",
            "elasticsearch_port": 9200,
            "elasticsearch_index_prefix": "test_ontologia",
        },
    ):
        repo = ElasticsearchRepository(["http://localhost:9200"])

        # Wait for repository to be available
        max_wait = 30
        for _ in range(max_wait):
            if repo.is_available():  # type: ignore[attr-defined]
                break
            time.sleep(1)
        else:
            pytest.fail("Elasticsearch repository not available")

        yield repo


@pytest.fixture
def redis_repo(
    redis_host="localhost",
    redis_port=6380,  # Updated to match test configuration
    redis_db=1,  # Use different DB for tests
):
    """Create Redis cache repository for testing."""
    if not docker_services:
        pytest.skip("Docker services not available")

    # Override settings for test
    with patch.dict(
        get_settings().model_dump(),
        {"redis_host": redis_host, "redis_port": redis_port, "redis_db": redis_db},
    ):
        repo = create_redis_cache_repository(f"redis://{redis_host}:{redis_port}/{redis_db}")

        # Wait for repository to be available
        max_wait = 30
        for _ in range(max_wait):
            if repo.backend.ping():  # Use backend ping method
                break
            time.sleep(1)
        else:
            pytest.fail("Redis repository not available")

        yield repo


@pytest.fixture
def duckdb_repo():
    """Create DuckDB repository for testing."""
    import os
    import tempfile

    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_integration.duckdb")

    repo = DuckDBRepository(duckdb_path=db_path)

    if not repo.is_available():  # type: ignore[attr-defined]
        pytest.skip("DuckDB not available")

    yield repo

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


class TestElasticsearchIntegration:
    """Test Elasticsearch repository integration."""

    def test_repository_availability(self, elasticsearch_repo):
        """Test that Elasticsearch repository is available."""
        assert elasticsearch_repo.is_available()  # type: ignore[attr-defined]

    def test_index_and_search_object(self, elasticsearch_repo):
        """Test indexing and searching objects."""
        # Create test object
        obj = ObjectInstance(
            object_type_rid="test_person",  # type: ignore[arg-type]
            object_type_api_name="test_person",  # type: ignore[arg-type]
            pk_value="person_123",  # type: ignore[arg-type]
            data={"name": "John Doe", "age": 30, "email": "john@example.com"},  # type: ignore[arg-type]
        )

        # Index the object
        success = elasticsearch_repo.index_object(obj)
        assert success

        # Wait for indexing
        time.sleep(2)

        # Search for the object
        results = elasticsearch_repo.search_by_text(
            object_type="test_person", query="John", limit=10
        )

        assert len(results) > 0
        assert any(result["pk_value"] == "person_123" for result in results)

    def test_update_object(self, elasticsearch_repo):
        """Test updating an existing object."""
        obj = ObjectInstance(
            object_type_rid="test_person",  # type: ignore[arg-type]
            object_type_api_name="test_person",  # type: ignore[arg-type]
            pk_value="person_456",  # type: ignore[arg-type]
            data={"name": "Jane Doe", "age": 25},  # type: ignore[arg-type]
        )

        # Index initial version
        elasticsearch_repo.index_object(obj)
        time.sleep(1)

        # Update object
        obj.data["age"] = 26  # type: ignore[attr-defined]
        success = elasticsearch_repo.index_object(obj)
        assert success

        time.sleep(1)

        # Verify update
        results = elasticsearch_repo.search_by_text(
            object_type="test_person", query="Jane", limit=10
        )

        updated_obj = next((r for r in reversed(results) if r["pk_value"] == "person_456"), None)
        assert updated_obj is not None
        assert updated_obj["data"]["age"] == 26

    def test_delete_object(self, elasticsearch_repo):
        """Test deleting an object."""
        obj = ObjectInstance(
            object_type_rid="test_person",  # type: ignore[arg-type]
            object_type_api_name="test_person",  # type: ignore[arg-type]
            pk_value="person_789",  # type: ignore[arg-type]
            data={"name": "Bob Smith"},  # type: ignore[arg-type]
        )

        # Index object
        elasticsearch_repo.index_object(obj)
        time.sleep(1)

        # Delete object
        success = elasticsearch_repo.delete_object(object_type="test_person", pk_value="person_789")
        assert success

        time.sleep(1)

        # Verify deletion
        results = elasticsearch_repo.search_by_text(
            object_type="test_person", query="Bob", limit=10
        )

        assert not any(r["pk_value"] == "person_789" for r in results)


class TestRedisIntegration:
    """Test Redis cache repository integration."""

    def test_repository_availability(self, redis_repo):
        """Test that Redis repository is available."""
        assert redis_repo.backend.ping()

    def test_set_and_get_cache(self, redis_repo):
        """Test setting and getting cache values."""
        key = "test_key_1"
        value = {"name": "Test Value", "data": [1, 2, 3]}
        ttl = 300

        # Set cache
        success = redis_repo.set(key, value, ttl_seconds=ttl)
        assert success

        # Get cache
        cached_value = redis_repo.get(key)
        assert cached_value == value

    def test_cache_expiration(self, redis_repo):
        """Test cache expiration."""
        key = "test_key_expires"
        value = {"temp": "data"}
        ttl = 2  # 2 seconds

        # Set cache with short TTL
        redis_repo.set(key, value, ttl_seconds=ttl)

        # Should be available immediately
        assert redis_repo.get(key) == value

        # Wait for expiration
        time.sleep(3)

        # Should be expired
        assert redis_repo.get(key) is None

    def test_cache_delete(self, redis_repo):
        """Test deleting cache entries."""
        key = "test_key_delete"
        value = {"to_delete": True}

        # Set cache
        redis_repo.set(key, value, ttl_seconds=300)
        assert redis_repo.get(key) == value

        # Delete cache
        success = redis_repo.delete(key)
        assert success

        # Should be gone
        assert redis_repo.get(key) is None

    def test_cache_clear_pattern(self, redis_repo):
        """Test clearing cache entries by pattern."""
        keys = ["test:pattern:1", "test:pattern:2", "other:key:1"]
        values = [{"id": 1}, {"id": 2}, {"id": 3}]

        # Set multiple cache entries
        for key, value in zip(keys, values, strict=False):
            redis_repo.set(key, value, ttl_seconds=300)

        # Clear by pattern
        deleted_count = redis_repo.delete_by_pattern("test:pattern:*")
        assert deleted_count == 2

        # Verify pattern matches are gone
        assert redis_repo.get("test:pattern:1") is None
        assert redis_repo.get("test:pattern:2") is None

        # Verify other entries remain
        assert redis_repo.get("other:key:1") == {"id": 3}


class TestDuckDBIntegration:
    """Test DuckDB repository integration."""

    def test_repository_availability(self, duckdb_repo):
        """Test that DuckDB repository is available."""
        assert duckdb_repo.is_available()  # type: ignore[attr-defined]

    def test_create_and_query_table(self, duckdb_repo):
        """Test creating tables and querying data."""
        # Create table
        create_sql = """
            CREATE TABLE test_objects (
                id INTEGER,
                name VARCHAR,
                value DOUBLE,
                category VARCHAR,
                created_at TIMESTAMP
            )
        """
        duckdb_repo.execute_query(create_sql, read_only=False)

        # Insert data
        insert_sql = """
            INSERT INTO test_objects VALUES
            (1, 'Object A', 10.5, 'Category 1', '2024-01-01 10:00:00'),
            (2, 'Object B', 20.0, 'Category 2', '2024-01-02 11:00:00'),
            (3, 'Object C', 15.5, 'Category 1', '2024-01-03 12:00:00')
        """
        duckdb_repo.execute_query(insert_sql, read_only=False)

        # Query data
        select_sql = "SELECT * FROM test_objects WHERE category = 'Category 1' ORDER BY id"
        results = duckdb_repo.execute_query(select_sql)

        assert len(results) == 2
        assert results[0][1] == "Object A"  # name column
        assert results[1][1] == "Object C"

    def test_parameterized_query(self, duckdb_repo):
        """Test parameterized queries."""
        # Create table
        duckdb_repo.execute_query(
            "CREATE TABLE test_params (id INTEGER, name VARCHAR, value DOUBLE)", read_only=False
        )

        # Insert with parameters
        duckdb_repo.execute_query(
            "INSERT INTO test_params VALUES (?, ?, ?)", params=[1, "Test", 42.5], read_only=False
        )

        # Query with parameters
        results = duckdb_repo.execute_query("SELECT * FROM test_params WHERE id = ?", params=[1])

        assert len(results) == 1
        assert results[0] == [1, "Test", 42.5]

    def test_scalar_query(self, duckdb_repo):
        """Test scalar queries."""
        # Setup data
        duckdb_repo.execute_query("CREATE TABLE test_scalar (value INTEGER)", read_only=False)
        duckdb_repo.execute_query(
            "INSERT INTO test_scalar VALUES (10), (20), (30)", read_only=False
        )

        # Test scalar query
        count = duckdb_repo.execute_scalar("SELECT COUNT(*) FROM test_scalar")
        assert count == 3

        sum_result = duckdb_repo.execute_scalar("SELECT SUM(value) FROM test_scalar")
        assert sum_result == 60

    def test_json_extraction(self, duckdb_repo):
        """Test JSON property extraction."""
        # Create table with JSON data
        duckdb_repo.execute_query(
            """
            CREATE TABLE test_json (
                id INTEGER,
                properties VARCHAR
            )
            """,
            read_only=False,
        )

        # Insert JSON data
        duckdb_repo.execute_query(
            """
            INSERT INTO test_json VALUES
            (1, '{"name": "John", "age": 30, "score": 85.5}'),
            (2, '{"name": "Jane", "age": 25, "score": 92.0}')
            """,
            read_only=False,
        )

        # Extract JSON properties
        results = duckdb_repo.execute_query(
            """
            SELECT
                json_extract_string(properties, '$.name') as name,
                CAST(json_extract(properties, '$.age') AS DOUBLE) as age,
                CAST(json_extract(properties, '$.score') AS DOUBLE) as score
            FROM test_json
            ORDER BY id
            """
        )

        assert len(results) == 2
        assert results[0] == ["John", 30.0, 85.5]
        assert results[1] == ["Jane", 25.0, 92.0]


class TestCrossServiceIntegration:
    """Test integration between multiple services."""

    def test_elasticsearch_duckdb_sync(self, elasticsearch_repo, duckdb_repo):
        """Test data synchronization between Elasticsearch and DuckDB."""
        # Create test data in DuckDB
        duckdb_repo.execute_query(
            """
            CREATE TABLE sync_test (
                id INTEGER,
                object_type VARCHAR,
                properties VARCHAR,
                sync_timestamp TIMESTAMP
            )
            """,
            read_only=False,
        )

        # Insert test data
        duckdb_repo.execute_query(
            """
            INSERT INTO sync_test VALUES
            (1, 'test_person', '{"name": "Sync User", "age": 35}', '2024-01-01 10:00:00'),
            (2, 'test_person', '{"name": "Another User", "age": 28}', '2024-01-01 11:00:00')
            """,
            read_only=False,
        )

        # Query from DuckDB
        db_results = duckdb_repo.execute_query(
            "SELECT id, properties FROM sync_test WHERE object_type = 'test_person'"
        )

        # Index in Elasticsearch
        for row in db_results:
            obj_id, properties_json = row
            obj = ObjectInstance(
                object_type_rid="test_person",  # type: ignore[arg-type]
                object_type_api_name="test_person",  # type: ignore[arg-type]
                pk_value=str(obj_id),  # type: ignore[arg-type]
                data=eval(properties_json),  # type: ignore[arg-type]
            )
            elasticsearch_repo.index_object(obj)

        # Wait for indexing
        time.sleep(2)

        # Search in Elasticsearch
        es_results = elasticsearch_repo.search_by_text(
            object_type="test_person", query="User", limit=10
        )

        assert len(es_results) == 2
        assert all(result["object_type_api_name"] == "test_person" for result in es_results)

    def test_cache_performance_layer(self, redis_repo, duckdb_repo):
        """Test caching layer for database queries."""
        # Setup test data
        duckdb_repo.execute_query(
            "CREATE TABLE cache_test (id INTEGER, data VARCHAR)", read_only=False
        )
        duckdb_repo.execute_query(
            "INSERT INTO cache_test VALUES (1, 'expensive_data'), (2, 'more_data')", read_only=False
        )

        # Simulate expensive query
        cache_key = "test_query:all_data"

        # Check cache first
        cached_result = redis_repo.get(cache_key)
        assert cached_result is None  # Not cached yet

        # Execute query and cache result
        db_result = duckdb_repo.execute_query("SELECT * FROM cache_test")
        redis_repo.set(cache_key, db_result, ttl_seconds=60)

        # Verify cache
        cached_result = redis_repo.get(cache_key)
        assert cached_result == db_result

        # Next query should hit cache
        # (In real implementation, we'd check cache before hitting DB)
        assert redis_repo.get(cache_key) is not None
