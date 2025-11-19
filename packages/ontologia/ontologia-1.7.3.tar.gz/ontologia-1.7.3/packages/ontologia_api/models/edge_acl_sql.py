from __future__ import annotations

from sqlmodel import Field, SQLModel


class EdgeNodeACL(SQLModel, table=True):
    """Allowed principals that can enqueue commands for a node.

    If no rows exist for a node, enqueue is allowed (open by default).
    If rows exist, the caller must present header X-Edge-Principal matching a row.
    """

    __tablename__ = "edge_node_acl"

    node_id: str = Field(primary_key=True)
    principal: str = Field(primary_key=True)
