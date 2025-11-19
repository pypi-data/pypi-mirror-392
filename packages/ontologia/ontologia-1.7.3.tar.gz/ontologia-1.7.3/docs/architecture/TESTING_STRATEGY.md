# 🧪 Modern Testing Strategy for Ontologia

> **🎯 PURPOSE**: Define comprehensive testing approach for framework, ontologies, and client implementations.

## 📊 Testing Pyramid

```
    🔍 E2E Tests (5%)
   ┌─────────────────┐
  │  🎭 Integration  │ (15%)
 ┌───────────────────────┐
│ 🧪 Unit Tests (80%)      │
└─────────────────────────┘
```

## 🏗️ Testing Architecture

### 🧪 **Unit Tests (80%)**
**Purpose**: Test individual components in isolation
**Speed**: < 100ms per test
**Location**: `tests/unit/`

```bash
tests/unit/
├── domain/                 # Domain logic tests
│   ├── test_metamodel/    # Metamodel business rules
│   ├── test_instances/    # Instance management
│   └── test_actions/      # Action execution
├── application/           # Application services
│   ├── test_actions_service/
│   ├── test_metamodel_service/
│   └── test_query_service/
├── infrastructure/        # Infrastructure components
│   ├── test_database/
│   ├── test_cache/
│   └── test_messaging/
└── shared/               # Shared utilities
    ├── test_validators/
    ├── test_serializers/
    └── test_exceptions/
```

### 🎭 **Integration Tests (15%)**
**Purpose**: Test component interactions
**Speed**: < 1s per test
**Location**: `tests/integration/`

```bash
tests/integration/
├── api/                   # API endpoint tests
│   ├── v2/               # API v2 endpoints
│   │   ├── test_objects/
│   │   ├── test_links/
│   │   ├── test_actions/
│   │   └── test_queries/
│   └── auth/             # Authentication flows
├── database/             # Database integration
│   ├── test_migrations/
│   ├── test_transactions/
│   └── test_performance/
├── external/             # External integrations
│   ├── test_temporal/
│   ├── test_redis/
│   └── test_filesystem/
└── workflows/            # Business workflows
    ├── test_data_import/
    ├── test_bulk_operations/
    └── test_realtime_sync/
```

### 🔍 **E2E Tests (5%)**
**Purpose**: Test complete user scenarios
**Speed**: < 10s per test
**Location**: `tests/e2e/`

```bash
tests/e2e/
├── scenarios/            # User scenarios
│   ├── test_full_workflow/
│   ├── test_multi_tenant/
│   └── test_data_pipeline/
├── performance/          # Performance scenarios
│   ├── test_load_testing/
│   ├── test_stress_testing/
│   └── test_benchmarks/
└── contracts/           # Contract tests
    ├── test_api_contracts/
    └── test_sdk_contracts/
```

## 🛠️ Enhanced Testing Infrastructure

### 📋 **Fixtures and Factories**
```python
# tests/fixtures/factories.py
import factory
from typing import Dict, Any
from ontologia.domain.metamodels.types import ObjectType, LinkType

class ObjectTypeFactory(factory.Factory):
    class Meta:
        model = ObjectType

    name = factory.Faker("word")
    display_name = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    properties = factory.LazyAttribute(
        lambda _: {"id": {"type": "string", "required": True}}
    )

class LinkTypeFactory(factory.Factory):
    class Meta:
        model = LinkType

    name = factory.Faker("word")
    source_object_type = factory.SubFactory(ObjectTypeFactory)
    target_object_type = factory.SubFactory(ObjectTypeFactory)
    properties = factory.LazyAttribute(
        lambda _: {"created_at": {"type": "datetime", "required": True}}
    )
```

### 🔧 **Enhanced Conftest**
```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_engine(f"sqlite:///{db_path}", poolclass=StaticPool)
    yield engine

    # Cleanup
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def multi_tenant_session():
    """Create session with multi-tenant support"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tenant-specific schemas
    with Session(engine) as session:
        session.exec("ATTACH DATABASE ':memory:' AS tenant_a")
        session.exec("ATTACH DATABASE ':memory:' AS tenant_b")
        yield session

@pytest.fixture
def performance_monitor():
    """Monitor performance during tests"""
    import time
    start_time = time.time()

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = start_time
            self.checkpoints = []

        def checkpoint(self, name: str):
            self.checkpoints.append({
                "name": name,
                "elapsed": time.time() - self.start_time
            })

        def assert_under(self, max_seconds: float):
            total = time.time() - self.start_time
            assert total < max_seconds, f"Test took {total:.2f}s, expected < {max_seconds}s"

    return PerformanceMonitor()
```

### 📊 **Test Data Management**
```python
# tests/fixtures/data.py
class TestDataManager:
    """Manage test data lifecycle"""

    def __init__(self, session: Session):
        self.session = session
        self.created_objects = []

    def create_object_type(self, **kwargs):
        obj_type = ObjectTypeFactory.create(**kwargs)
        self.session.add(obj_type)
        self.session.commit()
        self.created_objects.append(obj_type)
        return obj_type

    def create_link_type(self, **kwargs):
        link_type = LinkTypeFactory.create(**kwargs)
        self.session.add(link_type)
        self.session.commit()
        self.created_objects.append(link_type)
        return link_type

    def cleanup(self):
        """Clean up created test data"""
        for obj in reversed(self.created_objects):
            self.session.delete(obj)
        self.session.commit()

@pytest.fixture
def test_data_manager(session):
    """Fixture for managing test data"""
    manager = TestDataManager(session)
    yield manager
    manager.cleanup()
```

## 🎯 Testing Patterns

### 🧪 **Unit Test Pattern**
```python
# tests/unit/domain/test_metamodel_service.py
import pytest
from unittest.mock import Mock, patch
from ontologia.application.metamodel_service import MetamodelService

class TestMetamodelService:
    """Test metamodel service business logic"""

    def test_create_object_type_success(self, session, test_data_manager):
        """Test successful object type creation"""
        # Arrange
        service = MetamodelService(session)
        request = ObjectTypeFactory.build()

        # Act
        result = service.create_object_type(request)

        # Assert
        assert result.name == request.name
        assert result.id is not None
        assert result.properties == request.properties

    def test_create_object_type_validation_error(self, session):
        """Test object type creation with invalid data"""
        # Arrange
        service = MetamodelService(session)
        request = ObjectTypeFactory.build(name="")  # Invalid empty name

        # Act & Assert
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            service.create_object_type(request)

    @patch('ontologia.application.metamodel_service.external_api')
    def test_create_object_type_with_external_validation(self, mock_api, session):
        """Test object type creation with external validation"""
        # Arrange
        mock_api.validate_schema.return_value = True
        service = MetamodelService(session)
        request = ObjectTypeFactory.build()

        # Act
        result = service.create_object_type(request)

        # Assert
        assert result.name == request.name
        mock_api.validate_schema.assert_called_once_with(request)
```

### 🎭 **Integration Test Pattern**
```python
# tests/integration/api/v2/test_objects.py
import pytest
from fastapi.testclient import TestClient

class TestObjectsAPI:
    """Test objects API endpoints"""

    def test_create_object_success(self, client: TestClient, test_data_manager):
        """Test successful object creation via API"""
        # Arrange
        object_type = test_data_manager.create_object_type(
            name="Customer",
            properties={"email": {"type": "string", "required": True}}
        )

        request_data = {
            "object_type": object_type.name,
            "properties": {"email": "test@example.com"}
        }

        # Act
        response = client.post("/v2/objects", json=request_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["properties"]["email"] == "test@example.com"
        assert data["id"] is not None

    def test_create_object_validation_error(self, client: TestClient):
        """Test object creation with validation errors"""
        # Arrange
        request_data = {
            "object_type": "NonExistent",
            "properties": {"invalid": "data"}
        }

        # Act
        response = client.post("/v2/objects", json=request_data)

        # Assert
        assert response.status_code == 404
        assert "Object type not found" in response.json()["detail"]
```

### 🔍 **E2E Test Pattern**
```python
# tests/e2e/scenarios/test_full_workflow.py
import pytest
from playwright.sync_api import Page

class TestFullWorkflow:
    """Test complete user workflows"""

    def test_data_scientist_workflow(self, page: Page, performance_monitor):
        """Test complete data scientist workflow"""
        # Step 1: Login
        page.goto("/login")
        page.fill("[data-testid=username]", "scientist@example.com")
        page.fill("[data-testid=password]", "password")
        page.click("[data-testid=login-button]")

        performance_monitor.checkpoint("login_complete")

        # Step 2: Create object type
        page.goto("/object-types/new")
        page.fill("[data-testid=name]", "Customer")
        page.fill("[data-testid=description]", "Business customer")
        page.click("[data-testid=save-button]")

        performance_monitor.checkpoint("object_type_created")

        # Step 3: Create objects
        page.goto("/objects/new")
        page.select_option("[data-testid=object-type]", "Customer")
        page.fill("[data-testid=email]", "test@example.com")
        page.click("[data-testid=save-button]")

        performance_monitor.checkpoint("object_created")

        # Step 4: Query data
        page.goto("/query")
        page.fill("[data-testid=query]", "SELECT * FROM Customer")
        page.click("[data-testid=execute-button]")

        # Assert
        assert page.locator("[data-testid=results]").count() > 0
        performance_monitor.assert_under(5.0)  # Complete workflow under 5 seconds
```

## 📊 Performance Testing

### ⚡ **Benchmark Tests**
```python
# tests/performance/test_benchmarks.py
import pytest
import time
from ontologia.application.query_service import QueryService

class TestBenchmarks:
    """Performance benchmarks for critical operations"""

    @pytest.mark.benchmark
    def test_query_performance_large_dataset(self, session, benchmark):
        """Benchmark query performance on large dataset"""
        # Setup large dataset
        service = QueryService(session)

        # Benchmark query execution
        result = benchmark(service.execute_query, "SELECT * FROM LargeTable LIMIT 1000")

        # Assert performance requirements
        assert result.execution_time < 0.1  # 100ms max
        assert len(result.data) == 1000

    @pytest.mark.benchmark
    def test_bulk_insert_performance(self, session, benchmark):
        """Benchmark bulk insert operations"""
        service = BulkInsertService(session)
        data = [ObjectFactory.build() for _ in range(1000)]

        # Benchmark bulk insert
        result = benchmark(service.bulk_insert, data)

        # Assert performance requirements
        assert result.execution_time < 1.0  # 1s max for 1000 records
        assert result.inserted_count == 1000
```

## 🔒 Security Testing

### 🛡️ **Security Tests**
```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient

class TestAuthentication:
    """Test authentication and authorization"""

    def test_jwt_token_validation(self, client: TestClient):
        """Test JWT token validation"""
        # Test with valid token
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/v2/objects", headers=headers)
        assert response.status_code == 200

        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/v2/objects", headers=headers)
        assert response.status_code == 401

## 🧰 Stack Matrix

To validate all supported stack combinations locally, use the helper script:

```
bash scripts/test_stack_matrix.sh
```

It covers:
- Core SQL (minimal): unit + integration with `STORAGE_MODE=sql_only`
- DuckDB analytics: unit + performance with `STORAGE_MODE=sql_duckdb` and `RUN_BENCHMARK=1`
- Graph unified reads (Kùzu): traversal tests with `USE_UNIFIED_GRAPH=1`
- Redis cache: cache integration (requires Redis service + `redis` client)
- Elasticsearch: ES integration (requires ES service + client)
- NATS: event bus tests (requires `nats-py` + NATS server; unit tests also run with mocks when missing)

CI runs this matrix automatically via `.github/workflows/test-matrix.yml`, spinning up Redis/Elasticsearch/NATS services as needed. Benchmarks are gated by `RUN_BENCHMARK=true`.

    def test_tenant_isolation(self, client_a: TestClient, client_b: TestClient):
        """Test tenant data isolation"""
        # Create data in tenant A
        response_a = client_a.post("/v2/objects", json={
            "object_type": "Customer",
            "properties": {"name": "Customer A"}
        })
        assert response_a.status_code == 201

        # Verify tenant B cannot see tenant A data
        response_b = client_b.get("/v2/objects")
        objects_b = response_b.json()
        assert not any(obj["properties"]["name"] == "Customer A" for obj in objects_b)
```

## 📋 Test Configuration

### 🗂️ **Pytest Configuration**
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --cov=ontologia
    --cov=packages
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --benchmark-only
    --benchmark-sort=mean
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
    benchmark: Benchmark tests
```

### 🔄 **CI Integration**
```yaml
# .github/workflows/test.yml
name: 🧪 Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest-playwright
          playwright install

      - name: Run unit tests
        run: pytest tests/unit -v --cov-report=xml

      - name: Run integration tests
        run: pytest tests/integration -v

      - name: Run E2E tests
        run: pytest tests/e2e -v --slow

      - name: Run performance benchmarks
        run: pytest tests/performance --benchmark-only

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## 🎯 **Benefits of This Testing Strategy**

1. **📊 Clear Pyramid**: 80% unit, 15% integration, 5% E2E
2. **⚡ Fast Feedback**: Unit tests run in < 100ms
3. **🔒 Security Coverage**: Authentication and authorization tests
4. **📈 Performance Monitoring**: Automated benchmarks
5. **🎭 Real Scenarios**: E2E tests for user workflows
6. **🏗️ Architecture Validation**: Tests enforce architectural rules

**🚀 This comprehensive testing strategy ensures reliability, performance, and maintainability!**
