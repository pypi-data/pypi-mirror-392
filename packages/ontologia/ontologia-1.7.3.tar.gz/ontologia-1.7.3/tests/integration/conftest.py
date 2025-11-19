"""
Integration test configuration and fixtures.

This module provides pytest fixtures for setting up and tearing down
real services (Elasticsearch, Redis) for integration testing.
"""

import os
import time
from collections.abc import Generator
from typing import Any

import pytest
import requests

# Optional heavy dependencies for integration tests. When missing, skip module.
try:  # pragma: no cover - import guards for constrained envs
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

try:  # pragma: no cover
    from elasticsearch import Elasticsearch  # type: ignore
except Exception:  # pragma: no cover
    Elasticsearch = None  # type: ignore

# If required deps are unavailable, skip all tests in this module
if redis is None or Elasticsearch is None:  # pragma: no cover
    pytestmark = pytest.mark.skip(
        reason="Integration dependencies not available (redis/elasticsearch)"
    )

# Prefer automatic ephemeral containers via Testcontainers when available.
try:  # pragma: no cover
    from testcontainers.elasticsearch import ElasticsearchContainer  # type: ignore
    from testcontainers.redis import RedisContainer  # type: ignore

    _HAVE_TESTCONTAINERS = True
except Exception:  # pragma: no cover
    _HAVE_TESTCONTAINERS = False


@pytest.fixture(scope="session")
def docker_services() -> Generator[dict[str, Any], None, None]:
    """Start ephemeral Redis and Elasticsearch using Testcontainers if available.

    Falls back to docker-compose style local services if TESTCONTAINERS is not installed,
    but will skip if neither approach is possible.
    """
    if _HAVE_TESTCONTAINERS:
        # Start ES and Redis containers
        with (
            ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:8.13.0") as es_c,
            RedisContainer("redis:7-alpine") as r_c,
        ):
            # Disable ES security for tests
            es_c.with_env("discovery.type", "single-node").with_env(
                "xpack.security.enabled", "false"
            )
            es_url = es_c.get_url()
            try:
                redis_url = r_c.get_connection_url()
            except Exception:
                redis_url = f"redis://{r_c.get_container_host_ip()}:{r_c.get_exposed_port(6379)}"
            # Wait briefly for ES health
            deadline = time.time() + 60
            while time.time() < deadline:
                try:
                    resp = requests.get(f"{es_url}/_cluster/health", timeout=2)
                    if resp.ok:
                        break
                except Exception:
                    pass
                time.sleep(2)
            yield {"elasticsearch_url": es_url, "redis_url": redis_url}
            return
    # Testcontainers not available — try to use locally-running services
    # If env provides URLs, use them; otherwise skip
    es_url = os.getenv("ELASTICSEARCH_URL")
    redis_url = os.getenv("REDIS_URL")
    if es_url and redis_url:
        yield {"elasticsearch_url": es_url, "redis_url": redis_url}
    else:
        pytest.skip("No testcontainers and no local integration services configured")


@pytest.fixture
def elasticsearch_client(docker_services: dict[str, Any]) -> Generator[Any, None, None]:
    """
    Provide an Elasticsearch client for integration tests.

    Returns:
        Elasticsearch: Configured client connected to test instance
    """
    es = Elasticsearch([docker_services["elasticsearch_url"]])

    # Clean up any existing indices
    if es.indices.exists(index="*"):
        es.indices.delete(index="*")

    yield es

    # Clean up after test
    if es.indices.exists(index="*"):
        es.indices.delete(index="*")


@pytest.fixture
def redis_client(docker_services: dict[str, Any]) -> Generator[Any, None, None]:
    """
    Provide a Redis client for integration tests.

    Returns:
        redis.Redis: Configured client connected to test instance
    """
    r = redis.Redis.from_url(docker_services["redis_url"])

    # Clean up any existing data
    r.flushdb()

    yield r

    # Clean up after test
    r.flushdb()


@pytest.fixture
def integration_test_config(docker_services: dict[str, Any]) -> dict[str, Any]:
    """
    Provide configuration for integration tests.

    Returns:
        Dict[str, Any]: Configuration with real service endpoints
    """
    return {
        "elasticsearch": {
            "hosts": [docker_services["elasticsearch_url"]],
            "timeout": 30,
            "max_retries": 3,
        },
        "redis": {
            "url": docker_services["redis_url"],
            "decode_responses": True,
        },
        "duckdb": {
            "path": ":memory:",
            "read_only": False,
        },
    }
