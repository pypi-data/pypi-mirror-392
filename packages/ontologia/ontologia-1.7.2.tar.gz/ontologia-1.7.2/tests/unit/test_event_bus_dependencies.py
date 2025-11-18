from __future__ import annotations

from ontologia.domain.events import InProcessEventBus, NullEventBus
from packages.ontologia_api.dependencies import events


def _reset_caches() -> None:
    # Use a single helper to reset all related caches safely
    events.reset_dependencies_caches()


def test_shared_event_bus_defaults_to_inprocess(monkeypatch):
    monkeypatch.delenv("EVENT_BUS_BACKEND", raising=False)
    _reset_caches()

    bus = events.get_domain_event_bus()

    assert isinstance(bus, InProcessEventBus)


def test_shared_event_bus_supports_null_backend(monkeypatch):
    monkeypatch.setenv("EVENT_BUS_BACKEND", "none")
    _reset_caches()

    bus = events.get_domain_event_bus()

    assert isinstance(bus, NullEventBus)

    # Restore defaults to avoid leaking state between tests
    monkeypatch.setenv("EVENT_BUS_BACKEND", "inprocess")
    _reset_caches()
