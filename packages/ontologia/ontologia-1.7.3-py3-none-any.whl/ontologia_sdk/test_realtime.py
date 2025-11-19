"""
Tests for the real-time subscription implementation.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia_sdk.realtime import (
    EventType,
    RealtimeClient,
    RealtimeEvent,
    RealtimeSubscription,
    SubscriptionFilter,
    SubscriptionManager,
    create_realtime_client,
    subscribe_to_object,
    subscribe_to_object_type,
)


class TestRealtimeEvent:
    """Test RealtimeEvent dataclass."""

    def test_realtime_event_creation(self):
        """Test creating a real-time event."""
        event = RealtimeEvent(
            type=EventType.OBJECT_CREATED,
            data={"name": "John", "age": 30},
            object_type="person",
            object_id="person-1",
            metadata={"source": "api"},
        )

        assert event.type == EventType.OBJECT_CREATED
        assert event.data == {"name": "John", "age": 30}
        assert event.object_type == "person"
        assert event.object_id == "person-1"
        assert event.metadata == {"source": "api"}
        assert event.timestamp > 0

    def test_realtime_event_defaults(self):
        """Test real-time event with default values."""
        event = RealtimeEvent(type=EventType.OBJECT_UPDATED, data={"status": "active"})

        assert event.type == EventType.OBJECT_UPDATED
        assert event.object_type is None
        assert event.object_id is None
        assert event.metadata == {}
        assert event.timestamp > 0


class TestSubscriptionFilter:
    """Test SubscriptionFilter functionality."""

    def test_filter_creation(self):
        """Test creating subscription filter."""
        filter = SubscriptionFilter(
            object_types=["person", "company"],
            event_types=[EventType.OBJECT_CREATED, EventType.OBJECT_UPDATED],
            object_ids=["person-1", "company-1"],
            properties={"status": "active"},
        )

        assert filter.object_types == ["person", "company"]
        assert filter.event_types == [EventType.OBJECT_CREATED, EventType.OBJECT_UPDATED]
        assert filter.object_ids == ["person-1", "company-1"]
        assert filter.properties == {"status": "active"}

    def test_filter_matches_object_type(self):
        """Test filtering by object type."""
        filter = SubscriptionFilter(object_types=["person"])

        event1 = RealtimeEvent(type=EventType.OBJECT_CREATED, data={}, object_type="person")
        event2 = RealtimeEvent(type=EventType.OBJECT_CREATED, data={}, object_type="company")

        assert filter.matches(event1) is True
        assert filter.matches(event2) is False

    def test_filter_matches_event_type(self):
        """Test filtering by event type."""
        filter = SubscriptionFilter(event_types=[EventType.OBJECT_CREATED])

        event1 = RealtimeEvent(type=EventType.OBJECT_CREATED, data={})
        event2 = RealtimeEvent(type=EventType.OBJECT_UPDATED, data={})

        assert filter.matches(event1) is True
        assert filter.matches(event2) is False

    def test_filter_matches_object_id(self):
        """Test filtering by object ID."""
        filter = SubscriptionFilter(object_ids=["person-1"])

        event1 = RealtimeEvent(type=EventType.OBJECT_UPDATED, data={}, object_id="person-1")
        event2 = RealtimeEvent(type=EventType.OBJECT_UPDATED, data={}, object_id="person-2")

        assert filter.matches(event1) is True
        assert filter.matches(event2) is False

    def test_filter_matches_properties(self):
        """Test filtering by properties."""
        filter = SubscriptionFilter(properties={"status": "active"})

        event1 = RealtimeEvent(
            type=EventType.OBJECT_UPDATED, data={"status": "active", "name": "John"}
        )
        event2 = RealtimeEvent(
            type=EventType.OBJECT_UPDATED, data={"status": "inactive", "name": "Jane"}
        )

        assert filter.matches(event1) is True
        assert filter.matches(event2) is False

    def test_filter_matches_multiple_criteria(self):
        """Test filtering with multiple criteria."""
        filter = SubscriptionFilter(
            object_types=["person"],
            event_types=[EventType.OBJECT_UPDATED],
            properties={"status": "active"},
        )

        event1 = RealtimeEvent(
            type=EventType.OBJECT_UPDATED, data={"status": "active"}, object_type="person"
        )
        event2 = RealtimeEvent(
            type=EventType.OBJECT_CREATED, data={"status": "active"}, object_type="person"
        )
        event3 = RealtimeEvent(
            type=EventType.OBJECT_UPDATED, data={"status": "inactive"}, object_type="person"
        )

        assert filter.matches(event1) is True
        assert filter.matches(event2) is False  # Wrong event type
        assert filter.matches(event3) is False  # Wrong property value

    def test_filter_no_criteria_matches_all(self):
        """Test that filter with no criteria matches all events."""
        filter = SubscriptionFilter()

        event = RealtimeEvent(
            type=EventType.OBJECT_DELETED, data={}, object_type="any_type", object_id="any_id"
        )

        assert filter.matches(event) is True


class TestSubscriptionManager:
    """Test SubscriptionManager functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.manager = SubscriptionManager()

    def test_add_subscription(self):
        """Test adding a subscription."""
        filter = SubscriptionFilter(object_types=["person"])
        handler = MagicMock()

        sub_id = self.manager.add_subscription(filter, handler)

        assert sub_id.startswith("sub_")
        assert self.manager.get_subscription_count() == 1

    def test_remove_subscription(self):
        """Test removing a subscription."""
        filter = SubscriptionFilter(object_types=["person"])
        handler = MagicMock()

        sub_id = self.manager.add_subscription(filter, handler)
        success = self.manager.remove_subscription(sub_id)

        assert success is True
        assert self.manager.get_subscription_count() == 0

    def test_remove_nonexistent_subscription(self):
        """Test removing non-existent subscription."""
        success = self.manager.remove_subscription("nonexistent")
        assert success is False

    def test_get_matching_handlers(self):
        """Test getting handlers for matching events."""
        filter1 = SubscriptionFilter(object_types=["person"])
        filter2 = SubscriptionFilter(event_types=[EventType.OBJECT_CREATED])
        handler1 = MagicMock()
        handler2 = MagicMock()

        self.manager.add_subscription(filter1, handler1)
        self.manager.add_subscription(filter2, handler2)

        event = RealtimeEvent(type=EventType.OBJECT_CREATED, data={}, object_type="person")

        matching_handlers = self.manager.get_matching_handlers(event)

        assert len(matching_handlers) == 2
        assert handler1 in matching_handlers
        assert handler2 in matching_handlers

    def test_get_matching_handlers_partial_match(self):
        """Test getting handlers for partially matching events."""
        filter1 = SubscriptionFilter(object_types=["person"])
        filter2 = SubscriptionFilter(object_types=["company"])
        handler1 = MagicMock()
        handler2 = MagicMock()

        self.manager.add_subscription(filter1, handler1)
        self.manager.add_subscription(filter2, handler2)

        event = RealtimeEvent(type=EventType.OBJECT_CREATED, data={}, object_type="person")

        matching_handlers = self.manager.get_matching_handlers(event)

        assert len(matching_handlers) == 1
        assert handler1 in matching_handlers
        assert handler2 not in matching_handlers

    def test_clear_all_subscriptions(self):
        """Test clearing all subscriptions."""
        filter1 = SubscriptionFilter(object_types=["person"])
        filter2 = SubscriptionFilter(object_types=["company"])
        handler1 = MagicMock()
        handler2 = MagicMock()

        self.manager.add_subscription(filter1, handler1)
        self.manager.add_subscription(filter2, handler2)

        assert self.manager.get_subscription_count() == 2

        self.manager.clear_all()

        assert self.manager.get_subscription_count() == 0


class TestRealtimeClient:
    """Test RealtimeClient functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.mock_session = AsyncMock()
        self.client = RealtimeClient(
            self.mock_session,
            ws_url="ws://test.example.com/ws",
            max_reconnect_attempts=3,
            reconnect_delay=0.1,
        )

    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.session is self.mock_session
        assert self.client.ws_url == "ws://test.example.com/ws"
        assert self.client.max_reconnect_attempts == 3
        assert self.client.reconnect_delay == 0.1
        assert self.client._running is False
        assert self.client._websocket is None

    def test_derive_ws_url_from_session(self):
        """Test deriving WebSocket URL from session."""
        mock_client = MagicMock()
        mock_client.base_url = "https://api.example.com"
        self.mock_session._client = mock_client

        client = RealtimeClient(self.mock_session)

        assert client.ws_url == "wss://api.example.com/ws"

    @pytest.mark.asyncio
    async def test_connect_already_running(self):
        """Test connecting when already running."""
        with patch("ontologia_sdk.realtime.WEBSOCKETS_AVAILABLE", True):
            self.client._running = True

            await self.client.connect()

            # Should not attempt to connect
            assert self.client._websocket is None

    @pytest.mark.asyncio
    async def test_get_auth_headers_from_session_headers(self):
        """Test getting auth headers from session."""
        self.mock_session._headers = {"Authorization": "Bearer test-token"}

        headers = await self.client._get_auth_headers()

        assert headers == {"Authorization": "Bearer test-token"}

    @pytest.mark.asyncio
    async def test_get_auth_headers_from_session_token(self):
        """Test getting auth headers from session token."""
        self.mock_session.token = "test-token"
        self.mock_session._headers = None

        headers = await self.client._get_auth_headers()

        assert headers == {"Authorization": "Bearer test-token"}

    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test subscribing to events."""
        handler = MagicMock()

        sub_id = self.client.subscribe(
            object_types=["person"], event_types=[EventType.OBJECT_CREATED], handler=handler
        )

        assert sub_id.startswith("sub_")
        assert self.client._subscription_manager.get_subscription_count() == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribing from events."""
        handler = MagicMock()

        sub_id = self.client.subscribe(object_types=["person"], handler=handler)

        success = self.client.unsubscribe(sub_id)

        assert success is True
        assert self.client._subscription_manager.get_subscription_count() == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent(self):
        """Test unsubscribing non-existent subscription."""
        success = self.client.unsubscribe("nonexistent")
        assert success is False

    @pytest.mark.asyncio
    async def test_unsubscribe_all(self):
        """Test unsubscribing from all events."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        self.client.subscribe(object_types=["person"], handler=handler1)
        self.client.subscribe(object_types=["company"], handler=handler2)

        assert self.client._subscription_manager.get_subscription_count() == 2

        self.client.unsubscribe_all()

        assert self.client._subscription_manager.get_subscription_count() == 0

    def test_get_stats(self):
        """Test getting client statistics."""
        stats = self.client.get_stats()

        assert "events_received" in stats
        assert "events_processed" in stats
        assert "connection_drops" in stats
        assert "reconnections" in stats
        assert "subscriptions" in stats
        assert "connected" in stats
        assert "reconnect_count" in stats
        assert "last_heartbeat" in stats

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        with (
            patch.object(self.client, "connect") as mock_connect,
            patch.object(self.client, "disconnect") as mock_disconnect,
        ):
            async with self.client as client:
                assert client is self.client
                mock_connect.assert_called_once()

            mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_message_valid(self):
        """Test handling valid WebSocket message."""
        message_data = {
            "type": "object_created",
            "data": {"name": "John"},
            "object_type": "person",
            "object_id": "person-1",
            "metadata": {"source": "api"},
        }
        message = json.dumps(message_data)

        await self.client._handle_message(message)

        # Check event was queued
        assert not self.client._event_queue.empty()

        event = await self.client._event_queue.get()
        assert event.type == EventType.OBJECT_CREATED
        assert event.data == {"name": "John"}
        assert event.object_type == "person"
        assert event.object_id == "person-1"

    @pytest.mark.asyncio
    async def test_handle_message_invalid(self):
        """Test handling invalid WebSocket message."""
        invalid_message = "invalid json"

        # Should not raise exception
        await self.client._handle_message(invalid_message)

        # Event queue should remain empty
        assert self.client._event_queue.empty()

    @pytest.mark.asyncio
    async def test_process_event_batch(self):
        """Test processing event batch."""
        events = [
            RealtimeEvent(
                type=EventType.OBJECT_CREATED, data={"name": "John"}, object_type="person"
            ),
            RealtimeEvent(
                type=EventType.OBJECT_UPDATED, data={"status": "active"}, object_type="person"
            ),
        ]

        # Add a subscription
        handler = MagicMock()
        self.client.subscribe(object_types=["person"], handler=handler)

        await self.client._process_event_batch(events)

        # Handler should be called for each event
        assert handler.call_count == 2


class TestRealtimeSubscription:
    """Test RealtimeSubscription functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.mock_client = MagicMock()
        self.filter = SubscriptionFilter(object_types=["person"])
        self.subscription = RealtimeSubscription(self.mock_client, self.filter)

    @pytest.mark.asyncio
    async def test_start_subscription(self):
        """Test starting subscription."""
        self.mock_client.subscribe.return_value = "sub_1"

        await self.subscription.start()

        assert self.subscription._subscription_id == "sub_1"
        self.mock_client.subscribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_subscription(self):
        """Test stopping subscription."""
        self.subscription._subscription_id = "sub_1"

        await self.subscription.stop()

        assert self.subscription._subscription_id is None
        self.mock_client.unsubscribe.assert_called_once_with("sub_1")

    @pytest.mark.asyncio
    async def test_add_handler(self):
        """Test adding event handler."""
        handler = MagicMock()

        self.subscription.add_handler(handler)

        assert handler in self.subscription._handlers

    def test_remove_handler(self):
        """Test removing event handler."""
        handler = MagicMock()
        self.subscription._handlers.append(handler)

        success = self.subscription.remove_handler(handler)

        assert success is True
        assert handler not in self.subscription._handlers

    def test_remove_nonexistent_handler(self):
        """Test removing non-existent handler."""
        handler = MagicMock()

        success = self.subscription.remove_handler(handler)

        assert success is False

    def test_get_recent_events(self):
        """Test getting recent events from buffer."""
        events = [
            RealtimeEvent(type=EventType.OBJECT_CREATED, data={}),
            RealtimeEvent(type=EventType.OBJECT_UPDATED, data={}),
            RealtimeEvent(type=EventType.OBJECT_DELETED, data={}),
        ]

        # Add events to buffer
        for event in events:
            self.subscription._event_buffer.append(event)

        recent = self.subscription.get_recent_events(2)

        assert len(recent) == 2
        assert recent[0] == events[1]  # Second to last
        assert recent[1] == events[2]  # Last

    def test_clear_buffer(self):
        """Test clearing event buffer."""
        self.subscription._event_buffer.append(
            RealtimeEvent(type=EventType.OBJECT_CREATED, data={})
        )

        assert len(self.subscription._event_buffer) == 1

        self.subscription.clear_buffer()

        assert len(self.subscription._event_buffer) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        with (
            patch.object(self.subscription, "start") as mock_start,
            patch.object(self.subscription, "stop") as mock_stop,
        ):
            async with self.subscription as sub:
                assert sub is self.subscription
                mock_start.assert_called_once()

            mock_stop.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_create_realtime_client(self):
        """Test create_realtime_client convenience function."""
        mock_session = AsyncMock()

        client = await create_realtime_client(
            mock_session, ws_url="ws://custom.example.com/ws", max_reconnect_attempts=5
        )

        assert isinstance(client, RealtimeClient)
        assert client.session is mock_session
        assert client.ws_url == "ws://custom.example.com/ws"
        assert client.max_reconnect_attempts == 5

    def test_subscribe_to_object_type(self):
        """Test subscribe_to_object_type convenience function."""
        mock_client = MagicMock()
        mock_client.subscribe.return_value = "sub_1"
        handler = MagicMock()

        sub_id = subscribe_to_object_type(
            mock_client, "person", handler, [EventType.OBJECT_CREATED, EventType.OBJECT_UPDATED]
        )

        assert sub_id == "sub_1"
        mock_client.subscribe.assert_called_once_with(
            object_types=["person"],
            event_types=[EventType.OBJECT_CREATED, EventType.OBJECT_UPDATED],
            handler=handler,
        )

    def test_subscribe_to_object(self):
        """Test subscribe_to_object convenience function."""
        mock_client = MagicMock()
        mock_client.subscribe.return_value = "sub_1"
        handler = MagicMock()

        sub_id = subscribe_to_object(mock_client, "person", "person-1", handler)

        assert sub_id == "sub_1"
        mock_client.subscribe.assert_called_once_with(
            object_types=["person"], object_ids=["person-1"], handler=handler
        )


class TestEventType:
    """Test EventType enum."""

    def test_event_type_values(self):
        """Test event type enum values."""
        assert EventType.OBJECT_CREATED.value == "object_created"
        assert EventType.OBJECT_UPDATED.value == "object_updated"
        assert EventType.OBJECT_DELETED.value == "object_deleted"
        assert EventType.TYPE_CREATED.value == "type_created"
        assert EventType.TYPE_UPDATED.value == "type_updated"
        assert EventType.TYPE_DELETED.value == "type_deleted"
        assert EventType.LINK_CREATED.value == "link_created"
        assert EventType.LINK_UPDATED.value == "link_updated"
        assert EventType.LINK_DELETED.value == "link_deleted"
        assert EventType.CONNECTION_ESTABLISHED.value == "connection_established"
        assert EventType.CONNECTION_LOST.value == "connection_lost"
        assert EventType.ERROR.value == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
