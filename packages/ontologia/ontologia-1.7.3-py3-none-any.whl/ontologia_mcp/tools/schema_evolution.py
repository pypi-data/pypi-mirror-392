from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends

from ontologia_mcp.server import _schema_evolution_service, mcp


@mcp.tool()
def plan_schema_changes(
    definitions_dir: str | None = None,
    *,
    include_impact: bool = False,
    include_dependencies: bool = False,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    path = Path(definitions_dir).resolve() if definitions_dir else None
    return service.plan_schema_changes(
        definitions_dir=path,
        include_impact=include_impact,
        include_dependencies=include_dependencies,
    )


@mcp.tool()
def apply_schema_changes(
    definitions_dir: str | None = None,
    *,
    allow_destructive: bool = False,
    regenerate_sdk: bool = False,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    path = Path(definitions_dir).resolve() if definitions_dir else None
    return service.apply_schema_changes(
        definitions_dir=path,
        allow_destructive=allow_destructive,
        regenerate_sdk=regenerate_sdk,
    )


@mcp.tool()
def list_migration_tasks(
    status: str | None = None,
    service=Depends(_schema_evolution_service),
) -> list[dict[str, Any]]:
    return service.list_migration_tasks(status=status)


@mcp.tool()
def update_migration_task(
    task_rid: str,
    status: str,
    error_message: str | None = None,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    return service.update_migration_task(task_rid, status=status, error_message=error_message)
