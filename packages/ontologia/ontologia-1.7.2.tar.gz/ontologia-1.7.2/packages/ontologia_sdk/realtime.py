"""
Real-time subscription support for the Ontologia SDK.

Provides WebSocket-based real-time data streaming and event handling
with automatic reconnection, filtering, and batch processing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import weakref
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    from websockets.exceptions import ConnectionClosed, ConnectionClosedError

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None  # type: ignore[assignment]
    WebSocketClientProtocol = None  # type: ignore[assignment]
    ConnectionClosed = Exception  # type: ignore[assignment]
    ConnectionClosedError = Exception  # type: ignore[assignment]

from .session import ClientSession

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of real-time events."""

    OBJECT_CREATED = "object_created"
    OBJECT_UPDATED = "object_updated"
    OBJECT_DELETED = "object_deleted"
    TYPE_CREATED = "type_created"
    TYPE_UPDATED = "type_updated"
    TYPE_DELETED = "type_deleted"
    LINK_CREATED = "link_created"
    LINK_UPDATED = "link_updated"
    LINK_DELETED = "link_deleted"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    ERROR = "error"


@dataclass
class RealtimeEvent:
    """Real-time event data."""

    type: EventType
    data: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    object_type: str | None = None
    object_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionFilter:
    """Filter for subscription events."""

    object_types: list[str] | None = None
    event_types: list[EventType] | None = None
    object_ids: list[str] | None = None
    properties: dict[str, Any] | None = None  # Property-based filtering

    def matches(self, event: RealtimeEvent) -> bool:
        """Check if event matches this filter."""
        # Filter by object types
        if self.object_types and event.object_type not in self.object_types:
            return False

        # Filter by event types
        if self.event_types and event.type not in self.event_types:
            return False

        # Filter by object IDs
        if self.object_ids and event.object_id not in self.object_ids:
            return False

        # Filter by properties
        if self.properties:
            event_data = event.data
            for prop_name, expected_value in self.properties.items():
                if prop_name not in event_data or event_data[prop_name] != expected_value:
                    return False

        return True


class SubscriptionManager:
    """Manages multiple subscriptions and their filters."""

    def __init__(self):
        self._subscriptions: dict[str, SubscriptionFilter] = {}
        self._handlers: dict[str, list[Callable[[RealtimeEvent], None]]] = defaultdict(list)
        self._next_id = 1

    def add_subscription(
        self, filter: SubscriptionFilter, handler: Callable[[RealtimeEvent], None]
    ) -> str:
        """
        Add a new subscription.

        Args:
            filter: Subscription filter
            handler: Event handler function

        Returns:
            Subscription ID
        """
        sub_id = f"sub_{self._next_id}"
        self._next_id += 1

        self._subscriptions[sub_id] = filter
        self._handlers[sub_id].append(handler)

        return sub_id

    def remove_subscription(self, sub_id: str) -> bool:
        """
        Remove a subscription.

        Args:
            sub_id: Subscription ID

        Returns:
            True if subscription was removed
        """
        if sub_id in self._subscriptions:
            del self._subscriptions[sub_id]
            del self._handlers[sub_id]
            return True
        return False

    def get_matching_handlers(self, event: RealtimeEvent) -> list[Callable[[RealtimeEvent], None]]:
        """Get all handlers that match the given event."""
        matching_handlers = []

        for sub_id, filter in self._subscriptions.items():
            if filter.matches(event):
                matching_handlers.extend(self._handlers[sub_id])

        return matching_handlers

    def get_subscription_count(self) -> int:
        """Get total number of active subscriptions."""
        return len(self._subscriptions)

    def clear_all(self):
        """Clear all subscriptions."""
        self._subscriptions.clear()
        self._handlers.clear()


class RealtimeClient:
    """
    Real-time client for WebSocket-based event streaming.

    Provides automatic reconnection, event filtering, and batch processing.
    """

    def __init__(
        self,
        session: ClientSession,
        ws_url: str | None = None,
        max_reconnect_attempts: int = 5,
        reconnect_delay: float = 1.0,
        heartbeat_interval: float = 30.0,
        batch_size: int = 100,
        batch_timeout: float = 0.1,
    ):
        """
        Initialize real-time client.

        Args:
            session: ClientSession for authentication
            ws_url: WebSocket URL (derived from session URL if not provided)
            max_reconnect_attempts: Maximum reconnection attempts
            reconnect_delay: Delay between reconnection attempts
            heartbeat_interval: Heartbeat ping interval
            batch_size: Maximum events to batch together
            batch_timeout: Maximum time to wait for batch
        """
        self.session = session
        self.ws_url = ws_url or self._derive_ws_url()
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.heartbeat_interval = heartbeat_interval
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout

        self._websocket = None  # type: ignore[assignment]
        self._subscription_manager = SubscriptionManager()
        self._running = False
        self._reconnect_count = 0
        self._last_heartbeat = 0.0
        self._event_queue: asyncio.Queue[RealtimeEvent] = asyncio.Queue()
        self._batch_queue: deque[RealtimeEvent] = deque()
        self._weak_refs = weakref.WeakSet()

        # Statistics
        self._stats = {
            "events_received": 0,
            "events_processed": 0,
            "connection_drops": 0,
            "reconnections": 0,
        }

    def _derive_ws_url(self) -> str:
        """Derive WebSocket URL from session URL."""
        # This would extract the base URL from the session and convert to WS
        # For now, return a default
        if hasattr(self.session, "_client") and hasattr(self.session._client, "base_url"):
            http_url = self.session._client.base_url
            ws_url = http_url.replace("http://", "ws://").replace("https://", "wss://")
            return f"{ws_url}/ws"
        return "ws://localhost:8000/ws"

    async def connect(self) -> None:
        """Connect to WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets package is required for real-time functionality. Install with: pip install websockets"
            )

        if self._running:
            return

        self._running = True
        await self._connect_with_retry()

        # Start background tasks
        asyncio.create_task(self._message_receiver())
        asyncio.create_task(self._heartbeat_sender())
        asyncio.create_task(self._batch_processor())

    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        self._running = False

        if self._websocket:
            await self._websocket.close()
            self._websocket = None

    async def _connect_with_retry(self) -> None:
        """Connect with automatic retry logic."""
        for attempt in range(self.max_reconnect_attempts):
            try:
                # Get authentication token from session
                headers = await self._get_auth_headers()

                self._websocket = await websockets.connect(
                    self.ws_url, extra_headers=headers, ping_interval=self.heartbeat_interval
                )

                # Send subscription message
                await self._send_subscriptions()

                # Emit connection established event
                await self._emit_event(
                    RealtimeEvent(
                        type=EventType.CONNECTION_ESTABLISHED, data={"attempt": attempt + 1}
                    )
                )

                self._reconnect_count = 0
                logger.info(f"Connected to WebSocket (attempt {attempt + 1})")
                return

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

                if attempt < self.max_reconnect_attempts - 1:
                    await asyncio.sleep(self.reconnect_delay * (2**attempt))  # Exponential backoff
                    self._reconnect_count += 1
                    self._stats["reconnections"] += 1
                else:
                    await self._emit_event(
                        RealtimeEvent(
                            type=EventType.ERROR,
                            data={"error": str(e), "max_attempts_reached": True},
                        )
                    )
                    raise

    async def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for WebSocket connection."""
        headers = {}

        # Try to get token from session
        if hasattr(self.session, "_headers") and self.session._headers:
            headers.update(self.session._headers)
        elif hasattr(self.session, "token") and self.session.token:
            headers["Authorization"] = f"Bearer {self.session.token}"

        return headers

    async def _send_subscriptions(self) -> None:
        """Send current subscriptions to server."""
        if not self._websocket:
            return

        # Collect all filters
        all_filters = []
        for filter in self._subscription_manager._subscriptions.values():
            filter_dict = {
                "object_types": filter.object_types,
                "event_types": (
                    [t.value for t in filter.event_types] if filter.event_types else None
                ),
                "object_ids": filter.object_ids,
                "properties": filter.properties,
            }
            all_filters.append(filter_dict)

        # Send subscription message
        message = {"type": "subscribe", "filters": all_filters}

        await self._websocket.send(json.dumps(message))

    async def _message_receiver(self) -> None:
        """Background task to receive WebSocket messages."""
        while self._running:
            try:
                if not self._websocket:
                    await asyncio.sleep(0.1)
                    continue

                message = await asyncio.wait_for(self._websocket.recv(), timeout=1.0)

                await self._handle_message(message)

            except TimeoutError:
                continue
            except ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self._stats["connection_drops"] += 1
                await self._emit_event(
                    RealtimeEvent(
                        type=EventType.CONNECTION_LOST,
                        data={"reconnect_count": self._reconnect_count},
                    )
                )
                await self._handle_connection_loss()
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                await self._emit_event(RealtimeEvent(type=EventType.ERROR, data={"error": str(e)}))

    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)

            # Parse event
            event_type = EventType(data.get("type", "unknown"))
            event_data = data.get("data", {})

            event = RealtimeEvent(
                type=event_type,
                data=event_data,
                object_type=data.get("object_type"),
                object_id=data.get("object_id"),
                metadata=data.get("metadata", {}),
            )

            self._stats["events_received"] += 1

            # Add to event queue for batch processing
            await self._event_queue.put(event)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _batch_processor(self) -> None:
        """Background task to batch process events."""
        while self._running:
            try:
                # Wait for first event
                event = await asyncio.wait_for(self._event_queue.get(), timeout=self.batch_timeout)

                # Start batch
                batch = [event]
                deadline = time.time() + self.batch_timeout

                # Collect more events until batch is full or timeout
                while len(batch) < self.batch_size and time.time() < deadline:
                    try:
                        event = await asyncio.wait_for(
                            self._event_queue.get(), timeout=deadline - time.time()
                        )
                        batch.append(event)
                    except TimeoutError:
                        break

                # Process batch
                await self._process_event_batch(batch)

            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")

    async def _process_event_batch(self, events: list[RealtimeEvent]) -> None:
        """Process a batch of events."""
        for event in events:
            try:
                # Get matching handlers
                handlers = self._subscription_manager.get_matching_handlers(event)

                # Call handlers
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")

                self._stats["events_processed"] += len(events)

            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _heartbeat_sender(self) -> None:
        """Send periodic heartbeat messages."""
        while self._running:
            try:
                if self._websocket and not self._websocket.closed:
                    await self._websocket.ping()
                    self._last_heartbeat = time.time()

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")

    async def _handle_connection_loss(self) -> None:
        """Handle WebSocket connection loss."""
        if self._running:
            try:
                await self._connect_with_retry()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
                self._running = False

    async def _emit_event(self, event: RealtimeEvent) -> None:
        """Emit an internal event."""
        await self._event_queue.put(event)

    def subscribe(
        self,
        object_types: list[str] | None = None,
        event_types: list[EventType] | None = None,
        object_ids: list[str] | None = None,
        properties: dict[str, Any] | None = None,
        handler: Callable[[RealtimeEvent], None] | None = None,
    ) -> str:
        """
        Subscribe to real-time events.

        Args:
            object_types: Filter by object types
            event_types: Filter by event types
            object_ids: Filter by specific object IDs
            properties: Filter by object properties
            handler: Event handler function

        Returns:
            Subscription ID
        """
        if handler is None:

            def no_op_handler(event):
                None  # Default no-op handler

            handler = no_op_handler

        filter = SubscriptionFilter(
            object_types=object_types,
            event_types=event_types,
            object_ids=object_ids,
            properties=properties,
        )

        sub_id = self._subscription_manager.add_subscription(filter, handler)

        # Send updated subscriptions if connected
        if self._websocket and not self._websocket.closed:
            asyncio.create_task(self._send_subscriptions())

        return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            sub_id: Subscription ID

        Returns:
            True if unsubscribed successfully
        """
        success = self._subscription_manager.remove_subscription(sub_id)

        # Send updated subscriptions if connected
        if success and self._websocket and not self._websocket.closed:
            asyncio.create_task(self._send_subscriptions())

        return success

    def unsubscribe_all(self) -> None:
        """Unsubscribe from all events."""
        self._subscription_manager.clear_all()

        # Send updated subscriptions if connected
        if self._websocket and not self._websocket.closed:
            asyncio.create_task(self._send_subscriptions())

    def get_stats(self) -> dict[str, Any]:
        """Get real-time client statistics."""
        return {
            **self._stats,
            "subscriptions": self._subscription_manager.get_subscription_count(),
            "connected": self._websocket is not None and not self._websocket.closed,
            "reconnect_count": self._reconnect_count,
            "last_heartbeat": self._last_heartbeat,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


class RealtimeSubscription:
    """
    High-level subscription wrapper with convenience methods.
    """

    def __init__(self, client: RealtimeClient, filter: SubscriptionFilter):
        self.client = client
        self.filter = filter
        self._subscription_id: str | None = None
        self._handlers: list[Callable[[RealtimeEvent], None]] = []
        self._event_buffer: deque[RealtimeEvent] = deque(maxlen=1000)

    async def start(self) -> None:
        """Start the subscription."""
        if self._subscription_id is None:
            # Create combined handler that buffers events and calls user handlers
            def combined_handler(event: RealtimeEvent):
                self._event_buffer.append(event)
                for handler in self._handlers:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)

            self._subscription_id = self.client.subscribe(
                object_types=self.filter.object_types,
                event_types=self.filter.event_types,
                object_ids=self.filter.object_ids,
                properties=self.filter.properties,
                handler=combined_handler,
            )

    async def stop(self) -> None:
        """Stop the subscription."""
        if self._subscription_id:
            self.client.unsubscribe(self._subscription_id)
            self._subscription_id = None

    def add_handler(self, handler: Callable[[RealtimeEvent], None]) -> None:
        """Add an event handler."""
        self._handlers.append(handler)

    def remove_handler(self, handler: Callable[[RealtimeEvent], None]) -> bool:
        """Remove an event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)
            return True
        return False

    def get_recent_events(self, count: int = 10) -> list[RealtimeEvent]:
        """Get recent events from buffer."""
        return list(self._event_buffer)[-count:]

    def clear_buffer(self) -> None:
        """Clear the event buffer."""
        self._event_buffer.clear()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Convenience functions


async def create_realtime_client(
    session: ClientSession, ws_url: str | None = None, **kwargs
) -> RealtimeClient:
    """
    Create a real-time client.

    Args:
        session: ClientSession for authentication
        ws_url: WebSocket URL
        **kwargs: Additional arguments for RealtimeClient

    Returns:
        RealtimeClient instance
    """
    return RealtimeClient(session, ws_url, **kwargs)


def subscribe_to_object_type(
    client: RealtimeClient,
    object_type: str,
    handler: Callable[[RealtimeEvent], None],
    event_types: list[EventType] | None = None,
) -> str:
    """
    Subscribe to all events for a specific object type.

    Args:
        client: RealtimeClient instance
        object_type: Object type to subscribe to
        handler: Event handler function
        event_types: Specific event types to subscribe to

    Returns:
        Subscription ID
    """
    return client.subscribe(object_types=[object_type], event_types=event_types, handler=handler)


def subscribe_to_object(
    client: RealtimeClient,
    object_type: str,
    object_id: str,
    handler: Callable[[RealtimeEvent], None],
) -> str:
    """
    Subscribe to events for a specific object.

    Args:
        client: RealtimeClient instance
        object_type: Object type
        object_id: Object ID
        handler: Event handler function

    Returns:
        Subscription ID
    """
    return client.subscribe(object_types=[object_type], object_ids=[object_id], handler=handler)
