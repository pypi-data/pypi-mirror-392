import asyncio
import os
from dataclasses import dataclass
from datetime import timedelta
from time import time
from typing import Any

from ontologia.domain.events import InMemoryEventBus
from ontologia.edge import (
    EdgeCommand,
    EdgeRuntime,
    EdgeRuntimeConfig,
    InMemoryEntityStateStore,
    SensorDetection,
)


@dataclass(slots=True)
class Capabilities:
    level: str
    sensors: list[str]
    actuators: list[str]
    transports: list[str]


class EdgeNodeSim:
    """Minimal Python edge node simulator.

    - Announces HELLO on start
    - Periodically emits EVENTs via EdgeRuntime (SensorDetection)
    - Accepts COMMANDs and routes to a mock actuator
    """

    def __init__(self, node_id: str, capabilities: Capabilities) -> None:
        self.node_id = node_id
        self.capabilities = capabilities
        self.bus = InMemoryEventBus()
        self.store = InMemoryEntityStateStore()
        self.runtime = EdgeRuntime(
            store=self.store, bus=self.bus, config=EdgeRuntimeConfig(startup_load_state=True)
        )
        self._actuator_commands: list[EdgeCommand] = []

    async def start(self) -> None:
        self._register_mock_devices()
        await self.runtime.start()
        await self._send_hello()

    async def stop(self) -> None:
        await self.runtime.stop()

    def _register_mock_devices(self) -> None:
        # Register one mock actuator to capture commands
        class _Actuator:
            name = "led"

            def __init__(self, sink: list[EdgeCommand]) -> None:
                self._sink = sink

            async def execute(self, command: EdgeCommand) -> None:
                self._sink.append(command)

        self.runtime.register_actuator(_Actuator(self._actuator_commands))  # type: ignore[arg-type]

    async def _send_hello(self) -> None:
        hello = {
            "type": "HELLO",
            "msg_id": self._ulid(),
            "node_id": self.node_id,
            "public_key": "TEST_ONLY_PUBLIC_KEY",  # replace with real key in firmware
            "capabilities": {
                "level": self.capabilities.level,
                "sensors": self.capabilities.sensors,
                "actuators": self.capabilities.actuators,
                "transports": self.capabilities.transports,
            },
            "software": {"sim": True},
            "timestamp": int(time()),
            "ttl": 5,
            "nonce": self._ulid(),
            "signature": "TEST_ONLY_SIGNATURE",
        }
        # In a real setup we would POST to core; for now, just print
        print("HELLO:", hello)

    async def emit_temperature(self, value: float) -> None:
        detection = SensorDetection(
            sensor_id=f"{self.node_id}:temp-1",
            object_type="temperature",
            ttl=timedelta(seconds=10),
            metadata={"entity_id": f"{self.node_id}:room"},
            components={
                "reading": {"value": value, "unit": "C"},
                "identity": {"id": f"{self.node_id}:room"},
            },
            event_type="upsert",
        )
        await self.runtime.ingest(detection)

    async def dispatch(self, action: str, payload: dict[str, Any]) -> None:
        cmd = EdgeCommand(target="led", action=action, payload=payload)
        await self.runtime.dispatch(cmd)

    @staticmethod
    def _ulid() -> str:
        # Simple ULID-ish generator for demo purposes only
        return os.urandom(10).hex()


async def main() -> None:
    node = EdgeNodeSim(
        node_id="sim-node-01",
        capabilities=Capabilities(
            level="L1", sensors=["temp"], actuators=["led"], transports=["ws"]
        ),
    )
    await node.start()

    # Emit a few synthetic temperature events
    for value in [26.9, 27.3, 27.8]:
        await node.emit_temperature(value)
        await asyncio.sleep(0.1)

    # Dispatch a command to the actuator
    await node.dispatch("set", {"on": True})

    # Show stored snapshots and published events
    snapshots = await node.store.load_snapshots()
    print("Snapshots:", [s.entity_id for s in snapshots])
    print("Bus events:", [e.event_name for e in node.bus.events])

    await node.stop()


if __name__ == "__main__":
    asyncio.run(main())
