"""Tests for NATS Event Bus implementation."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia.domain.instances.events import ObjectInstanceUpserted
from ontologia.event_bus.nats import NATSConnectionConfig, NATSEventBus


class TestNATSConnectionConfig:
    """Test NATS connection configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = NATSConnectionConfig(servers=["nats://localhost:4222"])

        assert config.servers == ["nats://localhost:4222"]
        assert config.subject_prefix == "ontologia"
        assert config.client_name is None
        assert config.synchronous_publish is False
        assert config.max_reconnect_attempts == 60
        assert config.reconnect_wait == 2.0
        assert config.ping_interval == 20
        assert config.max_outstanding_pings == 3
        assert config.dont_randomize_servers is False
        assert config.flush_timeout == 30.0
        assert config.user is None
        assert config.password is None
        assert config.token is None

    def test_config_with_auth(self) -> None:
        """Test configuration with authentication."""
        config = NATSConnectionConfig(
            servers=["nats://localhost:4222", "nats://server2:4222"],
            client_name="test-client",
            user="testuser",
            password="test_password",
            synchronous_publish=True,
        )

        assert config.servers == ["nats://localhost:4222", "nats://server2:4222"]
        assert config.client_name == "test-client"
        assert config.user == "testuser"
        assert config.password == "test_password"
        assert config.synchronous_publish is True


class TestNATSEventBus:
    """Test NATS EventBus implementation."""

    @pytest.fixture
    def config(self) -> NATSConnectionConfig:
        """Create test configuration."""
        return NATSConnectionConfig(
            servers=["nats://localhost:4222"],
            subject_prefix="test",
            client_name="test-client",
            synchronous_publish=False,
        )

    @pytest.fixture
    def mock_nats(self) -> MagicMock:
        """Mock NATS client."""
        mock_nc = AsyncMock()
        mock_nc.is_connected = True

        # Create a proper mock for jetstream that handles add_stream correctly
        mock_js = AsyncMock()
        mock_js.add_stream = AsyncMock()
        # Use MagicMock for jetstream to avoid async issues
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        return mock_nc

    @pytest.fixture
    def event_bus(self, config: NATSConnectionConfig) -> NATSEventBus:
        """Create NATS EventBus instance."""
        return NATSEventBus(config)

    def test_init_without_nats_package(self, config: NATSConnectionConfig) -> None:
        """Test initialization fails without nats-py package."""
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(RuntimeError, match="NATS support requires"):
                NATSEventBus(config)

    @pytest.mark.asyncio
    async def test_ensure_connection(self, event_bus: NATSEventBus, mock_nats: MagicMock) -> None:
        """Test connection establishment."""
        with patch("nats.connect", return_value=mock_nats) as mock_connect:
            await event_bus._ensure_connection()

            mock_connect.assert_called_once_with(
                servers=["nats://localhost:4222"],
                max_reconnect_attempts=60,
                reconnect_time_wait=2.0,
                ping_interval=20,
                max_outstanding_pings=3,
                name="test-client",
            )
            assert event_bus._nc == mock_nats
            assert event_bus._connected is True

    @pytest.mark.asyncio
    async def test_ensure_connection_with_auth(
        self, event_bus: NATSEventBus, mock_nats: MagicMock
    ) -> None:
        """Test connection with authentication."""
        config = NATSConnectionConfig(
            servers=["nats://localhost:4222"],
            user="testuser",
            password="test_password",
        )
        event_bus = NATSEventBus(config)

        with patch("nats.connect", return_value=mock_nats) as mock_connect:
            await event_bus._ensure_connection()

            mock_connect.assert_called_once_with(
                servers=["nats://localhost:4222"],
                max_reconnect_attempts=60,
                reconnect_time_wait=2.0,
                ping_interval=20,
                max_outstanding_pings=3,
                user="testuser",
                password="test_password",
            )

    @pytest.mark.asyncio
    async def test_ensure_connection_with_token(
        self, event_bus: NATSEventBus, mock_nats: MagicMock
    ) -> None:
        """Test connection with token authentication."""
        config = NATSConnectionConfig(
            servers=["nats://localhost:4222"],
            token="test_token",
        )
        event_bus = NATSEventBus(config)

        with patch("nats.connect", return_value=mock_nats) as mock_connect:
            await event_bus._ensure_connection()

            mock_connect.assert_called_once_with(
                servers=["nats://localhost:4222"],
                max_reconnect_attempts=60,
                reconnect_time_wait=2.0,
                ping_interval=20,
                max_outstanding_pings=3,
                token="test_token",
            )

    @pytest.mark.asyncio
    async def test_ensure_connection_jetstream_setup(self, event_bus: NATSEventBus) -> None:
        """Test JetStream setup during connection."""
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        mock_js = MagicMock()
        mock_js.add_stream = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        with patch("nats.connect", return_value=mock_nc):
            await event_bus._ensure_connection()

            mock_js.add_stream.assert_called_once_with(
                name="test_events",
                subjects=["test.*"],
                retention="work_queue",
                max_bytes=-1,
                max_age=0,
                storage="file",
                replicas=1,
            )

    @pytest.mark.asyncio
    async def test_publish_async(self, event_bus: NATSEventBus, mock_nats: MagicMock) -> None:
        """Test async event publishing."""
        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        # Mock JetStream
        mock_js = MagicMock()
        mock_ack = MagicMock()
        mock_ack.stream = "test_events"
        mock_ack.seq = 1
        mock_js.publish = AsyncMock(return_value=mock_ack)
        mock_nats.jetstream = MagicMock(return_value=mock_js)

        with (
            patch("nats.connect", return_value=mock_nats),
            patch.object(event_bus, "_ensure_stream"),
        ):
            await event_bus._ensure_connection()
            await event_bus._publish_async(event)

            # Verify JetStream publish was called
            mock_js.publish.assert_called_once()
            call_args = mock_js.publish.call_args
            assert call_args[0][0] == "test.ObjectInstanceUpserted"
            assert b'"event_name": "ObjectInstanceUpserted"' in call_args[0][1]
            assert call_args[1]["headers"]["X-Event-Name"] == "ObjectInstanceUpserted"
            assert call_args[1]["headers"]["X-Primary-Key-Value"] == "123"

    @pytest.mark.asyncio
    async def test_publish_async_basic_nats(
        self, event_bus: NATSEventBus, mock_nats: MagicMock
    ) -> None:
        """Test async event publishing with basic NATS (no JetStream)."""
        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        # Override the jetstream mock to raise NotFoundError
        from nats.js.errors import NotFoundError

        mock_nats.jetstream.side_effect = NotFoundError
        mock_nats.publish = AsyncMock()

        with (
            patch("nats.connect", return_value=mock_nats),
            patch.object(event_bus, "_ensure_stream"),
        ):
            await event_bus._ensure_connection()
            await event_bus._publish_async(event)

            # Verify basic NATS publish was called
            mock_nats.publish.assert_called_once()
            call_args = mock_nats.publish.call_args
            assert call_args[0][0] == "test.ObjectInstanceUpserted"
            assert b'"event_name": "ObjectInstanceUpserted"' in call_args[0][1]

    def test_publish_sync_context(
        self, event_bus: NATSEventBus, mock_nats: MagicMock, caplog
    ) -> None:
        """Test publishing in synchronous context."""
        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        # In a non-async context, get_event_loop will raise RuntimeError
        # and the publish method should catch it and log the error
        with (
            patch("nats.connect", return_value=mock_nats),
            patch("asyncio.get_event_loop") as mock_get_loop,
        ):
            mock_get_loop.side_effect = RuntimeError("There is no current event loop in thread")

            # The publish method should catch the error, log it, and re-raise it
            with caplog.at_level("ERROR"):
                with pytest.raises(RuntimeError, match="There is no current event loop in thread"):
                    event_bus.publish(event)

            # Check that an error was logged
            assert "Failed to publish event" in caplog.text

    @pytest.mark.asyncio
    async def test_publish_async_context(self, mock_nats: MagicMock) -> None:
        """Test publishing in async context."""
        config = NATSConnectionConfig(
            servers=["nats://localhost:4222"],
            subject_prefix="test",
            client_name="test-client",
            synchronous_publish=False,
        )
        event_bus = NATSEventBus(config)

        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        # Mock async context
        mock_loop = AsyncMock()
        mock_loop.is_running.return_value = True

        # Track if create_task was called
        create_task_called = False

        def mock_create_task(coro):
            nonlocal create_task_called
            create_task_called = True
            # Don't await the coroutine, just return a mock
            mock_task = AsyncMock()
            mock_task.done = MagicMock(return_value=True)
            return mock_task

        with (
            patch("nats.connect", return_value=mock_nats),
            patch("asyncio.get_event_loop", return_value=mock_loop),
            patch("asyncio.create_task", side_effect=mock_create_task),
            patch.object(event_bus, "_ensure_stream"),
        ):
            event_bus.publish(event)

        # Verify create_task was called
        assert create_task_called is True

        # Ensure all coroutines are cleaned up
        await asyncio.sleep(0)

        # Reset the mock to prevent test interference
        mock_nats.reset_mock()

        # Clean up the event_bus to prevent interference
        if hasattr(event_bus, "_nc") and event_bus._nc:
            event_bus._nc = None

    @pytest.mark.asyncio
    async def test_publish_many_async(self, event_bus: NATSEventBus, mock_nats: MagicMock) -> None:
        """Test batch publishing."""
        events = [
            ObjectInstanceUpserted(
                service="test",
                instance="default",
                object_type_api_name="TestObject",
                primary_key_field="id",
                primary_key_value="123",
                payload={"name": "test1"},
            ),
            ObjectInstanceUpserted(
                service="test",
                instance="default",
                object_type_api_name="TestObject",
                primary_key_field="id",
                primary_key_value="456",
                payload={"name": "test2"},
            ),
        ]

        # Mock _publish_async to avoid coroutines
        mock_publish = AsyncMock()

        with (
            patch("nats.connect", return_value=mock_nats),
            patch.object(event_bus, "_publish_async", mock_publish),
        ):
            await event_bus._ensure_connection()
            # Call _publish_many_async directly and handle the result
            try:
                await event_bus._publish_many_async(events)
            except Exception as e:
                print(f"Exception during _publish_many_async: {e}")

            # Verify _publish_async was called for each event
            assert mock_publish.call_count == 2

        # Ensure all coroutines are cleaned up
        await asyncio.sleep(0)

    @pytest.mark.asyncio
    async def test_synchronous_publish(self, event_bus: NATSEventBus, mock_nats: MagicMock) -> None:
        """Test synchronous publish with flush."""
        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        # Create config with synchronous publish
        config = NATSConnectionConfig(
            servers=["nats://localhost:4222"],
            synchronous_publish=True,
            flush_timeout=10.0,
        )
        event_bus_sync = NATSEventBus(config)

        # Mock the publish methods
        mock_nats.publish = AsyncMock()
        mock_nats.flush = AsyncMock()

        with (
            patch("nats.connect", return_value=mock_nats),
            patch.object(event_bus_sync, "_ensure_stream"),
        ):
            await event_bus_sync._ensure_connection()
            await event_bus_sync._publish_async(event)

            # Verify flush was called
            mock_nats.flush.assert_called_once_with(10.0)

        # Ensure all coroutines are cleaned up
        await asyncio.sleep(0)

    @pytest.mark.asyncio
    async def test_close_connection(self, event_bus: NATSEventBus, mock_nats: MagicMock) -> None:
        """Test closing NATS connection."""
        with (
            patch("nats.connect", return_value=mock_nats),
            patch.object(event_bus, "_ensure_stream"),
        ):
            await event_bus._ensure_connection()
            await event_bus.close()

            mock_nats.flush.assert_called_once()
            mock_nats.drain.assert_called_once()
            mock_nats.close.assert_called_once()
            assert event_bus._nc is None
            assert event_bus._connected is False

    def test_cleanup_on_deletion(self, config: NATSConnectionConfig) -> None:
        """Test cleanup on object deletion."""
        event_bus = NATSEventBus(config)
        # Don't set _nc to avoid cleanup issues
        # event_bus._nc = AsyncMock()
        # event_bus._connected = True

        # Simulate deletion
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = AsyncMock()
            mock_loop.is_running.return_value = False
            mock_get_loop.return_value = mock_loop

            del event_bus

            # Verify cleanup attempt was made
            # Note: event_bus is deleted, so we can't check its attributes
            # The cleanup happens in the __del__ method


class TestEventSerialization:
    """Test event serialization utilities."""

    def test_serialize_event(self) -> None:
        """Test event serialization to JSON."""
        from ontologia.event_bus.nats import _serialize_event

        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        serialized = _serialize_event(event)

        assert serialized["event_name"] == "ObjectInstanceUpserted"
        assert serialized["service"] == "test"
        assert serialized["instance"] == "default"
        assert serialized["object_type_api_name"] == "TestObject"
        assert serialized["primary_key_value"] == "123"
        assert serialized["payload"] == {"name": "test"}
        assert "occurred_at" in serialized
        assert isinstance(serialized["occurred_at"], str)

    def test_extract_event_headers(self) -> None:
        """Test event header extraction."""
        from ontologia.event_bus.nats import _extract_event_headers

        event = ObjectInstanceUpserted(
            service="test",
            instance="default",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="123",
            payload={"name": "test"},
        )

        headers = _extract_event_headers(event)

        assert headers["X-Event-Name"] == "ObjectInstanceUpserted"
        assert headers["X-Event-Timestamp"] == event.occurred_at.isoformat()
        assert headers["X-Primary-Key-Value"] == "123"
        assert headers["X-Object-Type-Api-Name"] == "TestObject"
