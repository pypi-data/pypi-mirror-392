"""
Integration tests for analytics services with real services.

These tests validate that analytics services work correctly
with real DuckDB, Elasticsearch, and Redis instances.
"""

from datetime import datetime

import pytest

from ontologia.application.analytics_service import AnalyticsService
from ontologia.application.data_analysis_service import DataAnalysisService
from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository


class TestAnalyticsIntegration:
    """Test analytics services integration with real infrastructure."""

    def setup_test_data(self, duckdb_repo: DuckDBRepository):
        """Setup test data for analytics integration tests."""
        # Create test table with sample data
        duckdb_repo.execute_query(
            """
            CREATE TABLE IF NOT EXISTS analytics_integration_test (
                id INTEGER,
                name VARCHAR,
                department VARCHAR,
                salary DECIMAL(10,2),
                hire_date DATE,
                performance_score DECIMAL(3,1),
                is_active BOOLEAN,
                sync_timestamp TIMESTAMP
            )
        """,
            read_only=False,
        )

        # Insert test data
        duckdb_repo.execute_query(
            """
            INSERT INTO analytics_integration_test VALUES
            (1, 'Alice Johnson', 'Engineering', 95000.00, '2022-01-15', 4.5, TRUE, '2024-01-01 10:00:00'),
            (2, 'Bob Smith', 'Engineering', 87000.00, '2022-03-20', 4.2, TRUE, '2024-01-01 10:01:00'),
            (3, 'Carol Davis', 'Marketing', 72000.00, '2021-06-10', 3.8, TRUE, '2024-01-01 10:02:00'),
            (4, 'David Wilson', 'Marketing', 68000.00, '2023-02-28', 4.1, TRUE, '2024-01-01 10:03:00'),
            (5, 'Eva Brown', 'Engineering', 105000.00, '2020-09-15', 4.7, TRUE, '2024-01-01 10:04:00'),
            (6, 'Frank Miller', 'Sales', 65000.00, '2023-05-01', 3.5, TRUE, '2024-01-01 10:05:00'),
            (7, 'Grace Lee', 'Sales', 62000.00, '2022-11-20', 3.9, TRUE, '2024-01-01 10:06:00'),
            (8, 'Henry Taylor', 'Engineering', 92000.00, '2021-08-30', 4.3, TRUE, '2024-01-01 10:07:00'),
            (9, 'Iris Chen', 'Marketing', 75000.00, '2023-07-15', 4.0, TRUE, '2024-01-01 10:08:00'),
            (10, 'Jack Martin', 'Sales', 70000.00, '2022-04-10', 3.7, TRUE, '2024-01-01 10:09:00')
        """,
            read_only=False,
        )

    def test_statistical_analysis_integration(self, integration_test_config: dict):
        """Test statistical analysis with real DuckDB."""
        # Setup DuckDB repository
        duckdb_config = integration_test_config["duckdb"]
        duckdb_repo = DuckDBRepository(duckdb_config["path"])

        # Setup test data
        self.setup_test_data(duckdb_repo)

        # Create analytics service
        analytics_service = AnalyticsService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        # Test statistical analysis
        result = analytics_service.execute_aggregation(  # type: ignore[attr-defined]
            table_name="analytics_integration_test", property_name="salary", aggregation_type="avg"
        )

        assert result is not None
        assert isinstance(result, float)
        assert 75000 <= result <= 80000  # Reasonable average salary range

        # Test count aggregation
        count_result = analytics_service.execute_aggregation(  # type: ignore[attr-defined]
            table_name="analytics_integration_test", property_name="id", aggregation_type="count"
        )

        assert count_result == 10

        # Test min/max
        min_salary = analytics_service.execute_aggregation(  # type: ignore[attr-defined]
            table_name="analytics_integration_test", property_name="salary", aggregation_type="min"
        )

        assert min_salary == 62000.00

        max_salary = analytics_service.execute_aggregation(  # type: ignore[attr-defined]
            table_name="analytics_integration_test", property_name="salary", aggregation_type="max"
        )

        assert max_salary == 105000.00

    def test_data_analysis_service_integration(self, integration_test_config: dict):
        """Test data analysis service with real infrastructure."""
        # Setup repositories
        duckdb_config = integration_test_config["duckdb"]
        duckdb_repo = DuckDBRepository(duckdb_config["path"])

        self.setup_test_data(duckdb_repo)

        # Create data analysis service
        data_service = DataAnalysisService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        # Test statistical analysis
        from ontologia.application.data_analysis_service import AnalysisRequest, AnalysisType

        request = AnalysisRequest(
            id="test-statistical",
            object_type_api_name="analytics_integration_test",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["salary"],
            filters={"department": "Engineering"},
            parameters={},
            created_at=datetime.fromisoformat("2024-01-01T00:00:00Z"),  # type: ignore[arg-type]
        )

        import asyncio

        result = asyncio.run(data_service.execute_analysis(request, "test", "instance"))

        assert result is not None
        assert hasattr(result, "results")
        assert "count" in result.results
        assert result.results["count"] == 4  # 4 Engineering employees

        # Test trend analysis
        trend_request = AnalysisRequest(
            id="test-trend",
            object_type_api_name="analytics_integration_test",
            analysis_type=AnalysisType.TREND,
            properties=["salary"],
            filters={},
            parameters={
                "time_unit": "year",
                "timestamp_column": "hire_date",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
            },
            created_at=datetime.fromisoformat("2024-01-01T00:00:00Z"),  # type: ignore[arg-type]
        )

        trend_result = asyncio.run(data_service.execute_analysis(trend_request, "test", "instance"))

        assert trend_result is not None
        assert hasattr(trend_result, "results")
        assert "trend_data" in trend_result.results
        assert len(trend_result.results["trend_data"]) > 0

    def test_cross_service_analytics_workflow(
        self, integration_test_config: dict, redis_client, elasticsearch_client
    ):
        """Test complete analytics workflow across multiple services."""
        # Setup DuckDB with test data
        duckdb_config = integration_test_config["duckdb"]
        duckdb_repo = DuckDBRepository(duckdb_config["path"])
        self.setup_test_data(duckdb_repo)

        # Create services
        analytics_service = AnalyticsService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )
        data_service = DataAnalysisService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        # Create cache repository
        from ontologia.infrastructure.cache_repository import create_redis_cache_repository

        cache_repo = create_redis_cache_repository(integration_test_config["redis"]["url"])

        # Test caching analytics results
        cache_key = cache_repo.build_key("analytics", "avg_salary", "engineering")

        # First call - should compute and cache
        def compute_avg_salary():
            return analytics_service.execute_aggregation(  # type: ignore[attr-defined]
                table_name="analytics_integration_test",
                property_name="salary",
                aggregation_type="avg",
                filters={"department": "Engineering"},
            )

        avg_salary = cache_repo.get_or_set(cache_key, compute_avg_salary, ttl_seconds=300)
        assert avg_salary is not None
        assert 90000 <= avg_salary <= 100000  # Engineering salary range

        # Verify cached
        assert cache_repo.exists(cache_key) is True

        # Second call - should use cache
        cached_salary = cache_repo.get_or_set(cache_key, compute_avg_salary)
        assert cached_salary == avg_salary

        # Test indexing results in Elasticsearch
        from ontologia.infrastructure.elasticsearch_repository import ElasticsearchRepository

        es_repo = ElasticsearchRepository([integration_test_config["elasticsearch"]["hosts"][0]])

        # Create index for analytics results
        mapping = {
            "mappings": {
                "properties": {
                    "analysis_type": {"type": "keyword"},
                    "object_type": {"type": "keyword"},
                    "result_value": {"type": "double"},
                    "filters": {"type": "object"},
                    "computed_at": {"type": "date"},
                }
            }
        }

        es_repo.create_index("analytics_results", mapping)

        # Index analysis result
        result_doc = {
            "analysis_type": "average",
            "object_type": "analytics_integration_test",
            "result_value": avg_salary,
            "filters": {"department": "Engineering"},
            "computed_at": "2024-01-01T00:00:00Z",
        }

        es_repo.index_document("analytics_results", "avg_salary_eng", result_doc)  # type: ignore[attr-defined]

        # Verify indexed
        retrieved = es_repo.get_document("analytics_results", "avg_salary_eng")  # type: ignore[attr-defined]
        assert retrieved["_source"]["result_value"] == avg_salary
        assert retrieved["_source"]["filters"]["department"] == "Engineering"

    def test_performance_with_large_dataset(self, integration_test_config: dict):
        """Test analytics performance with larger dataset."""
        # Setup DuckDB
        duckdb_config = integration_test_config["duckdb"]
        duckdb_repo = DuckDBRepository(duckdb_config["path"])

        # Create larger dataset
        duckdb_repo.execute_query(
            """
            CREATE TABLE IF NOT EXISTS large_analytics_test (
                id INTEGER,
                category VARCHAR,
                value DECIMAL(10,2),
                timestamp TIMESTAMP,
                metadata JSON
            )
        """,
            read_only=False,
        )

        # Generate 10,000 records
        import random
        from datetime import datetime, timedelta

        categories = ["A", "B", "C", "D", "E"]
        base_time = datetime(2024, 1, 1)

        # Use DuckDB's efficient bulk insert
        values = []
        for i in range(10000):
            values.append(
                f"({i+1}, '{random.choice(categories)}', {random.uniform(100, 1000):.2f}, "
                f"'{(base_time + timedelta(hours=i)).isoformat()}', "
                f'\'{{"source": "test", "batch": {i//1000}}}\')'
            )

        duckdb_repo.execute_query(
            f"INSERT INTO large_analytics_test VALUES {','.join(values)}", read_only=False
        )

        # Create analytics service
        analytics_service = AnalyticsService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        # Test performance of aggregations
        import time

        start_time = time.time()
        avg_by_category = {}

        for category in categories:
            avg_value = analytics_service.execute_aggregation(  # type: ignore[attr-defined]
                table_name="large_analytics_test",
                property_name="value",
                aggregation_type="avg",
                filters={"category": category},
            )
            avg_by_category[category] = avg_value

        elapsed_time = time.time() - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 5.0  # 5 seconds max for 10k records
        assert len(avg_by_category) == 5
        assert all(100 <= val <= 1000 for val in avg_by_category.values())

        # Test trend analysis performance
        data_service = DataAnalysisService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        from ontologia.application.data_analysis_service import AnalysisRequest, AnalysisType

        trend_request = AnalysisRequest(
            id="performance-trend",
            object_type_api_name="large_analytics_test",
            analysis_type=AnalysisType.TREND,
            properties=["value"],
            filters={"category": "A"},
            parameters={
                "time_unit": "day",
                "timestamp_column": "timestamp",
                "start_date": "2024-01-01",
                "end_date": "2024-02-01",
            },
            created_at=datetime.fromisoformat("2024-01-01T00:00:00Z"),  # type: ignore[arg-type]
        )

        start_time = time.time()
        import asyncio

        trend_result = asyncio.run(data_service.execute_analysis(trend_request, "test", "instance"))
        trend_elapsed = time.time() - start_time

        assert trend_elapsed < 10.0  # 10 seconds max for trend analysis
        assert trend_result is not None
        assert hasattr(trend_result, "results")
        assert "trend_data" in trend_result.results

    def test_error_handling_and_recovery(self, integration_test_config: dict):
        """Test error handling and recovery in analytics services."""
        duckdb_config = integration_test_config["duckdb"]
        duckdb_repo = DuckDBRepository(duckdb_config["path"])

        analytics_service = AnalyticsService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )
        data_service = DataAnalysisService(
            instances_service=None,  # type: ignore[arg-type]
            metamodel_service=None,  # type: ignore[arg-type]
            duckdb_repo=duckdb_repo,
        )

        # Test invalid table name
        with pytest.raises(ValueError):
            analytics_service.execute_aggregation(  # type: ignore[attr-defined]
                table_name="nonexistent_table", property_name="value", aggregation_type="avg"
            )

        # Test invalid property name
        self.setup_test_data(duckdb_repo)

        with pytest.raises(ValueError):
            analytics_service.execute_aggregation(  # type: ignore[attr-defined]
                table_name="analytics_integration_test",
                property_name="nonexistent_property",
                aggregation_type="avg",
            )

        # Test invalid aggregation type
        with pytest.raises(ValueError):
            analytics_service.execute_aggregation(  # type: ignore[attr-defined]
                table_name="analytics_integration_test",
                property_name="salary",
                aggregation_type="invalid_aggregation",
            )

        # Test data analysis service error handling
        from ontologia.application.data_analysis_service import AnalysisRequest, AnalysisType

        invalid_request = AnalysisRequest(
            id="invalid-request",
            object_type_api_name="nonexistent_table",
            analysis_type=AnalysisType.STATISTICAL,
            properties=["invalid_property"],
            filters={},
            parameters={},
            created_at=datetime.fromisoformat("2024-01-01T00:00:00Z"),  # type: ignore[arg-type]
        )

        import asyncio

        with pytest.raises(ValueError):
            asyncio.run(data_service.execute_analysis(invalid_request, "test", "instance"))
