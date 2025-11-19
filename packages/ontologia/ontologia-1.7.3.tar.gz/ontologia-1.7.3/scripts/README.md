# 🚀 Ontologia Scripts

This directory contains utility scripts for managing, deploying, and operating Ontologia instances. All scripts follow modern Python patterns with standardized configuration, logging, and error handling.

## 📁 Script Organization

### Core Scripts
- **`setup.py`** - Interactive setup wizard for different deployment modes
- **`main_sync.py`** - Ontology synchronization between data stores
- **`guardrails_arch.py`** - Architecture compliance checker

### Data & Analytics Scripts
- **`prepare_duckdb_raw.py`** - Bootstrap DuckDB tables for DBT projects

### Agent & Workflow Scripts
- **`run_architect_agent.py`** - AI agent interface for automated ontology operations
- **`run_watcher_agent.py`** - Real-time event monitoring and plan generation
- **`run_temporal_worker.py`** - Temporal workflow worker

### Shared Utilities
- **`utils/`** - Common patterns and helpers for all scripts

## 🛠️ Usage Patterns

### Standard CLI Interface
All scripts support common arguments:
```bash
--log-level DEBUG|INFO|WARNING|ERROR|CRITICAL
--config-root /path/to/config
--quiet          # Suppress console output
--verbose        # Enable verbose output
--version        # Show version information
```

### Configuration
Scripts use Pydantic Settings for configuration management:
- Environment variables (`.env` file supported)
- Command-line arguments
- Configuration files

### Logging
Standardized logging with Rich formatting:
- Colored console output
- Structured file logging (optional)
- Configurable log levels
- Rich tracebacks in debug mode

## 📋 Script Details

### Setup Script (`setup.py`)

**Purpose**: Guided setup for different deployment modes

**Modes**:
- `core` - Minimal setup (PostgreSQL + API)
- `analytics` - Adds DuckDB + dbt + Dagster
- `full` - Complete enterprise stack

**Usage**:
```bash
# Interactive mode
python scripts/setup.py

# Direct mode selection
python scripts/setup.py --mode core
python scripts/setup.py --mode analytics
python scripts/setup.py --mode full
```

**Features**:
- Dependency checking
- Docker orchestration
- Configuration generation
- Service health checks
- SDK generation

### Synchronization Script (`main_sync.py`)

**Purpose**: Execute ontology synchronization between data stores

**Usage**:
```bash
python scripts/main_sync.py
```

**Environment Variables**:
- `KUZU_DB_PATH` - KùzuDB database path
- `DUCKDB_PATH` - DuckDB database path
- `ONTOLOGIA_CONFIG_ROOT` - Configuration directory

**Features**:
- Multi-database synchronization
- Graceful dependency handling
- Transaction safety
- Progress logging

### Architecture Guardrails (`guardrails_arch.py`)

**Purpose**: Enforce architectural rules and prevent disallowed imports

**Usage**:
```bash
python scripts/guardrails_arch.py
```

**Rules**:
- Blocks imports from restricted modules
- Configurable allowed paths
- Automated CI/CD integration

### DuckDB Preparation (`prepare_duckdb_raw.py`)

**Purpose**: Bootstrap minimal DuckDB tables for DBT projects

**Usage**:
```bash
python scripts/prepare_duckdb_raw.py
```

**Features**:
- Creates `raw_data` schema
- Seeds sample data
- Idempotent operations

### Agent Scripts

#### Architect Agent (`run_architect_agent.py`)

**Purpose**: AI-powered ontology operations via MCP

**Usage**:
```bash
python scripts/run_architect_agent.py "Create ObjectType 'product' with sku and name"
```

**Environment**:
- `OPENAI_API_KEY` - OpenAI API key
- `ONTOLOGIA_AGENT_TOKEN` - Service account token
- `ONTOLOGIA_MCP_URL` - MCP server URL

#### Watcher Agent (`run_watcher_agent.py`)

**Purpose**: Real-time event monitoring and autonomous plan generation

**Usage**:
```bash
# Continuous monitoring
python scripts/run_watcher_agent.py

# Single run
python scripts/run_watcher_agent.py --once

# Custom configuration
python scripts/run_watcher_agent.py --interval 60 --duration 30
```

**Features**:
- Event streaming
- Drift detection
- Automated plan generation
- Configurable filtering

#### Temporal Worker (`run_temporal_worker.py`)

**Purpose**: Host workflow and activity workers for Temporal

**Usage**:
```bash
python scripts/run_temporal_worker.py
```

**Environment**:
- `TEMPORAL_ADDRESS` - Temporal server address
- `TEMPORAL_NAMESPACE` - Namespace
- `TEMPORAL_TASK_QUEUE` - Task queue name

## 🔧 Development

### Adding New Scripts

1. Use the shared utilities in `utils/`
2. Follow the `BaseCLI` pattern for consistent interfaces
3. Add comprehensive docstrings
4. Include proper error handling
5. Update this README

### Script Template

```python
#!/usr/bin/env python3
"""
Script description.

Usage:
    python scripts/your_script.py [options]

Examples:
    python scripts/your_script.py --input data.json
"""

from __future__ import annotations

from scripts.utils import BaseCLI, ExitCode, ScriptConfig

class YourCLI(BaseCLI):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--input", required=True, help="Input file")

    def run(self, args) -> ExitCode:
        self.logger.info("Starting script execution")
        # Your logic here
        return ExitCode.SUCCESS

def main() -> ExitCode:
    cli = YourCLI("your_script", "Your script description")
    return cli.main()

if __name__ == "__main__":
    raise SystemExit(main())
```

## 🧪 Testing

Scripts are tested in the `tests/scripts/` directory:

```bash
# Run all script tests
pytest tests/scripts/

# Run specific script tests
pytest tests/scripts/test_setup.py
```

## 📚 Dependencies

### Core Dependencies
- `pydantic-settings` - Configuration management
- `rich` - Console output and formatting
- `ty` - Type checking (development)

### Optional Dependencies
- `duckdb` - Analytics scripts (`uv sync --group analytics`)
- `kuzu` - Graph database operations (`uv sync --group full`)
- `temporalio` - Workflow execution (`uv sync --group full`)
- `pydantic-ai` - AI agent functionality (`uv sync --group agents`)

## 🔒 Security

- Scripts validate configuration and inputs
- Sensitive data is logged at appropriate levels
- API tokens are handled securely
- File operations use proper permissions

## 📈 Monitoring

- All scripts provide structured logging
- Exit codes follow standard conventions
- Progress indicators for long operations
- Error reporting with context

## 🤝 Contributing

When modifying scripts:
1. Maintain backward compatibility
2. Update documentation
3. Add tests for new functionality
4. Follow the established patterns
5. Use the shared utilities when possible
