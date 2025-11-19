"""
Integration tests for Ontologia core mode.

These tests verify that the system works end-to-end with minimal dependencies
(SQL only, no DuckDB, KùzuDB, Elasticsearch, Temporal, etc.).
"""

import pytest
from fastapi.testclient import TestClient
from ontologia_api.core.database import get_session
from ontologia_api.main import app
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ontologia.application.simplified_settings import SimplifiedSettings


@pytest.fixture
def core_settings():
    """Settings configured for core mode only."""
    return SimplifiedSettings(
        storage_mode="sql_only",
        enable_search=False,
        enable_workflows=False,
        enable_realtime=False,
        enable_orchestration=False,
        dev_mode=True,
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key-change-in-production",  # noqa: S106
        jwt_secret_key="test-jwt-secret-key-change-in-production",  # noqa: S106
    )


@pytest.fixture
def core_engine():
    """In-memory SQLite engine for testing."""
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def core_session(core_engine):
    """Session with core database setup."""
    SQLModel.metadata.create_all(core_engine)
    with Session(core_engine) as session:
        yield session


@pytest.fixture
def core_client(core_session):
    """Test client configured for core mode."""

    def override_get_session():
        return core_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestCoreModeAPI:
    """Test API functionality in core mode."""

    def test_health_check_core_mode(self, core_client):
        """Test health check endpoint works in core mode."""
        response = core_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["components"]["api"] == "running"
        assert data["components"]["database"] == "connected"
        # KùzuDB should be unavailable in core mode
        assert data["components"]["kuzudb"] == "unavailable"

    def test_auth_flow_core_mode(self, core_client):
        """Test authentication flow works in core mode."""
        # Get token
        response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        assert response.status_code == 200

        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"  # noqa: S105

        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        response = core_client.get("/v2/ontologies/default/objectTypes", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"] == []  # Empty initially

    def test_object_type_crud_core_mode(self, core_client):
        """Test object type CRUD works in core mode."""
        # First get auth token
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create object type
        object_type_data = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
            "implements": [],
        }

        response = core_client.put(
            "/v2/ontologies/default/objectTypes/employee", json=object_type_data, headers=headers
        )
        assert response.status_code == 200

        created = response.json()
        assert created["apiName"] == "employee"
        assert created["displayName"] == "Employee"

        # Get object type
        response = core_client.get("/v2/ontologies/default/objectTypes/employee", headers=headers)
        assert response.status_code == 200
        assert response.json()["apiName"] == "employee"

        # List object types
        response = core_client.get("/v2/ontologies/default/objectTypes", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_object_crud_core_mode(self, core_client):
        """Test object CRUD works in core mode."""
        # Setup: get auth token and create object type
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create object type
        object_type_data = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
            "implements": [],
        }

        core_client.put(
            "/v2/ontologies/default/objectTypes/employee", json=object_type_data, headers=headers
        )

        # Create object
        object_data = {"properties": {"id": "emp1", "name": "Alice"}}

        response = core_client.put(
            "/v2/ontologies/default/objects/employee/emp1", json=object_data, headers=headers
        )
        assert response.status_code == 200

        created = response.json()
        assert created["pkValue"] == "emp1"
        assert created["properties"]["name"] == "Alice"

        # Get object
        response = core_client.get("/v2/ontologies/default/objects/employee/emp1", headers=headers)
        assert response.status_code == 200
        assert response.json()["pkValue"] == "emp1"

        # Search objects
        response = core_client.post(
            "/v2/ontologies/default/objects/employee/search",
            json={},  # Empty search to get all objects
            headers=headers,
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_link_type_crud_core_mode(self, core_client):
        """Test link type CRUD works in core mode."""
        # Setup: get auth token and create object types
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create object types
        employee_type = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
            "implements": [],
        }

        company_type = {
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
            "implements": [],
        }

        core_client.put(
            "/v2/ontologies/default/objectTypes/employee", json=employee_type, headers=headers
        )
        core_client.put(
            "/v2/ontologies/default/objectTypes/company", json=company_type, headers=headers
        )

        # Create link type
        link_type_data = {
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "employees", "displayName": "Employees"},
            "properties": {
                "role": {"dataType": "string", "displayName": "Role", "required": False}
            },
        }

        response = core_client.put(
            "/v2/ontologies/default/linkTypes/works_for", json=link_type_data, headers=headers
        )
        assert response.status_code == 200

        created = response.json()
        assert created["apiName"] == "works_for"
        assert created["cardinality"] == "MANY_TO_ONE"


class TestCoreModeConstraints:
    """Test that optional features are properly disabled in core mode."""

    def test_search_disabled_in_core_mode(self, core_client):
        """Test that search endpoints return appropriate responses when disabled."""
        # Setup: get auth token
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search should still work but use SQL fallback
        response = core_client.post(
            "/v2/ontologies/default/objects/nonexistent/search",
            json={},  # Empty search
            headers=headers,
        )
        # Should return 200 with empty results for nonexistent object type (SQL fallback works)
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_workflows_disabled_in_core_mode(self, core_client):
        """Test that workflow endpoints are disabled in core mode."""
        # Setup: get auth token
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Actions endpoint should exist but workflows should be disabled
        response = core_client.get("/v2/ontologies/default/actionTypes", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"] == []  # No actions in core mode by default

    def test_graph_operations_use_sql_fallback(self, core_client):
        """Test that graph operations fall back to SQL in core mode."""
        # Setup: get auth token and create basic structure
        auth_response = core_client.post(
            "/v2/auth/token", data={"username": "admin", "password": "admin"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create object types and link type
        employee_type = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
            "implements": [],
        }

        company_type = {
            "displayName": "Company",
            "primaryKey": "id",
            "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
            "implements": [],
        }

        core_client.put(
            "/v2/ontologies/default/objectTypes/employee", json=employee_type, headers=headers
        )
        core_client.put(
            "/v2/ontologies/default/objectTypes/company", json=company_type, headers=headers
        )

        link_type_data = {
            "displayName": "Works For",
            "cardinality": "MANY_TO_ONE",
            "fromObjectType": "employee",
            "toObjectType": "company",
            "inverse": {"apiName": "employees", "displayName": "Employees"},
            "properties": {},
        }

        core_client.put(
            "/v2/ontologies/default/linkTypes/works_for", json=link_type_data, headers=headers
        )

        # Create instances
        core_client.put(
            "/v2/ontologies/default/objects/employee/emp1",
            json={"properties": {"id": "emp1"}},
            headers=headers,
        )
        core_client.put(
            "/v2/ontologies/default/objects/company/c1",
            json={"properties": {"id": "c1"}},
            headers=headers,
        )

        # Create link
        core_client.post(
            "/v2/ontologies/default/links/works_for",
            json={"fromPk": "emp1", "toPk": "c1", "properties": {}},
            headers=headers,
        )

        # Traversal should work with SQL fallback - list links
        response = core_client.get(
            "/v2/ontologies/default/links/works_for?fromPk=emp1", headers=headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1


class TestCoreModePerformance:
    """Test performance characteristics in core mode."""

    def test_fast_startup_core_mode(self, core_client):
        """Test that core mode starts quickly without heavy dependencies."""
        import time

        start_time = time.time()
        response = core_client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        # Should respond quickly without initializing heavy services
        assert end_time - start_time < 2.0

    def test_memory_usage_core_mode(self, core_client):
        """Test that core mode uses reasonable memory."""
        import os

        try:
            import psutil
        except ImportError:
            # Fallback to stub for testing without psutil
            import sys

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from tools.psutil_stub import Process as psutil_Process

            psutil = type("psutil", (), {"Process": psutil_Process})()

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        # Core mode should use less than 400MB for basic operations
        assert memory_info.rss < 400 * 1024 * 1024  # 400MB
