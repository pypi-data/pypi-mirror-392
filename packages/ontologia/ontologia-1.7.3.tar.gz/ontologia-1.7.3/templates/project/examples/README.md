# Examples

This directory groups runnable examples and snippets by purpose.

## Quickstarts

Short scripts that mirror the onboarding journey.

- `quickstarts/library_quickstart.py` — use services directly without HTTP.
  ```bash
  uv run python templates/project/examples/quickstarts/library_quickstart.py
  ```
- `quickstarts/api_quickstart.py` — call the HTTP API via FastAPI TestClient.
  ```bash
  uv run python templates/project/examples/quickstarts/api_quickstart.py
  ```
- `quickstarts/mcp_tooling_quickstart.py` — manage the ontology via the MCP surface using a service token.
  ```bash
  uv run python templates/project/examples/quickstarts/mcp_tooling_quickstart.py
  ```

## Automation workflows

Utilities that support the Architect agent and other automated flows.

- `automation/issue_agent_service_token.py` — mint a JWT for `agent-architect-01` (prints JSON with the token).
  ```bash
  uv run python templates/project/examples/automation/issue_agent_service_token.py
  ```
- `automation/agent_apply_plan.py` — apply a sample ObjectType plan inside a sandbox created with `ontologia-cli genesis`.
  ```bash
  uv run python templates/project/examples/automation/agent_apply_plan.py
  ```

## Cookbook

Narrative, topic-focused walkthroughs that complement the documentation.

- `cookbook/example_unified_linktype.py` — define and interact with a unified LinkType.
- `cookbook/cookbook_01_dsl_search.py` → `cookbook_05_full_lifecycle_demo.py` — deep dives into DSL search, traversal, actions, pagination, and full lifecycle flows.

## Legacy

Older demos live under `legacy/` for archival purposes. They are kept for reference but are not part of the recommended onboarding path.
