"""
Simplified tests for ClientSession implementations.

Focus on testing the RemoteSession functionality and basic protocol compliance.
LocalSession tests require ontologia-core to be available.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia_sdk.session import ClientSession, RemoteSession, create_session


class TestClientSessionProtocol:
    """Test that ClientSession protocol is properly defined."""

    def test_protocol_is_runtime_checkable(self):
        """Verify protocol can be used with isinstance()."""
        # Check if __protocol__ attribute exists (runtime_checkable decorator)
        assert hasattr(ClientSession, "__protocol__") or hasattr(ClientSession, "_is_protocol")

    def test_protocol_methods_defined(self):
        """Verify all required methods are defined."""
        required_methods = [
            "get_object",
            "list_objects",
            "create_object",
            "update_object",
            "delete_object",
            "list_object_types",
            "get_object_type",
            "create_object_type",
            "update_object_type",
            "list_link_types",
            "get_link_type",
            "create_link_type",
            "get_linked_objects",
            "create_link",
            "close",
        ]

        for method in required_methods:
            assert hasattr(ClientSession, method)


class TestRemoteSession:
    """Test RemoteSession HTTP implementation."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.AsyncClient."""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def remote_session(self, mock_httpx_client):
        """Create RemoteSession with mocked HTTP client."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            session = RemoteSession(
                host="http://localhost:8000", token="test-token", ontology="test-ontology"
            )
            session._client = mock_httpx_client
            return session

    @pytest.mark.asyncio
    async def test_get_object_success(self, remote_session, mock_httpx_client):
        """Test successful object retrieval."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"pk": "test-1", "name": "Test Object"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        # Test
        result = await remote_session.get_object("test_type", "test-1")

        # Verify
        assert result == {"pk": "test-1", "name": "Test Object"}
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args
        assert "objects/test_type/test-1" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_get_object_not_found(self, remote_session, mock_httpx_client):
        """Test object not found handling."""
        # Mock 404 response
        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        mock_httpx_client.get.return_value = mock_response

        # Test
        result = await remote_session.get_object("test_type", "nonexistent")

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_list_objects_success(self, remote_session, mock_httpx_client):
        """Test successful object listing."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"pk": "test-1", "name": "Test 1"},
            {"pk": "test-2", "name": "Test 2"},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.get.return_value = mock_response

        # Test
        result = await remote_session.list_objects("test_type", limit=10)

        # Verify
        assert len(result) == 2
        assert result[0]["pk"] == "test-1"
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args
        assert call_args[1]["params"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_create_object_success(self, remote_session, mock_httpx_client):
        """Test successful object creation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"pk": "new-1", "name": "New Object"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post.return_value = mock_response

        # Test data
        data = {"name": "New Object", "value": 42}

        # Test
        result = await remote_session.create_object("test_type", data)

        # Verify
        assert result["pk"] == "new-1"
        assert result["name"] == "New Object"
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert call_args[1]["json"] == data

    @pytest.mark.asyncio
    async def test_delete_object_success(self, remote_session, mock_httpx_client):
        """Test successful object deletion."""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.delete.return_value = mock_response

        # Test
        result = await remote_session.delete_object("test_type", "test-1")

        # Verify
        assert result is True
        mock_httpx_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_object_not_found(self, remote_session, mock_httpx_client):
        """Test deletion of non-existent object."""
        # Mock 404 response
        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )
        mock_httpx_client.delete.return_value = mock_response

        # Test
        result = await remote_session.delete_object("test_type", "nonexistent")

        # Verify
        assert result is False

    @pytest.mark.asyncio
    async def test_close(self, remote_session, mock_httpx_client):
        """Test session cleanup."""
        await remote_session.close()
        mock_httpx_client.aclose.assert_called_once()


class TestSessionFactory:
    """Test session factory function."""

    def test_create_remote_session(self):
        """Test creating remote session."""
        with patch("ontologia_sdk.session.RemoteSession") as mock_remote:
            mock_session = MagicMock()
            mock_remote.return_value = mock_session

            result = create_session(
                host="http://localhost:8000", token="test-token", timeout=60.0, ontology="test"
            )

            assert result == mock_session
            # Accept additional kwargs (e.g., use_ogm) for forward compatibility
            called_args, called_kwargs = mock_remote.call_args
            for k, v in {
                "host": "http://localhost:8000",
                "token": "test-token",
                "timeout": 60.0,
                "ontology": "test",
            }.items():
                assert called_kwargs.get(k) == v

    def test_create_local_session(self):
        """Test creating local session."""
        with patch("ontologia_sdk.session.LocalSession") as mock_local:
            mock_session = MagicMock()
            mock_local.return_value = mock_session

            result = create_session(connection_string="sqlite:///./test.db")

            assert result == mock_session
            called_args, called_kwargs = mock_local.call_args
            assert called_kwargs.get("connection_string") == "sqlite:///./test.db"

    def test_create_session_both_params_error(self):
        """Test error when both host and connection_string provided."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            create_session(host="http://localhost:8000", connection_string="sqlite:///./test.db")

    def test_create_session_no_params_error(self):
        """Test error when neither host nor connection_string provided."""
        with pytest.raises(ValueError, match="Must specify either"):
            create_session()


class TestSessionCompatibility:
    """Test that both session implementations behave consistently."""

    @pytest.mark.asyncio
    async def test_protocol_compliance(self):
        """Test that both implementations comply with protocol."""
        # Create mock sessions
        with patch("httpx.AsyncClient"), patch("sqlmodel.create_engine"), patch("sqlmodel.Session"):
            remote = RemoteSession(host="http://localhost:8000")

            # Test LocalSession only if ontologia-core is available
            try:
                from ontologia_sdk.session import LocalSession

                local = LocalSession("sqlite:///./test.db")
                local_available = True
            except ImportError:
                local_available = False

            # Remote should be instance of ClientSession
            assert isinstance(remote, ClientSession)

            # Both should have required methods
            required_methods = [
                "get_object",
                "list_objects",
                "create_object",
                "update_object",
                "delete_object",
                "list_object_types",
                "get_object_type",
                "create_object_type",
                "update_object_type",
                "list_link_types",
                "get_link_type",
                "create_link_type",
                "get_linked_objects",
                "create_link",
                "close",
            ]

            for method in required_methods:
                assert hasattr(remote, method)
                assert callable(getattr(remote, method))

                if local_available:
                    assert hasattr(local, method)
                    assert callable(getattr(local, method))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
