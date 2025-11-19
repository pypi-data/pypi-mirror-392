from __future__ import annotations

import logging
from collections.abc import Callable

from ontologia.application.settings import Settings, get_settings
from ontologia.domain.events import DomainEventBus, InProcessEventBus, NullEventBus

from .kafka import KafkaConnectionConfig, KafkaEventBus
from .nats import NATSConnectionConfig, NATSEventBus

logger = logging.getLogger(__name__)

EventBusFactory = Callable[[Settings], DomainEventBus]

_FACTORIES: dict[str, EventBusFactory] = {}
_CACHE: dict[tuple, DomainEventBus] = {}


def register_event_bus_factory(
    name: str, factory: EventBusFactory, *, overwrite: bool = False
) -> None:
    key = name.strip().lower()
    if not key:
        raise ValueError("Event bus provider name cannot be empty")
    if key in _FACTORIES and not overwrite:
        raise ValueError(f"Event bus provider '{name}' is already registered")
    _FACTORIES[key] = factory


def reset_event_bus_cache() -> None:
    _CACHE.clear()


def _ensure_defaults_registered() -> None:
    if _FACTORIES:
        return

    register_event_bus_factory("in_process", lambda _: InProcessEventBus(), overwrite=True)
    register_event_bus_factory("inprocess", lambda _: InProcessEventBus(), overwrite=True)
    register_event_bus_factory("memory", lambda _: InProcessEventBus(), overwrite=True)

    register_event_bus_factory("null", lambda _: NullEventBus(), overwrite=True)
    register_event_bus_factory("disabled", lambda _: NullEventBus(), overwrite=True)
    register_event_bus_factory("none", lambda _: NullEventBus(), overwrite=True)

    register_event_bus_factory("kafka", _create_kafka_bus, overwrite=True)
    register_event_bus_factory("nats", _create_nats_bus, overwrite=True)


def _create_kafka_bus(settings: Settings) -> DomainEventBus:
    config = KafkaConnectionConfig(
        bootstrap_servers=settings.event_bus_kafka_bootstrap_servers,
        topic_prefix=settings.event_bus_kafka_topic_prefix,
        client_id=settings.event_bus_kafka_client_id,
        synchronous_publish=settings.event_bus_synchronous_publish,
        security_protocol=settings.event_bus_kafka_security_protocol,
        sasl_mechanism=settings.event_bus_kafka_sasl_mechanism,
        sasl_username=settings.event_bus_kafka_sasl_username,
        sasl_password=settings.event_bus_kafka_sasl_password,
    )
    return KafkaEventBus(config)


def _create_nats_bus(settings: Settings) -> DomainEventBus:
    config = NATSConnectionConfig(
        servers=settings.event_bus_nats_servers,
        subject_prefix=settings.event_bus_nats_subject_prefix,
        client_name=settings.event_bus_nats_client_name,
        synchronous_publish=settings.event_bus_synchronous_publish,
        max_reconnect_attempts=settings.event_bus_nats_max_reconnect_attempts,
        reconnect_wait=settings.event_bus_nats_reconnect_wait,
        ping_interval=settings.event_bus_nats_ping_interval,
        max_outstanding_pings=settings.event_bus_nats_max_outstanding_pings,
        dont_randomize_servers=settings.event_bus_nats_dont_randomize_servers,
        flush_timeout=settings.event_bus_nats_flush_timeout,
        user=settings.event_bus_nats_user,
        password=settings.event_bus_nats_password,
        token=settings.event_bus_nats_token,
    )
    return NATSEventBus(config)


def _cache_key(provider: str, settings: Settings) -> tuple:
    if provider in {"in_process", "inprocess", "memory", "null", "disabled", "none"}:
        return (provider,)

    if provider == "kafka":
        return (
            provider,
            tuple(settings.event_bus_kafka_bootstrap_servers),
            settings.event_bus_kafka_topic_prefix,
            settings.event_bus_kafka_client_id,
            settings.event_bus_synchronous_publish,
            settings.event_bus_kafka_security_protocol,
            settings.event_bus_kafka_sasl_mechanism,
            settings.event_bus_kafka_sasl_username,
        )

    if provider == "nats":
        return (
            provider,
            tuple(settings.event_bus_nats_servers),
            settings.event_bus_nats_subject_prefix,
            settings.event_bus_nats_client_name,
            settings.event_bus_synchronous_publish,
            settings.event_bus_nats_max_reconnect_attempts,
            settings.event_bus_nats_reconnect_wait,
            settings.event_bus_nats_ping_interval,
            settings.event_bus_nats_max_outstanding_pings,
            settings.event_bus_nats_dont_randomize_servers,
            settings.event_bus_nats_flush_timeout,
            settings.event_bus_nats_user,
            settings.event_bus_nats_token,
        )

    return (provider,)


def get_event_bus(settings: Settings | None = None, *, cache: bool = True) -> DomainEventBus:
    _ensure_defaults_registered()
    resolved_settings = settings or get_settings()
    provider_raw = resolved_settings.event_bus_provider or "in_process"
    provider = provider_raw.strip().lower().replace("-", "_")

    if provider not in _FACTORIES:
        logger.warning(
            "Unknown event bus provider '%s'; falling back to in_process implementation",
            provider_raw,
        )
        provider = "in_process"

    if not cache:
        return _FACTORIES[provider](resolved_settings)

    key = _cache_key(provider, resolved_settings)
    if key not in _CACHE:
        _CACHE[key] = _FACTORIES[provider](resolved_settings)
    return _CACHE[key]


__all__ = [
    "EventBusFactory",
    "KafkaConnectionConfig",
    "KafkaEventBus",
    "NATSConnectionConfig",
    "NATSEventBus",
    "get_event_bus",
    "register_event_bus_factory",
    "reset_event_bus_cache",
]
