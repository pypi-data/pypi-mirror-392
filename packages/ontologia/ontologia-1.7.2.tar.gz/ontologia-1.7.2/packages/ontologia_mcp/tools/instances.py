from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.instances import ObjectUpsertRequest
from ontologia_api.v2.schemas.search import ObjectSearchRequest

from ontologia_mcp.server import (
    _instances_editor_service,
    _instances_service,
    mcp,
)


@mcp.tool()
def list_objects(
    object_type_api_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    as_of: str | None = None,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """List object instances with optional filtering by ObjectType."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc
    result = service.list_objects(
        object_type_api_name,
        limit=limit,
        offset=offset,
        valid_at=as_of_dt,
    )
    return result.model_dump(exclude_none=True)


@mcp.tool()
def get_object(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """Fetch a single object instance by ObjectType and primary key."""

    result = service.get_object(object_type_api_name, pk_value)
    if result is None:
        raise ValueError(f"Object '{object_type_api_name}:{pk_value}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def upsert_object(
    object_type_api_name: str,
    pk_value: str,
    body: ObjectUpsertRequest,
    service=Depends(_instances_editor_service),
) -> dict[str, Any]:
    """Create or update an object instance with the provided properties."""

    result = service.upsert_object(object_type_api_name, pk_value, body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_object(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_instances_editor_service),
) -> dict[str, Any]:
    """Delete an object instance identified by ObjectType and primary key."""

    deleted = service.delete_object(object_type_api_name, pk_value)
    if not deleted:
        raise ValueError(f"Object '{object_type_api_name}:{pk_value}' not found")
    return {"status": "deleted", "objectType": object_type_api_name, "pkValue": pk_value}


@mcp.tool()
def search_objects(
    object_type_api_name: str,
    body: ObjectSearchRequest,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """Search for object instances using the Ontologia query DSL."""

    result = service.search_objects(object_type_api_name, body)
    return result.model_dump(exclude_none=True)
