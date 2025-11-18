from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from typing import Any

from ontologia.domain.events import DomainEvent, DomainEventBus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KafkaConnectionConfig:
    bootstrap_servers: Iterable[str]
    topic_prefix: str
    client_id: str | None = None
    synchronous_publish: bool = False
    security_protocol: str | None = None
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: str | None = None


class KafkaEventBus(DomainEventBus):
    def __init__(self, config: KafkaConnectionConfig) -> None:
        try:
            from confluent_kafka import Producer
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "Kafka support requires the 'confluent-kafka' package. Install it with 'pip install confluent-kafka'."
            ) from exc

        producer_config: dict[str, Any] = {
            "bootstrap.servers": ",".join(config.bootstrap_servers),
        }
        if config.client_id:
            producer_config["client.id"] = config.client_id
        if config.security_protocol:
            producer_config["security.protocol"] = config.security_protocol
        if config.sasl_mechanism:
            producer_config["sasl.mechanism"] = config.sasl_mechanism
        if config.sasl_username:
            producer_config["sasl.username"] = config.sasl_username
        if config.sasl_password:
            producer_config["sasl.password"] = config.sasl_password

        self._producer = Producer(producer_config)
        self._config = config

    def publish(self, event: DomainEvent) -> None:
        self._produce(event)

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self._produce(event)

    def _produce(self, event: DomainEvent) -> None:
        topic = f"{self._config.topic_prefix}.{event.event_name}"
        payload = json.dumps(_serialize_event(event)).encode("utf-8")
        key = _extract_event_key(event)

        def delivery_report(err, msg):  # pragma: no cover - callback path
            if err is not None:
                logger.error("Kafka delivery failed for %s: %s", msg.topic(), err)

        try:
            self._producer.produce(
                topic,
                value=payload,
                key=key.encode("utf-8") if key else None,
                callback=delivery_report if self._config.synchronous_publish else None,
            )
        except BufferError:  # pragma: no cover - backpressure path
            logger.warning("Kafka local queue is full; flushing producer")
            self._producer.poll(1.0)
            self._producer.produce(
                topic,
                value=payload,
                key=key.encode("utf-8") if key else None,
            )

        if self._config.synchronous_publish:
            self._producer.flush()
        else:
            self._producer.poll(0)


def _serialize_event(event: DomainEvent) -> dict[str, Any]:
    if is_dataclass(event):
        data = {field.name: getattr(event, field.name) for field in fields(event)}
    else:  # pragma: no cover - fallback path
        data = {key: value for key, value in vars(event).items() if not key.startswith("_")}

    data["event_name"] = event.event_name
    data["occurred_at"] = event.occurred_at.isoformat()

    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()

    return data


def _extract_event_key(event: DomainEvent) -> str | None:
    for attribute in ("primary_key_value", "object_type_api_name", "link_type_api_name"):
        value = getattr(event, attribute, None)
        if isinstance(value, str) and value:
            return value
    return None


__all__ = ["KafkaConnectionConfig", "KafkaEventBus"]
