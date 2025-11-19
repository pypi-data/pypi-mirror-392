from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel


class EdgeNode(SQLModel, table=True):
    """Registered EdgeNode with capabilities and public key."""

    __tablename__ = "edge_node"

    node_id: str = Field(primary_key=True, index=True)
    public_key: str | None = Field(default=None, description="Base64/PEM public key")
    level: str | None = Field(default=None, description="L0/L1/L2")
    sensors: list[str] | None = Field(default=None, sa_column=Column(JSON))
    actuators: list[str] | None = Field(default=None, sa_column=Column(JSON))
    transports: list[str] | None = Field(default=None, sa_column=Column(JSON))
    software: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    hw: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    # Protocol negotiation/preferences
    sig_algo: str | None = Field(default=None, description="Signature algorithm (e.g., ed25519)")
    canonical_mode: str | None = Field(default=None, description="json|cbor")
    last_seen: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)


class EdgeNodeState(SQLModel, table=True):
    """Latest reported STATE snapshot (for observability/debug)."""

    __tablename__ = "edge_node_state"

    node_id: str = Field(primary_key=True, index=True)
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)


class EdgeMessageReceipt(SQLModel, table=True):
    """Dedup table storing recently seen message ids with TTL expiry."""

    __tablename__ = "edge_msg_receipt"

    msg_id: str = Field(primary_key=True, index=True)
    node_id: str | None = Field(default=None, index=True)
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(index=True)

    @classmethod
    def compute_expiry(cls, ttl: int | None) -> datetime:
        seconds = ttl if ttl and ttl > 0 else 60
        return datetime.now(UTC) + timedelta(seconds=seconds)
