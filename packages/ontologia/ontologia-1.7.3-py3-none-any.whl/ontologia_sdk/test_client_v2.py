"""
Tests for the unified OntologyClient implementation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia_sdk.client_v2 import OntologyClient, create_local_client, create_remote_client


class TestOntologyClient:
    """Test OntologyClient unified functionality."""

    @pytest.mark.asyncio
    async def test_remote_client_initialization(self):
        """Test client initialization in remote mode."""
        with patch("ontologia_sdk.client_v2.create_session") as mock_create_session:
            # Mock session with RemoteSession-like attributes
            mock_session = MagicMock()
            mock_session._client = MagicMock()
            mock_session._headers = {}
            mock_create_session.return_value = mock_session

            client = OntologyClient(
                host="http://localhost:8000", token="test-token", ontology="test-ontology"
            )

            assert client.mode == "remote"
            assert client.is_remote
            assert not client.is_local
            assert client.ontology == "test-ontology"
            mock_create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_local_client_initialization(self):
        """Test client initialization in local mode."""
        with patch("ontologia_sdk.client_v2.create_session") as mock_create_session:
            from ontologia_sdk.session import LocalSession

            mock_session = MagicMock(spec=LocalSession)
            mock_create_session.return_value = mock_session

            client = OntologyClient(connection_string="sqlite:///./test.db")

            assert client.mode == "local"
            assert not client.is_remote
            assert client.is_local
            mock_create_session.assert_called_once()

    def test_invalid_initialization_both_params(self):
        """Test error when both host and connection_string provided."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            OntologyClient(host="http://localhost:8000", connection_string="sqlite:///./test.db")

    def test_invalid_initialization_no_params(self):
        """Test error when neither host nor connection_string provided."""
        with pytest.raises(ValueError, match="Must specify either"):
            OntologyClient()

    @pytest.mark.asyncio
    async def test_get_object_delegates_to_session(self):
        """Test that get_object delegates to session correctly."""
        mock_session = AsyncMock()
        mock_session.get_object.return_value = {"pk": "test-1", "name": "Test"}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.get_object("test_type", "test-1")

            assert result == {"pk": "test-1", "name": "Test"}
            mock_session.get_object.assert_called_once_with("test_type", "test-1")

    @pytest.mark.asyncio
    async def test_list_objects_delegates_to_session(self):
        """Test that list_objects delegates to session correctly."""
        mock_session = AsyncMock()
        mock_session.list_objects.return_value = [
            {"pk": "test-1", "name": "Test 1"},
            {"pk": "test-2", "name": "Test 2"},
        ]

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.list_objects("test_type", limit=10)

            assert len(result) == 2
            assert result[0]["pk"] == "test-1"
            mock_session.list_objects.assert_called_once_with("test_type", limit=10)

    @pytest.mark.asyncio
    async def test_create_object_delegates_to_session(self):
        """Test that create_object delegates to session correctly."""
        mock_session = AsyncMock()
        mock_session.create_object.return_value = {"pk": "new-1", "name": "New"}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            data = {"name": "New", "value": 42}
            result = await client.create_object("test_type", data)

            assert result == {"pk": "new-1", "name": "New"}
            mock_session.create_object.assert_called_once_with("test_type", data)

    @pytest.mark.asyncio
    async def test_update_object_delegates_to_session(self):
        """Test that update_object delegates to session correctly."""
        mock_session = AsyncMock()
        mock_session.update_object.return_value = {"pk": "test-1", "name": "Updated"}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            data = {"name": "Updated"}
            result = await client.update_object("test_type", "test-1", data)

            assert result == {"pk": "test-1", "name": "Updated"}
            mock_session.update_object.assert_called_once_with("test_type", "test-1", data)

    @pytest.mark.asyncio
    async def test_delete_object_delegates_to_session(self):
        """Test that delete_object delegates to session correctly."""
        mock_session = AsyncMock()
        mock_session.delete_object.return_value = True

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.delete_object("test_type", "test-1")

            assert result is True
            mock_session.delete_object.assert_called_once_with("test_type", "test-1")

    @pytest.mark.asyncio
    async def test_object_exists_true(self):
        """Test object_exists returns True when object exists."""
        mock_session = AsyncMock()
        mock_session.get_object.return_value = {"pk": "test-1", "name": "Test"}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.object_exists("test_type", "test-1")

            assert result is True

    @pytest.mark.asyncio
    async def test_object_exists_false(self):
        """Test object_exists returns False when object doesn't exist."""
        mock_session = AsyncMock()
        mock_session.get_object.return_value = None

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.object_exists("test_type", "nonexistent")

            assert result is False

    @pytest.mark.asyncio
    async def test_count_objects(self):
        """Test count_objects returns correct count."""
        mock_session = AsyncMock()
        mock_session.list_objects.return_value = [
            {"pk": "test-1"},
            {"pk": "test-2"},
            {"pk": "test-3"},
        ]

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result = await client.count_objects("test_type")

            assert result == 3
            mock_session.list_objects.assert_called_once_with("test_type")

    @pytest.mark.asyncio
    async def test_get_or_create_object_existing(self):
        """Test get_or_create_object returns existing object."""
        mock_session = AsyncMock()
        existing_obj = {"pk": "test-1", "name": "Test"}
        mock_session.get_object.return_value = existing_obj

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            result, was_created = await client.get_or_create_object(
                "test_type", "test-1", {"name": "Test"}
            )

            assert result == existing_obj
            assert was_created is False
            mock_session.get_object.assert_called_once_with("test_type", "test-1")
            mock_session.create_object.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_object_new(self):
        """Test get_or_create_object creates new object."""
        mock_session = AsyncMock()
        mock_session.get_object.return_value = None
        created_obj = {"pk": "new-1", "name": "New"}
        mock_session.create_object.return_value = created_obj

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")
            data = {"name": "New"}
            result, was_created = await client.get_or_create_object("test_type", "new-1", data)

            assert result == created_obj
            assert was_created is True
            mock_session.get_object.assert_called_once_with("test_type", "new-1")
            mock_session.create_object.assert_called_once_with("test_type", data)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        mock_session = AsyncMock()

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            async with OntologyClient(host="http://localhost:8000") as client:
                assert client is not None
                # Use the client to ensure it's properly initialized
                await client.list_object_types()

            # Verify close was called
            mock_session.close.assert_called_once()

    def test_sync_methods(self):
        """Test synchronous convenience methods."""
        mock_session = AsyncMock()
        mock_session.get_object.return_value = {"pk": "test-1", "name": "Test"}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            client = OntologyClient(host="http://localhost:8000")

            # Test sync method
            result = client.get_object_sync("test_type", "test-1")
            assert result == {"pk": "test-1", "name": "Test"}

    def test_string_representations(self):
        """Test string representations of the client."""
        mock_session = MagicMock()

        # Test remote client
        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_session):
            # Add RemoteSession-like attributes to mock
            mock_session._client = MagicMock()
            mock_session._headers = {}

            client = OntologyClient(host="http://localhost:8000", ontology="test")

            str_repr = str(client)
            assert "Remote" in str_repr
            assert "test" in str_repr

            repr_str = repr(client)
            assert "mode=remote" in repr_str
            assert "ontology=test" in repr_str

        # Test local client
        from ontologia_sdk.session import LocalSession

        mock_local_session = MagicMock(spec=LocalSession)
        # Add LocalSession-like attributes to mock
        mock_local_session.connection_string = "sqlite:///./test.db"
        mock_local_session._services = {}

        with patch("ontologia_sdk.client_v2.create_session", return_value=mock_local_session):
            client = OntologyClient(connection_string="sqlite:///./test.db")

            str_repr = str(client)
            assert "Local" in str_repr

            repr_str = repr(client)
            assert "mode=local" in repr_str


class TestClientFactoryFunctions:
    """Test convenience factory functions."""

    def test_create_remote_client(self):
        """Test create_remote_client factory function."""
        with patch("ontologia_sdk.client_v2.OntologyClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            result = create_remote_client(
                host="http://localhost:8000", token="test-token", ontology="test", timeout=60.0
            )

            assert result == mock_client
            mock_client_class.assert_called_once_with(
                host="http://localhost:8000",
                token="test-token",
                ontology="test",
                timeout=60.0,
                headers=None,
            )

    def test_create_local_client(self):
        """Test create_local_client factory function."""
        with patch("ontologia_sdk.client_v2.OntologyClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            result = create_local_client(connection_string="sqlite:///./test.db", ontology="test")

            assert result == mock_client
            mock_client_class.assert_called_once_with(
                connection_string="sqlite:///./test.db", ontology="test"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
