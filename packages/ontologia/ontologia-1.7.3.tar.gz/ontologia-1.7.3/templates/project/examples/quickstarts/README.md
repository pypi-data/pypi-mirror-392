# Quickstarts

Guided, runnable scripts that mirror common onboarding paths. All examples assume you are in the repo root.

## Prerequisites

- Python toolchain managed with uv:
  - `uv sync` (core deps)
  - Optional agents/MCP: `uv sync --group agents`
- Start the API (optional for SDK mock fallbacks):
  ```bash
  PYTHONPATH=packages:. uv run uvicorn ontologia_api.main:app --reload
  # Docs: http://127.0.0.1:8000/docs
  ```
- Obtain a token (if calling the live API):
  ```bash
  curl -X POST http://127.0.0.1:8000/v2/auth/token \
       -H "Content-Type: application/x-www-form-urlencoded" \
       -d "username=admin&password=admin"
  ```

## Scripts

- library_quickstart.py — Services-only path (no HTTP). Uses in-memory SQLite.
  ```bash
  uv run python templates/project/examples/quickstarts/library_quickstart.py
  ```

- api_quickstart.py — SDK-first path; defaults to Mock client unless ONTOLOGIA_API_URL is set.
  ```bash
  export ONTOLOGIA_API_URL=http://127.0.0.1:8000
  uv run python templates/project/examples/quickstarts/api_quickstart.py
  ```

- mcp_tooling_quickstart.py — Manage ontology via MCP tools with a service token.
  ```bash
  # install agents deps once
  uv sync --group agents
  # service token: either export ONTOLOGIA_AGENT_TOKEN or generate one:
  uv run python templates/project/examples/automation/issue_agent_service_token.py
  export ONTOLOGIA_MCP_URL=http://127.0.0.1:8000/mcp
  uv run python templates/project/examples/quickstarts/mcp_tooling_quickstart.py
  ```
