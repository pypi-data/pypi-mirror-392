# DBT Guide (Phase 1)

This guide explains how to run and work with the DBT project used for Ontologia's transformations.

## Structure

- Project: `example_project/dbt_project/`
  - `dbt_project.yml`: DBT configuration (models/materializations)
  - `profiles.yml`: DBT profile. Uses `DUCKDB_PATH` env var for the DuckDB database path.
  - `models/`
    - `bronze/`: raw sources (declared via `sources`)
    - `silver/`: staging models (cleaning/standardization)
    - `gold/`: models consumed by the sync service

## Prerequisites

- Install dev dependencies:

```bash
uv sync --dev
```

- Set the database path:

```bash
export DUCKDB_PATH=$(pwd)/data/.local/local.duckdb
```

## Bootstrap & Build

Prepare raw tables and build the pipeline:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

What it does:
- Creates `employees_tbl` and `works_for_tbl` in DuckDB if missing (with seed rows)
- Runs `dbt deps` and `dbt build` (Bronze → Silver → Gold)
- Runs the sync loader to populate KùzuDB from Gold models

## Running DBT directly

From the project root:

```bash
cd example_project/dbt_project
export DBT_PROFILES_DIR=$(pwd)
uv run dbt deps
uv run dbt build
```

## Data Quality

- Gold `ontologia_employees`:
  - `id`: `unique`, `not_null`
- Gold `ontologia_works_for`:
  - `emp_id`: `not_null`
  - `company_id`: `not_null`

Add more tests as needed in `models/gold/schema.yml`.

## Data Contracts

Gold models in DBT serve as **data contracts** that define the expected schema and quality standards for your data. These contracts can be validated against your ontology definitions using the `ontologia test-contract` command.

### Contract Validation

Validate that your gold datasets match the ontology definitions:

```bash
# From the project root
uv run ontologia-cli test-contract --dir ./ontologia

# Or from anywhere with explicit paths
uv run ontologia-cli test-contract \
  --dir ./ontologia \
  --duckdb-path ./data/.local/local.duckdb
```

### Contract Benefits

1. **Schema Consistency**: Ensures DBT gold tables match ontology property definitions
2. **Type Validation**: Validates data type compatibility between ontology and physical tables
3. **Quality Assurance**: Enforces data quality rules defined in your ontology
4. **CI/CD Integration**: Include contract testing in your pipeline for continuous validation

### Example Contract Test Output

```bash
$ uv run ontologia-cli test-contract --dir ./ontologia

Status      ObjectType    Dataset/Table          Details
OK          employee      ontologia_employees    Schema matches object definition
OK          company       ontologia_companies    Schema matches object definition
ERROR       order         ontologia_orders        Type mismatch for 'order_date': expected timestamp, found string

❌ Contract tests failed with 1 error(s).
```

### Best Practices for Data Contracts

1. **Golden Records**: Use gold models as your single source of truth for data contracts
2. **Schema Evolution**: Update ontology definitions when changing gold model schemas
3. **Quality Rules**: Define comprehensive quality checks in your ontology definitions
4. **Regular Testing**: Include contract testing in your CI/CD pipeline
5. **Documentation**: Document contract violations and resolution procedures

## Docs & Lineage

Generate and serve your DBT docs:

```bash
cd example_project/dbt_project
export DBT_PROFILES_DIR=$(pwd)
uv run dbt docs generate
uv run dbt docs serve  # local server
```

## Notes

- To assume Gold schema in the sync and skip legacy renames:

```bash
export SYNC_ASSUME_GOLD_SCHEMA=1
```

- Unified graph mode (obrigatório): mantenha `features.use_unified_graph = true` em `ontologia.toml` (o padrão). Overrides que tentam desativar são ignorados.
