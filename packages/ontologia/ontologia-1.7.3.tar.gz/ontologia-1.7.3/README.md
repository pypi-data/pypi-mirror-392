# Ontologia

[![Test Matrix](https://github.com/kevinqz/ontologia/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/kevinqz/ontologia/actions/workflows/test-matrix.yml)
[![Nightly Benchmarks](https://github.com/kevinqz/ontologia/actions/workflows/nightly-benchmarks.yml/badge.svg)](https://github.com/kevinqz/ontologia/actions/workflows/nightly-benchmarks.yml)

## Test Matrix and Stacks

Run the entire stack matrix locally:

```
bash scripts/test_stack_matrix.sh
```

This exercises:
- Core SQL (minimal stack): unit + integration
- Analytics + DuckDB (if installed): unit + performance (RUN_BENCHMARK=1)
- Graph unified reads with Kùzu (if installed)
- Redis cache integration (if Redis is available)
- Elasticsearch integration (if Elasticsearch is available)
- NATS Event Bus (if nats-py and a NATS server are available)

CI runs this matrix automatically via `.github/workflows/test-matrix.yml`.
Optional stacks are detected and executed only when their dependencies/services are available.

[![CI](https://github.com/kevinqz/ontologia/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/kevinqz/ontologia/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/kevinqz/ontologia/branch/main/graph/badge.svg)](https://codecov.io/gh/kevinqz/ontologia)

See AGENTS.md for an agent-friendly runbook (Codex, Claude CLI, FactoryAI, etc.).

> **🏗️ Architecture Reference**: See [ARCHITECTURE_LEDGER.md](./ARCHITECTURE_LEDGER.md) for the complete project structure and organization guidelines.

Ontologia is a comprehensive framework monorepo for ontology-as-code platforms that unifies schema management, graph traversal, action execution, real-time processing, and AI-powered automation. It combines SQLModel/Registro for the metamodel with optional KùzuDB acceleration for traversal-heavy workloads, and ships a generated Python SDK featuring a fluent query DSL.

## 📦 Framework Overview

Ontologia is organized as a framework monorepo with a core package and specialized libraries:

```
ontologia/
├── ontologia/                    # Core framework
│   ├── domain/                   # Domain models and business logic
│   ├── application/              # Application services
│   └── infrastructure/           # Core infrastructure
└── packages/                     # Specialized libraries
    ├── datacatalog/             # Versioned data management
    ├── ontologia_api/           # FastAPI web service
    ├── ontologia_cli/           # Command-line interface
    ├── ontologia_sdk/           # Python client library
    ├── ontologia_agent/         # AI-powered automation
    ├── ontologia_edge/          # Edge node management
    ├── ontologia_mcp/           # Model Context Protocol server
    └── ontologia_dagster/       # Data orchestration integration
```

## 🚀 Key Capabilities

- **Ontology as Code** – Author ObjectTypes and LinkTypes in YAML, validate/diff/apply with the CLI.
- **Generated SDK** – Typed models, link proxies, actions namespace, DSL filters, and typed pagination helpers.
- **Security & RBAC** – OAuth2 password flow with JWT access tokens, global roles, and tenant-scoped permissions.
- **Actions Runtime** – Submission criteria, validation rules, synchronous execution, and optional Temporal workflows.
- **Graph + Relational Storage** – SQLModel remains source of truth while KùzuDB provides high-performance traversals.
- **Hybrid Query Engine** – Multi-hop traversal plans that combine SQL filters with link navigation.
- **Real-time Processing** – Event-driven architecture with gRPC-based entity management and decision engines.
- **AI Integration** – Model Context Protocol server for AI assistant integration and intelligent automation.
- **Data Orchestration** – Dagster integration for complex data pipeline orchestration.
- **Data Catalog** – Versioned data management with branching, transactions, and governance.

## 📚 Package Documentation

### Core Framework
- **[ontologia/README.md](./ontologia/README.md)** - Core ontology management system, domain models, and application services

### API & Client Libraries
- **[packages/ontologia_api/README.md](./packages/ontologia_api/README.md)** - FastAPI web service with REST endpoints, WebSocket support, and authentication
- **[packages/ontologia_sdk/README.md](./packages/ontologia_sdk/README.md)** - Python client library with typed interfaces and fluent query DSL
- **[packages/ontologia_cli/README.md](./packages/ontologia_cli/README.md)** - Command-line interface for ontology management and development workflows

### Data & Processing
- **[packages/datacatalog/README.md](./packages/datacatalog/README.md)** - Versioned data management with branching, transactions, and governance
- **[packages/ontologia_edge/README.md](./packages/ontologia_edge/README.md)** - Edge node management with cryptographic identity, mesh networking, and graduated autonomy
- **[packages/ontologia_dagster/README.md](./packages/ontologia_dagster/README.md)** - Data orchestration integration with Dagster for complex pipelines

### AI & Automation
- **[packages/ontologia_agent/README.md](./packages/ontologia_agent/README.md)** - AI-powered ontology management with intelligent automation and analysis
- **[packages/ontologia_mcp/README.md](./packages/ontologia_mcp/README.md)** - Model Context Protocol server for AI assistant integration

## 📖 Documentation

Comprehensive documentation lives under `docs/` and is published with MkDocs Material.

- Browse locally with `uvx mkdocs serve` (http://127.0.0.1:8000)
- Start at [`docs/index.md`](docs/index.md) for the curated navigation
- Onboarding, environment preparation, and ontology-as-code workflow: [`docs/getting-started.md`](docs/getting-started.md)
- Architecture diagrams and deployment notes: [`docs/platform/architecture.md`](docs/platform/architecture.md)
- Historical reports and ADRs are archived under [`docs/archive/`](docs/archive/)

### OGM-first Workflow (Python as Source of Truth)

Ontologia supports defining your ontology in pure Python using the OGM (`ObjectModel`/`LinkModel`). Treat Python as the source of truth and export to YAML when needed.

- Define models under `ontology_definitions/models/` (see `ontology_definitions/models/core.py`).
- Apply from Python: `uv run ontologia-cli apply --source python --module ontology_definitions.models`.
- Export YAML: `uv run ontologia-cli export:yaml --module ontology_definitions.models --out ontologia`.
- Legacy YAML remains supported via `--source yaml`.

See `docs/migration_ogm.md` for a migration guide from YAML to Python.

## 🛠️ Installation

### Install the Core Framework
```bash
pip install ontologia
```

### Install with Specific Packages
```bash
# Core + API
pip install ontologia[api]

# Core + SDK + CLI
pip install ontologia[sdk,cli]

# Full framework with all packages
pip install ontologia[full]

# Development installation
pip install ontologia[dev]
```

### Local Development
Install via [uv](https://github.com/astral-sh/uv):

```bash
uv sync --dev
```

## 🚀 Quickstart

### 0. Bootstrap a sandbox (optional but recommended)

Create an isolated Ontologia ecosystem with the new Typer-based CLI:

```bash
uv run ontologia-cli genesis --name my_sandbox --directory ./sandboxes --start-services --bootstrap
cd sandboxes/my_sandbox
```

Launch the interactive Architect agent:

```bash
ontologia agent
```

### 1. Apply database migrations

```bash
just db-upgrade
# or: uv run alembic upgrade head
```

### 2. Generate the SDK

```bash
uv run ontologia-cli --dir ontologia generate-sdk --source local
```

### 3. Run the API

```bash
PYTHONPATH=apps:packages:. uv run uvicorn ontologia_api.main:app --reload
# OpenAPI docs → http://127.0.0.1:8000/docs
```

### 4. Obtain an access token

```bash
curl -X POST http://127.0.0.1:8000/v2/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"
```

### 5. Load sample data

```bash
export DUCKDB_PATH=$(pwd)/data/.local/local.duckdb
uv run just pipeline   # prepare → dbt build → sync
```

### 6. Explore with the SDK

```python
from ontologia_sdk.client import OntologyClient
from ontologia_sdk.ontology.objects import Employee

TOKEN = "<paste-access-token>"
client = OntologyClient(host="http://127.0.0.1:8000", ontology="default", token=TOKEN)

engineers = (
    Employee.search_builder(client)
    .where(Employee.dept == "ENG")
    .order_by(Employee.name.asc())
    .all_typed()
)

alice = Employee.get(client, "e1")
alice.actions.promote(level="L3")
```

## 🔧 Ontology as Code (OaC)

- Create sandboxes with `uv run ontologia-cli genesis --name <project>`
- Pair with the interactive Architect agent via `ontologia agent`
- Store ontology YAML under `ontologia/object_types/` and `ontologia/link_types/`
- Follow the workflow in [`docs/OAC_GUIDE.md`](docs/OAC_GUIDE.md)

Common CLI usage:

```bash
# Validate definitions
uv run ontologia-cli --dir ontologia validate

# Diff against running environment
uv run ontologia-cli --dir ontologia diff --host http://127.0.0.1:8000 --ontology default

# Apply changes
uv run ontologia-cli --dir ontologia apply --host http://127.0.0.1:8000 --ontology default --yes
```

## 🧪 Testing & Quality

```bash
uv run pytest
```

Highlights:
- Property-based coverage of the `_safe_rule_eval` engine
- Schemathesis-backed contract tests validating responses against the OpenAPI spec
- End-to-end lifecycle scenarios
- Performance baselines using `pytest-benchmark`

Run `just check` to execute formatting, linting, typing, and the full suite.

### Dev Extras for Full Test Suite

Some test modules require optional dependencies:
- MCP tools: `fastmcp` (install with `uv sync --group mcp`)
- Temporal actions: `temporalio` (install with `uv sync --group workflows`)
- Analytics/Sync: `duckdb`, `polars` (install with `uv sync --group analytics`)
- Graph (optional): `kuzu` (install with `uv sync --group graph`)

Recommended setup to run everything locally:

```bash
just setup
uv sync --group mcp --group workflows --group analytics --group graph
just test
just check
```

## 📋 Examples

- `example_project/examples/quickstarts/api_quickstart.py` – SDK-first walkthrough
- `example_project/examples/cookbook/cookbook_01_dsl_search.py` – Fluent query DSL
- `example_project/examples/cookbook/cookbook_02_link_traversal.py` – Link proxies
- `example_project/examples/cookbook/cookbook_03_actions_namespace.py` – Actions
- `example_project/examples/cookbook/cookbook_04_pagination.py` – Pagination
- `example_project/examples/cookbook/cookbook_05_full_lifecycle_demo.py` – Full lifecycle

## ⏰ Temporal & Async Actions

Temporal integration is optional and controlled with `USE_TEMPORAL_ACTIONS`:

```bash
just temporal-up        # Start the dev stack
just temporal-worker    # Run the worker

export TEMPORAL_ADDRESS=127.0.0.1:7233
export TEMPORAL_NAMESPACE=default
export TEMPORAL_TASK_QUEUE=actions
```

## 🤖 AI Integration

### Model Context Protocol (MCP)
```bash
# Start MCP server for AI assistant integration
python -m ontologia_mcp.server

# Claude Desktop configuration
{
  "mcpServers": {
    "ontologia": {
      "command": "python",
      "args": ["-m", "ontologia_mcp.server"],
      "env": {
        "ONTOLOGIA_BASE_URL": "http://localhost:8000",
        "ONTOLOGIA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### AI Agent
```bash
# Launch interactive AI agent
ontologia agent

# Run specific agent tasks
ontologia agent --task analyze-schema
ontologia agent --task optimize-queries
```

## 📊 Edge Node Processing

```bash
# Start edge node management server
python -m ontologia_edge.server

# Use gRPC client for high-performance operations
from ontologia_edge import EntityManager
manager = EntityManager("localhost:50051")
```

## 🔄 Data Orchestration

```bash
# Start Dagster with Ontologia integration
dagster dev -m ontologia_dagster.definitions

# Run orchestrated pipelines
dagster run -c config.yaml
```

## 🏗️ Architecture

The Ontologia framework follows a clean architecture pattern:

- **Domain Layer**: Core business logic and entity models
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External integrations and technical concerns
- **API Layer**: HTTP/gRPC interfaces and client libraries
- **CLI Layer**: Command-line tools and developer utilities

Each package maintains clear boundaries and dependencies while providing comprehensive functionality for ontology management at scale.

## 🤝 Contributing

1. `uv sync --dev`
2. Regenerate the SDK after modifying ontology YAML or the generator
3. Run `uv run pytest` (or `just check`)
4. Serve docs with `uvx mkdocs serve` to validate content changes

When contributing:
- Follow the established architectural patterns
- Maintain backward compatibility in public APIs
- Add comprehensive tests for new functionality
- Update relevant documentation
- Ensure all package READMEs are kept in sync

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- **Registro**: SQLModel-based metamodel foundation
- **KùzuDB**: High-performance graph database for traversals
- **Temporal**: Durable workflow execution
- **Dagster**: Data orchestration platform
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings management

Historical ADRs and verification reports remain available in [`docs/archive/`](docs/archive/).
