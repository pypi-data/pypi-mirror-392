from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol


@dataclass(slots=True)
class EdgeCommand:
    target: str
    action: str
    payload: dict[str, object]


class SensorDriver(Protocol):
    name: str

    async def start(self, runtime: EdgeRuntime) -> None: ...

    async def stop(self) -> None: ...


class ActuatorDriver(Protocol):
    name: str

    async def execute(self, command: EdgeCommand) -> None: ...


if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .runtime import EdgeRuntime

__all__ = ["ActuatorDriver", "EdgeCommand", "SensorDriver"]
