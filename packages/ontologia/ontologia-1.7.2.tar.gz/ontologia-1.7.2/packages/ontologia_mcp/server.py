"""MCP server (FastMCP) for Ontologia.

This module defines the FastMCP instance, shared dependencies, and utility helpers.
Tool functions are organized under ontologia_mcp.tools.* modules and registered via the shared MCP instance.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends
from fastmcp import FastMCP  # type: ignore
from ontologia_api.core.auth import UserPrincipal, require_role
from ontologia_api.core.database import get_session
from ontologia_api.core.temporal import get_temporal_client
from ontologia_api.dependencies.realtime import ensure_runtime_started, get_runtime
from ontologia_api.services.actions_service import ActionsService
from ontologia_api.services.analytics_service import AnalyticsService
from ontologia_api.services.change_set_service import ChangeSetService
from ontologia_api.services.data_analysis_service import DataAnalysisService
from ontologia_api.services.datacatalog_service import DataCatalogService
from ontologia_api.services.instances_service import InstancesService
from ontologia_api.services.linked_objects_service import LinkedObjectsService
from ontologia_api.services.metamodel_service import MetamodelService
from ontologia_api.services.migration_execution_service import MigrationExecutionService
from ontologia_api.services.schema_evolution_service import SchemaEvolutionService
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session

DEFAULT_SERVICE = "ontology"
DEFAULT_INSTANCE = "default"

mcp = FastMCP("ontologia-mcp")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_root(env_value: str | None, default_relative: Path) -> Path:
    if env_value:
        candidate = Path(env_value)
        if not candidate.is_absolute():
            candidate = (_project_root() / candidate).resolve()
        else:
            candidate = candidate.resolve()
        return candidate
    return (_project_root() / default_relative).resolve()


def _data_root() -> Path:
    return _resolve_root(os.getenv("ONTOLOGIA_AGENT_DATA_ROOT"), Path("data/uploads"))


def _dbt_models_root() -> Path:
    return _resolve_root(
        os.getenv("ONTOLOGIA_DBT_MODELS_ROOT"),
        Path("example_project/dbt_project/models"),
    )


def _resolve_path_in_root(path_str: str, root: Path) -> Path:
    root_resolved = root.resolve()
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = (root_resolved / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(
            f"Path '{candidate}' is outside the allowed directory '{root_resolved}'."
        ) from exc
    return candidate


@contextmanager
def _engine(connection_url: str) -> Iterator[Engine]:
    engine = create_engine(connection_url)
    try:
        yield engine
    finally:  # pragma: no cover - defensive cleanup
        engine.dispose()


def _run_sync(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def _serialize_realtime_event(event) -> dict[str, Any]:
    return {
        "sequence": event.sequence,
        "eventType": event.event_type,
        "entityId": event.entity_id,
        "objectType": event.object_type,
        "provenance": event.provenance,
        "updatedAt": event.updated_at.isoformat() if event.updated_at else None,
        "expiresAt": event.expires_at.isoformat() if event.expires_at else None,
        "components": {key: dict(value) for key, value in event.components.items()},
        "metadata": dict(event.metadata),
    }


def _service(principal: UserPrincipal | None) -> tuple[str, str]:
    _ = principal
    return DEFAULT_SERVICE, DEFAULT_INSTANCE


def _metamodel_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> MetamodelService:
    service, instance = _service(principal)
    return MetamodelService(session, service=service, instance=instance, principal=principal)


def _instances_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> InstancesService:
    service, instance = _service(principal)
    return InstancesService(session, service=service, instance=instance, principal=principal)


def _instances_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> InstancesService:
    service, instance = _service(principal)
    return InstancesService(session, service=service, instance=instance, principal=principal)


def _datacatalog_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> DataCatalogService:
    service, instance = _service(principal)
    return DataCatalogService(session, service=service, instance=instance, principal=principal)


def _datacatalog_read_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> DataCatalogService:
    service, instance = _service(principal)
    return DataCatalogService(session, service=service, instance=instance, principal=principal)


def _linked_objects_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> LinkedObjectsService:
    service, instance = _service(principal)
    return LinkedObjectsService(session, service=service, instance=instance, principal=principal)


def _linked_objects_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> LinkedObjectsService:
    service, instance = _service(principal)
    return LinkedObjectsService(session, service=service, instance=instance, principal=principal)


def _data_analysis_service() -> DataAnalysisService:
    return DataAnalysisService()


def _change_sets_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> ChangeSetService:
    service, instance = _service(principal)
    return ChangeSetService(session, service=service, instance=instance, principal=principal)


def _change_sets_admin_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
) -> ChangeSetService:
    service, instance = _service(principal)
    return ChangeSetService(session, service=service, instance=instance, principal=principal)


def _serialize_change_set(service: ChangeSetService, record) -> dict[str, Any]:
    dataset = service._dataset_by_rid(record.dataset_rid)
    dataset_api_name = dataset.api_name if dataset else record.api_name
    return {
        "apiName": record.api_name,
        "rid": record.rid,
        "name": record.name,
        "status": record.status,
        "targetObjectType": record.target_object_type,
        "baseBranch": record.base_branch,
        "description": record.description,
        "datasetApiName": dataset_api_name,
        "createdAt": record.created_at.isoformat(),
        "createdBy": record.created_by,
        "approvedAt": record.approved_at.isoformat() if record.approved_at else None,
        "payload": dict(record.payload or {}),
    }


def _analytics_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> AnalyticsService:
    service, instance = _service(principal)
    return AnalyticsService(session, service=service, instance=instance, principal=principal)


def _schema_evolution_service(
    metamodel: MetamodelService = Depends(_metamodel_service),
    analytics: AnalyticsService = Depends(_analytics_service),
) -> SchemaEvolutionService:
    return SchemaEvolutionService(metamodel, analytics)


def _migration_execution_context(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
):
    service_name, instance = _service(principal)
    return MigrationExecutionService(session), service_name, instance


def _actions_viewer_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ActionsService:
    service, instance = _service(principal)
    return ActionsService(session, service=service, instance=instance, principal=principal)


def _actions_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    temporal_client=Depends(get_temporal_client),
) -> ActionsService:
    service, instance = _service(principal)
    return ActionsService(
        session,
        service=service,
        instance=instance,
        temporal_client=temporal_client,
        principal=principal,
    )


def _relative_to_project(path: Path) -> str:
    project = _project_root()
    try:
        return str(path.relative_to(project))
    except ValueError:  # pragma: no cover - defensive
        return str(path)


def _pipeline_command() -> list[str]:
    override = os.getenv("ONTOLOGIA_PIPELINE_COMMAND")
    if override:
        return override.split()
    return ["ontologia-cli", "pipeline", "run"]


def _write_text_file(path: Path, content: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.rstrip("\n") + "\n"
    path.write_text(normalized, encoding="utf-8")
    return {
        "path": _relative_to_project(path),
        "bytes_written": len(normalized.encode("utf-8")),
    }


# Register tools by importing modules after 'mcp' and helpers are defined.
from ontologia_mcp.tools.actions import (  # noqa: F401,F403
    execute_action,
    list_actions,
)
from ontologia_mcp.tools.analytics import aggregate_objects  # noqa: F401,F403
from ontologia_mcp.tools.change_sets import (  # noqa: F401,F403
    approve_change_set,
    create_change_set,
    list_change_sets,
)
from ontologia_mcp.tools.data_analysis import (  # noqa: F401,F403
    analyze_data_source,
    analyze_relational_schema,
    analyze_rest_endpoint,
    analyze_sql_table,
)
from ontologia_mcp.tools.dbt_pipeline import (  # noqa: F401,F403
    write_dbt_model,
    write_dbt_schema,
)
from ontologia_mcp.tools.instances import (  # noqa: F401,F403
    delete_object,
    get_object,
    list_objects,
    search_objects,
    upsert_object,
)
from ontologia_mcp.tools.linked_objects import (  # noqa: F401,F403
    create_link,
    delete_link,
    get_link,
    list_links,
)
from ontologia_mcp.tools.metamodel import (  # noqa: F401,F403
    delete_link_type,
    delete_object_type,
    get_object_type,
    list_link_types,
    list_object_types,
    upsert_link_type,
    upsert_object_type,
)
from ontologia_mcp.tools.migration_execution import (  # noqa: F401,F403
    run_migration_task,
    run_pending_migrations,
)
from ontologia_mcp.tools.schema_evolution import (  # noqa: F401,F403
    apply_schema_changes,
    list_migration_tasks,
    plan_schema_changes,
    update_migration_task,
)


@mcp.tool()
def stream_ontology_events(
    duration_seconds: float = 5.0,
    *,
    max_events: int = 100,
    object_types: list[str] | None = None,
    entity_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Collect real-time events from in-memory runtime for a bounded window."""
    if max_events <= 0:
        return {
            "events": [],
            "count": 0,
            "durationSeconds": duration_seconds,
            "objectTypes": object_types or [],
            "entityIds": entity_ids or [],
        }

    object_type_set = {str(it) for it in object_types} if object_types else None
    entity_id_set = {str(it) for it in entity_ids} if entity_ids else None

    async def _collect(
        seconds: float,
        limit: int,
        types: set[str] | None,
        ids: set[str] | None,
    ) -> list[dict[str, Any]]:
        await ensure_runtime_started()
        runtime = get_runtime()
        queue = runtime.subscribe_events()
        events: list[dict[str, Any]] = []
        loop = asyncio.get_running_loop()
        deadline = loop.time() + max(seconds, 0)
        try:
            while len(events) < limit:
                timeout = deadline - loop.time()
                if timeout <= 0:
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=timeout)
                except TimeoutError:
                    break
                if types and event.object_type not in types:
                    continue
                if ids and event.entity_id not in ids:
                    continue
                events.append(_serialize_realtime_event(event))
        finally:
            runtime.unsubscribe_events(queue)
        return events

    events = _run_sync(_collect(duration_seconds, max_events, object_type_set, entity_id_set))
    return {
        "events": events,
        "count": len(events),
        "durationSeconds": duration_seconds,
        "objectTypes": sorted(object_type_set) if object_type_set else [],
        "entityIds": sorted(entity_id_set) if entity_id_set else [],
    }


@mcp.tool()
def run_pipeline(timeout_seconds: int = 1800) -> dict[str, Any]:
    """Execute the Ontologia data pipeline and return captured logs."""
    command = _pipeline_command()
    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(_project_root()))
    try:
        result = subprocess.run(  # noqa: S603
            command,
            cwd=_project_root(),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            f"Unable to execute pipeline command {' '.join(command)}: executable not found"
        ) from exc
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - defensive
        raise TimeoutError(
            f"Pipeline command {' '.join(command)} timed out after {timeout_seconds}s"
        ) from exc

    status = "ok" if result.returncode == 0 else "error"
    return {
        "status": status,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": command,
    }


app = mcp.http_app()
