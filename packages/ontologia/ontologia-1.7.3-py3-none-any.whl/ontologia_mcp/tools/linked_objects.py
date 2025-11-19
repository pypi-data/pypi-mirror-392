from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.linked_objects import LinkCreateRequest

from ontologia_mcp.server import (
    _linked_objects_editor_service,
    _linked_objects_service,
    mcp,
)


@mcp.tool()
def create_link(
    link_type_api_name: str,
    body: LinkCreateRequest,
    service=Depends(_linked_objects_editor_service),
) -> dict[str, Any]:
    """Create a link between two objects following the LinkType definition."""

    result = service.create_link(link_type_api_name, body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def get_link(
    link_type_api_name: str,
    from_pk: str,
    to_pk: str,
    as_of: str | None = None,
    service=Depends(_linked_objects_service),
) -> dict[str, Any]:
    """Fetch a specific link between two objects."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc

    result = service.get_link(link_type_api_name, from_pk, to_pk, valid_at=as_of_dt)
    if result is None:
        raise ValueError(f"Link '{link_type_api_name}' from '{from_pk}' to '{to_pk}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def list_links(
    link_type_api_name: str,
    from_pk: str | None = None,
    to_pk: str | None = None,
    as_of: str | None = None,
    service=Depends(_linked_objects_service),
) -> dict[str, Any]:
    """List links of a LinkType, optionally filtered by endpoints."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc

    result = service.list_links(link_type_api_name, from_pk=from_pk, to_pk=to_pk, valid_at=as_of_dt)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_link(
    link_type_api_name: str,
    from_pk: str,
    to_pk: str,
    service=Depends(_linked_objects_editor_service),
) -> dict[str, Any]:
    """Delete a link between two objects."""

    deleted = service.delete_link(link_type_api_name, from_pk, to_pk)
    if not deleted:
        raise ValueError(f"Link '{link_type_api_name}' from '{from_pk}' to '{to_pk}' not found")
    return {
        "status": "deleted",
        "linkType": link_type_api_name,
        "fromPk": from_pk,
        "toPk": to_pk,
    }
