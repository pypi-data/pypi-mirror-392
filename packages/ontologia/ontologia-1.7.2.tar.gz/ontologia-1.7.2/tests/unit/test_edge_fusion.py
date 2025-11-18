from datetime import timedelta

import pytest

from ontologia.domain.events import InMemoryEventBus
from ontologia.edge import InMemoryEntityStateStore, SensorDetection, SensorFusionEngine


@pytest.mark.asyncio
async def test_sensor_fusion_generates_entity_event():
    store = InMemoryEntityStateStore()
    bus = InMemoryEventBus()
    engine = SensorFusionEngine(store, bus=bus)

    await engine.load()

    detection = SensorDetection(
        sensor_id="radar-1",
        object_type="vehicle",
        ttl=timedelta(seconds=1),
        components={"telemetry": {"speed": 42}},
        metadata={"entity_id": "veh-123"},
    )

    event = await engine.ingest(detection)

    assert event.entity_id == "veh-123"
    snapshots = await store.load_snapshots()
    assert snapshots and snapshots[0].components["telemetry"]["speed"] == 42
    assert any(getattr(item, "entity_id", None) == "veh-123" for item in bus.events)
