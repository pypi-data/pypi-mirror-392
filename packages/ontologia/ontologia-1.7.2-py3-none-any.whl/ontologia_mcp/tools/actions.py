from __future__ import annotations

import os
from typing import Any

from fastapi import Depends
from ontologia_api.core.settings import get_settings
from ontologia_api.v2.schemas.actions import ActionExecuteRequest

from ontologia_mcp.server import _actions_editor_service, _actions_viewer_service, mcp


@mcp.tool()
def list_actions(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_actions_viewer_service),
) -> list[dict[str, Any]]:
    """List available Actions for a specific object instance."""

    context = {
        "user": {
            "id": service.principal.user_id if service.principal else "agent",
            "roles": service.principal.roles if service.principal else [],
            "tenants": service.principal.tenants if service.principal else {},
        }
    }
    actions = service.list_available_actions(object_type_api_name, pk_value, context=context)
    out: list[dict[str, Any]] = []
    for act in actions:
        params = {
            key: {
                "dataType": str(value.get("dataType")),
                "displayName": str(value.get("displayName")),
                "description": value.get("description"),
                "required": bool(value.get("required", True)),
            }
            for key, value in (act.parameters or {}).items()
        }
        out.append(
            {
                "apiName": act.api_name,
                "rid": getattr(act, "rid", None),
                "displayName": getattr(act, "display_name", act.api_name),
                "description": getattr(act, "description", None),
                "targetObjectType": act.target_object_type_api_name,
                "parameters": params,
            }
        )
    return out


@mcp.tool()
async def execute_action(
    object_type_api_name: str,
    pk_value: str,
    action_api_name: str,
    body: ActionExecuteRequest,
    service=Depends(_actions_editor_service),
) -> dict[str, Any]:
    """Execute an Action for an object, honoring Temporal configuration when enabled."""

    settings = get_settings()
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    params = dict(body.parameters or {})
    user_ctx = {
        "id": service.principal.user_id if service.principal else "agent",
        "roles": service.principal.roles if service.principal else [],
        "tenants": service.principal.tenants if service.principal else {},
    }
    if use_temporal:
        result = await service.execute_action_async(
            object_type_api_name,
            pk_value,
            action_api_name,
            params,
            user=user_ctx,
        )
    else:
        result = service.execute_action(
            object_type_api_name,
            pk_value,
            action_api_name,
            params,
            user=user_ctx,
        )
    return result
