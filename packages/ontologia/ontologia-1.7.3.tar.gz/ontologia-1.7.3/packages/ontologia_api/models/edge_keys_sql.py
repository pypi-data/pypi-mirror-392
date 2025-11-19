from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class EdgeNodeKey(SQLModel, table=True):
    """Edge node public keys with rotation and revocation support."""

    __tablename__ = "edge_node_key"

    key_id: str = Field(primary_key=True, index=True)
    node_id: str = Field(index=True)
    public_key: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = Field(default=None)
    active: bool = Field(default=False, index=True)
