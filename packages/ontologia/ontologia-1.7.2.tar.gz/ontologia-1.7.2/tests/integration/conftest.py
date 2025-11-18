"""
Integration test configuration and fixtures.

This module provides pytest fixtures for setting up and tearing down
real services (Elasticsearch, Redis) for integration testing.
"""

import subprocess
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
    pytestmark = pytest.mark.skip(reason="Integration dependencies not available (redis/elasticsearch)")


@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Path to the docker-compose test file."""
    return "docker-compose.test.yml"


@pytest.fixture(scope="session")
def docker_services(docker_compose_file: str) -> Generator[dict[str, Any], None, None]:
    """
    Start and stop Docker services for integration tests.

    This fixture manages the lifecycle of Docker containers used in
    integration tests, ensuring they are properly started and stopped.
    """
    # Start services
    subprocess.run(
        ["docker-compose", "-f", docker_compose_file, "up", "-d"],
        check=True,
        capture_output=True,
    )

    # Wait for services to be ready
    time.sleep(30)  # Give services time to start

    # Wait for Elasticsearch to be healthy
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:9200/_cluster/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:  # type: ignore[attr-defined]
            pass
        time.sleep(2)
    else:
        raise RuntimeError("Elasticsearch failed to start")

    # Wait for Redis to be ready
    for i in range(max_retries):
        try:
            r = redis.Redis(host="localhost", port=6380)
            if r.ping():
                break
        except redis.exceptions.ConnectionError:  # type: ignore[attr-defined]
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Redis failed to start")

    yield {
        "elasticsearch_url": "http://localhost:9200",
        "redis_url": "redis://localhost:6380",
    }

    # Stop services
    subprocess.run(
        ["docker-compose", "-f", docker_compose_file, "down"],
        check=True,
        capture_output=True,
    )


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
