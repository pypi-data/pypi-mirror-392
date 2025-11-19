from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EdgeHello(BaseModel):
    type: str = Field("HELLO", description="Message type")
    msg_id: str
    node_id: str
    public_key: str
    capabilities: dict[str, Any]
    software: dict[str, Any] | None = None
    hw: dict[str, Any] | None = None
    timestamp: int
    ttl: int | None = None
    nonce: str
    signature: str


class EdgeState(BaseModel):
    type: str = Field("STATE", description="Message type")
    msg_id: str
    node_id: str
    state: dict[str, Any]
    timestamp: int
    ttl: int | None = None
    nonce: str
    signature: str


class EdgeEvent(BaseModel):
    type: str = Field("EVENT", description="Message type")
    msg_id: str
    node_id: str
    ont_type: str
    subject: str
    predicate: str
    object: Any | None = None
    unit: str | None = None
    components: dict[str, dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    timestamp: int
    ttl: int | None = None
    nonce: str
    signature: str

    def to_components(self) -> dict[str, dict[str, Any]]:
        if self.components:
            return {k: dict(v) for k, v in self.components.items()}
        obs = {
            "ont_type": self.ont_type,
            "predicate": self.predicate,
            "value": self.object,
        }
        if self.unit is not None:
            obs["unit"] = self.unit
        return {"observation": obs}
