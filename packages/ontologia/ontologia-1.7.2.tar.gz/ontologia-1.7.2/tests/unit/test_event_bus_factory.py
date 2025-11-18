import logging

from ontologia.application.settings import Settings
from ontologia.domain.events import InProcessEventBus, NullEventBus
from ontologia.event_bus import get_event_bus, reset_event_bus_cache


def setup_function():
    reset_event_bus_cache()


def test_get_event_bus_returns_in_process_by_default():
    settings = Settings(event_bus_provider="in_process")
    bus = get_event_bus(settings=settings, cache=False)
    assert isinstance(bus, InProcessEventBus)


def test_get_event_bus_supports_null_provider():
    settings = Settings(event_bus_provider="null")
    bus = get_event_bus(settings=settings, cache=False)
    assert isinstance(bus, NullEventBus)


def test_unknown_provider_falls_back_to_in_process(caplog):
    settings = Settings(event_bus_provider="does-not-exist")
    with caplog.at_level(logging.WARNING):
        bus = get_event_bus(settings=settings, cache=False)
    assert isinstance(bus, InProcessEventBus)
    assert any("Unknown event bus provider" in record.message for record in caplog.records)
