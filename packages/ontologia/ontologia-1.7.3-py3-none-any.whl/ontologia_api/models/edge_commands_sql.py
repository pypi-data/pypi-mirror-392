from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel


class CommandReceipt(SQLModel, table=True):
    """Durable record of edge commands lifecycle.

    Tracks enqueue -> delivery -> ack lifecycle with timestamps
    for observability and retry analysis.
    """

    __tablename__ = "edge_command_receipt"

    id: str = Field(primary_key=True, index=True)
    node_id: str = Field(index=True)
    target: str
    action: str
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    status: str = Field(default="queued", index=True)
    retries: int = Field(default=0)
    max_retries: int = Field(default=3)
    ack_timeout_seconds: int = Field(default=30)

    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    delivered_at: datetime | None = Field(default=None, index=True)
    acked_at: datetime | None = Field(default=None, index=True)
    expires_at: datetime | None = Field(default=None, index=True)
