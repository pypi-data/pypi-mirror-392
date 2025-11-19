"""
api/main.py
-----------
Aplicação FastAPI principal - Ontology Stack API.

Esta é uma implementação OSS da API de Ontologia do Palantir Foundry.

Arquitetura:
- Camada de Apresentação: FastAPI routers (REST endpoints)
- Camada de Serviço: Lógica de negócio
- Camada de Repositório: Acesso a dados
- Camada de Dados: SQLModel (relacional) + KuzuDB (grafo)

Para executar:
    uvicorn ontologia_api.main:app --reload

Acesse a documentação em:
    http://localhost:8000/docs
"""

import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy import true
from sqlalchemy.orm import selectinload
from sqlmodel import Session, SQLModel, select

try:
    from ontologia_mcp import app as mcp_app  # type: ignore
except Exception:  # pragma: no cover - optional MCP server
    mcp_app = None  # type: ignore
from fastapi.responses import Response

from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia_api.api.context import mount_contexts
from ontologia_api.api.contexts import get_default_contexts
from ontologia_api.core.database import engine
from ontologia_api.core.ddd import APIBootstrapper
from ontologia_api.core.docs import (
    API_TAGS,
    DEFAULT_ERROR_COMPONENTS,
    SECURITY_SCHEMES,
    SERVERS_METADATA,
    SWAGGER_UI_PARAMETERS,
    api_error_schema,
)
from ontologia_api.core.edge_metrics import metrics_response
from ontologia_api.core.edge_tracing import setup_tracing
from ontologia_api.core.settings import get_settings
from ontologia_api.core.temporal import connect_temporal
from ontologia_api.core.udp_ingest import start_udp_server
from ontologia_api.dependencies import (
    ensure_runtime_started,
    run_realtime_enricher,
    shutdown_runtime,
)
from ontologia_api.dependencies.edge_commands_retry import run_edge_command_retry_loop
from ontologia_api.dependencies.events import get_elasticsearch_repository
from ontologia_api.event_handlers.search import create_indexes_for_object_types
from ontologia_api.repositories.kuzudb_repository import get_kuzu_repo
from ontologia_api.v2.bounded_contexts import BOUNDED_CONTEXTS

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    testing = os.getenv("TESTING") in ("1", "true", "True")
    # Startup
    logger.info("Iniciando Ontology Stack API...")
    # Optional OpenTelemetry tracing
    setup_tracing()
    # Import edge models so SQLModel sees them during create_all
    try:
        from ontologia_api.models.edge_acl_sql import EdgeNodeACL  # noqa: F401
        from ontologia_api.models.edge_commands_sql import CommandReceipt  # noqa: F401
        from ontologia_api.models.edge_keys_sql import EdgeNodeKey  # noqa: F401
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to import edge models: %s", exc)
    logger.info("Criando tabelas do metamodelo no banco de dados...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tabelas criadas com sucesso.")

    # (Tests) Previously printed startup counts here; removed para reduzir ruído.

    if not testing:
        _bootstrap_search_indexes()

    # Inicializar KuzuDB (o singleton já cria o schema)
    if not testing:
        kuzu_repo = get_kuzu_repo()
        if kuzu_repo.is_available():
            logger.info("KuzuDB inicializado e pronto.")
        else:
            logger.warning("KuzuDB não disponível. Funcionalidades de grafo desabilitadas.")

    # Auto-load action modules to ensure executors are registered
    try:
        import importlib

        for module in (
            "ontologia_api.actions.test_actions",
            "ontologia_api.actions.system_actions",
        ):
            try:
                importlib.import_module(module)
            except Exception as exc:
                logger.warning("Failed to load actions module %s: %s", module, exc)
        logger.info("Actions executors loaded.")
    except Exception as e:
        logger.warning("Failed to initialize actions executors: %s", e)

    if not testing:
        realtime_stop_event = asyncio.Event()
        try:
            await ensure_runtime_started()
            app.state.realtime_stop_event = realtime_stop_event
            app.state.realtime_task = asyncio.create_task(
                run_realtime_enricher(realtime_stop_event)
            )
            # Start UDP ingest if enabled
            try:
                app.state.udp_transport = await start_udp_server()
            except Exception as udp_exc:  # pragma: no cover - optional
                logger.warning("Failed to start UDP ingest: %s", udp_exc)
            # Start edge command retry loop
            app.state.edge_retry_stop_event = asyncio.Event()
            app.state.edge_retry_task = asyncio.create_task(
                run_edge_command_retry_loop(app.state.edge_retry_stop_event)
            )
        except Exception as exc:  # pragma: no cover - enrichment startup is best-effort
            logger.warning("Failed to start real-time enricher: %s", exc)

    # Initialize Temporal client (singleton) if enabled
    app.state.temporal_client = None
    if not testing:
        try:
            settings = get_settings()
            use_temporal = settings.use_temporal_actions or os.getenv(
                "USE_TEMPORAL_ACTIONS", "0"
            ) in (
                "1",
                "true",
                "True",
            )
            if use_temporal:
                logger.info("Initializing Temporal client…")
                app.state.temporal_client = await connect_temporal(settings)
                logger.info("Temporal client ready.")
        except Exception as e:
            # Do not fail API startup if Temporal is misconfigured
            logger.warning("Failed to initialize Temporal client: %s", e)

    yield

    # Shutdown
    logger.info("Encerrando Ontology Stack API...")
    if not testing:
        try:
            kuzu_repo = get_kuzu_repo()
            if kuzu_repo.is_available():
                kuzu_repo.close()
        except Exception:
            pass
        realtime_task = getattr(app.state, "realtime_task", None)
        realtime_stop = getattr(app.state, "realtime_stop_event", None)
        if realtime_stop is not None:
            realtime_stop.set()
        if realtime_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await realtime_task
        # Stop UDP server
        udp_transport = getattr(app.state, "udp_transport", None)
        if udp_transport is not None:
            try:
                udp_transport.close()
            except Exception:
                pass
        # Stop edge retry loop
        edge_retry_task = getattr(app.state, "edge_retry_task", None)
        edge_retry_stop = getattr(app.state, "edge_retry_stop_event", None)
        if edge_retry_stop is not None:
            edge_retry_stop.set()
        if edge_retry_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await edge_retry_task
        await shutdown_runtime()
    # Drop Temporal client reference
    try:
        app.state.temporal_client = None
    except Exception:
        pass


def _bootstrap_search_indexes() -> None:
    es_repo = get_elasticsearch_repository()
    if not es_repo:
        return

    try:
        with Session(engine) as session:
            statement = (
                select(ObjectType)
                .where(ObjectType.is_latest == true())
                .options(selectinload(ObjectType.property_types))
            )
            object_types = session.exec(statement).all()

        if not object_types:
            return

        payload: list[dict[str, object]] = []
        for ot in object_types:
            property_map = {
                prop.api_name: prop.data_type for prop in getattr(ot, "property_types", []) or []
            }
            payload.append({"api_name": ot.api_name, "properties": property_map})

        create_indexes_for_object_types(es_repo, payload)
        logger.info(
            "INFO: Elasticsearch indexes bootstrapped for object types: "
            + ", ".join(sorted(ot["api_name"] for ot in payload))
        )

    except Exception as exc:  # pragma: no cover - startup resilience
        logger.warning("Failed to bootstrap search indexes: %s", exc)


# Criar aplicação FastAPI
_API_DESCRIPTION = """
# 🏗️ Ontologia Stack API

A comprehensive, production-ready REST API for ontology management, data governance, and intelligent automation.

## 🎯 Overview

The Ontologia Stack API delivers enterprise-grade ontology management capabilities with a modern, cloud-native architecture. It combines the power of graph databases with relational storage, providing a unified platform for data modeling, analytics, and automation.

## ✨ Key Features

### 📊 **Metamodel Management**
- **Programmatic Schema Control** – Define ObjectTypes, LinkTypes, Interfaces, and Actions as code
- **Schema Evolution** – Safe, backward-compatible schema changes with validation
- **Type System** – Rich property types, validation rules, and inheritance
- **Index Management** – Automatic index configuration for optimal query performance

### 🔍 **Hybrid Query Engine**
- **Relational + Graph** – Combine SQL filtering with graph traversals in single requests
- **Advanced Filtering** – Complex boolean expressions, range queries, and text search
- **Aggregation Analytics** – Built-in analytics with grouping, metrics, and time-series
- **Performance Optimization** – Query planning, caching, and connection pooling

### ⚡ **Action & Workflow System**
- **Synchronous Execution** – Immediate action execution with validation
- **Temporal Integration** – Durable workflow orchestration for complex processes
- **Custom Actions** – Register and execute custom business logic
- **Monitoring** – Execution history, performance metrics, and error tracking

### 🔐 **Enterprise Security**
- **JWT Authentication** – OAuth2-compliant token-based authentication
- **Role-Based Access Control** – Granular permissions with global and tenant scopes
- **Multi-Tenancy** – Isolated ontologies with cross-tenant capabilities
- **Audit Logging** – Comprehensive audit trails for compliance

### 📈 **Data Catalog & Versioning**
- **Git-like Branching** – Create, merge, and manage dataset branches
- **ACID Transactions** – Ensure data integrity with transactional operations
- **Lineage Tracking** – Complete data lineage and change history
- **Governance** – Data quality rules, validation, and compliance controls

## 🚀 Quick Start

### 1. **Authentication**
```bash
# Get your JWT token
curl -X POST http://localhost:8001/v2/auth/token \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=admin&password=admin"
```

### 2. **Create an ObjectType**
```bash
curl -X POST http://localhost:8001/v2/ontologies/default/object-types \\
  -H "Authorization: Bearer <your-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "apiName": "employee",
    "displayName": "Employee",
    "description": "Company employee record",
    "propertyTypes": [
      {"apiName": "name", "dataType": "string", "required": true},
      {"apiName": "email", "dataType": "string", "required": true},
      {"apiName": "department", "dataType": "string"}
    ]
  }'
```

### 3. **Create Object Instances**
```bash
curl -X POST http://localhost:8001/v2/ontologies/default/objects \\
  -H "Authorization: Bearer <your-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "objectTypeApiName": "employee",
    "objects": [
      {"rid": "emp_001", "properties": {"name": "Alice", "email": "alice@company.com", "department": "Engineering"}},
      {"rid": "emp_002", "properties": {"name": "Bob", "email": "bob@company.com", "department": "Sales"}}
    ]
  }'
```

### 4. **Query with Traversal**
```bash
curl -X POST http://localhost:8001/v2/ontologies/default/objects/search \\
  -H "Authorization: Bearer <your-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "select": {"objectTypeApiName": "employee"},
    "where": {"property": "department", "op": "eq", "value": "Engineering"},
    "orderBy": [{"property": "name", "direction": "ASC"}]
  }'
```

## 🏛️ Architecture

### **Storage Layer**
- **Primary Store**: PostgreSQL with SQLModel for relational data
- **Graph Engine**: KùzuDB for high-performance traversals
- **Search**: Elasticsearch for full-text search and analytics
- **Cache**: Redis for session management and caching

### **Service Layer**
- **API Gateway**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT-based auth with role-based permissions
- **Validation**: Pydantic models for request/response validation
- **Orchestration**: Temporal for workflow management

### **Integration Layer**
- **MCP Server**: Model Context Protocol for AI integration
- **gRPC Services**: High-performance real-time entity management
- **Event System**: Real-time updates and notifications
- **Data Pipelines**: dbt integration for ETL workflows

## 📚 API Organization

### **Core Resources**
- **Object Types** – Schema definitions and metamodel management
- **Link Types** – Relationship schemas and constraints
- **Objects** – Instance data with CRUD operations
- **Links** – Relationship instances and traversal

### **Advanced Features**
- **Actions** – Business logic execution and workflows
- **Analytics** – Aggregation queries and metrics
- **Datasets** – Versioned data management
- **Interfaces** – Polymorphic type contracts

### **System APIs**
- **Authentication** – Token management and validation
- **Health** – System monitoring and diagnostics
- **Query Types** – Saved query templates
- **Change Sets** – Schema change tracking

## 🔧 Development Tools

### **SDK Generation**
```bash
# Generate typed Python SDK
ontologia-cli generate-sdk --source local
```

### **CLI Integration**
```bash
# Validate ontology definitions
ontologia-cli validate --dir ./ontology

# Apply schema changes
ontologia-cli apply --host http://localhost:8001 --ontology default
```

### **Testing**
```bash
# Run integration tests
pytest tests/integration/

# Contract testing with Schemathesis
pytest tests/contracts/
```

## 🌐 Deployment Options

### **Local Development**
```bash
uvicorn ontologia_api.main:app --reload --port 8001
```

### **Docker Deployment**
```bash
docker-compose up -d  # Includes all dependencies
```

### **Kubernetes**
```bash
helm install ontologia ./charts/ontologia
```

## 📖 Documentation

- **API Reference**: This interactive documentation
- **SDK Guide**: `/packages/ontologia_sdk/README.md`
- **CLI Reference**: `/packages/ontologia_cli/README.md`
- **Architecture**: `/docs/platform/architecture.md`
- **Tutorials**: `/docs/getting-started.md`

## 🤝 Community & Support

- **GitHub**: https://github.com/ontologia/ontologia
- **Documentation**: https://ontologia.dev
- **Discord**: https://discord.gg/ontologia
- **Issues**: https://github.com/ontologia/ontologia/issues

---

**Built with ❤️ using FastAPI, SQLModel, and modern Python tooling**

---

Explore the endpoints below, supply a bearer token via the **Authorize** button, and use the
examples embedded in each response schema to jumpstart automation.
"""

app = FastAPI(
    title="🏗️ Ontology Stack API",
    version="1.0.0",
    description=_API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=API_TAGS,
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
    contact={
        "name": "Ontologia Development Team",
        "url": "https://ontologia.dev",
        "email": "dev@ontologia.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
        "identifier": "MIT",
    },
    terms_of_service="https://ontologia.dev/terms",
    servers=SERVERS_METADATA,
)


# Prometheus metrics endpoint
@app.get("/metrics")
def prometheus_metrics() -> Response:
    payload, content_type = metrics_response()
    return Response(content=payload, media_type=content_type)


# Configurar CORS para permitir acesso de frontends
settings = get_settings()
if settings.environment == "development":
    cors_origins = ["*"]
else:
    # Em produção, especificar origens permitidas
    cors_origins = getattr(settings, "cors_origins", [])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routers ---


# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.

    Returns:
        Status da API
    """
    return {
        "service": "Ontology Stack API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check detalhado.

    Returns:
        Status dos componentes
    """
    kuzu_repo = get_kuzu_repo()

    # DB connectivity probe
    db_status = "connected"
    try:
        with Session(engine) as s:
            s.exec(select(1))
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "components": {
            "api": "running",
            "database": db_status,
            "kuzudb": "available" if kuzu_repo.is_available() else "unavailable",
        },
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe with optional dependencies.

    - Database connectivity (SQLModel)
    - KuzuDB availability
    - Redis ping if REDIS_URL is set
    """
    kuzu_repo = get_kuzu_repo()
    # DB connectivity
    db_status = "connected"
    try:
        with Session(engine) as s:
            s.exec(select(1))
    except Exception as e:  # pragma: no cover - depends on env
        db_status = f"error: {e}"

    # Redis connectivity (optional)
    import os

    redis_status = "skipped"
    redis_url = os.getenv("REDIS_URL") or os.getenv("EDGE_REDIS_URL")
    if redis_url:
        try:
            import redis.asyncio as redis  # type: ignore

            client = redis.from_url(redis_url, decode_responses=True)
            pong = await client.ping()  # type: ignore
            redis_status = "connected" if pong else "error: no pong"
        except Exception as e:  # pragma: no cover - optional
            redis_status = f"error: {e}"

    status_overall = (
        "ready"
        if db_status == "connected"
        and (redis_status in {"connected", "skipped"})
        and (kuzu_repo.is_available())
        else "not_ready"
    )
    return {
        "status": status_overall,
        "components": {
            "database": db_status,
            "kuzudb": "available" if kuzu_repo.is_available() else "unavailable",
            "redis": redis_status,
        },
    }


# Compose the FastAPI application using the DDD bootstrapper
bootstrapper = APIBootstrapper()
bootstrapper.register_many(BOUNDED_CONTEXTS)
bootstrapper.mount(app)
app.state.api_bootstrapper = bootstrapper
if mcp_app is not None:
    app.mount("/mcp", mcp_app)

# Mount the DDD-aligned bounded contexts under /v3
mount_contexts(app, get_default_contexts())


def _build_openapi_schema():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=API_TAGS,
    )
    components = schema.setdefault("components", {})
    components.setdefault("schemas", {})["ApiError"] = api_error_schema()
    responses = components.setdefault("responses", {})
    responses.update(DEFAULT_ERROR_COMPONENTS["responses"])
    components.setdefault("securitySchemes", {}).update(SECURITY_SCHEMES)
    schema["servers"] = SERVERS_METADATA

    exempt_paths = {"/", "/health", "/v2/auth/token"}
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method == "parameters":
                continue
            operation.setdefault("responses", {}).setdefault(
                "500", {"$ref": "#/components/responses/ServerError"}
            )
            if path in exempt_paths:
                continue
            security = operation.setdefault("security", [])
            bearer_ref = {"BearerAuth": []}
            if bearer_ref not in security:
                security.append(bearer_ref)
            responses_map = operation.setdefault("responses", {})
            responses_map.setdefault("401", {"$ref": "#/components/responses/UnauthorizedError"})
            responses_map.setdefault("403", {"$ref": "#/components/responses/ForbiddenError"})
            responses_map.setdefault("429", {"$ref": "#/components/responses/TooManyRequestsError"})

    return schema


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = _build_openapi_schema()
    return app.openapi_schema


cast(Any, app).openapi = custom_openapi


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("ONTOLOGY STACK API")
    logger.info("=" * 60)
    logger.info("Iniciando servidor de desenvolvimento...")
    logger.info("Documentação: http://localhost:8000/docs")
    logger.info("=" * 60)

    uvicorn.run(
        "ontologia_api.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
