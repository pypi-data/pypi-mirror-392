"""Domain event definitions and publishing contract."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Protocol, TypeVar, runtime_checkable

logger = logging.getLogger(__name__)

TEvent = TypeVar("TEvent", bound="DomainEvent")
EventHandler = Callable[[TEvent], Awaitable[None] | None]


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_name(self) -> str:
        return self.__class__.__name__


# Re-export context-specific events for backward compatibility
# TODO: add metamodel events when available in core

from ontologia.domain.instances.events import (  # noqa: F401 - Re-exports for compatibility
    LinkCreated,
    LinkDeleted,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
)


@runtime_checkable
class DomainEventBus(Protocol):
    """Interface for publishing domain events."""

    def publish(self, event: DomainEvent) -> None:  # pragma: no cover - interface
        ...

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)


@runtime_checkable
class SubscribableEventBus(DomainEventBus, Protocol):
    """Extension of DomainEventBus that supports in-process subscriptions.

    This augments the pure publishing contract with `subscribe`/`unsubscribe`
    used by in-process handler registration. Distributed implementations are
    expected to wire handlers out-of-process and thus need not implement it.
    """

    def subscribe(
        self, event_type: type[TEvent], handler: EventHandler[TEvent]
    ) -> None:  # pragma: no cover - interface
        ...

    def unsubscribe(
        self, event_type: type[TEvent], handler: EventHandler[TEvent]
    ) -> None:  # pragma: no cover - interface
        ...


class NullEventBus:
    """No-op event bus used by default."""

    def publish(self, event: DomainEvent) -> None:
        return None

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        return None


class InMemoryEventBus:
    """Test helper event bus that accumulates events."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    @property
    def events(self) -> list[DomainEvent]:
        return list(self._events)

    def publish(self, event: DomainEvent) -> None:
        self._events.append(event)

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)


@dataclass(frozen=True, slots=True, kw_only=True)
class ObjectTypeSynced(DomainEvent):
    """Event published when an ObjectType synchronization is completed."""

    object_type_api_name: str
    sync_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    records_processed: int = 0
    incremental: bool = False


class InProcessEventBus:
    """Simple in-process event bus with synchronous and async handler support."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler[DomainEvent]]] = defaultdict(list)
        self._lock = RLock()
        self._background_tasks: set[asyncio.Task[None]] = set()

    def subscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        with self._lock:
            self._handlers[event_type].append(handler)  # type: ignore[arg-type]

    def unsubscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        with self._lock:
            handlers = self._handlers.get(event_type)
            if not handlers:
                return
            try:
                handlers.remove(handler)  # type: ignore[arg-type]
            except ValueError:
                return
            if not handlers:
                self._handlers.pop(event_type, None)

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()

    def publish(self, event: DomainEvent) -> None:
        handlers = self._matching_handlers(type(event))
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    self._dispatch_async(result)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Error handling domain event %s", event.event_name)

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)

    def _matching_handlers(self, event_cls: type[DomainEvent]) -> list[EventHandler[DomainEvent]]:
        with self._lock:
            handlers: list[EventHandler[DomainEvent]] = []
            for registered_cls, registered_handlers in self._handlers.items():
                if issubclass(event_cls, registered_cls):
                    handlers.extend(registered_handlers)
            return handlers

    def _dispatch_async(self, awaitable: Awaitable[None]) -> None:
        async def _runner() -> None:
            await awaitable

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_runner())
        else:
            task = loop.create_task(_runner())
            # Store reference to prevent task from being garbage collected
            self._background_tasks.add(task)
            # Remove task from set when completed to prevent memory leak
            task.add_done_callback(self._background_tasks.discard)
