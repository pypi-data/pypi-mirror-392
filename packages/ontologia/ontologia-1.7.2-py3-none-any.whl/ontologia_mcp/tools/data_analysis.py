from __future__ import annotations

from typing import Any

from fastapi import Depends
from sqlalchemy import inspect

from ontologia_mcp.server import (
    _data_analysis_service,
    _data_root,
    _engine,
    _resolve_path_in_root,
    mcp,
)


@mcp.tool()
def analyze_data_source(
    source_path: str,
    sample_size: int = 100,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile a tabular data source (CSV/TSV/Parquet) for ontology planning."""

    resolved_root = _data_root()
    resolved_path = _resolve_path_in_root(source_path, resolved_root)
    profile = service.profile_source(resolved_path, sample_size=sample_size)
    profile.update(
        {
            "base_directory": str(resolved_root),
            "resolved_path": str(resolved_path),
        }
    )
    return profile


@mcp.tool()
def analyze_sql_table(
    connection_url: str,
    table_name: str,
    sample_size: int = 100,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile a relational database table accessible via SQLAlchemy."""

    return service.profile_sql_table(
        connection_url,
        table_name,
        sample_size=sample_size,
    )


@mcp.tool()
def analyze_rest_endpoint(
    url: str,
    sample_size: int = 100,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    array_path: str | None = None,
    timeout_seconds: float = 30.0,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile JSON responses served by REST endpoints."""

    return service.profile_rest_endpoint(
        url,
        sample_size=sample_size,
        method=method,
        headers=headers,
        array_path=array_path,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def analyze_relational_schema(
    connection_url: str,
    *,
    schema: str | None = None,
    include_views: bool = False,
) -> dict[str, Any]:
    """Inspect relational schema metadata (tables + foreign keys)."""

    try:
        with _engine(connection_url) as engine:
            inspector = inspect(engine)

            tables: dict[str, list[str]] = {}
            for table_name in inspector.get_table_names(schema=schema):
                cols = inspector.get_columns(table_name, schema=schema)
                tables[table_name] = [str(col.get("name")) for col in cols]

            views: dict[str, list[str]] = {}
            if include_views:
                for view_name in inspector.get_view_names(schema=schema):
                    cols = inspector.get_columns(view_name, schema=schema)
                    views[view_name] = [str(col.get("name")) for col in cols]

            foreign_keys: list[dict[str, Any]] = []
            for table_name in tables:
                for fk in inspector.get_foreign_keys(table_name, schema=schema):
                    foreign_keys.append(
                        {
                            "fromTable": table_name,
                            "fromColumns": list(fk.get("constrained_columns") or []),
                            "toTable": fk.get("referred_table"),
                            "toColumns": list(fk.get("referred_columns") or []),
                            "name": fk.get("name"),
                            "schema": schema,
                            "referredSchema": fk.get("referred_schema"),
                        }
                    )

            payload: dict[str, Any] = {
                "tables": tables,
                "foreignKeys": foreign_keys,
            }
            if include_views:
                payload["views"] = views
            return payload
    except Exception as exc:  # pragma: no cover - defensive error mapping
        raise ValueError(f"Failed to analyze relational schema: {exc}") from exc
