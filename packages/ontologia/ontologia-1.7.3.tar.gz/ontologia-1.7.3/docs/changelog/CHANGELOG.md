## [1.7.3] - 2025-11-17

### Fixed
- DI protocol compliance across core, API, and SDK layers
- Type errors in NATS event bus implementation (importlib.util usage)
- SQLAlchemy expression typing in edge repositories (desc() and cast() usage)
- Request parameter handling in API routers (Request parameter ordering)
- Elasticsearch repository Pydantic model handling (model_dump/dict typing)
- Duplicate return statement in service providers

### Changed
- Centralized dependency injection via factory functions
- Improved type safety with Protocol-based repositories
- Enhanced generated code exclusion from type checking (protobuf files)
- Standardized import patterns for dynamic module loading

### Technical Debt
- Resolved all Ty type checker errors across 236 files
- Cleaned up duplicate code statements
- Standardized SQLAlchemy expression patterns
- Enhanced type casting for Pydantic models

## [0.2.4] - 2025-10-25

- Added: Architecture guardrails script `scripts/guardrails_arch.py` with `Justfile` target `arch` (now part of `just check`).
- Changed: Centralized business services in core `ontologia/application/**` with API shims for backward compatibility:
  - `analytics_service.py`, `data_analysis_service.py`, `schema_evolution_service.py`, `change_set_service.py`, `datacatalog_service.py`, `migration_execution_service.py`, `query_planner.py` (used by `query_service.py`).
  - API keeps thin reexports under `apps/api/services/` to avoid breaking imports.
- Changed: Settings moved to core at `ontologia/application/settings.py` and reexported by `apps/api/core/settings.py`.
- Reorganized: Monorepo packages moved to `packages/**` (`ontologia_cli`, `ontologia_sdk`, `ontologia_agent`, `ontologia_dagster`, `ontologia_edge`, `datacatalog`); removed empty legacy root folders.
- Packaging: Wheel config updated to include `packages/ontologia_cli` and `packages/ontologia_sdk` in `[tool.hatch.build.targets.wheel].packages`.
- Quality: `just check` passes (Black, Ruff, Ty, tests). Test suite: 152 passing.
- Migration guidance: Prefer imports from `ontologia.application.*` and `ontologia.infrastructure.*`; API shims remain for a transition period.

## [0.2.2] - 2025-10-10

- Added: Temporal Actions endpoints (behind `USE_TEMPORAL_ACTIONS`):
  - Blocking execute via Temporal workflow: `POST /v2/ontologies/{ontology}/objects/{type}/{pk}/actions/{action}/execute`
  - Fire-and-forget start: `POST /v2/ontologies/{ontology}/objects/{type}/{pk}/actions/{action}/start`
  - Status: `GET /v2/ontologies/{ontology}/actions/runs/{workflowId}`
  - Cancel: `POST /v2/ontologies/{ontology}/actions/runs/{workflowId}:cancel`
- Added: Centralized configuration via Pydantic Settings (`api/core/settings.py`).
- Added: Temporal Web UI service in `docker-compose.temporal.yml` (http://localhost:8233).
- Added: Dagster daily schedule `pipeline_daily` for `pipeline_job`.
- Improved: Temporal activity retry policy in `ActionWorkflow`.
- Docs: New/updated guides (`docs/ACTIONS.md`, `docs/ENVIRONMENT.md`, `README.md`) for Temporal usage.
- Tests: Extended integration tests for Temporal start/status/cancel (suite now 54 passing).

# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-10-05

- Added: Advanced search endpoint `POST /v2/ontologies/{ontology}/objects/{type}/search` with filters (`eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `contains`, `in`), `orderBy`, and pagination.
- Added: Bulk load endpoints:
  - Objects: `POST /v2/ontologies/{ontology}/objects/{type}/load` (upsert multiple objects)
  - Links: `POST /v2/ontologies/{ontology}/links/{linkType}/load` (create/delete multiple links)
- Added: Analytics endpoint `POST /v2/ontologies/{ontology}/aggregate` supporting `COUNT`, `SUM`, `AVG` with optional `groupBy` and `where` (SQL fallback; graph path planned).
- Docs: Updated `docs/API_REFERENCE.md` and `docs/ONBOARDING.md` with examples for search, bulk, and analytics.
- Tests: Integration tests added for search, bulk, and aggregate; full suite passes (36).

## [0.2.0] - 2025-10-05

- Traversal endpoint implemented: `GET /v2/ontologies/{ontology}/objects/{type}/{pk}/{linkType}` with pagination and graph-backed reads (when `USE_GRAPH_READS=1`) plus SQL fallback.
- Repo/docs reorg: centralized docs under `docs/` (guides, reports, ADR), onboarding, architecture, API reference, environment, sync.
- Examples: Added `examples/library_quickstart.py` and `examples/api_quickstart.py`; updated `examples/README.md`.
- Hygiene: Ignored DB artifacts; moved legacy demo tests to `examples/legacy/`.
- Tests: Suite green (33) at the time of tagging.
