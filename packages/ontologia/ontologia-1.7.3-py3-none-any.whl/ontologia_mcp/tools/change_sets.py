from __future__ import annotations

from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.change_sets import ChangeSetApproveRequest, ChangeSetCreateRequest

from ontologia_mcp.server import (
    _change_sets_admin_service,
    _change_sets_editor_service,
    _serialize_change_set,
    mcp,
)


@mcp.tool()
def create_change_set(
    name: str,
    target_object_type: str,
    description: str | None = None,
    base_branch: str | None = None,
    changes: list[dict[str, Any]] | None = None,
    service=Depends(_change_sets_editor_service),
) -> dict[str, Any]:
    """Create a change set for scenario-based write-backs."""

    request = ChangeSetCreateRequest(
        name=name,
        targetObjectType=target_object_type,
        description=description,
        baseBranch=base_branch,
        changes=list(changes or []),
    )
    record = service.create_change_set(request)
    return _serialize_change_set(service, record)


@mcp.tool()
def list_change_sets(
    status: str | None = None,
    service=Depends(_change_sets_editor_service),
) -> list[dict[str, Any]]:
    """List change sets with optional status filter."""

    items = service.list_change_sets(status)
    return [_serialize_change_set(service, it) for it in items]


@mcp.tool()
def approve_change_set(
    change_set_rid: str,
    commit_message: str | None = None,
    approved_by: str | None = None,
    service=Depends(_change_sets_admin_service),
) -> dict[str, Any]:
    """Approve a change set and advance its dataset branch."""

    request = ChangeSetApproveRequest(approvedBy=approved_by, commitMessage=commit_message)
    record = service.approve_change_set(change_set_rid, request)
    return _serialize_change_set(service, record)
