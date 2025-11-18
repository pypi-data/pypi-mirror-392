from __future__ import annotations

from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.search import AggregateRequest

from ontologia_mcp.server import _analytics_service, mcp


@mcp.tool()
def aggregate_objects(
    body: AggregateRequest,
    service=Depends(_analytics_service),
) -> dict[str, Any]:
    """Run aggregate metrics (count/sum/avg) with optional grouping over objects."""

    result = service.aggregate(body)
    return result.model_dump(exclude_none=True)
