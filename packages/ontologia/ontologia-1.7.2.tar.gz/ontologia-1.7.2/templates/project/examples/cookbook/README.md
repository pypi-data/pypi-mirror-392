# Cookbook

Topic-focused walkthroughs that complement the docs. Run from the repo root.

## Prerequisites

- Core deps: `uv sync`
- Recommended: run the API locally
  ```bash
  PYTHONPATH=apps:packages:. uv run uvicorn ontologia_api.main:app --reload
  ```
- Token (for API-backed examples):
  ```bash
  curl -X POST http://127.0.0.1:8000/v2/auth/token \
       -H "Content-Type: application/x-www-form-urlencoded" \
       -d "username=admin&password=admin"
  ```

## Index

- `example_unified_linktype.py` — Define and traverse a unified LinkType.
- `cookbook_01_dsl_search.py` — Fluent search DSL and ordering.
- `cookbook_02_link_traversal.py` — Typed link traversal patterns.
- `cookbook_03_actions_namespace.py` — Actions via object-level namespaces.
- `cookbook_04_pagination.py` — Typed pagination helpers.
- `cookbook_05_full_lifecycle_demo.py` — End-to-end lifecycle.

## Run

```bash
echo "TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v2/auth/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin' | jq -r .access_token)" > /dev/null
uv run python example_project/examples/cookbook/cookbook_01_dsl_search.py
```
