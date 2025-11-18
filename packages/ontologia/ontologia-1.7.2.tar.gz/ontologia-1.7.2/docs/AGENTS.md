# Repository Guidelines

## Project Structure & Module Organization
- Core library: `ontologia/` (domain, application, infrastructure).
- Packages: `packages/` (`ontologia_api`, `ontologia_cli`, `ontologia_sdk`, `ontologia_mcp`, `ontologia_edge`, etc.).
- Tests: `tests/` (pytest entry via `pyproject.toml`).
- Docs: `docs/` + `mkdocs.yml`; architecture notes in `ARCHITECTURE_LEDGER.md`.
- Config/data/templates: `config/`, `data/`, `templates/`, `ontology_definitions/`, `scripts/`.

## Build, Test, and Development Commands
Use Just + uv (see `Justfile`). Common examples:
- Setup: `just setup` — create dev env with `uv sync --dev`.
- Format: `just fmt` — Black + Ruff auto-fix.
- Lint: `just lint` — Ruff checks.
- Type check: `just type` — Ty/Pyright/Mypy per availability.
- Tests: `just test` or `uv run pytest -q`.
- Full check: `just check` — fmt → lint → arch → type → test.
- Run API: `just serve` (FastAPI via Uvicorn).
- Pipeline: `just pipeline` (uses `ontologia-cli`).

## Coding Style & Naming Conventions
- Python 3.11+; CI runs 3.11/3.12/3.13 and a forward-compat check on 3.14-dev. Prefer latest CPython locally, but keep code 3.11-compatible.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Linting: Ruff configured in `pyproject.toml` with selective ignores; import sort via Ruff (`I`).
- Types: prefer typed public APIs; strict in core domain per `tool.ty`/mypy settings.
- Pre-commit: `just precommit` before pushing.

## Testing Guidelines
- Framework: `pytest`; paths under `tests/`.
- Naming: files `test_*.py`, functions `test_*`.
- Markers: `unit`, `integration`, `slow`, `benchmark` (see `pyproject.toml`).
- Run quickly with `just test`; parallelization via `-n auto` if using `pytest-xdist`.

## Commit & Pull Request Guidelines
- Commit style: Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `test:`). Example: `feat: add ActionType CRUD with validation`.
- PRs: concise description, linked issues, screenshots for UI or API examples, notes on tests and migrations; pass `just check`.

## Security & Configuration Tips
- Config: copy `.env.example` to `.env`; common vars: `DUCKDB_PATH`, `ONTOLOGIA_CONFIG_ROOT`, `HOST`, `PORT`.
- Secrets: never commit credentials; prefer env vars.
- Optional groups: `uv sync --group agents` (agent tooling), `--group dev` (dev tools).

## PEP 723 Scripts
- Use for small, isolated examples and tools. Run with `uv run`.
- Examples: `examples/pep723/api_health.py`, `examples/pep723/openapi_fetch.py`.
- Override target with `BASE_URL` or `HOST`/`PORT` (defaults `127.0.0.1:8000`).

## References
- CLI entry: `ontologia-cli` (see `packages/ontologia_cli`).
- API service: `packages/ontologia_api`.
- More: `README.md` and `ARCHITECTURE_LEDGER.md`.

## Testing Playbook

This section captures how to consistently set up, run, and interpret tests across environments. It complements the Justfile.

- Environment setup:
  - `just setup` creates the dev env via `uv sync --dev` and installs test tooling.
  - Optional dependency groups (install as needed to enable specific test families):
    - Search: `uv sync --group search` (Elasticsearch client)
    - Workflows: `uv sync --group workflows` (Temporal)
    - MCP: `uv sync --group mcp` (Model Context Protocol)
    - Edge: `uv sync --group edge` (Redis, cryptography)
    - Orchestration: `uv sync --group orchestration` (Dagster)
  - Async tests: `pytest-asyncio` is part of `[dependency-groups].dev` (installed by `just setup`).

- Configuration and env vars:
  - Base test env in `pytest.ini` and `pyproject.toml` (e.g., `TESTING=1`, SQLite defaults).
  - Simplified settings default to in-memory SQLite for isolation. Override with:
    - `STORAGE_MODE=sql_only|sql_duckdb|sql_kuzu` when you want explicit storage.
    - `DATABASE_URL=sqlite:///:memory:` forces core/minimal semantics.
  - Common optional endpoints: Elasticsearch, Temporal, Redis, Kùzu are not required for core tests; related suites are skip-guarded when not installed.

- Running tests:
  - Full suite: `just test` or `PYTHONPATH=packages:. uv run pytest -q`
  - Unit-only: `PYTHONPATH=packages:. uv run pytest -q tests/unit`
  - Integration-only: `PYTHONPATH=packages:. uv run pytest -q tests/integration`
  - XML report: append `--junitxml=test-results/latest.xml` to persist JUnit.

- Type checks and lint:
  - Types: `just type` (Ty → Pyright → Mypy fallback). Core strictness focuses on `ontologia/`.
  - Lint: `just fmt` to auto-format + Ruff fixes; `just lint` for checks.

- Cache reset and test isolation:
  - Settings: `ontologia.application.settings.get_settings.cache_clear()` or use new helper(s) below.
  - Event bus + dependency singletons: `packages.ontologia_api.dependencies.events.reset_dependencies_caches()` clears settings, event bus, and repo singletons for clean test runs.

- Known testing pitfalls and resolutions:
  - Async tests failing with “async def functions are not natively supported”: ensure `just setup` has been run to install `pytest-asyncio`.
  - Optional deps missing (Temporal/ES/MCP/Redis): suites are skip-guarded. Install the relevant `uv --group` if you need to exercise them.
  - Graph repository NotImplemented: core paths now fall back to SQL when graph is unavailable (`GraphInstancesRepository.get_by_pk` returns `None`).
  - Unique constraint failures for query types in integration tests: fixtures must be idempotent; ensure teardown/unique values per run.
  - SQLite in-memory persistence across re-runs: the integration fixture uses a named `sqlite:///file:{nodeid}?mode=memory&cache=shared` engine. Re-running a single test multiple times in the same process may reuse the shared cache and keep state (e.g., auto-incremented QueryType versions). Run the full suite in a fresh process (`just test`) or adjust the fixture to drop tables at start if you need clean re-runs of a single test in dev.
  - ABAC filtering assertions: verify test settings for role/tag mappings align with expectations.
  - Dataset fixtures: some sync/integration tests expect specific datasets (e.g., `works_for_rels_ds`); ensure fixture creation runs or add setup.

- Core-first strategy (what we enforce in CI):
  - Unit suite should be green: `uv run pytest -q tests/unit`.
  - Type-check core: `uv run ty check` (remaining strict issues are tracked in docs/reports).
  - Full suite may require optional groups; CI jobs can matrix-install `search`/`workflows` as needed.

- Artifacts and reports:
  - Latest comprehensive test report: `docs/reports/test_report_2025-11-13.md` (clusters, triage, and action plan).
  - JUnit XML: `test-results/latest.xml`, unit-only: `test-results/unit-latest.xml`.

Use this playbook to reproduce results locally and to guide incremental fixes. If you change test setup behavior (fixtures/settings/providers), please update this section.
