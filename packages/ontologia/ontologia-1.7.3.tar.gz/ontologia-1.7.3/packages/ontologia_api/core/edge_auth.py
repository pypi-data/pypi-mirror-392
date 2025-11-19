from __future__ import annotations

import os

from fastapi import Header, HTTPException, status


async def require_edge_token(x_edge_token: str | None = Header(default=None)) -> None:
    """Simple shared-secret check for edge endpoints.

    If EDGE_SHARED_TOKEN is set, require header X-Edge-Token to match.
    If not set, allow (no-op) to keep local/dev flows simple.
    """
    expected = os.getenv("EDGE_SHARED_TOKEN")
    if not expected:
        return
    if x_edge_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid edge token")


async def require_edge_admin(x_edge_admin_token: str | None = Header(default=None)) -> None:
    """Stronger guard for admin endpoints (keys/receipts).

    If EDGE_ADMIN_TOKEN is set, require header X-Edge-Admin-Token to match.
    If not set, allow.
    """
    expected = os.getenv("EDGE_ADMIN_TOKEN")
    if not expected:
        return
    if x_edge_admin_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
