# 🏗️ Ontologia Architecture Ledger

> **🎯 PURPOSE**: Single source of truth for understanding the entire codebase structure. Every architectural decision, file organization, and structural change is documented here. **MUST BE REVIEWED before every major change**.
>
> **🌟 Multi-Tenancy Context**: This is the **FRAMEWORK** repository. Business ontologies live in SEPARATE repositories. Client implementations live in THEIR OWN repositories. This repo provides the core engine, tools, and templates.

## 📊 Architecture Philosophy & Status

### **🏗️ Current Architecture State: MODERNIZED**
```bash
✅ Framework Repository (State-of-the-Art)
├── 🧬 ontologia/           # Clean domain + application layers
├── 📦 packages/            # Distribution packages (API, CLI, etc.)
├── 🧪 tests/               # Modern testing infrastructure
├── 📚 docs/                # User-centric documentation
├── 🛠️ scripts/             # Utility and automation scripts
├── 🎭 templates/           # Project scaffolding templates
├── 🎮 playground/          # Development environment
└── ⚙️ config/              # Configuration management
```

### **🎯 Architecture Health Score: 85/100**
- ✅ **Domain Separation**: Clean domain/application split
- ✅ **Testing Infrastructure**: State-of-the-art testing framework
- ✅ **Documentation**: User-centric, modern structure
- ✅ **Multi-Tenancy**: Proper isolation strategy
- ⚠️ **Package Organization**: Needs minor cleanup
- ⚠️ **Legacy Code**: Some technical debt remains

### **🚀 Recent Improvements (Last 30 Days)**
1. **🧪 Testing Infrastructure**: Complete SotA testing framework
2. **📚 Documentation Restructure**: User-centric content organization
3. **🏗️ Domain Clean Architecture**: Proper layer separation
4. **🔧 Modern Tooling**: Pydantic Settings, Ty, Ruff, Black, Pytest
5. **🏢 Multi-Tenancy Strategy**: Clear separation patterns

## 📁 Root Directory Structure (CURRENT STATE)

### **✅ Well-Organized Root Files**
```bash
📄 ontologia.toml           # Project configuration (Pydantic Settings)
📄 pyproject.toml           # Modern Python packaging
📄 pyproject.test.toml      # Testing configuration
📄 alembic.ini              # Database migration config
📄 mkdocs.yml               # Documentation site config
📄 Justfile                 # Task automation
📄 README.md                # Project overview
📄 CHANGELOG.md             # Version history
📄 ONTOLOGIA_SDK_ROADMAP.md # Development roadmap
📄 .env.example             # Environment template
📄 .gitignore               # Git ignore rules
📄 .pre-commit-config.yaml  # Git hooks
```

### **🗂️ Core Directory Structure**
```bash
ontologia/                  # 🧬 Core framework engine
├── domain/                 # 🎯 Pure domain logic
│   ├── metamodels/        # Schema definitions
│   ├── instances/         # Instance management
│   ├── change_sets/       # Change tracking
│   └── shared/            # Shared domain types
├── application/           # 🔄 Application services
│   ├── metamodel_service.py
│   ├── instances_service.py
│   ├── actions_service.py
│   └── analytics_service.py
├── infrastructure/        # 🔧 External concerns (DB, APIs)
│   ├── repositories/      # Data access layer
│   ├── external_apis/     # External service clients
│   ├── temporal/          # Workflow orchestration
│   └── cache/             # Caching layer
├── actions/               # ⚡ Dynamic action system
│   ├── temporal/          # Temporal workflow actions
│   ├── exceptions.py      # Action error handling
│   └── registry.py        # Action registration
└── event_handlers/        # 📡 Event processing
    ├── cache.py           # Cache invalidation
    ├── graph.py           # Graph event handlers
    └── __init__.py
```

### **📦 Distribution Packages**
```bash
packages/                  # 📦 Framework distribution packages
├── ontologia_api/         # 🌐 FastAPI REST API
│   ├── core/              # API configuration and middleware
│   ├── dependencies/      # FastAPI dependencies
│   ├── v2/                # API v2 implementation
│   │   ├── routers/       # Route definitions
│   │   ├── schemas/       # Pydantic models
│   │   └── handlers/      # Business logic handlers
│   └── actions/           # API action endpoints
├── ontologia_cli/         # 💻 Command-line interface
│   ├── main.py            # CLI entry point
│   ├── config.py          # CLI configuration
│   └── playground.py      # Development environment
├── ontologia_agent/       # 🤖 AI agent integration
│   ├── engine.py          # Agent execution engine
│   ├── skills/            # Agent skill definitions
│   └── __init__.py
└── datacatalog/           # 📊 Data catalog integration
    ├── models.py          # Data catalog models
    └── __init__.py
```

### **🧪 Modern Testing Infrastructure**
```bash
tests/                     # 🧪 State-of-the-art testing framework
├── fixtures/              # 🛠️ Test data and utilities
│   ├── factories.py       # Factory pattern for test data
│   └── enhanced_conftest.py # Modern pytest fixtures
├── unit/                  # 🔬 Unit tests (80% of tests)
│   └── examples/          # Reference implementations
├── integration/           # 🔗 Integration tests (15%)
│   ├── api/               # API integration tests
│   └── domain/            # Domain integration tests
├── e2e/                   # 🔍 End-to-end tests (5%)
├── performance/           # ⚡ Performance benchmarks
├── contracts/             # 📋 API contract tests
└── conftest.py            # Base pytest configuration
```

### **📚 User-Centric Documentation**
```bash
docs/                      # 📚 Modern documentation structure
├── index.md               # 🏠 User-friendly landing page
├── getting-started/       # 🚀 User onboarding journey
├── ontology-design/       # 🧬 Business domain design
├── framework-development/ # 🏗️ Core engine development
├── deployment/            # 🚀 Installation and operations
├── integration/           # 🔧 External system integration
├── reference/             # 📋 Complete technical reference
├── tutorials/             # 🎓 Step-by-step learning paths
├── guides/                # 📖 Practical how-to guides
├── architecture/          # 🏛️ System design documentation
│   ├── DOCUMENTATION_STRATEGY.md
│   ├── MULTI_TENANCY_STRATEGY.md
│   └── TESTING_STRATEGY.md
└── archive/               # 📦 Historical documentation
```

## 🔌 Event Bus Abstraction

- Core services depend on the `DomainEventBus` protocol for publishing (`publish`, `publish_many`).
- In-process subscription is modeled via `SubscribableEventBus` (extends `DomainEventBus` with `subscribe`/`unsubscribe`).
- The application resolves a concrete bus via `ontologia.event_bus.get_event_bus()` and registers handlers only when the bus is in-process.
- Distributed buses (e.g., Kafka) publish events; handler wiring occurs out-of-process.

## 🧬 OGM-first Source of Truth

- Author object/link types in Python under `ontology_definitions/models/` using `ObjectModel` and `LinkModel`.
- CLI commands:
  - `ontologia-cli apply --source python --module ontology_definitions.models` applies schema from Python.
  - `ontologia-cli export:yaml --module ontology_definitions.models --out ontologia` exports YAML for interoperability.
  - `--source yaml` remains supported for legacy workflows.
- See `docs/migration_ogm.md` for a step-by-step migration guide.

### **🛠️ Supporting Infrastructure**
```bash
scripts/                   # 🛠️ Automation and utility scripts
├── main_sync.py           # Main synchronization script
├── prepare_duckdb_raw.py  # DuckDB data preparation
├── guardrails_arch.py     # Architecture validation
└── __init__.py

templates/                 # 🎭 Project scaffolding templates
└── project/               # Project template collection
    ├── dbt_project/       # DBT project templates
    ├── examples/          # Example projects
    └── ontology/          # Ontology templates

playground/                # 🎮 Development environment
├── README.md              # Playground setup guide
├── docker-compose.yml     # Development services
└── scripts/               # Playground utilities

config/                    # ⚙️ Configuration management
├── redis.conf             # Redis configuration
├── temporal/              # Temporal workflow config
│   ├── helmfile.yaml
│   ├── values-postgres.yaml
│   └── values-temporal.yaml
└── alembic/               # Database migration config
    ├── env.py
    ├── script.py.mako
    └── versions/          # Migration versions

alembic/                   # 🗄️ Database migrations
├── versions/              # Migration version files
│   ├── d0b63df993c6_initial_schema.py
│   ├── 8f5b8f7e2c6d_add_dataset_governance_fields.py
│   └── 3d47cf7fa5eb_add_metamodel_versioning.py
├── env.py                 # Alembic environment
├── script.py.mako         # Migration template
└── README                 # Migration documentation

infra/                     # 🏗️ Infrastructure as Code
└── temporal/              # Temporal deployment configs
    ├── helmfile.yaml
    ├── values-postgres.yaml
    └── values-temporal.yaml

data/                      # 📊 Data directory (gitignored)
└── realtime/              # Real-time data processing
    └── rules/             # Processing rules
```

## 🎯 Architecture Patterns & Principles

### **🏗️ Clean Architecture Implementation**
```python
# ✅ Proper layer separation
## 🎯 **Proposed Clean Root Structure**

### 📋 **Ideal Root (After Cleanup)**
```bash
ontologia/
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── ARCHITECTURE_LEDGER.md   # 🏗️ STRUCTURE DOCUMENTATION
├── Justfile                 # Task runner
├── README.md               # 📖 ONLY MARKDOWN AT ROOT
├── config/                  # All configurations
├── examples/                # 📚 Project templates and examples
├── infra/                   # Infrastructure code
├── ontologia/               # 🧬 Core domain
├── packages/                # 📦 Distribution packages
├── playground/              # 🎮 Development env
├── scripts/                 # 🛠️ Utility scripts
├── templates/               # 🎭 Project templates
└── tests/                   # 🧪 Test suite

# 🗄️ Hidden data directory (gitignored)
.data/                      # Environment-specific data
├── development/            # Dev databases and projects
├── staging/               # Staging data
├── production/            # Production data
└── shared/                # Cross-project shared data
```

## 🔄 **Migration Plan**

### Phase 1: Database Cleanup
```bash
# Move all DB files to data/
mkdir -p data/databases
mv *.db data/databases/
mv *.duckdb data/databases/
```

### Phase 2: Config Consolidation
```bash
# Create config subdirectories
mkdir -p config/docker config/alembic
mv docker-compose.*.yml config/docker/
mv alembic.ini config/alembic/
```

### Phase 3: Documentation Cleanup
```bash
# Move markdown files to docs/
mkdir -p docs/{changelog,guides,roadmaps}
mv CHANGELOG.md docs/changelog/
mv DOCKER_*.md docs/guides/
mv *_ROADMAP.md docs/roadmaps/
```

## 📝 **Maintenance Rules**

### ✅ **Before Every Commit:**
1. [ ] Review this LEDGER file
2. [ ] Update if any new files/folders added
3. [ ] Ensure new files follow the structure
4. [ ] No new markdown files at root (except README updates)

### 🚫 **Forbidden at Root:**
- Database files (.db, .duckdb)
- Multiple markdown files (README.md only)
- Scattered config files
- Temporary/cache files

### ✅ **Allowed at Root:**
- Configuration files (.toml, .yaml, .ini)
- Build/dependency files (pyproject.toml, uv.lock)
- Development tool files (.pre-commit-config.yaml, Justfile)
- Single README.md as project overview

---

**🎯 This LEDGER is the living architecture document. Keep it accurate!**
