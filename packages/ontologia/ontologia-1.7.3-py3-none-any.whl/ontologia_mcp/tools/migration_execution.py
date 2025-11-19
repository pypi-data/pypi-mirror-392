from __future__ import annotations

from fastapi import Depends

from ontologia_mcp.server import _migration_execution_context, mcp


@mcp.tool()
def run_migration_task(
    task_rid: str,
    *,
    dry_run: bool = False,
    batch_size: int | None = None,
    ctx=Depends(_migration_execution_context),
) -> dict[str, object]:
    service, tenant_service, tenant_instance = ctx
    return service.run_task(
        service=tenant_service,
        instance=tenant_instance,
        task_rid=task_rid,
        dry_run=dry_run,
        batch_size=batch_size,
    )


@mcp.tool()
def run_pending_migrations(
    *,
    dry_run: bool = False,
    limit: int | None = None,
    batch_size: int | None = None,
    ctx=Depends(_migration_execution_context),
) -> list[dict[str, object]]:
    service, tenant_service, tenant_instance = ctx
    return service.run_pending_tasks(
        service=tenant_service,
        instance=tenant_instance,
        dry_run=dry_run,
        limit=limit,
        batch_size=batch_size,
    )
