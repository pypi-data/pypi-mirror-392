from __future__ import annotations

from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.metamodel import (
    LinkTypePutRequest,
    ObjectTypePutRequest,
)

from ontologia_mcp.server import _metamodel_service, mcp


@mcp.tool()
def upsert_object_type(
    api_name: str,
    schema: ObjectTypePutRequest,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Create or update an ObjectType definition."""

    result = service.upsert_object_type(api_name, schema)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_object_type(
    api_name: str,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Delete an ObjectType by apiName."""

    service.delete_object_type(api_name)
    return {"status": "deleted", "apiName": api_name}


@mcp.tool()
def get_object_type(
    api_name: str,
    version: int | None = None,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Fetch a single ObjectType definition."""

    result = service.get_object_type(api_name, version=version)
    if result is None:
        raise ValueError(f"ObjectType '{api_name}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def upsert_link_type(
    api_name: str,
    schema: LinkTypePutRequest,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Create or update a LinkType definition."""

    result = service.upsert_link_type(api_name, schema)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_link_type(
    api_name: str,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Delete a LinkType by apiName."""

    service.delete_link_type(api_name)
    return {"status": "deleted", "apiName": api_name}


@mcp.tool()
def list_object_types(
    service=Depends(_metamodel_service),
) -> list[dict[str, Any]]:
    """List all ObjectTypes available in the current ontology."""

    items = service.list_object_types()
    return [item.model_dump(exclude_none=True) for item in items]


@mcp.tool()
def list_link_types(
    service=Depends(_metamodel_service),
) -> list[dict[str, Any]]:
    """List all LinkTypes available in the current ontology."""

    items = service.list_link_types()
    return [item.model_dump(exclude_none=True) for item in items]
