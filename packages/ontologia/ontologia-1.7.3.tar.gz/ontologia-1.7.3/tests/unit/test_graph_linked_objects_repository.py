"""Tests for GraphLinkedObjectsRepository traversal methods."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from ontologia.domain.metamodels.instances.models_sql import LinkedObject
from ontologia.infrastructure.persistence.graph.linked_objects_repository import (
    GraphLinkedObjectsRepository,
)


class TestGraphLinkedObjectsRepository:
    """Test cases for GraphLinkedObjectsRepository traversal methods."""

    @pytest.fixture
    def mock_graph_client(self):
        """Create a mock graph client."""
        client = Mock()
        client.is_available.return_value = True
        return client

    @pytest.fixture
    def mock_session_factory(self):
        """Create a mock session factory."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_graph_client, mock_session_factory):
        """Create repository instance with mock client."""
        return GraphLinkedObjectsRepository(
            graph_client=mock_graph_client, session_factory=mock_session_factory
        )

    @pytest.fixture
    def sample_rows(self):
        """Sample query result rows."""
        return [
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-001",
                "targetPkValue": "comp-001",
                "data": '{"since": "2024-01-01", "role": "developer"}',
                "rid": "edge-001",
            },
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-002",
                "targetPkValue": "comp-001",
                "data": '{"since": "2024-02-01", "role": "designer"}',
                "rid": "edge-002",
            },
        ]

    def test_graph_client_available(self, repository, mock_graph_client):
        """Test that graph client availability is checked correctly."""
        assert repository._graph_client() == mock_graph_client

    def test_graph_client_unavailable(self, repository):
        """Test behavior when graph client is not available."""
        repository.graph_client = None
        assert repository._graph_client() is None

    def test_graph_client_is_available_false(self, repository, mock_graph_client):
        """Test behavior when client reports unavailable."""
        mock_graph_client.is_available.return_value = False
        assert repository._graph_client() is None

    def test_row_to_dict_with_dict(self):
        """Test converting dict row to dictionary."""
        row = {"key": "value", "number": 42}
        columns = ["key", "number"]
        result = GraphLinkedObjectsRepository._row_to_dict(row, columns)
        assert result == {"key": "value", "number": 42}

    def test_row_to_dict_with_object(self):
        """Test converting object row to dictionary."""

        class RowObj:
            def __init__(self):
                self.key = "value"
                self.number = 42

            def get(self, attr, default=None):
                return getattr(self, attr, default)

        row = RowObj()
        columns = ["key", "number"]
        result = GraphLinkedObjectsRepository._row_to_dict(row, columns)
        assert result == {"key": "value", "number": 42}

    def test_parse_properties_dict(self):
        """Test parsing properties when already a dict."""
        props = {"key": "value", "number": 42}
        result = GraphLinkedObjectsRepository._parse_properties(props)
        assert result == {"key": "value", "number": 42}

    def test_parse_properties_json_string(self):
        """Test parsing properties from JSON string."""
        props = '{"key": "value", "number": 42}'
        result = GraphLinkedObjectsRepository._parse_properties(props)
        assert result == {"key": "value", "number": 42}

    def test_parse_properties_none(self):
        """Test parsing None properties."""
        result = GraphLinkedObjectsRepository._parse_properties(None)
        assert result == {}

    def test_parse_properties_invalid_json(self):
        """Test parsing invalid JSON string."""
        props = "invalid json"
        result = GraphLinkedObjectsRepository._parse_properties(props)
        assert result == {}

    def test_rows_to_linked_objects(self, repository, sample_rows):
        """Test converting rows to LinkedObject instances."""
        result = repository._rows_to_linked_objects(sample_rows)
        assert len(result) == 2

        obj1 = result[0]
        assert isinstance(obj1, LinkedObject)
        assert obj1.link_type_api_name == "works_for"
        assert obj1.link_type_rid == "lt-123"
        assert obj1.source_pk_value == "emp-001"
        assert obj1.target_pk_value == "comp-001"
        assert obj1.data == {"since": "2024-01-01", "role": "developer"}
        assert obj1.rid == "edge-001"

    def test_rows_to_linked_objects_with_invalid_row(self, repository, sample_rows):
        """Test handling invalid rows during conversion."""
        invalid_rows = sample_rows + [{"invalid": "row"}]
        result = repository._rows_to_linked_objects(invalid_rows)
        # Should only convert valid rows
        assert len(result) == 2

    def test_rows_to_linked_objects_edge_cases(self, repository):
        """Test handling various edge cases during conversion."""
        edge_case_rows = [
            # Valid row
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-001",
                "targetPkValue": "comp-001",
                "data": '{"since": "2024-01-01"}',
                "rid": "edge-001",
            },
            # Missing linkTypeApiName
            {
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-002",
                "targetPkValue": "comp-001",
                "data": '{"since": "2024-02-01"}',
                "rid": "edge-002",
            },
            # Missing sourcePkValue
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "targetPkValue": "comp-001",
                "data": '{"since": "2024-03-01"}',
                "rid": "edge-003",
            },
            # Empty row
            {},
            # Row with None values for required fields
            {
                "linkTypeApiName": None,
                "linkTypeRid": None,
                "sourcePkValue": None,
                "targetPkValue": None,
                "data": '{"since": "2024-04-01"}',
                "rid": "edge-004",
            },
            # Valid row with missing optional fields
            {
                "linkTypeApiName": "reports_to",
                "linkTypeRid": "lt-456",
                "sourcePkValue": "emp-003",
                "targetPkValue": "emp-001",
                "data": '{"since": "2024-05-01"}',
                # Missing rid (optional)
            },
        ]

        result = repository._rows_to_linked_objects(edge_case_rows)

        # Should only convert valid rows (first and last)
        assert len(result) == 2
        assert result[0].link_type_api_name == "works_for"
        assert result[0].source_pk_value == "emp-001"
        assert result[1].link_type_api_name == "reports_to"
        assert result[1].source_pk_value == "emp-003"
        assert result[1].rid is None  # Optional field should be None

    @pytest.mark.asyncio
    async def test_traverse_outgoing_success(self, repository, mock_graph_client):
        """Test successful outgoing traversal."""
        # Mock the _rows_from_result method to return test data
        test_rows = [
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-001",
                "targetPkValue": "comp-001",
                "data": {"since": "2024-01-01", "role": "developer"},  # Use data field
                "rid": "edge-001",
            },
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-002",
                "targetPkValue": "comp-001",
                "data": {"since": "2024-02-01", "role": "designer"},  # Use data field
                "rid": "edge-002",
            },
        ]

        with patch.object(repository, "_rows_from_result", return_value=test_rows):
            result = await repository.traverse_outgoing("lt-123", "emp-001", limit=10)

        assert len(result) == 2
        assert all(isinstance(obj, LinkedObject) for obj in result)
        assert result[0].source_pk_value == "emp-001"
        assert result[0].target_pk_value == "comp-001"
        assert result[0].data == {"since": "2024-01-01", "role": "developer"}

    @pytest.mark.asyncio
    async def test_traverse_outgoing_with_valid_at(self, repository, mock_graph_client):
        """Test outgoing traversal with temporal filter."""
        mock_result = Mock()
        mock_result.get_as_df.return_value = Mock()
        mock_graph_client.execute.return_value = mock_result

        valid_at = datetime(2024, 1, 1)
        await repository.traverse_outgoing("lt-123", "emp-001", valid_at=valid_at)

        # Verify query includes temporal filtering
        call_args = mock_graph_client.execute.call_args
        query = call_args[0][0]
        assert "validFrom" in query
        assert "validTo" in query
        assert "$valid_at" in query

    @pytest.mark.asyncio
    async def test_traverse_outgoing_no_client(self, repository):
        """Test outgoing traversal when no client available."""
        repository.graph_client = None
        result = await repository.traverse_outgoing("lt-123", "emp-001")
        assert result == []

    @pytest.mark.asyncio
    async def test_traverse_outgoing_exception(self, repository, mock_graph_client):
        """Test outgoing traversal handles exceptions."""
        mock_graph_client.execute.side_effect = Exception("Query failed")

        result = await repository.traverse_outgoing("lt-123", "emp-001")
        assert result == []

    @pytest.mark.asyncio
    async def test_traverse_incoming_success(self, repository, mock_graph_client):
        """Test successful incoming traversal."""
        # Mock the _rows_from_result method to return test data
        test_rows = [
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-001",
                "targetPkValue": "comp-001",
                "data": {"since": "2024-01-01", "role": "developer"},  # Use data field
                "rid": "edge-001",
            },
            {
                "linkTypeApiName": "works_for",
                "linkTypeRid": "lt-123",
                "sourcePkValue": "emp-002",
                "targetPkValue": "comp-001",
                "data": {"since": "2024-02-01", "role": "designer"},  # Use data field
                "rid": "edge-002",
            },
        ]

        with patch.object(repository, "_rows_from_result", return_value=test_rows):
            result = await repository.traverse_incoming("lt-123", "comp-001", limit=10)

        assert len(result) == 2
        assert all(isinstance(obj, LinkedObject) for obj in result)
        assert result[0].target_pk_value == "comp-001"
        assert result[0].data == {"since": "2024-01-01", "role": "developer"}

    @pytest.mark.asyncio
    async def test_traverse_incoming_with_valid_at(self, repository, mock_graph_client):
        """Test incoming traversal with temporal filter."""
        mock_result = Mock()
        mock_result.get_as_df.return_value = Mock()
        mock_graph_client.execute.return_value = mock_result

        valid_at = datetime(2024, 1, 1)
        await repository.traverse_incoming("lt-123", "comp-001", valid_at=valid_at)

        # Verify query includes temporal filtering
        call_args = mock_graph_client.execute.call_args
        query = call_args[0][0]
        assert "validFrom" in query
        assert "validTo" in query
        assert "$valid_at" in query

    @pytest.mark.asyncio
    async def test_traverse_incoming_no_client(self, repository):
        """Test incoming traversal when no client available."""
        repository.graph_client = None
        result = await repository.traverse_incoming("lt-123", "comp-001")
        assert result == []

    @pytest.mark.asyncio
    async def test_traverse_incoming_exception(self, repository, mock_graph_client):
        """Test incoming traversal handles exceptions."""
        mock_graph_client.execute.side_effect = Exception("Query failed")

        result = await repository.traverse_incoming("lt-123", "comp-001")
        assert result == []

    def test_run_query_with_params(self, repository, mock_graph_client):
        """Test running query with parameters."""
        mock_result = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.columns = []
        mock_df.shape = (0, 0)
        mock_result.get_as_df.return_value = mock_df
        mock_graph_client.execute.return_value = mock_result

        result = repository._run_query("MATCH (n) RETURN n", {"param": "value"})

        mock_graph_client.execute.assert_called_once_with("MATCH (n) RETURN n", {"param": "value"})
        assert result == []

    def test_run_query_without_params(self, repository, mock_graph_client):
        """Test running query without parameters."""
        mock_result = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.columns = []
        mock_df.shape = (0, 0)
        mock_result.get_as_df.return_value = mock_df
        mock_graph_client.execute.return_value = mock_result

        result = repository._run_query("MATCH (n) RETURN n")

        mock_graph_client.execute.assert_called_once_with("MATCH (n) RETURN n")
        assert result == []

    def test_run_query_client_none(self, repository):
        """Test running query when client is None."""
        repository.graph_client = None
        result = repository._run_query("MATCH (n) RETURN n")
        assert result == []

    def test_run_query_exception(self, repository, mock_graph_client):
        """Test running query handles exceptions."""
        mock_graph_client.execute.side_effect = Exception("Query failed")

        result = repository._run_query("MATCH (n) RETURN n")
        assert result == []

    def test_rows_from_result_none(self, repository):
        """Test processing None result."""
        result = repository._rows_from_result(None)
        assert result == []

    def test_rows_from_result_empty_df(self, repository):
        """Test processing empty DataFrame result."""
        mock_result = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=0)
        mock_df.columns = []
        mock_result.get_as_df.return_value = mock_df

        result = repository._rows_from_result(mock_result)
        assert result == []
