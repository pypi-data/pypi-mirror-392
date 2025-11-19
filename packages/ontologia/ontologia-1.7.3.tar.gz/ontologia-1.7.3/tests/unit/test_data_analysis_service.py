"""
test_data_analysis_service.py
------------------------------
Unit tests for DataAnalysisService.

Tests data analysis operations using DuckDB with in-memory database.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from ontologia.application.data_analysis_service import (
    AnalysisRequest,
    AnalysisType,
    DataAnalysisService,
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
    if not repo.is_available():
        pytest.skip("DuckDB not available for testing")

    # Setup sample data for all tests
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
def data_analysis_service(duckdb_repo):
    """Create DataAnalysisService for testing."""
    mock_instances = Mock()
    mock_metamodel = Mock()
    return DataAnalysisService(mock_instances, mock_metamodel, duckdb_repo)


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


class TestDataAnalysisService:
    """Test cases for DataAnalysisService."""

    @pytest.mark.asyncio
    async def test_execute_count_query(self, data_analysis_service, duckdb_repo):
        """Test statistical analysis execution."""
        request = AnalysisRequest(
            id="test-statistical",
            object_type_api_name="test_object",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["value"],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        result = await data_analysis_service._execute_statistical_analysis(
            request, "test", "instance"
        )

        assert isinstance(result, dict)
        assert result["count"] == 5
        assert result["mean"] == 20.2  # 101.0 / 5
        assert result["min"] == 10.5
        assert result["max"] == 30.0
        assert result["median"] == 20.0
        assert "stddev" in result
        assert "q1" in result
        assert "q3" in result

    @pytest.mark.asyncio
    async def test_execute_statistical_analysis(self, data_analysis_service, duckdb_repo):
        """Test statistical analysis with filters."""
        request = AnalysisRequest(
            id="test-statistical-filtered",
            object_type_api_name="test_object",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["value"],
            filters={"category": "Category 1"},
            parameters={},
            created_at=datetime.now(),
        )

        result = await data_analysis_service._execute_statistical_analysis(
            request, "test", "instance"
        )

        assert result["count"] == 3  # Items A, C, E
        assert result["mean"] == 18.666666666666668  # (10.5 + 15.5 + 30.0) / 3

    @pytest.mark.asyncio
    async def test_execute_trend_analysis(self, data_analysis_service, duckdb_repo):
        """Test trend analysis execution."""
        request = AnalysisRequest(
            id="test-trend",
            object_type_api_name="test_object",
            analysis_type=AnalysisType.TREND,
            properties=["value"],
            filters={},
            parameters={"time_unit": "day", "timestamp_column": "sync_timestamp"},
            created_at=datetime.now(),
        )

        result = await data_analysis_service._execute_trend_analysis(request, "test", "instance")

        assert isinstance(result, dict)
        assert "trend_data" in result
        assert result["time_unit"] == "day"
        assert result["property"] == "value"
        assert result["periods_analyzed"] == 5  # 5 days of data

        trend_data = result["trend_data"]
        assert len(trend_data) == 5
        assert all(isinstance(item, dict) for item in trend_data)
        assert all("period" in item and "value" in item and "count" in item for item in trend_data)

    @pytest.mark.asyncio
    async def test_generate_insights(self, data_analysis_service, duckdb_repo):
        """Test statistical insight generation."""
        results = {
            "count": 1000,
            "mean": 50.0,
            "stddev": 7.5,
            "median": 49.0,
            "min": 10.0,
            "max": 90.0,
        }

        insights = data_analysis_service._generate_statistical_insights(results)

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any("1,000 records" in insight for insight in insights)
        assert any("Average value is 50.00" in insight for insight in insights)
        assert any("standard deviation" in insight for insight in insights)
        assert any("symmetric" in insight for insight in insights)

    @pytest.mark.asyncio
    async def test_generate_distribution_insights(self, data_analysis_service):
        """Test distribution insight generation."""
        results = {"Category A": 450, "Category B": 300, "Category C": 150, "Category D": 100}

        insights = data_analysis_service._generate_distribution_insights(results)

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any("4 distinct values" in insight for insight in insights)
        assert any("Category A" in insight for insight in insights)
        assert any("45.0%" in insight for insight in insights)
        assert any("moderate concentration" in insight for insight in insights)

    @pytest.mark.asyncio
    async def test_generate_trend_insights(self, data_analysis_service):
        """Test trend insight generation."""
        results = [
            {"period": "2024-01-01", "value": 10.0},
            {"period": "2024-01-02", "value": 15.0},
            {"period": "2024-01-03", "value": 20.0},
            {"period": "2024-01-04", "value": 18.0},
        ]

        insights = data_analysis_service._generate_trend_insights(results)

        assert isinstance(insights, list)
        assert len(insights) > 0
        assert any("4 time periods" in insight for insight in insights)
        assert any("Upward trend" in insight for insight in insights)

    @pytest.mark.asyncio
    async def test_generate_insights_error_handling(self, data_analysis_service):
        """Test insight generation error handling."""
        insights = await data_analysis_service._generate_insights(
            {"error": "test error"}, AnalysisType.STATISTICAL
        )

        assert isinstance(insights, list)
        assert len(insights) > 0

    @pytest.mark.asyncio
    async def test_analysis_without_properties_raises_error(self, data_analysis_service):
        """Test that analysis requiring properties raises errors when not provided."""
        request = AnalysisRequest(
            id="test-error",
            object_type_api_name="test_object",
            analysis_type=AnalysisType.STATISTICAL,
            properties=[],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        with pytest.raises(ValueError, match="Properties list is required"):
            await data_analysis_service._execute_statistical_analysis(request, "test", "instance")

    def test_service_initialization(self, duckdb_repo):
        """Test service initialization."""
        mock_instances = Mock()
        mock_metamodel = Mock()

        service = DataAnalysisService(mock_instances, mock_metamodel, duckdb_repo)

        assert service.instances_service == mock_instances
        assert service.metamodel_service == mock_metamodel
        assert service.duckdb_repo == duckdb_repo
        assert service.logger is not None

    def test_service_initialization_without_repo(self):
        """Test service initialization creates default repo when not provided."""
        mock_instances = Mock()
        mock_metamodel = Mock()

        service = DataAnalysisService(mock_instances, mock_metamodel)

        assert service.instances_service == mock_instances
        assert service.metamodel_service == mock_metamodel
        assert service.duckdb_repo is not None
        assert isinstance(service.duckdb_repo, DuckDBRepository)


if __name__ == "__main__":
    pytest.main([__file__])
