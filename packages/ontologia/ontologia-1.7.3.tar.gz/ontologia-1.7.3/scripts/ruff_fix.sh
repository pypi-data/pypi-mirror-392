#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required (https://github.com/astral-sh/uv)" >&2
  exit 1
fi

uv pip install ruff >/dev/null
uv run ruff check . --fix
echo "Ruff autofix completed. Review changes and run tests."

