"""
test_analytics_service.py
------------------------
Unit tests for AnalyticsService.

Tests analytics operations using DuckDB with in-memory database.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from ontologia.application.analytics_service import (
    AnalyticsQuery,
    AnalyticsService,
    AnalyticsType,
)
from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository


@pytest.fixture(scope="class")
def duckdb_repo():
    """Create DuckDB repository for testing."""
    # Use file-based database for testing to ensure persistence
    import os
    import tempfile

    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.duckdb")

    repo = DuckDBRepository(duckdb_path=db_path)

    # Setup sample data for all tests
    if not repo.is_available():
        pytest.skip("DuckDB not available for testing")

    with repo.get_connection(read_only=False) as conn:
        create_table_sql = """
            CREATE TABLE ot_test_object (
                id INTEGER,
                name VARCHAR,
                value DOUBLE,
                category VARCHAR,
                sync_timestamp TIMESTAMP
            )
        """

        insert_data_sql = """
            INSERT INTO ot_test_object VALUES
            (1, 'Item A', 10.5, 'Category 1', '2024-01-01 10:00:00'),
            (2, 'Item B', 20.0, 'Category 2', '2024-01-02 11:00:00'),
            (3, 'Item C', 15.5, 'Category 1', '2024-01-03 12:00:00'),
            (4, 'Item D', 25.0, 'Category 2', '2024-01-04 13:00:00'),
            (5, 'Item E', 30.0, 'Category 1', '2024-01-05 14:00:00')
        """

        conn.execute(create_table_sql)
        conn.execute(insert_data_sql)

    yield repo

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def analytics_service(duckdb_repo):
    """Create AnalyticsService for testing."""
    mock_instances = Mock()
    mock_metamodel = Mock()
    return AnalyticsService(mock_instances, mock_metamodel, duckdb_repo)


@pytest.fixture
def sample_data(duckdb_repo):
    """Create sample data for testing."""
    if not duckdb_repo.is_available():
        pytest.skip("DuckDB not available for testing")

    # Create sample table with test data
    create_table_sql = """
        CREATE TABLE ot_test_object (
            id INTEGER,
            name VARCHAR,
            value DOUBLE,
            category VARCHAR,
            sync_timestamp TIMESTAMP
        )
    """

    insert_data_sql = """
        INSERT INTO ot_test_object VALUES
        (1, 'Item A', 10.5, 'Category 1', '2024-01-01 10:00:00'),
        (2, 'Item B', 20.0, 'Category 2', '2024-01-02 11:00:00'),
        (3, 'Item C', 15.5, 'Category 1', '2024-01-03 12:00:00'),
        (4, 'Item D', 25.0, 'Category 2', '2024-01-04 13:00:00'),
        (5, 'Item E', 30.0, 'Category 1', '2024-01-05 14:00:00')
    """

    # Use the same connection for both operations
    with duckdb_repo.get_connection(read_only=False) as conn:
        conn.execute(create_table_sql)
        conn.execute(insert_data_sql)


class TestAnalyticsService:
    """Test cases for AnalyticsService."""

    @pytest.mark.asyncio
    async def test_execute_count_query(self, analytics_service, duckdb_repo):
        """Test count query execution."""
        query = AnalyticsQuery(
            id="test-count",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.COUNT,
            property_name=None,
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_count_query(query, "test", "instance")

        assert result == 5
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_execute_count_query_with_filters(self, analytics_service, duckdb_repo):
        """Test count query with filters."""
        query = AnalyticsQuery(
            id="test-count-filtered",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.COUNT,
            property_name=None,
            filters={"category": "Category 1"},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_count_query(query, "test", "instance")

        assert result == 3  # Items A, C, E

    @pytest.mark.asyncio
    async def test_execute_sum_query(self, analytics_service, duckdb_repo):
        """Test sum query execution."""
        query = AnalyticsQuery(
            id="test-sum",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.SUM,
            property_name="value",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_sum_query(query, "test", "instance")

        assert result == 101.0  # 10.5 + 20.0 + 15.5 + 25.0 + 30.0
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_execute_average_query(self, analytics_service, duckdb_repo):
        """Test average query execution."""
        query = AnalyticsQuery(
            id="test-avg",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.AVERAGE,
            property_name="value",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_average_query(query, "test", "instance")

        assert result == 20.2  # 101.0 / 5
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_execute_min_query(self, analytics_service, duckdb_repo):
        """Test min query execution."""
        query = AnalyticsQuery(
            id="test-min",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.MIN,
            property_name="value",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_min_query(query, "test", "instance")

        assert result == 10.5

    @pytest.mark.asyncio
    async def test_execute_max_query(self, analytics_service, duckdb_repo):
        """Test max query execution."""
        query = AnalyticsQuery(
            id="test-max",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.MAX,
            property_name="value",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_max_query(query, "test", "instance")

        assert result == 30.0

    @pytest.mark.asyncio
    async def test_execute_distribution_query(self, analytics_service, duckdb_repo):
        """Test distribution query execution."""
        query = AnalyticsQuery(
            id="test-distribution",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.DISTRIBUTION,
            property_name="category",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        result = await analytics_service._execute_distribution_query(query, "test", "instance")

        assert isinstance(result, dict)
        assert result["Category 1"] == 3  # Items A, C, E
        assert result["Category 2"] == 2  # Items B, D

    @pytest.mark.asyncio
    async def test_query_without_property_name_raises_error(self, analytics_service):
        """Test that queries requiring property names raise errors when not provided."""
        query = AnalyticsQuery(
            id="test-error",
            object_type_api_name="test_object",
            analytics_type=AnalyticsType.SUM,
            property_name=None,
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        with pytest.raises(ValueError, match="Property name is required"):
            await analytics_service._execute_sum_query(query, "test", "instance")

    def test_service_initialization(self, duckdb_repo):
        """Test service initialization."""
        mock_instances = Mock()
        mock_metamodel = Mock()

        service = AnalyticsService(mock_instances, mock_metamodel, duckdb_repo)

        assert service.instances_service == mock_instances
        assert service.metamodel_service == mock_metamodel
        assert service.duckdb_repo == duckdb_repo
        assert service.logger is not None

    def test_service_initialization_without_repo(self):
        """Test service initialization creates default repo when not provided."""
        mock_instances = Mock()
        mock_metamodel = Mock()

        service = AnalyticsService(mock_instances, mock_metamodel)

        assert service.instances_service == mock_instances
        assert service.metamodel_service == mock_metamodel
        assert service.duckdb_repo is not None
        assert isinstance(service.duckdb_repo, DuckDBRepository)


if __name__ == "__main__":
    pytest.main([__file__])
