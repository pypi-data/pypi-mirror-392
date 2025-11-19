"""
Performance benchmarking suite for ontologia platform.

These tests measure the performance of critical operations to establish
baseline metrics and prevent performance regressions.
"""

import time
from unittest.mock import Mock

import pytest

from ontologia.application.analytics_service import AnalyticsService
from ontologia.application.data_analysis_service import DataAnalysisService
from ontologia.application.instances_service import InstancesService
from ontologia.application.linked_objects_service import LinkedObjectsService
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository


@pytest.fixture
def benchmark_duckdb_repo():
    """Create DuckDB repository for benchmarking."""
    import os
    import tempfile

    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "benchmark.duckdb")

    repo = DuckDBRepository(duckdb_path=db_path)
    if not repo.is_available():
        pytest.skip("DuckDB not available for benchmarking")
    # Setup benchmark schema
    setup_benchmark_schema(repo)

    yield repo

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_instances_service():
    """Create mock InstancesService for benchmarking."""
    service = Mock(spec=InstancesService)
    return service


@pytest.fixture
def mock_linked_objects_service():
    """Create mock LinkedObjectsService for benchmarking."""
    service = Mock(spec=LinkedObjectsService)
    return service


@pytest.fixture
def benchmark_analytics_service(benchmark_duckdb_repo):
    """Create AnalyticsService for benchmarking."""
    return AnalyticsService(
        instances_service=None,  # type: ignore[arg-type]
        metamodel_service=None,  # type: ignore[arg-type]
        duckdb_repo=benchmark_duckdb_repo,
    )


@pytest.fixture
def benchmark_data_analysis_service(benchmark_duckdb_repo):
    """Create DataAnalysisService for benchmarking."""
    return DataAnalysisService(
        instances_service=None,  # type: ignore[arg-type]
        metamodel_service=None,  # type: ignore[arg-type]
        duckdb_repo=benchmark_duckdb_repo,
    )


def setup_benchmark_schema(repo: DuckDBRepository):
    """Setup schema for performance benchmarking."""

    # Create benchmark tables
    repo.execute_query(
        """
        CREATE TABLE benchmark_objects (
            id INTEGER,
            object_type VARCHAR,
            name VARCHAR,
            value DOUBLE,
            category VARCHAR,
            created_at TIMESTAMP,
            properties VARCHAR
        )
    """,
        read_only=False,
    )

    repo.execute_query(
        """
        CREATE TABLE benchmark_relationships (
            id INTEGER,
            source_id INTEGER,
            target_id INTEGER,
            link_type VARCHAR,
            properties VARCHAR,
            created_at TIMESTAMP
        )
    """,
        read_only=False,
    )

    # Generate test data
    generate_benchmark_data(repo)


def generate_benchmark_data(repo: DuckDBRepository):
    """Generate substantial test data for benchmarking."""

    # Generate 10,000 objects
    objects_data = []
    for i in range(10000):
        objects_data.append(
            (
                i + 1,
                f"object_type_{i % 10}",
                f"Object {i + 1}",
                float(i * 10.5),
                f"category_{i % 5}",
                f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d} 10:00:00",
                f'{{"field1": "value_{i}", "field2": {i * 2.5}, "field3": true}}',
            )
        )

    # Batch insert objects
    repo.execute_query(
        """
        INSERT INTO benchmark_objects VALUES
    """
        + ",".join(["(?, ?, ?, ?, ?, ?, ?)"] * len(objects_data)),
        params={"values": [item for sublist in objects_data for item in sublist]},  # type: ignore[arg-type]
        read_only=False,
    )

    # Generate relationships (average 3 relationships per object)
    relationships_data = []
    rel_id = 1
    for source_id in range(1, 10001):
        # Create 2-4 relationships for each object
        num_relationships = 2 + (source_id % 3)
        for j in range(num_relationships):
            target_id = ((source_id + j * 7) % 10000) + 1  # Distribute relationships
            if target_id != source_id:  # Avoid self-relationships
                relationships_data.append(
                    (
                        rel_id,
                        source_id,
                        target_id,
                        f"link_type_{j % 5}",
                        f'{{"strength": {j * 0.1}, "weight": {j * 2}}}',
                        f"2024-{(j % 12) + 1:02d}-{(j % 28) + 1:02d} 11:00:00",
                    )
                )
                rel_id += 1

    # Batch insert relationships
    repo.execute_query(
        """
        INSERT INTO benchmark_relationships VALUES
    """
        + ",".join(["(?, ?, ?, ?, ?, ?)"] * len(relationships_data)),
        params={"values": [item for sublist in relationships_data for item in sublist]},  # type: ignore[arg-type]
        read_only=False,
    )


class TestObjectCreationPerformance:
    """Benchmark object creation operations."""

    def test_create_single_object_performance(self, benchmark, mock_instances_service):
        """Benchmark creating a single object."""

        def create_object():
            obj = ObjectInstance(
                object_type_api_name="test_object",
                primary_key_value="test_123",
                properties={"name": "Test Object", "value": 42},
            )
            # Simulate object creation
            return obj

        result = benchmark(create_object)
        assert result is not None

    def test_create_batch_objects_performance(self, benchmark):
        """Benchmark creating multiple objects in batch."""

        def create_batch_objects():
            objects = []
            for i in range(1000):
                obj = ObjectInstance(
                    object_type_api_name="batch_object",
                    primary_key_value=f"batch_{i}",
                    properties={"name": f"Batch Object {i}", "value": i},
                )
                objects.append(obj)
            return objects

        result = benchmark(create_batch_objects)
        assert len(result) == 1000

    def test_duckdb_bulk_insert_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark bulk insert operations in DuckDB."""

        def bulk_insert():
            # Create temporary table for bulk insert test
            benchmark_duckdb_repo.execute_query(
                "CREATE TABLE bulk_test (id INTEGER, data VARCHAR)", read_only=False
            )

            # Bulk insert 1000 records
            data = [(i, f"data_{i}") for i in range(1000)]
            # Create parameterized query for bulk insert
            placeholders = ",".join(["(?, ?)"] * len(data))
            benchmark_duckdb_repo.execute_query(
                f"INSERT INTO bulk_test VALUES {placeholders}",  # noqa: S608
                params=[item for sublist in data for item in sublist],
                read_only=False,
            )

            # Count inserted records
            count = benchmark_duckdb_repo.execute_scalar("SELECT COUNT(*) FROM bulk_test")
            return count

        result = benchmark(bulk_insert)
        assert result == 1000


class TestQueryPerformance:
    """Benchmark query operations."""

    def test_simple_select_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark simple SELECT queries."""

        def simple_select():
            return benchmark_duckdb_repo.execute_query(
                "SELECT * FROM benchmark_objects WHERE category = 'category_1' LIMIT 100"
            )

        result = benchmark(simple_select)
        assert len(result) > 0

    def test_complex_join_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark complex JOIN queries."""

        def complex_join():
            return benchmark_duckdb_repo.execute_query(
                """
                SELECT
                    o.id, o.name, o.category,
                    r.target_id, r.link_type
                FROM benchmark_objects o
                LEFT JOIN benchmark_relationships r ON o.id = r.source_id
                WHERE o.category = 'category_1'
                ORDER BY o.id
                LIMIT 1000
            """
            )

        result = benchmark(complex_join)
        assert len(result) > 0

    def test_aggregation_query_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark aggregation queries."""

        def aggregation_query():
            return benchmark_duckdb_repo.execute_query(
                """
                SELECT
                    category,
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MAX(value) as max_value,
                    MIN(value) as min_value
                FROM benchmark_objects
                GROUP BY category
                ORDER BY count DESC
            """
            )

        result = benchmark(aggregation_query)
        assert len(result) == 5  # 5 categories

    def test_json_extraction_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark JSON property extraction."""

        def json_extraction():
            return benchmark_duckdb_repo.execute_query(
                """
                SELECT
                    JSON_EXTRACT_STRING(properties, '$.field1') as field1,
                    JSON_EXTRACT_DOUBLE(properties, '$.field2') as field2,
                    JSON_EXTRACT_BOOL(properties, '$.field3') as field3
                FROM benchmark_objects
                WHERE category = 'category_1'
                LIMIT 1000
            """
            )

        result = benchmark(json_extraction)
        assert len(result) > 0


class TestAnalyticsPerformance:
    """Benchmark analytics operations."""

    def test_count_aggregation_performance(self, benchmark, benchmark_analytics_service):
        """Benchmark count aggregation performance."""
        from ontologia.domain.analytics.models import AggregationType, AnalysisRequest

        request = AnalysisRequest(
            object_type="benchmark_objects", aggregation_type=AggregationType.COUNT, filters=[]
        )

        def count_aggregation():
            return benchmark_analytics_service.execute_aggregation(request)

        result = benchmark(count_aggregation)
        assert result == 10000

    def test_sum_aggregation_performance(self, benchmark, benchmark_analytics_service):
        """Benchmark sum aggregation performance."""
        from ontologia.domain.analytics.models import AggregationType, AnalysisRequest

        request = AnalysisRequest(
            object_type="benchmark_objects",
            aggregation_type=AggregationType.SUM,
            property_name="value",
            filters=[],
        )

        def sum_aggregation():
            return benchmark_analytics_service.execute_aggregation(request)

        result = benchmark(sum_aggregation)
        assert result > 0

    def test_distribution_aggregation_performance(self, benchmark, benchmark_analytics_service):
        """Benchmark distribution aggregation performance."""
        from ontologia.domain.analytics.models import AggregationType, AnalysisRequest

        request = AnalysisRequest(
            object_type="benchmark_objects",
            aggregation_type=AggregationType.DISTRIBUTION,
            property_name="category",
            filters=[],
        )

        def distribution_aggregation():
            return benchmark_analytics_service.execute_aggregation(request)

        result = benchmark(distribution_aggregation)
        assert len(result) == 5  # 5 categories

    def test_statistical_analysis_performance(self, benchmark, benchmark_data_analysis_service):
        """Benchmark statistical analysis performance."""
        from ontologia.domain.analytics.models import AnalysisRequest, AnalysisType

        request = AnalysisRequest(
            object_type="benchmark_objects",
            analysis_type=AnalysisType.STATISTICAL,
            property_name="value",
            filters=[],
        )

        def statistical_analysis():
            return benchmark_data_analysis_service.execute_analysis(request)

        result = benchmark(statistical_analysis)
        assert "count" in result
        assert "mean" in result

    def test_trend_analysis_performance(self, benchmark, benchmark_data_analysis_service):
        """Benchmark trend analysis performance."""
        from ontologia.domain.analytics.models import AnalysisRequest, AnalysisType, TimeRange

        time_range = TimeRange(start_date="2024-01-01", end_date="2024-12-31")

        request = AnalysisRequest(
            object_type="benchmark_objects",
            analysis_type=AnalysisType.TREND,
            property_name="created_at",
            time_unit="month",
            time_range=time_range,
            filters=[],
        )

        def trend_analysis():
            return benchmark_data_analysis_service.execute_analysis(request)

        result = benchmark(trend_analysis)
        assert len(result) > 0


class TestGraphTraversalPerformance:
    """Benchmark graph traversal operations."""

    def test_sql_traversal_performance(self, benchmark, mock_linked_objects_service):
        """Benchmark SQL-based traversal (single-use benchmark call)."""

        def sql_traversal():
            time.sleep(0.001)  # Simulate database query time
            return [{"target_id": i, "depth": 1} for i in range(10)]

        sql_result = benchmark(sql_traversal)
        assert len(sql_result) == 10

    def test_graph_traversal_performance(self, benchmark, mock_linked_objects_service):
        """Benchmark graph-based traversal (single-use benchmark call)."""

        def graph_traversal():
            time.sleep(0.0005)  # Simulate faster graph query time
            return [{"target_id": i, "depth": 1} for i in range(10)]

        graph_result = benchmark(graph_traversal)
        assert len(graph_result) == 10

    def test_relationship_traversal_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark relationship traversal queries."""

        def relationship_traversal():
            return benchmark_duckdb_repo.execute_query(
                """
                WITH RECURSIVE connected_objects AS (
                    -- Base case: start with object 1
                    SELECT source_id, target_id, 1 as depth
                    FROM benchmark_relationships
                    WHERE source_id = 1

                    UNION ALL

                    -- Recursive case: traverse relationships
                    SELECT r.source_id, r.target_id, co.depth + 1
                    FROM benchmark_relationships r
                    JOIN connected_objects co ON r.source_id = co.target_id
                    WHERE co.depth < 3  -- Limit depth to 3 levels
                )
                SELECT * FROM connected_objects
                ORDER BY depth, source_id, target_id
            """
            )

        result = benchmark(relationship_traversal)
        assert len(result) > 0


class TestMemoryUsagePerformance:
    """Benchmark memory usage patterns."""

    def test_large_dataset_memory_usage(self, benchmark, benchmark_duckdb_repo):
        """Benchmark memory usage with large datasets."""

        def large_dataset_query():
            # Query that returns large result set
            return benchmark_duckdb_repo.execute_query(
                """
                SELECT * FROM benchmark_objects
                WHERE category IN ('category_1', 'category_2', 'category_3')
                ORDER BY id
            """
            )

        result = benchmark(large_dataset_query)
        assert len(result) > 0

    def test_streaming_query_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark streaming query performance."""

        def streaming_query():
            # Simulate streaming by processing in chunks
            chunk_size = 1000
            all_results = []

            for offset in range(0, 10000, chunk_size):
                chunk = benchmark_duckdb_repo.execute_query(
                    """
                    SELECT id, name, value FROM benchmark_objects
                    ORDER BY id
                    LIMIT ? OFFSET ?
                """,
                    params=[chunk_size, offset],
                )
                all_results.extend(chunk)

            return len(all_results)

        result = benchmark(streaming_query)
        assert result == 10000


class TestConcurrentOperations:
    """Benchmark concurrent operation performance."""

    def test_concurrent_queries_performance(self, benchmark, benchmark_duckdb_repo):
        """Benchmark performance of concurrent queries."""
        import queue
        import threading

        results = queue.Queue()

        def worker_query():
            result = benchmark_duckdb_repo.execute_query(
                """
                SELECT COUNT(*) FROM benchmark_objects
                WHERE category = ?
            """,
                params=[f"category_{threading.get_ident() % 5}"],
            )
            results.put(result)

        def concurrent_queries():
            threads = []
            for _i in range(10):  # 10 concurrent queries
                thread = threading.Thread(target=worker_query)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Collect results
            all_results = []
            while not results.empty():
                all_results.append(results.get())

            return len(all_results)

        result = benchmark(concurrent_queries)
        assert result == 10


class TestPerformanceRegressionDetection:
    """Tests to detect performance regressions."""

    def test_performance_baseline_establishment(self, benchmark, benchmark_analytics_service):
        """Establish performance baselines for critical operations."""
        from ontologia.domain.analytics.models import AggregationType, AnalysisRequest

        # Baseline for count operation
        count_request = AnalysisRequest(
            object_type="benchmark_objects", aggregation_type=AggregationType.COUNT, filters=[]
        )

        def count_baseline():
            return benchmark_analytics_service.execute_aggregation(count_request)

        count_result = benchmark(count_baseline)

        # Baseline for distribution operation
        dist_request = AnalysisRequest(
            object_type="benchmark_objects",
            aggregation_type=AggregationType.DISTRIBUTION,
            property_name="category",
            filters=[],
        )

        def distribution_baseline():
            return benchmark_analytics_service.execute_aggregation(dist_request)

        dist_result = benchmark(distribution_baseline)

        # These results establish the baseline
        assert count_result == 10000
        assert len(dist_result) == 5

        # In CI/CD, we would compare these against previous benchmarks
        # and fail if performance degrades beyond acceptable thresholds
