"""
data_analysis_service.py
-------------------------
Service for data analysis operations in the ontology system.

Provides functionality for analyzing ontology data, generating insights,
and performing statistical analysis on object instances and relationships.
"""

# ruff: noqa: S608  # SQL injection warnings - table names are controlled by application

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Type of data analysis operations."""

    STATISTICAL = "statistical"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    TREND = "trend"


@dataclass
class AnalysisRequest:
    """Represents a data analysis request."""

    id: str
    object_type_api_name: str
    analysis_type: AnalysisType
    properties: list[str]
    filters: dict[str, Any]
    parameters: dict[str, Any]
    created_at: datetime


@dataclass
class AnalysisResult:
    """Represents the result of a data analysis operation."""

    request_id: str
    analysis_type: AnalysisType
    results: dict[str, Any]
    insights: list[str]
    metadata: dict[str, Any]
    computed_at: datetime
    execution_time_ms: float


class DataAnalysisService:
    """
    Service for data analysis and insights generation.

    Handles various types of data analysis including statistical analysis,
    pattern detection, anomaly detection, and trend analysis.
    """

    def __init__(
        self, instances_service, metamodel_service, duckdb_repo: DuckDBRepository | None = None
    ):
        """
        Initialize data analysis service.

        Args:
            instances_service: Service for instance operations
            metamodel_service: Service for metamodel operations
            duckdb_repo: DuckDB repository for analytics queries
        """
        self.instances_service = instances_service
        self.metamodel_service = metamodel_service
        self.duckdb_repo = duckdb_repo or DuckDBRepository()
        self.logger = logging.getLogger(__name__)

    async def execute_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> AnalysisResult:
        """
        Execute a data analysis request.

        Args:
            request: Analysis request to execute
            service: Service name
            instance: Instance name

        Returns:
            Analysis result with insights and metadata
        """
        start_time = datetime.now()

        self.logger.info(f"Executing analysis: {request.id}")

        try:
            if request.analysis_type == AnalysisType.STATISTICAL:
                results = await self._execute_statistical_analysis(request, service, instance)
            elif request.analysis_type == AnalysisType.DISTRIBUTION:
                results = await self._execute_distribution_analysis(request, service, instance)
            elif request.analysis_type == AnalysisType.CORRELATION:
                results = await self._execute_correlation_analysis(request, service, instance)
            elif request.analysis_type == AnalysisType.PATTERN:
                results = await self._execute_pattern_analysis(request, service, instance)
            elif request.analysis_type == AnalysisType.ANOMALY:
                results = await self._execute_anomaly_analysis(request, service, instance)
            elif request.analysis_type == AnalysisType.TREND:
                results = await self._execute_trend_analysis(request, service, instance)
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            insights = await self._generate_insights(results, request.analysis_type)

            return AnalysisResult(
                request_id=request.id,
                analysis_type=request.analysis_type,
                results=results,
                insights=insights,
                metadata={
                    "object_type": request.object_type_api_name,
                    "properties": request.properties,
                    "filters": request.filters,
                },
                computed_at=datetime.now(),
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise

    async def get_object_type_summary(
        self,
        object_type_api_name: str,
        service: str,
        instance: str,
        *,
        include_properties: bool = True,
        sample_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Get a comprehensive summary of an object type.

        Args:
            object_type_api_name: API name of the object type
            service: Service name
            instance: Instance name
            include_properties: Whether to include property analysis
            sample_size: Optional sample size for analysis

        Returns:
            Summary with statistics and insights
        """
        self.logger.info(f"Getting summary for object type: {object_type_api_name}")

        try:
            if not self.duckdb_repo.is_available():
                raise RuntimeError("DuckDB is not available for analysis")

            # Build table name based on object type
            table_name = f"ot_{object_type_api_name}"

            # Get basic counts and date ranges
            basic_stats_sql = f"""
                SELECT
                    COUNT(*) as total_instances,
                    MIN(valid_from) as min_created_date,
                    MAX(valid_from) as max_created_date,
                    MIN(transaction_to) as min_updated_date,
                    MAX(transaction_to) as max_updated_date,
                    COUNT(CASE WHEN valid_from >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as created_last_30_days
                FROM {table_name}
            """

            basic_stats = self.duckdb_repo.execute_query(basic_stats_sql, {}, read_only=False)

            if not basic_stats:
                return {
                    "object_type": object_type_api_name,
                    "total_instances": 0,
                    "created_date_range": None,
                    "updated_date_range": None,
                    "property_summary": {} if include_properties else None,
                    "relationship_summary": {},
                    "data_quality_score": 0.0,
                }

            row = basic_stats[0]
            total_instances = int(row[0]) if row[0] is not None else 0
            min_created = str(row[1]) if row[1] is not None else None
            max_created = str(row[2]) if row[2] is not None else None
            min_updated = str(row[3]) if row[3] is not None else None
            max_updated = str(row[4]) if row[4] is not None else None
            created_last_30 = int(row[5]) if row[5] is not None else 0

            # Calculate data quality score based on completeness and recency
            data_quality_score = 0.0
            if total_instances > 0:
                completeness_score = 0.8  # Base score for having data
                recency_score = min(
                    created_last_30 / total_instances * 0.2, 0.2
                )  # Recent activity bonus
                data_quality_score = completeness_score + recency_score

            property_summary = {}
            if include_properties:
                # Get property statistics (simplified - would need schema introspection)
                property_stats_sql = f"""
                    SELECT
                        COUNT(*) as non_null_count,
                        COUNT(DISTINCT {table_name}.id) as distinct_instances
                    FROM {table_name}
                    WHERE 1=1  -- Placeholder for actual property analysis
                """

                try:
                    prop_stats = self.duckdb_repo.execute_query(
                        property_stats_sql, {}, read_only=False
                    )
                    if prop_stats:
                        property_summary = {
                            "analyzed_properties": 0,
                            "avg_completeness": 0.0,
                            "most_common_values": {},
                        }
                except Exception as e:
                    self.logger.warning(f"Property analysis failed: {e}")
                    property_summary = {}

            # Get relationship summary (simplified)
            relationship_summary = {
                "total_relationships": 0,
                "relationship_types": [],
                "avg_connections_per_instance": 0.0,
            }

            return {
                "object_type": object_type_api_name,
                "total_instances": total_instances,
                "created_date_range": (
                    {"start": min_created, "end": max_created}
                    if min_created and max_created
                    else None
                ),
                "updated_date_range": (
                    {"start": min_updated, "end": max_updated}
                    if min_updated and max_updated
                    else None
                ),
                "property_summary": property_summary if include_properties else None,
                "relationship_summary": relationship_summary,
                "data_quality_score": data_quality_score,
                "recent_activity": {
                    "created_last_30_days": created_last_30,
                    "creation_rate": created_last_30 / 30.0 if created_last_30 > 0 else 0.0,
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get object type summary: {e}")
            # Return default values on error
            return {
                "object_type": object_type_api_name,
                "total_instances": 0,
                "created_date_range": None,
                "updated_date_range": None,
                "property_summary": {} if include_properties else None,
                "relationship_summary": {},
                "data_quality_score": 0.0,
            }

    async def detect_anomalies(
        self,
        object_type_api_name: str,
        properties: list[str],
        service: str,
        instance: str,
        *,
        method: str = "statistical",
        threshold: float = 2.0,
    ) -> list[dict[str, Any]]:
        """
        Detect anomalies in object instance data.

        Args:
            object_type_api_name: API name of the object type
            properties: Properties to analyze for anomalies
            service: Service name
            instance: Instance name
            method: Anomaly detection method
            threshold: Threshold for anomaly detection

        Returns:
            List of detected anomalies
        """
        self.logger.info(f"Detecting anomalies for {object_type_api_name}")

        try:
            # Create analysis request
            request = AnalysisRequest(
                id=f"anomaly_detection_{object_type_api_name}",
                object_type_api_name=object_type_api_name,
                analysis_type=AnalysisType.ANOMALY,
                properties=properties,
                filters={},
                parameters={"method": method, "threshold": threshold},
                created_at=datetime.now(),
            )

            # Execute analysis
            result = await self.execute_analysis(request, service, instance)

            # Extract anomalies from results
            anomalies = result.results.get("anomalies", [])

            # Add metadata to each anomaly
            for anomaly in anomalies:
                anomaly["object_type"] = object_type_api_name
                anomaly["detection_method"] = method
                anomaly["threshold"] = threshold
                anomaly["detected_at"] = datetime.now().isoformat()

            return anomalies

        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []

    async def generate_insights_report(
        self,
        object_types: list[str],
        analysis_types: list[AnalysisType],
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """
        Generate a comprehensive insights report.

        Args:
            object_types: List of object types to analyze
            analysis_types: Types of analysis to perform
            service: Service name
            instance: Instance name

        Returns:
            Comprehensive insights report
        """
        self.logger.info("Generating insights report")

        try:
            # Initialize report structure with explicit typing to satisfy type checkers
            report_data: dict[str, Any] = {
                "summary": {"total_objects": 0, "total_analyses": 0},
                "cross_object_insights": [],
                "recommendations": [],
            }
            # Use plain assignments to avoid inline type comments that some tooling misinterprets
            report_data["object_summaries"] = {}  # dict[str, dict[str, Any]]
            report_data["analysis_results"] = {}  # dict[str, dict[str, Any]]

            # Generate summaries for each object type
            for object_type in object_types:
                summary = await self.get_object_type_summary(object_type, service, instance)
                report_data["object_summaries"][object_type] = summary  # type: ignore[assignment]

            # Perform requested analyses
            for object_type in object_types:
                for analysis_type in analysis_types:
                    # Create analysis request with default properties
                    request = AnalysisRequest(
                        id=f"report_{object_type}_{analysis_type.value}",
                        object_type_api_name=object_type,
                        analysis_type=analysis_type,
                        properties=["id"],  # Default property
                        filters={},
                        parameters={},
                        created_at=datetime.now(),
                    )

                    try:
                        result = await self.execute_analysis(request, service, instance)

                        key = f"{object_type}_{analysis_type.value}"
                        report_data["analysis_results"][key] = {  # type: ignore[assignment]
                            "results": result.results,
                            "insights": result.insights,
                            "execution_time_ms": result.execution_time_ms,
                        }
                    except Exception as e:
                        self.logger.warning(
                            f"Analysis failed for {object_type}/{analysis_type.value}: {e}"
                        )
                        report_data["analysis_results"][f"{object_type}_{analysis_type.value}"] = {  # type: ignore[assignment]
                            "error": str(e)
                        }

            # Generate cross-object insights
            total_instances = sum(
                summary.get("total_instances", 0)
                for summary in report_data["object_summaries"].values()
            )

            if total_instances > 0:
                report_data["cross_object_insights"].append(
                    f"Total of {total_instances:,} instances across {len(object_types)} object types"
                )

            # Generate recommendations based on data quality scores
            low_quality_objects = [
                obj_type
                for obj_type, summary in report_data["object_summaries"].items()
                if summary.get("data_quality_score", 0) < 0.5
            ]

            if low_quality_objects:
                report_data["recommendations"].append(
                    f"Consider data quality improvements for: {', '.join(low_quality_objects)}"
                )

            return report_data

        except Exception as e:
            self.logger.error(f"Insights report generation failed: {e}")
            raise

    async def _execute_statistical_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute statistical analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if not request.properties:
            raise ValueError("Properties list is required for statistical analysis")

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build statistical analysis query for the first property
        property_name = request.properties[0]
        sql = f"""
            SELECT
                COUNT(*) as count,
                AVG({property_name}) as mean,
                STDDEV({property_name}) as stddev,
                MIN({property_name}) as min_val,
                MAX({property_name}) as max_val,
                MEDIAN({property_name}) as median,
                QUANTILE({property_name}, 0.25) as q1,
                QUANTILE({property_name}, 0.75) as q3
            FROM {table_name}{where_clause}
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            if not rows:
                return {"error": "No data found for analysis"}

            row = rows[0]
            if isinstance(row, (list, tuple)):
                return {
                    "count": int(row[0]) if row[0] is not None else 0,
                    "mean": float(row[1]) if row[1] is not None else 0.0,
                    "stddev": float(row[2]) if row[2] is not None else 0.0,
                    "min": float(row[3]) if row[3] is not None else 0.0,
                    "max": float(row[4]) if row[4] is not None else 0.0,
                    "median": float(row[5]) if row[5] is not None else 0.0,
                    "q1": float(row[6]) if row[6] is not None else 0.0,
                    "q3": float(row[7]) if row[7] is not None else 0.0,
                }
            else:
                return {"error": "Unexpected result format"}

        except Exception as e:
            self.logger.error(f"Statistical analysis failed: {e}")
            raise

    async def _execute_distribution_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute distribution analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if not request.properties:
            raise ValueError("Properties list is required for distribution analysis")

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Analyze distribution for the first property
        property_name = request.properties[0]

        # Get frequency distribution
        sql = f"""
            SELECT
                {property_name} as value,
                COUNT(*) as frequency,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
            FROM {table_name}{where_clause}
            GROUP BY {property_name}
            ORDER BY frequency DESC
            LIMIT 100
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            distribution = []
            total_count = 0

            for row in rows:
                if isinstance(row, (list, tuple)) and len(row) >= 3:
                    value = str(row[0]) if row[0] is not None else "NULL"
                    frequency = int(row[1]) if row[1] is not None else 0
                    percentage = float(row[2]) if row[2] is not None else 0.0

                    distribution.append(
                        {"value": value, "frequency": frequency, "percentage": percentage}
                    )
                    total_count += frequency

            # Calculate distribution statistics
            distinct_values = len(distribution)
            most_common = distribution[0] if distribution else None

            return {
                "distribution": distribution,
                "total_count": total_count,
                "distinct_values": distinct_values,
                "most_common": most_common,
                "property": property_name,
            }

        except Exception as e:
            self.logger.error(f"Distribution analysis failed: {e}")
            raise

    async def _execute_correlation_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute correlation analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if len(request.properties) < 2:
            raise ValueError("At least 2 properties required for correlation analysis")

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Analyze correlations between first two properties
        prop1, prop2 = request.properties[0], request.properties[1]

        sql = f"""
            SELECT
                CORR({prop1}, {prop2}) as correlation,
                COUNT(*) as sample_size,
                AVG({prop1}) as avg_prop1,
                AVG({prop2}) as avg_prop2,
                STDDEV({prop1}) as stddev_prop1,
                STDDEV({prop2}) as stddev_prop2
            FROM {table_name}{where_clause}
            WHERE {prop1} IS NOT NULL AND {prop2} IS NOT NULL
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            if not rows:
                return {"error": "No valid data found for correlation analysis"}

            row = rows[0]
            if isinstance(row, (list, tuple)) and len(row) >= 6:
                correlation = float(row[0]) if row[0] is not None else 0.0
                sample_size = int(row[1]) if row[1] is not None else 0
                avg_prop1 = float(row[2]) if row[2] is not None else 0.0
                avg_prop2 = float(row[3]) if row[3] is not None else 0.0
                stddev_prop1 = float(row[4]) if row[4] is not None else 0.0
                stddev_prop2 = float(row[5]) if row[5] is not None else 0.0

                # Interpret correlation strength
                strength = "none"
                if abs(correlation) >= 0.8:
                    strength = "strong"
                elif abs(correlation) >= 0.5:
                    strength = "moderate"
                elif abs(correlation) >= 0.3:
                    strength = "weak"

                return {
                    "correlation": correlation,
                    "strength": strength,
                    "sample_size": sample_size,
                    "property1": prop1,
                    "property2": prop2,
                    "property1_stats": {"mean": avg_prop1, "stddev": stddev_prop1},
                    "property2_stats": {"mean": avg_prop2, "stddev": stddev_prop2},
                }
            else:
                return {"error": "Unexpected result format"}

        except Exception as e:
            self.logger.error(f"Correlation analysis failed: {e}")
            raise

    async def _execute_pattern_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute pattern analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if not request.properties:
            raise ValueError("Properties list is required for pattern analysis")

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Analyze patterns for the first property
        property_name = request.properties[0]

        # Look for frequency patterns and sequences
        sql = f"""
            WITH ranked_data AS (
                SELECT
                    {property_name} as value,
                    COUNT(*) as frequency,
                    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as rank
                FROM {table_name}{where_clause}
                WHERE {property_name} IS NOT NULL
                GROUP BY {property_name}
            ),
            pattern_stats AS (
                SELECT
                    COUNT(*) as distinct_values,
                    SUM(frequency) as total_count,
                    MAX(frequency) as max_frequency,
                    MIN(frequency) as min_frequency,
                    AVG(frequency) as avg_frequency
                FROM ranked_data
            )
            SELECT
                rd.value,
                rd.frequency,
                rd.rank,
                ps.distinct_values,
                ps.total_count,
                ps.max_frequency,
                ps.min_frequency,
                ps.avg_frequency,
                (rd.frequency * 1.0 / ps.avg_frequency) as frequency_ratio
            FROM ranked_data rd, pattern_stats ps
            ORDER BY rd.frequency DESC
            LIMIT 50
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            patterns = []
            stats = {}

            for row in rows:
                if isinstance(row, (list, tuple)) and len(row) >= 9:
                    value = str(row[0]) if row[0] is not None else "NULL"
                    frequency = int(row[1]) if row[1] is not None else 0
                    rank = int(row[2]) if row[2] is not None else 0

                    if not stats:  # Initialize stats from first row
                        stats = {
                            "distinct_values": int(row[3]) if row[3] is not None else 0,
                            "total_count": int(row[4]) if row[4] is not None else 0,
                            "max_frequency": int(row[5]) if row[5] is not None else 0,
                            "min_frequency": int(row[6]) if row[6] is not None else 0,
                            "avg_frequency": float(row[7]) if row[7] is not None else 0.0,
                        }

                    frequency_ratio = float(row[8]) if row[8] is not None else 0.0

                    patterns.append(
                        {
                            "value": value,
                            "frequency": frequency,
                            "rank": rank,
                            "frequency_ratio": frequency_ratio,
                        }
                    )

            # Identify pattern types
            pattern_types = []
            if stats.get("max_frequency", 0) > stats.get("avg_frequency", 0) * 3:
                pattern_types.append("highly_concentrated")
            elif stats.get("max_frequency", 0) > stats.get("avg_frequency", 0) * 1.5:
                pattern_types.append("moderately_concentrated")
            else:
                pattern_types.append("well_distributed")

            return {
                "patterns": patterns,
                "statistics": stats,
                "pattern_types": pattern_types,
                "property": property_name,
            }

        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            raise

    async def _execute_anomaly_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute anomaly analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if not request.properties:
            raise ValueError("Properties list is required for anomaly analysis")

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Get anomaly detection parameters
        method = request.parameters.get("method", "statistical")
        threshold = request.parameters.get("threshold", 2.0)
        property_name = request.properties[0]

        if method == "statistical":
            # Statistical anomaly detection using z-score
            sql = f"""
                WITH stats AS (
                    SELECT
                        AVG({property_name}) as mean,
                        STDDEV({property_name}) as stddev,
                        COUNT(*) as total_count
                    FROM {table_name}{where_clause}
                    WHERE {property_name} IS NOT NULL
                ),
                anomalies AS (
                    SELECT
                        {property_name} as value,
                        ({property_name} - s.mean) / NULLIF(s.stddev, 0) as z_score,
                        ABS(({property_name} - s.mean) / NULLIF(s.stddev, 0)) as abs_z_score
                    FROM {table_name}, stats s
                    {where_clause}
                    WHERE {property_name} IS NOT NULL
                    AND ABS(({property_name} - s.mean) / NULLIF(s.stddev, 0)) > ?
                )
                SELECT
                    a.value,
                    a.z_score,
                    a.abs_z_score,
                    s.mean,
                    s.stddev,
                    s.total_count
                FROM anomalies a, stats s
                ORDER BY a.abs_z_score DESC
                LIMIT 100
            """

            params["threshold"] = threshold

        elif method == "iqr":
            # Interquartile Range method
            sql = f"""
                WITH quartiles AS (
                    SELECT
                        QUANTILE({property_name}, 0.25) as q1,
                        QUANTILE({property_name}, 0.75) as q3,
                        COUNT(*) as total_count
                    FROM {table_name}{where_clause}
                    WHERE {property_name} IS NOT NULL
                ),
                bounds AS (
                    SELECT
                        q.q1,
                        q.q3,
                        q.q3 - q.q1 as iqr,
                        q.q1 - 1.5 * (q.q3 - q.q1) as lower_bound,
                        q.q3 + 1.5 * (q.q3 - q.q1) as upper_bound,
                        q.total_count
                    FROM quartiles q
                )
                SELECT
                    {property_name} as value,
                    ({property_name} - b.lower_bound) / NULLIF(b.iqr, 0) as lower_distance,
                    ({property_name} - b.upper_bound) / NULLIF(b.iqr, 0) as upper_distance,
                    b.lower_bound,
                    b.upper_bound,
                    b.iqr,
                    b.total_count
                FROM {table_name}, bounds b
                {where_clause}
                WHERE {property_name} IS NOT NULL
                AND ({property_name} < b.lower_bound OR {property_name} > b.upper_bound)
                ORDER BY
                    CASE
                        WHEN {property_name} < b.lower_bound THEN (b.lower_bound - {property_name}) / NULLIF(b.iqr, 0)
                        ELSE ({property_name} - b.upper_bound) / NULLIF(b.iqr, 0)
                    END DESC
                LIMIT 100
            """
        else:
            raise ValueError(f"Unsupported anomaly detection method: {method}")

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            anomalies = []
            stats = {}

            for row in rows:
                if isinstance(row, (list, tuple)):
                    if method == "statistical" and len(row) >= 6:
                        value = float(row[0]) if row[0] is not None else 0.0
                        z_score = float(row[1]) if row[1] is not None else 0.0
                        abs_z_score = float(row[2]) if row[2] is not None else 0.0

                        if not stats:  # Initialize stats from first row
                            stats = {
                                "mean": float(row[3]) if row[3] is not None else 0.0,
                                "stddev": float(row[4]) if row[4] is not None else 0.0,
                                "total_count": int(row[5]) if row[5] is not None else 0,
                            }

                        anomalies.append(
                            {
                                "value": value,
                                "z_score": z_score,
                                "abs_z_score": abs_z_score,
                                "anomaly_type": "statistical",
                            }
                        )

                    elif method == "iqr" and len(row) >= 7:
                        value = float(row[0]) if row[0] is not None else 0.0
                        lower_distance = float(row[1]) if row[1] is not None else 0.0
                        upper_distance = float(row[2]) if row[2] is not None else 0.0

                        if not stats:  # Initialize stats from first row
                            stats = {
                                "lower_bound": float(row[3]) if row[3] is not None else 0.0,
                                "upper_bound": float(row[4]) if row[4] is not None else 0.0,
                                "iqr": float(row[5]) if row[5] is not None else 0.0,
                                "total_count": int(row[6]) if row[6] is not None else 0,
                            }

                        anomaly_type = "lower_outlier" if lower_distance > 0 else "upper_outlier"
                        distance = (
                            abs(lower_distance) if lower_distance > 0 else abs(upper_distance)
                        )

                        anomalies.append(
                            {"value": value, "distance": distance, "anomaly_type": anomaly_type}
                        )

            return {
                "anomalies": anomalies,
                "statistics": stats,
                "method": method,
                "threshold": threshold,
                "property": property_name,
                "anomaly_count": len(anomalies),
            }

        except Exception as e:
            self.logger.error(f"Anomaly analysis failed: {e}")
            raise

    async def _execute_trend_analysis(
        self,
        request: AnalysisRequest,
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """Execute trend analysis."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analysis")

        if not request.properties:
            raise ValueError("Properties list is required for trend analysis")

        # Check for timestamp column in parameters
        timestamp_col = request.parameters.get("timestamp_column", "sync_timestamp")
        property_name = request.properties[0]

        # Build table name based on object type
        table_name = f"ot_{request.object_type_api_name}"

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build trend analysis query with DATE_TRUNC
        time_unit = request.parameters.get("time_unit", "day")
        sql = f"""
            SELECT
                DATE_TRUNC('{time_unit}', {timestamp_col}) as period,
                AVG({property_name}) as avg_value,
                COUNT(*) as count
            FROM {table_name}{where_clause}
            GROUP BY DATE_TRUNC('{time_unit}', {timestamp_col})
            ORDER BY period
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            trend_data = []
            for row in rows:
                if isinstance(row, (list, tuple)) and len(row) >= 3:
                    trend_data.append(
                        {
                            "period": str(row[0]),
                            "value": float(row[1]) if row[1] is not None else 0.0,
                            "count": int(row[2]) if row[2] is not None else 0,
                        }
                    )

            return {
                "trend_data": trend_data,
                "time_unit": time_unit,
                "property": property_name,
                "periods_analyzed": len(trend_data),
            }

        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            raise

    async def _generate_insights(
        self,
        results: dict[str, Any],
        analysis_type: AnalysisType,
    ) -> list[str]:
        """Generate insights from analysis results."""
        insights = []

        # Handle error cases
        if not results or "error" in results:
            return [
                "Analysis error: Unable to generate insights due to errors in the analysis result"
            ]

        try:
            if analysis_type == AnalysisType.STATISTICAL:
                insights = self._generate_statistical_insights(results)
            elif analysis_type == AnalysisType.DISTRIBUTION:
                insights = self._generate_distribution_insights(results)
            elif analysis_type == AnalysisType.TREND:
                insights = self._generate_trend_insights(results)
            else:
                insights = [
                    f"Analysis completed using {analysis_type.value} method",
                    "Review detailed results for specific insights",
                ]
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            insights = ["Unable to generate insights due to analysis error"]

        return insights

    def _generate_statistical_insights(self, results: dict[str, Any]) -> list[str]:
        """Generate insights from statistical analysis results."""
        insights = []

        if "count" in results:
            count = results["count"]
            insights.append(f"Dataset contains {count:,} records")

        if "mean" in results and "stddev" in results:
            mean = results["mean"]
            stddev = results["stddev"]
            cv = (stddev / mean * 100) if mean != 0 else 0

            insights.append(f"Average value is {mean:.2f} with standard deviation of {stddev:.2f}")

            if cv < 15:
                insights.append("Data shows low variability (CV < 15%)")
            elif cv < 30:
                insights.append("Data shows moderate variability (CV 15-30%)")
            else:
                insights.append("Data shows high variability (CV > 30%)")

        if "median" in results and "mean" in results:
            median = results["median"]
            mean = results["mean"]
            skew_indicator = (mean - median) / median if median != 0 else 0

            if abs(skew_indicator) < 0.1:
                insights.append("Distribution appears approximately symmetric")
            elif skew_indicator > 0.1:
                insights.append("Distribution shows right skew (mean > median)")
            else:
                insights.append("Distribution shows left skew (mean < median)")

        if "min" in results and "max" in results:
            range_val = results["max"] - results["min"]
            insights.append(f"Value range spans {range_val:.2f} units")

        return insights

    def _generate_distribution_insights(self, results: dict[str, Any]) -> list[str]:
        """Generate insights from distribution analysis results."""
        insights = []

        if isinstance(results, dict):
            total_count = sum(results.values())
            insights.append(f"Distribution covers {len(results)} distinct values")

            if total_count > 0:
                # Find most common value
                most_common = max(results.items(), key=lambda x: x[1])
                percentage = (most_common[1] / total_count) * 100
                insights.append(
                    f"Most common value '{most_common[0]}' represents {percentage:.1f}% of data"
                )

                # Check for concentration
                if percentage > 50:
                    insights.append("Data is highly concentrated around single value")
                elif percentage > 25:
                    insights.append("Data shows moderate concentration")
                else:
                    insights.append("Data is well distributed across values")

        return insights

    def _generate_trend_insights(self, results: dict[str, Any]) -> list[str]:
        """Generate insights from trend analysis results."""
        insights = []

        if isinstance(results, list) and len(results) > 1:
            insights.append(f"Trend analysis covers {len(results)} time periods")

            # Simple trend detection
            values = [item.get("value", 0) for item in results if isinstance(item, dict)]
            if len(values) >= 2:
                first_val = values[0]
                last_val = values[-1]
                change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

                if change_pct > 5:
                    insights.append(f"Upward trend detected (+{change_pct:.1f}% change)")
                elif change_pct < -5:
                    insights.append(f"Downward trend detected ({change_pct:.1f}% change)")
                else:
                    insights.append("Trend appears stable (minimal change)")

        return insights
