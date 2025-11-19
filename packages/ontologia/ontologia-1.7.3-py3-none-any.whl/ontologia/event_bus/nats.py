"""NATS EventBus implementation for high-performance event streaming."""

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
class NATSConnectionConfig:
    """Configuration for NATS connection."""

    servers: Iterable[str]
    subject_prefix: str = "ontologia"
    client_name: str | None = None
    synchronous_publish: bool = False
    max_reconnect_attempts: int = 60
    reconnect_wait: float = 2.0
    ping_interval: int = 20
    max_outstanding_pings: int = 3
    dont_randomize_servers: bool = False
    flush_timeout: float = 30.0
    user: str | None = None
    password: str | None = None
    token: str | None = None


class NATSEventBus(DomainEventBus):
    """NATS-based EventBus implementation."""

    def __init__(self, config: NATSConnectionConfig) -> None:
        from importlib import util as importlib_util

        if importlib_util.find_spec("nats") is None:
            raise RuntimeError(
                "NATS support requires the 'nats-py' package. Install it with 'pip install nats-py'."
            )

        self._config = config
        self._nc = None
        self._js = None
        self._connected = False

    async def _ensure_connection(self) -> None:
        """Ensure NATS connection is established."""
        if self._nc is None or not self._nc.is_connected:
            import nats
            from nats.js.errors import NotFoundError

            connect_options = {
                "servers": list(self._config.servers),
                "max_reconnect_attempts": self._config.max_reconnect_attempts,
                "reconnect_time_wait": self._config.reconnect_wait,
                "ping_interval": self._config.ping_interval,
                "max_outstanding_pings": self._config.max_outstanding_pings,
            }

            if self._config.client_name:
                connect_options["name"] = self._config.client_name
            if self._config.user:
                connect_options["user"] = self._config.user
            if self._config.password:
                connect_options["password"] = self._config.password
            if self._config.token:
                connect_options["token"] = self._config.token

            self._nc = await nats.connect(**connect_options)

            # Enable JetStream for persistence and replay
            try:
                self._js = self._nc.jetstream()
                # Create stream for ontologia events if it doesn't exist
                await self._ensure_stream()
            except NotFoundError:
                logger.warning("JetStream not available, using basic NATS")
                self._js = None

            self._connected = True
            logger.info("Connected to NATS servers: %s", ", ".join(self._config.servers))

    async def _ensure_stream(self) -> None:
        """Ensure JetStream stream exists."""
        if self._js is None:
            return

        stream_config = {
            "name": f"{self._config.subject_prefix}_events",
            "subjects": [f"{self._config.subject_prefix}.*"],
            "retention": "work_queue",  # Messages are removed after ack
            "max_bytes": -1,  # Unlimited size
            "max_age": 0,  # No expiration
            "storage": "file",  # Persistent storage
            "replicas": 1,  # Single replica for now
        }

        try:
            await self._js.add_stream(**stream_config)
            logger.info("Created JetStream stream: %s", stream_config["name"])
        except Exception as e:
            if "stream name already in use" not in str(e):
                logger.warning("Failed to create JetStream stream: %s", e)

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to NATS."""
        import asyncio

        from nats.errors import NoServersError

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a task
                asyncio.create_task(self._publish_async(event))
            else:
                # If we're not in an async context, run in new loop
                asyncio.run(self._publish_async(event))
        except NoServersError as e:
            logger.error("NATS connection failed: %s", e)
            raise
        except Exception as e:
            logger.error("Failed to publish event %s: %s", event.event_name, e)
            raise

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        """Publish multiple events to NATS."""
        import asyncio

        from nats.errors import NoServersError

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a task
                asyncio.create_task(self._publish_many_async(events))
            else:
                # If we're not in an async context, run in new loop
                asyncio.run(self._publish_many_async(events))
        except NoServersError as e:
            logger.error("NATS connection failed: %s", e)
            raise
        except Exception as e:
            logger.error("Failed to publish events: %s", e)
            raise

    async def _publish_async(self, event: DomainEvent) -> None:
        """Async publish implementation."""
        await self._ensure_connection()

        subject = f"{self._config.subject_prefix}.{event.event_name}"
        payload = json.dumps(_serialize_event(event)).encode("utf-8")
        headers = _extract_event_headers(event)

        try:
            if self._js is not None:
                # Use JetStream for persistence
                ack = await self._js.publish(subject, payload, headers=headers)
                logger.debug(
                    "Published event %s to JetStream: %s (stream: %s, seq: %s)",
                    event.event_name,
                    subject,
                    ack.stream,
                    ack.seq,
                )
            else:
                # Use basic NATS
                await self._nc.publish(subject, payload, headers=headers)
                logger.debug("Published event %s to NATS: %s", event.event_name, subject)

            if self._config.synchronous_publish:
                await self._nc.flush(self._config.flush_timeout)

        except Exception as e:
            logger.error("Failed to publish event %s: %s", event.event_name, e)
            raise

    async def _publish_many_async(self, events: Iterable[DomainEvent]) -> None:
        """Async batch publish implementation."""
        await self._ensure_connection()

        publish_tasks = []
        for event in events:
            publish_tasks.append(self._publish_async(event))

        # Wait for all publishes to complete
        import asyncio

        await asyncio.gather(*publish_tasks, return_exceptions=True)

    async def close(self) -> None:
        """Close NATS connection."""
        if self._nc is not None:
            try:
                await self._nc.flush()
                await self._nc.drain()
                await self._nc.close()
            except Exception as e:
                logger.warning("Error closing NATS connection: %s", e)
            finally:
                self._nc = None
                self._js = None
                self._connected = False
                logger.info("NATS connection closed")

    def __del__(self) -> None:
        """Cleanup on deletion."""
        try:
            if (
                hasattr(self, "_nc")
                and self._nc is not None
                and hasattr(self, "_connected")
                and self._connected
            ):
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.close())
                    else:
                        # Best effort cleanup
                        self._nc = None
                        self._js = None
                        self._connected = False
                except Exception:
                    pass  # Silently fail during cleanup
        except Exception:
            pass  # Silently fail during cleanup


def _serialize_event(event: DomainEvent) -> dict[str, Any]:
    """Serialize a domain event to JSON-serializable dict."""
    if is_dataclass(event):
        data = {field.name: getattr(event, field.name) for field in fields(event)}
    else:  # pragma: no cover - fallback path
        data = {key: value for key, value in vars(event).items() if not key.startswith("_")}

    data["event_name"] = event.event_name
    data["occurred_at"] = event.occurred_at.isoformat()

    # Convert datetime objects to ISO strings
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif hasattr(value, "__dict__"):
            # Convert complex objects to dict representation
            try:
                data[key] = value.__dict__
            except Exception:
                data[key] = str(value)

    return data


def _extract_event_headers(event: DomainEvent) -> dict[str, str]:
    """Extract NATS headers from event metadata."""
    headers = {}

    # Add event metadata as headers for filtering
    headers["X-Event-Name"] = event.event_name
    headers["X-Event-Timestamp"] = event.occurred_at.isoformat()

    # Add common event identifiers as headers
    for attribute in ("primary_key_value", "object_type_api_name", "link_type_api_name"):
        value = getattr(event, attribute, None)
        if isinstance(value, str) and value:
            header_name = f"X-{attribute.replace('_', '-').title()}"
            headers[header_name] = value

    return headers


__all__ = ["NATSConnectionConfig", "NATSEventBus"]
