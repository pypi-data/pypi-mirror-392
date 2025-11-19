from __future__ import annotations

from typing import Any

from ontologia_mcp.server import _dbt_models_root, _resolve_path_in_root, _write_text_file, mcp


@mcp.tool()
def write_dbt_model(
    model_path: str,
    sql: str,
) -> dict[str, Any]:
    """Write or overwrite a dbt model file within the project models directory."""

    root = _dbt_models_root()
    resolved = _resolve_path_in_root(model_path, root)
    return _write_text_file(resolved, sql)


@mcp.tool()
def write_dbt_schema(
    schema_path: str,
    yaml: str,
) -> dict[str, Any]:
    """Write or overwrite a dbt schema.yml file within the project models directory."""

    root = _dbt_models_root()
    resolved = _resolve_path_in_root(schema_path, root)
    if resolved.suffix not in {".yml", ".yaml"}:
        raise ValueError("dbt schema files must end with .yml or .yaml")
    return _write_text_file(resolved, yaml)
