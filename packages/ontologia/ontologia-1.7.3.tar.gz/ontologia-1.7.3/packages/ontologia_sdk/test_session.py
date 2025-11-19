"""
Comprehensive tests for ClientSession implementations.

Tests both RemoteSession and LocalSession to ensure consistent behavior
and proper error handling.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia_sdk.session import ClientSession, LocalSession, RemoteSession, create_session


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


class TestLocalSession:
    """Test LocalSession direct core implementation."""

    @pytest.fixture
    def mock_sqlmodel_engine(self):
        """Mock SQLModel engine and session."""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)

        with (
            patch("sqlmodel.create_engine", return_value=mock_engine),
            patch("sqlmodel.Session", return_value=mock_session),
        ):
            return mock_engine, mock_session, mock_session_factory

    @pytest.fixture
    def mock_core_services(self):
        """Mock ontologia-core services."""
        mock_metamodel_service = MagicMock()
        mock_instances_service = MagicMock()
        mock_linked_service = MagicMock()

        mock_metamodel_repo = MagicMock()
        mock_instances_repo = MagicMock()
        mock_linked_repo = MagicMock()

        with (
            patch(
                "ontologia.infrastructure.persistence.sql.SQLMetamodelRepository",
                return_value=mock_metamodel_repo,
            ),
            patch(
                "ontologia.infrastructure.persistence.sql.SQLObjectInstanceRepository",
                return_value=mock_instances_repo,
            ),
            patch(
                "ontologia.infrastructure.persistence.sql.SQLLinkedObjectRepository",
                return_value=mock_linked_repo,
            ),
            patch("ontologia.application.MetamodelService", return_value=mock_metamodel_service),
            patch("ontologia.application.InstancesService", return_value=mock_instances_service),
            patch("ontologia.application.LinkedObjectsService", return_value=mock_linked_service),
        ):
            return {
                "metamodel": mock_metamodel_service,
                "instances": mock_instances_service,
                "linked": mock_linked_service,
            }

    @pytest.fixture
    def local_session(self, mock_sqlmodel_engine, mock_core_services):
        """Create LocalSession with mocked dependencies."""
        mock_engine, mock_session, mock_session_factory = mock_sqlmodel_engine

        session = LocalSession("sqlite:///./test.db")
        session.engine = mock_engine
        session.session_factory = mock_session_factory
        session._services = mock_core_services

        return session, mock_session, mock_session_factory

    @pytest.mark.asyncio
    async def test_get_object_success(self, local_session):
        """Test successful object retrieval via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock instance
        mock_instance = MagicMock()
        mock_instance.model_dump.return_value = {"pk": "test-1", "name": "Test Object"}
        session._services["instances"].get_object.return_value = mock_instance

        # Test
        result = await session.get_object("test_type", "test-1")

        # Verify
        assert result == {"pk": "test-1", "name": "Test Object"}
        # New API passes (service, instance, object_type, pk)
        called_args = session._services["instances"].get_object.call_args[0]
        assert called_args[-2:] == ("test_type", "test-1")
        mock_session_factory.assert_called()

    @pytest.mark.asyncio
    async def test_get_object_not_found(self, local_session):
        """Test object not found via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock None return
        session._services["instances"].get_object.return_value = None

        # Test
        result = await session.get_object("test_type", "nonexistent")

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_list_objects_success(self, local_session):
        """Test successful object listing via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock instances
        mock_instance1 = MagicMock()
        mock_instance1.model_dump.return_value = {"pk": "test-1", "name": "Test 1"}
        mock_instance2 = MagicMock()
        mock_instance2.model_dump.return_value = {"pk": "test-2", "name": "Test 2"}

        # SDK now expects a response with `.objects`
        from types import SimpleNamespace

        session._services["instances"].list_objects.return_value = SimpleNamespace(
            objects=[mock_instance1, mock_instance2]
        )

        # Test
        result = await session.list_objects("test_type", limit=10)

        # Verify
        assert len(result) == 2
        assert result[0]["pk"] == "test-1"
        called = session._services["instances"].list_objects.call_args
        # Accept service + instance leading args
        assert called[0][-1] == "test_type"

    @pytest.mark.asyncio
    async def test_create_object_success(self, local_session):
        """Test successful object creation via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock request and instance
        mock_instance = MagicMock()
        mock_instance.model_dump.return_value = {"pk": "new-1", "name": "New Object"}

        with patch(
            "ontologia.application.instances_service.ObjectUpsertRequest"
        ) as mock_request_class:
            mock_request = MagicMock()
            mock_request_class.return_value = mock_request

            session._services["instances"].upsert_object.return_value = mock_instance

            # Test data
            data = {"name": "New Object", "value": 42}

            # Test
            result = await session.create_object("test_type", data)

            # Verify
            assert result["pk"] == "new-1"
            mock_request_class.assert_called_once_with(pk_value="auto-generated", properties=data)
            session._services["instances"].upsert_object.assert_called_once_with(
                "default", "default", "test_type", mock_request.pk_value, mock_request.properties
            )

    @pytest.mark.asyncio
    async def test_delete_object_success(self, local_session):
        """Test successful object deletion via core."""
        session, mock_session, mock_session_factory = local_session

        session._services["instances"].delete_object.return_value = True

        # Test
        result = await session.delete_object("test_type", "test-1")

        # Verify
        assert result is True
        called = session._services["instances"].delete_object.call_args
        # Accept service + instance leading args; last two should be object_type and pk
        assert called[0][-2:] == ("test_type", "test-1")

    @pytest.mark.asyncio
    async def test_list_object_types_success(self, local_session):
        """Test successful object type listing via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock object types
        mock_obj_type1 = MagicMock()
        mock_obj_type1.model_dump.return_value = {"api_name": "type1", "display_name": "Type 1"}
        mock_obj_type2 = MagicMock()
        mock_obj_type2.model_dump.return_value = {"api_name": "type2", "display_name": "Type 2"}

        session._services["metamodel"].list_object_types.return_value = [
            mock_obj_type1,
            mock_obj_type2,
        ]

        # Test
        result = await session.list_object_types()

        # Verify
        assert len(result) == 2
        assert result[0]["api_name"] == "type1"
        session._services["metamodel"].list_object_types.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_linked_objects_success(self, local_session):
        """Test successful linked objects retrieval via core."""
        session, mock_session, mock_session_factory = local_session

        # Mock linked objects
        mock_linked1 = MagicMock()
        mock_linked1.model_dump.return_value = {"pk": "linked-1", "name": "Linked 1"}
        mock_linked2 = MagicMock()
        mock_linked2.model_dump.return_value = {"pk": "linked-2", "name": "Linked 2"}

        session._services["linked"].get_linked_objects.return_value = [mock_linked1, mock_linked2]

        # Test
        result = await session.get_linked_objects(
            "source_type", "source-1", "link_type", "outgoing"
        )

        # Verify
        assert len(result) == 2
        assert result[0]["pk"] == "linked-1"
        session._services["linked"].get_linked_objects.assert_called_once_with(
            "source_type", "source-1", "link_type", "outgoing"
        )

    @pytest.mark.asyncio
    async def test_close(self, local_session):
        """Test session cleanup."""
        session, mock_session, mock_session_factory = local_session

        # Mock engine dispose
        session.engine.dispose = MagicMock()

        await session.close()
        session.engine.dispose.assert_called_once()


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
            _args, _kwargs = mock_remote.call_args
            for k, v in {
                "host": "http://localhost:8000",
                "token": "test-token",
                "timeout": 60.0,
                "ontology": "test",
            }.items():
                assert _kwargs.get(k) == v

    def test_create_local_session(self):
        """Test creating local session."""
        with patch("ontologia_sdk.session.LocalSession") as mock_local:
            mock_session = MagicMock()
            mock_local.return_value = mock_session

            result = create_session(connection_string="sqlite:///./test.db")

            assert result == mock_session
            _args, _kwargs = mock_local.call_args
            assert _kwargs.get("connection_string") == "sqlite:///./test.db"

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
            local = LocalSession("sqlite:///./test.db")

            # Both should be instances of ClientSession
            assert isinstance(remote, ClientSession)
            assert isinstance(local, ClientSession)

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
                assert hasattr(local, method)
                assert callable(getattr(remote, method))
                assert callable(getattr(local, method))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
