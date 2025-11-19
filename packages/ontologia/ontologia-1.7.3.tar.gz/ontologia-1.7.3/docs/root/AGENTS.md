# Agent Runbook (Codex, Claude CLI, FactoryAI, etc.)

This runbook tells automated agents exactly how to work with this repo. It minimizes ambiguity and makes CI pass on the first try.

## Quick Facts

- Python: 3.11, 3.12, 3.13, 3.14 (tested)
- Package/runner: `uv` (fast Python package manager)
- Monorepo: `ontologia/` + `packages/`
- CI: GitHub Actions (`.github/workflows/tests.yml`)
- Coverage: Codecov (`codecov.yml`)

## Environment Prep

- Install Python 3.11+ and Docker (for integration via Testcontainers).
- Sync dependencies (creates `.venv`):
  - `uv sync --dev`
- All commands assume: `PYTHONPATH=packages:.`

## Quality Gates (Local)

- Lint: `uv run ruff check .`
- Format check: `uv run black --check .`
- Types: `PYTHONPATH=packages:. uv run mypy . --hide-error-codes --no-error-summary`
- Full local gate: `just check` (fmt → lint → type → test)

## Tests

- Unit + Contracts (fast):
  - `PYTHONPATH=packages:. uv run pytest -q tests/unit tests/contracts`
- Integration (Redis + Elasticsearch via Testcontainers):
  - With Docker running: `PYTHONPATH=packages:. uv run pytest -q tests/integration`
  - Fallback to local endpoints:
    - `ELASTICSEARCH_URL=http://localhost:9200 REDIS_URL=redis://localhost:6379 PYTHONPATH=packages:. uv run pytest -q tests/integration`
- Benchmarks (opt‑in):
  - `RUN_BENCHMARK=true PYTHONPATH=packages:. uv run pytest -q tests/unit -k benchmark`

## CI Behavior (What to Expect)

- Jobs (Linux, macOS, Windows):
  - `quality`: ruff, black check, mypy (3.11–3.14)
  - `unit-contracts`: pytest with xdist, coverage + JUnit artifacts (3.11–3.14)
  - `integration` (Linux): Testcontainers (Redis + Elasticsearch)
  - `nightly-benchmarks`: saves `.benchmarks` artifacts
- Coverage upload to Codecov runs on Linux + Python 3.11 only.
- Coverage gate: `--cov-fail-under=60` (raise after baseline).

Additional jobs:

- `pre-commit`: runs repo’s hooks in CI (same as local `just precommit`)
- `docs`: builds MkDocs with `--strict` and uploads `site/` as an artifact
- `package`: builds wheel/sdist and runs `twine check`
- `security`: runs `pip-audit` against direct and resolved dependencies (advisory check)

## Common Tasks

- Implement a feature:
  - Add code under `ontologia/` or `packages/`
  - Run `just check` locally; fix lint/type issues
  - Run unit + contracts; add/update tests if needed
  - If integration‑related, run `tests/integration` with Docker
- Fix a failing test:
  - Run the specific test file/function: `uv run pytest -q path::test_name`
  - Use logs: logging is enabled (replaced raw prints)
- Add a dependency:
  - Add to `pyproject.toml` (project or dev group)
  - `uv sync` and commit lockfile changes if present

## Conventions

- Commits: Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`, etc.)
- Style: Ruff/Black enforced in CI; fix before pushing
- Types: mypy strict-ish; prefer typed signatures
- Tests: prefer fast unit tests; mark heavy ones as integration or benchmark

## Integration Notes

- Testcontainers manages Redis/Elasticsearch automatically; no manual compose required in CI
- If Docker is unavailable locally, set `ELASTICSEARCH_URL`/`REDIS_URL` to a running stack and tests will use it; otherwise integration tests skip

## Artifacts & Debugging

- CI stores JUnit + coverage at `build/test-results/`
- Nightly job uploads `.benchmarks/` for performance history

## Pitfalls

- Windows path quirks: CI uses Python to create directories instead of `mkdir -p`
- Analytics service: identifier validation added; Ruff may still flag S608 (false positive when identifiers are validated)
- Import order in a few modules intentionally fixed to avoid cycles (per-file ignore I001 present)

## Where to Change Things

- CI workflow: `.github/workflows/tests.yml`
- Testcontainers config: `tests/integration/conftest.py`
- Codecov thresholds/comments: `codecov.yml`
- Lint/type config: `pyproject.toml`
- Contributor docs: `CONTRIBUTING.md`

## Minimal OK Checklist (Before PR)

- [ ] `uv run ruff check .` → OK
- [ ] `uv run black --check .` → OK
- [ ] `PYTHONPATH=packages:. uv run mypy .` → OK
- [ ] `PYTHONPATH=packages:. uv run pytest -q tests/unit tests/contracts` → OK
- [ ] Integration‑specific changes validated (Docker): `PYTHONPATH=packages:. uv run pytest -q tests/integration`

If you are an agent: follow this runbook verbatim. If something fails, attach the failing command output and the file diff you propose to change.
