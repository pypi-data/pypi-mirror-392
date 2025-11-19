Contributing Guide

Branching

- Default branches: `main` (stable), `develop` (integration). Feature branches off `develop`.
- Open PRs against `develop` unless it’s a hotfix targeting `main`.

Commit Messages

- Follow Conventional Commits:
  `type(scope): short summary`
  Common types: feat, fix, chore, docs, test, refactor, perf, ci, build, style, revert.
- The repo enforces this via a commit-msg hook (pre-commit).

Local Setup

- Install toolchain: `uv sync --dev`
- Install hooks: `just precommit-install`
- Run full quality gate: `just check`

Release Workflow

- Bump version: `just version-bump patch|minor|major` (updates `pyproject.toml` and `CHANGELOG.md`).
- Full release: `just release patch` then `just publish`.
- Tagging triggers CI release to PyPI: push a tag like `v1.7.2`.
- Update `docs/changelog/CHANGELOG.md` entry with actual notes.

CI/CD

- CI runs on PRs and pushes to `main`/`develop`: lint, format check, type check, guardrails, tests.
- Release runs on `v*` tags: builds artifacts, publishes to PyPI, creates GitHub Release with notes.
- Docs deploy runs on `main`: builds and publishes MkDocs to `gh-pages`.

Testing

- Unit + Contracts:
  - `PYTHONPATH=packages:. uv run pytest -q tests/unit tests/contracts`
- Integration (Redis + Elasticsearch):
  - Preferred (Docker running): Testcontainers automatically provisions services:
    - `PYTHONPATH=packages:. uv run pytest -q tests/integration`
  - Fallback to local endpoints:
    - `ELASTICSEARCH_URL=http://localhost:9200 REDIS_URL=redis://localhost:6379 \
       PYTHONPATH=packages:. uv run pytest -q tests/integration`
- Benchmarks (opt-in):
  - `RUN_BENCHMARK=true PYTHONPATH=packages:. uv run pytest -q tests/unit -k benchmark`

CI Jobs

- `quality`: Ruff (lint), Black (check), Mypy (types)
- `unit-contracts`: unit + contracts (parallel via `pytest-xdist`), coverage + JUnit XML artifacts
- `integration`: integration tests using Testcontainers (Docker available on the runner)

Artifacts are uploaded under `build/test-results` for CI visibility.

Security

- Do not include secrets in code or tests. Use environment variables and GitHub Secrets.
- Report vulnerabilities via a private issue or email the maintainer.
