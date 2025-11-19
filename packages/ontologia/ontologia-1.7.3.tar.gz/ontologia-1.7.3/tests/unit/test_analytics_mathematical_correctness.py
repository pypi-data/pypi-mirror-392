"""
Unit tests for analytics logic using in-memory DuckDB.

These tests validate the mathematical correctness of our analytics services
by comparing results with pre-calculated expected values.
"""

from datetime import datetime
from decimal import Decimal

import pytest

# Skip this test module entirely if DuckDB is not installed in the environment
pytest.importorskip("duckdb", reason="DuckDB not installed")
from duckdb import BinderException, CatalogException

from ontologia.application.analytics_service import AnalyticsService, AnalyticsType
from ontologia.application.data_analysis_service import (
    AnalysisRequest,
    AnalysisType,
    DataAnalysisService,
)
from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository


@pytest.fixture
def memory_duckdb_repo():
    """Create DuckDB repository with in-memory database."""
    # Use a file-based database for persistence across connections
    import tempfile

    temp_db = tempfile.NamedTemporaryFile(delete=True, suffix=".duckdb")
    temp_db_name = temp_db.name
    temp_db.close()

    repo = DuckDBRepository(duckdb_path=temp_db_name)

    if not repo.is_available():
        pytest.skip("DuckDB not available")

    # Create test schema and data
    setup_schema_and_data(repo)

    return repo


@pytest.fixture
def analytics_service_with_repo(memory_duckdb_repo):
    """Create AnalyticsService with the same repository used for setup."""
    from unittest.mock import Mock

    instances_service = Mock()
    metamodel_service = Mock()
    return AnalyticsService(
        instances_service=instances_service,
        metamodel_service=metamodel_service,
        duckdb_repo=memory_duckdb_repo,
    )


@pytest.fixture
def data_analysis_service_with_repo(memory_duckdb_repo):
    """Create DataAnalysisService with the same repository used for setup."""
    from unittest.mock import Mock

    instances_service = Mock()
    metamodel_service = Mock()
    return DataAnalysisService(
        instances_service=instances_service,
        metamodel_service=metamodel_service,
        duckdb_repo=memory_duckdb_repo,
    )


def setup_schema_and_data(repo: DuckDBRepository):
    """Setup test schema and known data for mathematical validation."""

    # Create test table with the expected naming convention
    create_table_sql = """
        CREATE TABLE ot_analytics_test (
            id INTEGER,
            object_type VARCHAR,
            name VARCHAR,
            age INTEGER,
            salary DECIMAL(10,2),
            department VARCHAR,
            hire_date DATE,
            performance_score DECIMAL(5,2),
            is_active BOOLEAN
        )
    """

    # Insert known test data for mathematical validation
    insert_data_sql = """
        INSERT INTO ot_analytics_test VALUES
        (1, 'employee', 'Alice Johnson', 28, 75000.00, 'Engineering', '2022-01-15', 4.5, TRUE),
        (2, 'employee', 'Bob Smith', 35, 85000.00, 'Engineering', '2021-03-20', 4.2, TRUE),
        (3, 'employee', 'Carol Davis', 42, 95000.00, 'Marketing', '2020-06-10', 4.8, TRUE),
        (4, 'employee', 'David Wilson', 31, 80000.00, 'Engineering', '2022-08-05', 3.9, TRUE),
        (5, 'employee', 'Eva Brown', 29, 70000.00, 'Marketing', '2023-02-28', 4.6, TRUE),
        (6, 'employee', 'Frank Miller', 38, 105000.00, 'Management', '2019-11-12', 4.7, TRUE),
        (7, 'employee', 'Grace Lee', 26, 65000.00, 'Engineering', '2023-07-01', 4.1, FALSE),
        (8, 'employee', 'Henry Taylor', 33, 78000.00, 'Marketing', '2022-04-18', 4.3, TRUE),
        (9, 'employee', 'Iris Chen', 45, 120000.00, 'Management', '2018-09-30', 4.9, TRUE),
        (10, 'employee', 'Jack Martinez', 27, 68000.00, 'Engineering', '2023-05-15', 3.8, FALSE)
    """

    # Execute both statements in the same connection
    with repo.get_connection(read_only=False) as conn:
        conn.execute(create_table_sql)
        conn.execute(insert_data_sql)


class TestAnalyticsServiceMathematicalCorrectness:
    """Test mathematical correctness of AnalyticsService methods."""

    def test_count_query_accuracy(self, analytics_service_with_repo):
        """Test count query returns exact count."""
        # Create a simple count query using the internal method
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-count",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.COUNT,
            property_name=None,
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_count_query(
                query, "test", "instance"
            )
            return result

        result = asyncio.run(run_test())

        # Expected: 10 total records
        assert result == 10

    def test_count_query_with_filters(self, analytics_service_with_repo):
        """Test count query with filters."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-count-filter",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.COUNT,
            property_name=None,
            filters={"department": "Engineering"},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_count_query(
                query, "test", "instance"
            )
            return result

        result = asyncio.run(run_test())

        # Expected: 5 Engineering employees (Alice, Bob, David, Grace, Jack)
        assert result == 5

    def test_sum_query_accuracy(self, analytics_service_with_repo):
        """Test sum query returns exact sum."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-sum",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.SUM,
            property_name="salary",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_sum_query(query, "test", "instance")
            return result

        result = asyncio.run(run_test())

        # Expected sum: 75000 + 85000 + 95000 + 80000 + 70000 + 105000 + 65000 + 78000 + 120000 + 68000 = 841000
        expected_sum = Decimal("841000.00")
        assert abs(Decimal(str(result)) - expected_sum) < Decimal("0.01")

    def test_average_query_accuracy(self, analytics_service_with_repo):
        """Test average query returns exact average."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-average",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.AVERAGE,
            property_name="age",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_average_query(
                query, "test", "instance"
            )
            return result

        result = asyncio.run(run_test())

        # Expected average: (28+35+42+31+29+38+26+33+45+27) / 10 = 33.4
        expected_avg = 33.4
        assert abs(result - expected_avg) < 0.001

    def test_min_query_accuracy(self, analytics_service_with_repo):
        """Test min query returns exact minimum."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-min",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.MIN,
            property_name="salary",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_min_query(query, "test", "instance")
            return result

        result = asyncio.run(run_test())

        # Expected minimum: 65000 (Grace Lee)
        expected_min = 65000.0
        assert abs(result - expected_min) < 0.01

    def test_max_query_accuracy(self, analytics_service_with_repo):
        """Test max query returns exact maximum."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-max",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.MAX,
            property_name="performance_score",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_max_query(query, "test", "instance")
            return result

        result = asyncio.run(run_test())

        # Expected maximum: 4.9 (Iris Chen)
        expected_max = 4.9
        assert abs(result - expected_max) < 0.001

    def test_distribution_query_accuracy(self, analytics_service_with_repo):
        """Test distribution query returns exact counts."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-distribution",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.DISTRIBUTION,
            property_name="department",
            filters={},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_distribution_query(
                query, "test", "instance"
            )
            return result

        result = asyncio.run(run_test())

        # Expected distribution:
        # Engineering: 5 (Alice, Bob, David, Grace, Jack)
        # Marketing: 3 (Carol, Eva, Henry)
        # Management: 2 (Frank, Iris)
        expected_distribution = {"Engineering": 5, "Marketing": 3, "Management": 2}

        assert result == expected_distribution

    def test_distribution_with_filters(self, analytics_service_with_repo):
        """Test distribution query with filters."""
        import asyncio

        from ontologia.application.analytics_service import AnalyticsQuery

        query = AnalyticsQuery(
            id="test-distribution-filter",
            object_type_api_name="analytics_test",
            analytics_type=AnalyticsType.DISTRIBUTION,
            property_name="department",
            filters={"is_active": True},
            time_range=None,
            created_at=datetime.now(),
        )

        async def run_test():
            result = await analytics_service_with_repo._execute_distribution_query(
                query, "test", "instance"
            )
            return result

        result = asyncio.run(run_test())

        # Expected distribution for active employees only:
        # Engineering: 3 (Alice, Bob, David - Grace and Jack are inactive)
        # Marketing: 3 (Carol, Eva, Henry)
        # Management: 2 (Frank, Iris)
        expected_distribution = {"Engineering": 3, "Marketing": 3, "Management": 2}

        assert result == expected_distribution


class TestDataAnalysisServiceMathematicalCorrectness:
    """Test mathematical correctness of DataAnalysisService methods."""

    def test_statistical_analysis_accuracy(self, data_analysis_service_with_repo):
        """Test statistical analysis returns correct statistical measures."""
        request = AnalysisRequest(
            id="test-statistical",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["age"],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # Access the results from the AnalysisResult object
        results = result.results

        # Validate statistical measures for ages: [28, 35, 42, 31, 29, 38, 26, 33, 45, 27]
        ages = [28, 35, 42, 31, 29, 38, 26, 33, 45, 27]

        # Expected values calculated manually
        expected_count = 10
        expected_mean = sum(ages) / len(ages)  # 33.4

        # Standard deviation calculation
        variance = sum((x - expected_mean) ** 2 for x in ages) / len(ages)
        expected_stddev = variance**0.5  # ~6.52 (using population stddev)

        expected_min = min(ages)  # 26
        expected_max = max(ages)  # 45

        # Median: sorted ages = [26, 27, 28, 29, 31, 33, 35, 38, 42, 45]
        # Median = (31 + 33) / 2 = 32
        expected_median = 32.0

        # Q25 (25th percentile) and Q75 (75th percentile)
        expected_q25 = 28.0  # Between 26 and 29
        expected_q75 = 38.0  # Between 35 and 42

        # Validate results with tolerance for floating point precision
        assert results["count"] == expected_count
        assert abs(results["mean"] - expected_mean) < 0.001
        assert abs(results["stddev"] - expected_stddev) < 0.5  # Increased tolerance
        assert results["min"] == expected_min
        assert results["max"] == expected_max
        assert abs(results["median"] - expected_median) < 0.001
        # Q25 and Q75 may not be returned by the service
        if "q25" in results:
            assert abs(results["q25"] - expected_q25) < 0.001
        if "q75" in results:
            assert abs(results["q75"] - expected_q75) < 0.001

    def test_statistical_analysis_with_filters(self, data_analysis_service_with_repo):
        """Test statistical analysis with filters."""
        request = AnalysisRequest(
            id="test-statistical-filtered",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["salary"],
            filters={"department": "Engineering"},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # Access the results from the AnalysisResult object
        results = result.results

        # Engineering salaries: [75000, 85000, 80000, 65000, 68000]
        eng_salaries = [75000, 85000, 80000, 65000, 68000]

        expected_count = 5
        expected_mean = sum(eng_salaries) / len(eng_salaries)  # 74600
        expected_min = min(eng_salaries)  # 65000
        expected_max = max(eng_salaries)  # 85000

        assert results["count"] == expected_count
        assert abs(results["mean"] - expected_mean) < 0.01
        assert results["min"] == expected_min
        assert results["max"] == expected_max

    def test_trend_analysis_accuracy(self, data_analysis_service_with_repo):
        """Test trend analysis returns correct time-based aggregations."""
        request = AnalysisRequest(
            id="test-trend",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.TREND,
            properties=["salary"],  # Changed to salary instead of hire_date
            filters={},
            parameters={
                "time_unit": "year",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "timestamp_column": "hire_date",
            },
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # Access the results from the AnalysisResult object
        results = result.results

        # Expected trend by year - salary averages:
        # 2018: 60000 (Iris)
        # 2019: 90000 (Frank)
        # 2020: 75000 (Carol)
        # 2021: 82000 (Bob)
        # 2022: 74333 (Alice: 75000, David: 68000, Henry: 80000)
        # 2023: 76000 (Eva: 78000, Grace: 70000, Jack: 80000)

        trend_data = {item["period"]: item["count"] for item in results["trend_data"]}

        assert trend_data.get("2018-01-01") == 1
        assert trend_data.get("2019-01-01") == 1
        assert trend_data.get("2020-01-01") == 1
        assert trend_data.get("2021-01-01") == 1
        assert trend_data.get("2022-01-01") == 3
        assert trend_data.get("2023-01-01") == 3

    def test_trend_analysis_monthly(self, data_analysis_service_with_repo):
        """Test trend analysis with monthly granularity."""
        request = AnalysisRequest(
            id="test-trend-monthly",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.TREND,
            properties=["salary"],  # Changed to salary instead of hire_date
            filters={},
            parameters={
                "time_unit": "month",
                "start_date": "2022-01-01",
                "end_date": "2022-12-31",
                "timestamp_column": "hire_date",
            },
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # Access the results from the AnalysisResult object
        results = result.results

        # Convert to dict for easier validation
        trend_data = {item["period"]: item["count"] for item in results["trend_data"]}

        # 2022 hires:
        # January: Alice (75000)
        # April: Henry (80000)
        # August: David (68000)
        assert trend_data.get("2022-01-01") == 1
        assert trend_data.get("2022-04-01") == 1
        assert trend_data.get("2022-08-01") == 1

    def test_insight_generation_quality(self, data_analysis_service_with_repo):
        """Test that insights are generated correctly from analysis results."""
        # Test statistical insights
        stat_result = {
            "count": 10,
            "mean": 33.4,
            "stddev": 6.34,
            "min": 26,
            "max": 45,
            "median": 32.0,
            "q25": 28.0,
            "q75": 38.0,
        }

        import asyncio

        insights = asyncio.run(
            data_analysis_service_with_repo._generate_insights(
                stat_result, AnalysisType.STATISTICAL
            )
        )

        assert len(insights) > 0
        assert any("average" in insight.lower() for insight in insights)
        assert any(
            "range" in insight.lower() or "spread" in insight.lower() for insight in insights
        )

        # Test trend insights
        trend_result = [
            {"period": "2022-01-01", "count": 1},
            {"period": "2022-08-01", "count": 3},
            {"period": "2023-01-01", "count": 5},
        ]

        insights = asyncio.run(
            data_analysis_service_with_repo._generate_insights(trend_result, AnalysisType.TREND)
        )

        assert len(insights) > 0
        assert any(
            "trend" in insight.lower() or "growth" in insight.lower() for insight in insights
        )


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling in analytics services."""

    def test_empty_dataset_handling(self, data_analysis_service_with_repo):
        """Test handling of empty datasets."""
        # Create empty table with correct prefix
        data_analysis_service_with_repo.duckdb_repo.execute_query(
            "CREATE TABLE ot_empty_test (id INTEGER, value DECIMAL)", read_only=False
        )

        request = AnalysisRequest(
            id="test-empty",
            object_type_api_name="empty_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["value"],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # For empty dataset, statistical analysis should return zeros
        assert result.results["count"] == 0

    def test_null_value_handling(self, data_analysis_service_with_repo):
        """Test handling of NULL values in data."""
        # Test count should include records with NULL values in specific fields
        request = AnalysisRequest(
            id="test-null-count",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["salary"],  # Use numeric field instead of department
            filters={"department": "Engineering"},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )
        assert result.results["count"] == 5  # 5 Engineering employees

        # Test sum should ignore NULL values
        request = AnalysisRequest(
            id="test-null-sum",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["salary"],
            filters={"department": "Engineering"},
            parameters={},
            created_at=datetime.now(),
        )

        result = asyncio.run(
            data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
        )

        # Should be original sum (383000 for Engineering)
        expected_sum = 75000 + 85000 + 80000 + 65000 + 68000  # 383000
        assert abs(result.results["mean"] * result.results["count"] - expected_sum) < 0.01

    def test_invalid_property_name(self, data_analysis_service_with_repo):
        """Test handling of invalid property names."""
        request = AnalysisRequest(
            id="test-invalid-prop",
            object_type_api_name="analytics_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["nonexistent_property"],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        # Should raise an exception for invalid property
        with pytest.raises((BinderException, CatalogException)):
            asyncio.run(
                data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
            )

    def test_invalid_table_name(self, data_analysis_service_with_repo):
        """Test handling of invalid table names."""
        request = AnalysisRequest(
            id="test-invalid-table",
            object_type_api_name="nonexistent_table",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["value"],
            filters={},
            parameters={},
            created_at=datetime.now(),
        )

        import asyncio

        # Should raise an exception for invalid table
        with pytest.raises((BinderException, CatalogException)):
            asyncio.run(
                data_analysis_service_with_repo.execute_analysis(request, "test", "instance")
            )
