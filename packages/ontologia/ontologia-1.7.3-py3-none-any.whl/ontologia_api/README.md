# Ontologia API - FastAPI Web Service Package

## Overview

The `ontologia_api` package provides the public API layer for the Ontologia framework, built on FastAPI. This package serves as the stable, production-ready interface that exposes ontology management capabilities through RESTful endpoints, WebSocket connections, and asynchronous workflow orchestration.

## Architecture

The API package follows clean architecture principles with clear separation of concerns:

```
ontologia_api/
├── actions/           # Temporal workflows and activities
├── core/              # Core application infrastructure & DDD bootstrapper
├── dependencies/      # FastAPI dependency injection
├── event_handlers/    # Event processing and caching
├── handlers/          # HTTP request handlers
├── migrations/        # Database migration workflows
├── repositories/      # Data access layer
├── services/          # Business logic services
└── v2/bounded_contexts.py  # Declarative bounded-context catalogue
```

### DDD Assembly via Bounded Contexts

The API surface is orchestrated through the `core.ddd` module which exposes a
`BoundedContext` dataclass and an `APIBootstrapper`. Each bounded context groups
routers, lifecycle hooks, and documentation metadata that belong to a specific
domain slice (e.g. modeling, runtime, analytics).

```python
from ontologia_api.core.ddd import APIBootstrapper
from ontologia_api.v2.bounded_contexts import BOUNDED_CONTEXTS

bootstrapper = APIBootstrapper()
bootstrapper.register_many(BOUNDED_CONTEXTS)
bootstrapper.mount(app)
```

This arrangement keeps the FastAPI application aligned with Ontologia's
“ontology-as-code” philosophy—domain concepts remain explicit, and routers are
composed according to their bounded context boundaries.

## Core Components

### FastAPI Application (`main.py`)

The main application configures and serves the API:

```python
from fastapi import FastAPI
from ontologia_api.core.settings import get_settings
from ontologia_api.core.database import engine
from ontologia_api.handlers import router

app = FastAPI(
    title="Ontologia API",
    description="Ontology management and data catalog API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(router, prefix="/api/v1")
```

### Core Infrastructure (`core/`)

#### Settings Management
```python
from ontologia_api.core.settings import get_settings

settings = get_settings()
# Access configuration
database_url = settings.database_url
redis_url = settings.redis_url
temporal_address = settings.temporal_address
```

#### Database Configuration
```python
from ontologia_api.core.database import get_db, engine

# Database dependency
async def get_db_session():
    async with get_db() as session:
        yield session
```

#### Authentication & Authorization
```python
from ontologia_api.core.auth import get_current_user, verify_token

# JWT-based authentication
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_token(token)
    return user
```

### Request Handlers (`handlers/`)

RESTful endpoint implementations:

#### Instance Management
```python
from ontologia_api.handlers.instances import router as instances_router

# CRUD operations for ontology instances
@instances_router.post("/instances")
async def create_instance(
    instance_data: InstanceCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new ontology instance."""
    instance = await instances_service.create(instance_data, db)
    return InstanceResponse.from_orm(instance)
```

#### Relationship Management
```python
from ontologia_api.handlers.links import router as links_router

# Link/relationship operations
@links_router.post("/links")
async def create_link(
    link_data: LinkCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a relationship between instances."""
    link = await links_service.create(link_data, db)
    return LinkResponse.from_orm(link)
```

### Services Layer (`services/`)

Business logic implementation:

#### Actions Service
```python
from ontologia_api.services.actions_service import ActionsService

class ActionsService:
    async def execute_action(
        self,
        action_name: str,
        parameters: dict,
        user_id: str
    ) -> ActionResult:
        """Execute a registered action with parameters."""
        # Validate action exists
        # Check permissions
        # Execute via Temporal workflow
        # Return result
        pass
```

#### Metamodel Service
```python
from ontologia_api.services.metamodel_service import MetamodelService

class MetamodelService:
    async def create_object_type(
        self,
        object_type_data: ObjectTypeCreate
    ) -> ObjectType:
        """Create a new object type in the ontology."""
        # Validate schema
        # Check naming conflicts
        # Persist to database
        # Update search indices
        pass
```

### Repository Layer (`repositories/`)

Data access implementations:

#### Multi-Database Support
```python
from ontologia_api.repositories.instances_repository import InstancesRepository

class InstancesRepository:
    def __init__(self):
        self.postgres_repo = PostgreSQLRepository()
        self.kuzu_repo = KuzuDBRepository()
        self.cache_repo = RedisRepository()

    async def get_instance(self, instance_id: str) -> Instance:
        # Try cache first
        # Fall back to PostgreSQL
        # Use KùzuDB for relationship queries
        pass
```

#### Search Integration
```python
from ontologia_api.repositories.elasticsearch_repository import ElasticsearchRepository

class ElasticsearchRepository:
    async def search_instances(self, query: SearchQuery) -> SearchResult:
        """Full-text search across ontology instances."""
        # Build Elasticsearch query
        # Execute search
        # Return ranked results
        pass
```

### Temporal Workflows (`actions/`)

Asynchronous workflow orchestration:

#### Workflow Definitions
```python
from ontologia_api.actions.temporal.workflows import ActionWorkflow

@workflow.defn
class ActionWorkflow:
    @workflow.run
    async def run(self, action_config: ActionConfig) -> ActionResult:
        """Execute action as asynchronous workflow."""
        # Validate preconditions
        # Execute activities
        # Handle compensation
        # Return result
        pass
```

#### Activity Implementations
```python
from ontologia_api.actions.temporal.activities import run_registered_action

@activity.defn
async def run_registered_action(action_name: str, params: dict) -> dict:
    """Execute individual action activity."""
    # Load action implementation
    # Execute with parameters
    # Handle errors and retries
    pass
```

## API Endpoints

### Ontology Management

#### Object Types
```http
GET    /api/v1/object-types          # List all object types
POST   /api/v1/object-types          # Create new object type
GET    /api/v1/object-types/{id}     # Get specific object type
PUT    /api/v1/object-types/{id}     # Update object type
DELETE /api/v1/object-types/{id}     # Delete object type
```

#### Instances
```http
GET    /api/v1/instances              # List instances with filtering
POST   /api/v1/instances              # Create new instance
GET    /api/v1/instances/{id}         # Get specific instance
PUT    /api/v1/instances/{id}         # Update instance
DELETE /api/v1/instances/{id}         # Delete instance
```

#### Relationships
```http
GET    /api/v1/links                  # List relationships
POST   /api/v1/links                  # Create relationship
GET    /api/v1/links/{id}             # Get specific relationship
DELETE /api/v1/links/{id}             # Delete relationship
```

### Search and Query

#### Search
```http
GET    /api/v1/search                 # Full-text search
POST   /api/v1/search/query           # Complex query execution
GET    /api/v1/search/suggest         # Auto-suggestions
```

#### Analytics
```http
GET    /api/v1/analytics/overview     # System overview statistics
POST   /api/v1/analytics/aggregate    # Data aggregation
GET    /api/v1/analytics/lineage      # Data lineage queries
```

### Actions and Workflows

#### Actions
```http
GET    /api/v1/actions                # List available actions
POST   /api/v1/actions/{name}/execute # Execute specific action
GET    /api/v1/actions/{name}/status  # Get execution status
```

#### Workflows
```http
GET    /api/v1/workflows              # List workflow executions
POST   /api/v1/workflows              # Start new workflow
GET    /api/v1/workflows/{id}         # Get workflow details
```

### Data Catalog Integration

#### Datasets
```http
GET    /api/v1/datasets               # List datasets
POST   /api/v1/datasets               # Create dataset
GET    /api/v1/datasets/{id}          # Get dataset details
PUT    /api/v1/datasets/{id}          # Update dataset
```

#### Transactions
```http
GET    /api/v1/datasets/{id}/transactions     # List transactions
POST   /api/v1/datasets/{id}/transactions     # Create transaction
GET    /api/v1/datasets/{id}/transactions/{tx_id}  # Get transaction
```

## Usage Examples

### Client Usage

```python
import httpx
from ontologia_sdk import OntologyClient

# Using the SDK client
client = OntologyClient(base_url="http://localhost:8000")

# Create object type
person_type = await client.create_object_type({
    "name": "Person",
    "properties": [
        {"name": "name", "type": "string", "required": True},
        {"name": "email", "type": "string", "format": "email"}
    ]
})

# Create instance
person = await client.create_instance("Person", {
    "name": "John Doe",
    "email": "john@example.com"
})
```

### Direct HTTP Usage

```python
import httpx

async with httpx.AsyncClient() as client:
    # Create object type
    response = await client.post(
        "http://localhost:8000/api/v1/object-types",
        json={
            "name": "Company",
            "properties": [
                {"name": "name", "type": "string", "required": True},
                {"name": "founded_date", "type": "date"}
            ]
        }
    )
    company_type = response.json()

    # Create instance
    response = await client.post(
        "http://localhost:8000/api/v1/instances",
        json={
            "object_type_name": "Company",
            "data": {
                "name": "Acme Corp",
                "founded_date": "2020-01-01"
            }
        }
    )
    company = response.json()
```

## WebSocket Support

### Real-time Updates

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received update: {data}")

# Connect to real-time updates
ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws/updates",
    on_message=on_message
)
ws.run_forever()
```

### Event Streaming

```python
# Subscribe to specific object type updates
ws_url = "ws://localhost:8000/ws/object-types/Person/updates"
ws = websocket.WebSocketApp(ws_url, on_message=on_message)
ws.run_forever()
```

## Authentication

### JWT Token Authentication

```python
import httpx

# Login to get token
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"username": "user@example.com", "password": "password"}
    )
    token_data = response.json()
    access_token = token_data["access_token"]

    # Use token for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(
        "http://localhost:8000/api/v1/instances",
        headers=headers
    )
```

### API Key Authentication

```python
headers = {"X-API-Key": "your-api-key-here"}
response = await client.get(
    "http://localhost:8000/api/v1/object-types",
    headers=headers
)
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ontologia
REDIS_URL=redis://localhost:6379

# Temporal
TEMPORAL_ADDRESS=localhost:7233
TEMPORAL_NAMESPACE=default

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# External Services
ELASTICSEARCH_URL=http://localhost:9200
KUZU_DB_PATH=data/graph.kuzu
```

### Settings File

```python
from ontologia_api.core.settings import Settings

settings = Settings(
    database_url="postgresql://...",
    redis_url="redis://...",
    temporal_address="localhost:7233",
    debug=False,
    cors_origins=["http://localhost:3000"]
)
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "ontologia_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ontologia
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ontologia
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

## Performance Optimization

### Caching Strategy
- Redis for frequently accessed instances
- Application-level caching for object types
- CDN for static API documentation

### Database Optimization
- Connection pooling with asyncpg
- Read replicas for query scaling
- Optimized indexes for common queries

### Async Processing
- Temporal workflows for long-running operations
- Background tasks for index updates
- Streaming responses for large datasets

## Monitoring and Observability

### Metrics
```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests')
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
```

### Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("API request", method="GET", path="/api/v1/instances", user_id="123")
```

### Health Checks
```http
GET /health          # Basic health check
GET /health/ready    # Readiness probe
GET /health/live     # Liveness probe
```

## Testing

### Test Structure
```python
import pytest
from httpx import AsyncClient
from ontologia_api.main import app

@pytest.mark.asyncio
async def test_create_object_type():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/object-types",
            json={"name": "TestType", "properties": []}
        )
        assert response.status_code == 201
```

### Integration Tests
- Database transaction tests
- Temporal workflow tests
- End-to-end API tests

## 🧭 Domain-Driven API Surface (v3)

To complement the Foundry-compatible `/v2` routes, the API now publishes a `/v3`
surface grouped by bounded contexts. Each context curates the routers that belong to a
particular part of the ontology platform, making the topology explicit:

| Bounded Context | Prefix | Highlights |
| ---------------- | ------ | ---------- |
| **Metamodel** | `/v3/ontologies/{ontologyApiName}/metamodel` | Author object, link, interface, query, and action types programmatically. |
| **Runtime** | `/v3/ontologies/{ontologyApiName}/runtime` | Manage instances, execute actions, and run analytics with a single prefix. |
| **Governance** | `/v3/ontologies/{ontologyApiName}/governance` | Operate change sets, dataset branches, and schema migrations cohesively. |
| **Streams** | `/v3/ontologies/{ontologyApiName}/streams` | Access hybrid real-time projections and WebSocket streams. |
| **System Access** | `/v3/system/auth` | Handle authentication and cross-context system flows. |

All `/v3` routers reuse the same application-layer services as `/v2`, giving teams a
state-of-the-art, DDD-aligned façade without breaking existing integrations.

## Dependencies

Core dependencies:
- **FastAPI**: Web framework and API documentation
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **TemporalIO**: Workflow orchestration
- **Redis**: Caching and sessions
- **Elasticsearch**: Full-text search

## Version Information

Current version: `0.1.0`

API follows semantic versioning with backward compatibility guarantees.

## Contributing

When contributing to the API package:
1. Follow OpenAPI specification for new endpoints
2. Add comprehensive request/response models
3. Include proper error handling and status codes
4. Write tests for all endpoints
5. Update API documentation

## License

This package is part of the Ontologia framework and follows the same license terms.
