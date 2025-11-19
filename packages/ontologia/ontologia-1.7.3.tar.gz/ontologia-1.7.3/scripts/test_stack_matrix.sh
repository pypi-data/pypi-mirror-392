#!/usr/bin/env bash
set -euo pipefail

echo "Ontologia stack test matrix"
echo "This script runs pytest across common stack profiles."

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

run() { echo "+ $*"; eval "$*"; }

have_cmd() { command -v "$1" >/dev/null 2>&1; }

PYTEST="pytest -q"

echo "\n[1/6] Core SQL (minimal stack)"
run "STORAGE_MODE=sql_only RUN_BENCHMARK=0 $PYTEST tests/unit tests/integration"

echo "\n[2/6] Analytics + DuckDB"
if python - <<'PY'
import importlib.util as u; print('OK' if u.find_spec('duckdb') else 'MISSING')
PY
| grep -q OK; then
  TMP_DB=$(mktemp -t ontologia_bench.XXXXXX.duckdb)
  echo "Using DuckDB at $TMP_DB"
  run "RUN_BENCHMARK=1 STORAGE_MODE=sql_duckdb ONTOLOGIA_DUCKDB_PATH=$TMP_DB $PYTEST tests/unit tests/performance tests/integration"
  rm -f "$TMP_DB"
else
  echo "DuckDB not installed. Install with: pip install duckdb (or 'uv add duckdb')"
fi

echo "\n[3/6] Graph (Kùzu) reads (optional)"
if python - <<'PY'
import importlib.util as u; print('OK' if u.find_spec('kuzu') else 'MISSING')
PY
| grep -q OK; then
  run "USE_UNIFIED_GRAPH=1 $PYTEST tests/integration/test_api_v2_traversal_unified.py"
else
  echo "Kùzu not installed. Install with: pip install kuzu"
fi

echo "\n[4/6] Redis cache integration (optional)"
if python - <<'PY'
import importlib.util as u; print('OK' if u.find_spec('redis') else 'MISSING')
PY
| grep -q OK; then
  run "$PYTEST tests/integration/test_cache_integration.py"
else
  echo "redis-py not installed or Redis service not running; skipping."
fi

echo "\n[5/6] Elasticsearch integration (optional)"
if python - <<'PY'
import importlib.util as u; print('OK' if u.find_spec('elasticsearch') else 'MISSING')
PY
| grep -q OK; then
  run "$PYTEST tests/integration/test_elasticsearch_integration.py"
else
  echo "Elasticsearch client not installed or service not running; skipping."
fi

echo "\n[6/6] NATS event bus (optional)"
if python - <<'PY'
import importlib.util as u; print('OK' if u.find_spec('nats') else 'MISSING')
PY
| grep -q OK; then
  run "$PYTEST tests/unit/test_nats_event_bus.py"
else
  echo "nats-py not installed or NATS server not running; running mocked tests instead."
  run "$PYTEST -k nats tests/unit"
fi

echo "\nMatrix run complete."
