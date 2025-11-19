"""System-wide bounded contexts such as authentication."""

from __future__ import annotations

from fastapi import APIRouter
from ontologia_api.api.context import BoundedContext
from ontologia_api.v2.routers import auth


def build_contexts() -> list[BoundedContext]:
    """Assemble cross-cutting system bounded contexts."""

    auth_router = APIRouter(
        prefix="/v3/system/auth",
        tags=["System"],
    )
    auth_router.include_router(auth.router, tags=["System"])

    return [
        BoundedContext(
            name="System Access",
            router=auth_router,
            summary="Identity and authentication endpoints shared across bounded contexts.",
        )
    ]


__all__ = ["build_contexts"]
