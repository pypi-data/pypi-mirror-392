"""
🛠️ Enhanced Test Fixtures for Ontologia
Modern fixtures with better isolation, performance monitoring, and multi-tenancy support.
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Ensure project paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
PKG_DIR = os.path.join(ROOT_DIR, "packages")
if PKG_DIR not in sys.path:
    sys.path.insert(0, PKG_DIR)

from fastapi.testclient import TestClient
from ontologia_api.core.auth import UserPrincipal, get_current_user
from ontologia_api.core.database import get_session
from ontologia_api.dependencies.events import reset_dependencies_caches
from ontologia_api.main import app

# Import factories
from tests.fixtures.factories import (
    create_test_scenario,
)


class PerformanceMonitor:
    """Monitor performance during tests"""

    def __init__(self):
        self.start_time = time.time()
        self.checkpoints = []
        self.memory_usage = []

    def checkpoint(self, name: str):
        """Record a performance checkpoint"""
        elapsed = time.time() - self.start_time
        self.checkpoints.append(
            {"name": name, "elapsed": elapsed, "memory_mb": self._get_memory_usage()}
        )

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
        except ImportError:
            # Fallback to stub for testing without psutil
            import os
            import sys

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
            from tools.psutil_stub import Process as psutil_Process

            psutil = type("psutil", (), {"Process": psutil_Process})()

        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def assert_under(self, max_seconds: float, checkpoint_name: str | None = None):
        """Assert total time or checkpoint time is under threshold"""
        if checkpoint_name:
            checkpoint = next((c for c in self.checkpoints if c["name"] == checkpoint_name), None)
            assert checkpoint is not None, f"Checkpoint '{checkpoint_name}' not found"
            elapsed = checkpoint["elapsed"]
        else:
            elapsed = time.time() - self.start_time

        assert elapsed < max_seconds, f"Operation took {elapsed:.3f}s, expected < {max_seconds}s"

    def assert_memory_under(self, max_mb: float):
        """Assert memory usage is under threshold"""
        current_memory = self._get_memory_usage()
        assert (
            current_memory < max_mb
        ), f"Memory usage {current_memory:.1f}MB, expected < {max_mb}MB"


class TestDataManager:
    """Manage test data lifecycle with proper cleanup"""

    def __init__(self, session: Session, tenant_id: str = "default"):
        self.session = session
        self.tenant_id = tenant_id
        self.created_objects = []
        self.created_links = []
        self.created_types = []

    def create_object_type(self, **kwargs):
        """Create and track an object type"""
        from tests.fixtures.factories import ObjectTypeFactory

        obj_type = ObjectTypeFactory.create(**kwargs)
        self.session.add(obj_type)
        self.session.commit()
        self.session.refresh(obj_type)
        self.created_types.append(obj_type)
        return obj_type

    def create_link_type(self, **kwargs):
        """Create and track a link type"""
        from tests.fixtures.factories import LinkTypeFactory

        link_type = LinkTypeFactory.create(**kwargs)
        self.session.add(link_type)
        self.session.commit()
        self.session.refresh(link_type)
        self.created_types.append(link_type)
        return link_type

    def create_object_instance(self, object_type, **kwargs):
        """Create and track an object instance"""
        from tests.fixtures.factories import ObjectInstanceFactory

        instance = ObjectInstanceFactory.create(
            object_type=object_type, tenant_id=self.tenant_id, **kwargs
        )
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        self.created_objects.append(instance)
        return instance

    def create_linked_objects(self, link_type, source, target, **kwargs):
        """Create and track linked objects"""
        from tests.fixtures.factories import LinkedObjectFactory

        link = LinkedObjectFactory.create(
            link_type=link_type,
            source_object=source,
            target_object=target,
            tenant_id=self.tenant_id,
            **kwargs,
        )
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        self.created_links.append(link)
        return link

    def create_scenario(self, customers_count: int = 3, products_count: int = 5):
        """Create a complete test scenario"""
        scenario_data = create_test_scenario(customers_count, products_count)

        # Create object types
        created_types = {}
        for obj_type in scenario_data["object_types"]:
            created_type = self.create_object_type(**obj_type.__dict__)
            created_types[obj_type.name] = created_type

        # Create link types
        created_link_types = {}
        for link_type in scenario_data["link_types"]:
            created_link_type = self.create_link_type(**link_type.__dict__)
            created_link_types[link_type.name] = created_link_type

        # Create instances
        created_instances = {}
        for instance in scenario_data["object_instances"]:
            obj_type = created_types[instance.object_type.name]
            created_instance = self.create_object_instance(
                object_type=obj_type, properties=instance.properties
            )
            created_instances[instance.id] = created_instance

        return {
            "object_types": created_types,
            "link_types": created_link_types,
            "object_instances": created_instances,
        }

    def cleanup(self):
        """Clean up all created test data"""
        try:
            # Delete in reverse order to handle foreign keys
            for link in reversed(self.created_links):
                self.session.delete(link)

            for obj in reversed(self.created_objects):
                self.session.delete(obj)

            for type_obj in reversed(self.created_types):
                self.session.delete(type_obj)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


# 🗄️ Database Fixtures


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_engine(f"sqlite:///{db_path}", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    try:
        yield engine
    finally:
        # Cleanup
        Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def memory_db():
    """Create in-memory database for fast testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session():
    """Create an isolated in-memory DB session for each test.

    Ensures all ORM models are imported before creating tables to avoid
    missing-table errors during tests. Using an in-memory engine provides
    test isolation and avoids cross-test contamination.
    """
    # Ensure a clean dependency state before wiring a new engine/session
    try:
        reset_dependencies_caches()
    except Exception:
        pass

    # Create an in-memory engine per test
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # Ensure models are imported so metadata includes all tables
    try:
        import registro.core.resource  # noqa: F401

        import ontologia.domain.metamodels.instances.models_sql  # noqa: F401
        import ontologia.domain.metamodels.types.action_type  # noqa: F401
        import ontologia.domain.metamodels.types.link_type  # noqa: F401
        import ontologia.domain.metamodels.types.object_type  # noqa: F401
        import ontologia.domain.metamodels.types.property_type  # noqa: F401
    except Exception:
        pass
    SQLModel.metadata.create_all(engine)
    with Session(engine, autoflush=False, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def multi_tenant_session():
    """Create session with multi-tenant support"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create tenant-specific schemas (simulated)
        session.exec(text("CREATE TABLE IF NOT EXISTS tenant_a_objects (id TEXT PRIMARY KEY)"))  # type: ignore[arg-type]
        session.exec(text("CREATE TABLE IF NOT EXISTS tenant_b_objects (id TEXT PRIMARY KEY)"))  # type: ignore[arg-type]
        yield session


# 🧪 Data Management Fixtures


@pytest.fixture
def test_data_manager(session):
    """Fixture for managing test data lifecycle"""
    manager = TestDataManager(session)
    yield manager
    manager.cleanup()


@pytest.fixture
def tenant_data_manager(multi_tenant_session):
    """Fixture for managing tenant-specific test data"""
    manager = TestDataManager(multi_tenant_session, tenant_id="tenant_a")
    yield manager
    manager.cleanup()


@pytest.fixture
def sample_scenario(test_data_manager):
    """Create a sample business scenario for testing"""
    return test_data_manager.create_scenario(customers_count=3, products_count=5)


# 🌐 API Client Fixtures


@pytest.fixture
def client(session):
    """Create test client with database session override"""

    def get_session_override():
        yield session

    test_principal = UserPrincipal(
        user_id="test_user", roles=["admin"], tenants={"default": ["read", "write"]}  # type: ignore[arg-type]
    )

    async def get_current_user_override():
        return test_principal

    # Override DB session to use the same session fixture and bypass auth

    # Align the API's engine with this test's engine to avoid mismatches
    try:
        import ontologia_api.core.database as _api_db
        import ontologia_api.main as _api_main

        eng = session.get_bind()  # type: ignore[attr-defined]
        if eng is not None:
            try:
                # Recreate schema on the shared engine to guarantee presence
                SQLModel.metadata.create_all(eng)
            except Exception:
                pass
            _api_db.engine = eng
            try:
                _api_main.engine = eng  # also patch local reference held by app module
            except Exception:
                pass
    except Exception:
        pass

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    with TestClient(app) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest.fixture
def tenant_client(multi_tenant_session):
    """Create test client for tenant-specific operations"""

    def get_session_override():
        yield multi_tenant_session

    test_principal = UserPrincipal(
        user_id="tenant_user", roles=["user"], tenants={"tenant_a": ["read", "write"]}  # type: ignore[arg-type]
    )

    async def get_current_user_override():
        return test_principal

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)

    try:
        yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def readonly_client(session):
    """Create test client with read-only permissions"""

    def get_session_override():
        yield session

    test_principal = UserPrincipal(
        user_id="readonly_user", roles=["readonly"], tenants={"default": ["read"]}  # type: ignore[arg-type]
    )

    async def get_current_user_override():
        return test_principal

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)

    try:
        yield client
    finally:
        app.dependency_overrides.clear()


# ⚡ Performance Fixtures


@pytest.fixture
def performance_monitor():
    """Monitor performance during tests"""
    return PerformanceMonitor()


@pytest.fixture
def slow_test_threshold():
    """Configure threshold for slow tests"""
    return float(os.getenv("SLOW_TEST_THRESHOLD", "2.0"))


# 🎭 Mock Fixtures


@pytest.fixture
def mock_external_api():
    """Mock external API calls"""
    with patch("ontologia.infrastructure.external_api") as mock:
        mock.validate_schema.return_value = True
        mock.notify_webhook.return_value = {"status": "success"}
        yield mock


@pytest.fixture
def mock_temporal_client():
    """Mock Temporal workflow client"""
    with patch("ontologia.infrastructure.temporal_client") as mock:
        mock.start_workflow.return_value = "workflow_id_123"
        mock.get_workflow_status.return_value = {"status": "completed"}
        yield mock


@pytest.fixture
def mock_redis_cache():
    """Mock Redis cache operations"""
    with patch("ontologia.infrastructure.redis_client") as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        yield mock


# 🔒 Security Fixtures


@pytest.fixture
def admin_user():
    """Create admin user principal"""
    return UserPrincipal(
        user_id="admin_user", roles=["admin"], tenants={"*": ["read", "write", "admin"]}  # type: ignore[arg-type]
    )


@pytest.fixture
def regular_user():
    """Create regular user principal"""
    return UserPrincipal(
        user_id="regular_user", roles=["user"], tenants={"default": ["read", "write"]}  # type: ignore[arg-type]
    )


@pytest.fixture
def readonly_user():
    """Create readonly user principal"""
    return UserPrincipal(user_id="readonly_user", roles=["readonly"], tenants={"default": ["read"]})  # type: ignore[arg-type]


# 📊 Environment Fixtures


@pytest.fixture
def test_config():
    """Test configuration override"""
    return {
        "database": {"url": "sqlite:///:memory:", "echo": False},
        "api": {"debug": True, "host": "localhost", "port": 8000},
        "security": {"jwt_secret": "test_secret", "jwt_expire_hours": 1},
        "performance": {"query_timeout": 5.0, "max_results": 1000},
    }


@pytest.fixture
def development_config():
    """Development environment configuration"""
    return {
        "database": {"url": "sqlite:///dev.db", "echo": True},
        "api": {"debug": True, "host": "127.0.0.1", "port": 8000},
        "logging": {"level": "DEBUG"},
    }


# 🧪 Custom Assertions


class Assertions:
    """Custom assertion helpers for testing"""

    @staticmethod
    def assert_valid_object_type(obj_type):
        """Assert object type is valid"""
        assert obj_type.name is not None and len(obj_type.name) > 0
        assert obj_type.primary_key in obj_type.properties
        assert obj_type.properties[obj_type.primary_key].required

    @staticmethod
    def assert_valid_link_type(link_type):
        """Assert link type is valid"""
        assert link_type.source_object_type is not None
        assert link_type.target_object_type is not None
        assert link_type.name is not None and len(link_type.name) > 0

    @staticmethod
    def assert_tenant_isolation(data_a, data_b):
        """Assert tenant data is properly isolated"""
        ids_a = {obj.id for obj in data_a}
        ids_b = {obj.id for obj in data_b}
        assert ids_a.isdisjoint(ids_b), "Tenant data is not isolated"

    @staticmethod
    def assert_performance_under(operation, max_seconds):
        """Assert operation completes within time limit"""
        start_time = time.time()
        result = operation()
        elapsed = time.time() - start_time
        assert elapsed < max_seconds, f"Operation took {elapsed:.3f}s, expected < {max_seconds}s"
        return result


@pytest.fixture
def assertions():
    """Provide custom assertions to tests"""
    return Assertions()


# 🎯 Test Markers and Configuration

pytest_plugins = ["pytest_benchmark"]


def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (database, external services)"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests (slow, full workflows)")
    config.addinivalue_line("markers", "performance: Performance tests and benchmarks")
    config.addinivalue_line("markers", "security: Security and authentication tests")
    config.addinivalue_line("markers", "slow: Slow running tests (run separately)")
    config.addinivalue_line("markers", "multi_tenant: Multi-tenancy specific tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test location
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add slow marker for performance tests
        if "performance" in str(item.fspath) or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)
