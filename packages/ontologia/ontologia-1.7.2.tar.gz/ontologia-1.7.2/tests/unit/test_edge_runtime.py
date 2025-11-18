from datetime import timedelta

import pytest

from ontologia.domain.events import InMemoryEventBus
from ontologia.edge import (
    EdgeCommand,
    EdgeRuntime,
    EdgeRuntimeConfig,
    InMemoryEntityStateStore,
    SensorDetection,
)


class _TestSensor:
    def __init__(self, name: str, detection: SensorDetection) -> None:
        self.name = name
        self._detection = detection
        self.started = False
        self.stopped = False

    async def start(self, runtime: EdgeRuntime) -> None:
        self.started = True
        await runtime.ingest(self._detection)

    async def stop(self) -> None:
        self.stopped = True


class _TestActuator:
    def __init__(self) -> None:
        self.name = "motor"
        self.commands: list[EdgeCommand] = []

    async def execute(self, command: EdgeCommand) -> None:
        self.commands.append(command)


@pytest.mark.asyncio
async def test_edge_runtime_processes_sensor_and_command():
    store = InMemoryEntityStateStore()
    bus = InMemoryEventBus()
    runtime = EdgeRuntime(store=store, bus=bus, config=EdgeRuntimeConfig())

    detection = SensorDetection(
        sensor_id="lidar-1",
        object_type="obstacle",
        ttl=timedelta(seconds=5),
        metadata={"entity_id": "obs-9"},
        components={"pose": {"x": 1, "y": 2}},
    )

    sensor = _TestSensor("lidar", detection)
    runtime.register_sensor(sensor)  # type: ignore[arg-type]

    actuator = _TestActuator()
    runtime.register_actuator(actuator)  # type: ignore[arg-type]

    await runtime.start()
    snapshots = await store.load_snapshots()
    assert snapshots and snapshots[0].entity_id == "obs-9"
    assert sensor.started and not sensor.stopped
    assert any(getattr(event, "entity_id", None) == "obs-9" for event in bus.events)

    command = EdgeCommand(target="motor", action="set-speed", payload={"value": 3})
    await runtime.dispatch(command)
    assert actuator.commands[-1] == command

    await runtime.stop()
    assert sensor.stopped
