from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

from ontologia.domain.events import DomainEventBus, NullEventBus

from .fusion import SensorDetection, SensorFusionEngine
from .sdk import ActuatorDriver, EdgeCommand, SensorDriver
from .storage import EntityStateStore


@dataclass(slots=True)
class EdgeRuntimeConfig:
    startup_load_state: bool = True


class EdgeRuntime:
    def __init__(
        self,
        *,
        store: EntityStateStore,
        bus: DomainEventBus | None = None,
        fusion: SensorFusionEngine | None = None,
        config: EdgeRuntimeConfig | None = None,
    ) -> None:
        self._store = store
        self._bus = bus or NullEventBus()
        self._fusion = fusion or SensorFusionEngine(store, bus=self._bus)
        self._config = config or EdgeRuntimeConfig()
        self._sensors: list[SensorDriver] = []
        self._actuators: dict[str, ActuatorDriver] = {}
        self._running = False
        self._lock = asyncio.Lock()

    @property
    def fusion(self) -> SensorFusionEngine:
        return self._fusion

    def register_sensor(self, driver: SensorDriver) -> None:
        self._sensors.append(driver)

    def register_actuator(self, driver: ActuatorDriver) -> None:
        self._actuators[driver.name] = driver

    async def start(self) -> None:
        async with self._lock:
            if self._running:
                return
            if self._config.startup_load_state:
                await self._fusion.load()
            for driver in self._sensors:
                await driver.start(self)
            self._running = True

    async def stop(self) -> None:
        async with self._lock:
            if not self._running:
                return
            for driver in self._sensors:
                await driver.stop()
            self._running = False

    async def ingest(self, detection: SensorDetection) -> None:
        await self._fusion.ingest(detection)

    async def dispatch(self, command: EdgeCommand) -> None:
        driver = self._actuators.get(command.target)
        if driver is None:
            raise KeyError(f"No actuator registered for target '{command.target}'")
        await driver.execute(command)

    async def heartbeat(self) -> datetime:
        return datetime.now(UTC)


__all__ = ["EdgeRuntime", "EdgeRuntimeConfig"]
