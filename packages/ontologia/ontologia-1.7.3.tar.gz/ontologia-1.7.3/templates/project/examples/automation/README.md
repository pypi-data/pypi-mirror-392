# Automation

Utilities that support the Architect agent and automated workflows.

## Prerequisites

- Install agent/MCP extras once:
  ```bash
  uv sync --group agents
  ```

## Issue a service token

Mint a long-lived token for the built-in `agent-architect-01` user (kept in memory for dev):

```bash
uv run python templates/project/examples/automation/issue_agent_service_token.py
```

Output JSON contains the token and user context. You can export it for other examples:

```bash
export ONTOLOGIA_AGENT_TOKEN=$(uv run python templates/project/examples/automation/issue_agent_service_token.py | jq -r .token)
```

## Apply a sample plan with the Architect agent

Run inside a sandbox created with `ontologia-cli genesis` (the script reads `.ontologia/state.json`).

```bash
uv run python templates/project/examples/automation/agent_apply_plan.py
```

The script creates a feature branch and writes a sample ObjectType YAML. Review and apply with the CLI or via PR.
