"""
analytics_service.py
---------------------
Service for analytics operations in the ontology system.

Provides functionality for data analysis, metrics collection,
and analytics reporting within the ontology framework.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository

logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    """Type of analytics operations."""

    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    DISTRIBUTION = "distribution"
    TREND = "trend"


@dataclass
class AnalyticsQuery:
    """Represents an analytics query."""

    id: str
    object_type_api_name: str
    analytics_type: AnalyticsType
    property_name: str | None
    filters: dict[str, Any]
    time_range: tuple[datetime, datetime] | None
    created_at: datetime


@dataclass
class AnalyticsResult:
    """Represents an analytics result."""

    query_id: str
    result: Any
    metadata: dict[str, Any]
    computed_at: datetime
    execution_time_ms: float


class AnalyticsService:
    """
    Service for analytics operations and data analysis.

    Handles various analytics operations including aggregations,
    trend analysis, distribution analysis, and custom metrics.
    """

    def __init__(
        self, instances_service, metamodel_service, duckdb_repo: DuckDBRepository | None = None
    ):
        """
        Initialize analytics service.

        Args:
            instances_service: Service for instance operations
            metamodel_service: Service for metamodel operations
            duckdb_repo: DuckDB repository for analytics queries
        """
        self.instances_service = instances_service
        self.metamodel_service = metamodel_service
        self.duckdb_repo = duckdb_repo or DuckDBRepository()
        self.logger = logging.getLogger(__name__)

    # --- Internal identifier safety helpers ---
    @staticmethod
    def _safe_identifier(name: str) -> str:
        """Validate a SQL identifier (letters, digits, underscore) to avoid injection.

        Returns the identifier unchanged if valid; raises ValueError otherwise.
        """
        import re

        if not isinstance(name, str) or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ValueError(f"Invalid SQL identifier: {name!r}")
        return name

    @classmethod
    def _table_for_object_type(cls, object_type_api_name: str) -> str:
        return cls._safe_identifier(f"ot_{object_type_api_name}")

    async def execute_analytics_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> AnalyticsResult:
        """
        Execute an analytics query.

        Args:
            query: Analytics query to execute
            service: Service name
            instance: Instance name

        Returns:
            Analytics result with computed data
        """
        start_time = datetime.now()

        self.logger.info(f"Executing analytics query: {query.id}")

        try:
            if query.analytics_type == AnalyticsType.COUNT:
                result = await self._execute_count_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.SUM:
                result = await self._execute_sum_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.AVERAGE:
                result = await self._execute_average_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.MIN:
                result = await self._execute_min_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.MAX:
                result = await self._execute_max_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.DISTRIBUTION:
                result = await self._execute_distribution_query(query, service, instance)
            elif query.analytics_type == AnalyticsType.TREND:
                result = await self._execute_trend_query(query, service, instance)
            else:
                raise ValueError(f"Unsupported analytics type: {query.analytics_type}")

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return AnalyticsResult(
                query_id=query.id,
                result=result,
                metadata={
                    "object_type": query.object_type_api_name,
                    "analytics_type": query.analytics_type.value,
                    "filters": query.filters,
                },
                computed_at=datetime.now(),
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self.logger.error(f"Analytics query failed: {e}")
            raise

    async def get_object_type_metrics(
        self,
        object_type_api_name: str,
        service: str,
        instance: str,
        *,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive metrics for an object type.

        Args:
            object_type_api_name: API name of the object type
            service: Service name
            instance: Instance name
            time_range: Optional time range for analysis

        Returns:
            Dictionary with various metrics
        """
        self.logger.info(f"Getting metrics for object type: {object_type_api_name}")

        try:
            if not self.duckdb_repo.is_available():
                raise RuntimeError("DuckDB is not available for analytics")

            # Build table name based on object type (safe identifier)
            table_name = self._table_for_object_type(object_type_api_name)

            # Build WHERE clause for time range
            time_clause = ""
            params = {}

            if time_range:
                start_time, end_time = time_range
                time_clause = " WHERE valid_from >= ? AND valid_to <= ?"
                params = {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}

            # Get total count
            count_sql = f"SELECT COUNT(*) as count FROM {table_name}{time_clause}"
            total_count = self.duckdb_repo.execute_scalar(count_sql, params, read_only=False)
            total_count = int(total_count) if total_count is not None else 0

            # Get today's created count (assuming valid_from represents creation time)
            today = datetime.now().date()
            today_clause = " WHERE DATE(valid_from) = ?"
            today_params = {"today": today.isoformat()}

            if time_range:
                today_clause = " AND DATE(valid_from) = ?"
                today_params.update(params)
                today_params["today"] = today.isoformat()

            created_today_sql = (
                f"SELECT COUNT(*) as count FROM {table_name}{time_clause}{today_clause}"
            )
            created_today = self.duckdb_repo.execute_scalar(
                created_today_sql, today_params, read_only=False
            )
            created_today = int(created_today) if created_today is not None else 0

            # Get updated count (assuming transaction_to represents updates)
            updated_today_sql = f"SELECT COUNT(*) as count FROM {table_name}{time_clause} WHERE DATE(transaction_to) = ?"
            updated_params = dict(params)
            updated_params["update_date"] = today.isoformat()
            updated_today = self.duckdb_repo.execute_scalar(
                updated_today_sql, updated_params, read_only=False
            )
            updated_today = int(updated_today) if updated_today is not None else 0

            # Get growth trend (last 7 days)
            growth_trend_sql = f"""
            SELECT
                DATE(valid_from) as date,
                COUNT(*) as count
            FROM {table_name}{time_clause}
            WHERE valid_from >= DATE_SUB(CURRENT_DATE, INTERVAL '7 days')
            GROUP BY DATE(valid_from)
            ORDER BY date DESC
            """

            growth_rows = self.duckdb_repo.execute_query(growth_trend_sql, params, read_only=False)
            growth_trend = []
            for row in growth_rows:
                if isinstance(row, (list, tuple)) and len(row) >= 2:
                    growth_trend.append(
                        {"date": str(row[0]), "count": int(row[1]) if row[1] is not None else 0}
                    )

            # Get most common properties (simplified - would need schema introspection)
            most_common_properties = {}

            return {
                "total_count": total_count,
                "created_today": created_today,
                "updated_today": updated_today,
                "most_common_properties": most_common_properties,
                "growth_trend": growth_trend,
            }

        except Exception as e:
            self.logger.error(f"Failed to get object type metrics: {e}")
            # Return default values on error
            return {
                "total_count": 0,
                "created_today": 0,
                "updated_today": 0,
                "most_common_properties": {},
                "growth_trend": [],
            }

    async def get_property_analytics(
        self,
        object_type_api_name: str,
        property_name: str,
        analytics_type: AnalyticsType,
        service: str,
        instance: str,
        *,
        filters: dict[str, Any] | None = None,
    ) -> Any:
        """
        Get analytics for a specific property.

        Args:
            object_type_api_name: API name of the object type
            property_name: Name of the property to analyze
            analytics_type: Type of analytics to perform
            service: Service name
            instance: Instance name
            filters: Optional filters to apply

        Returns:
            Analytics result for the property
        """
        self.logger.info(f"Getting property analytics: {object_type_api_name}.{property_name}")

        # Create analytics query
        query = AnalyticsQuery(
            id=f"property_analytics_{property_name}_{analytics_type.value}",
            object_type_api_name=object_type_api_name,
            analytics_type=analytics_type,
            property_name=property_name,
            filters=filters or {},
            time_range=None,
            created_at=datetime.now(),
        )

        # Execute the query
        result = await self.execute_analytics_query(query, service, instance)
        return result.result

    async def generate_report(
        self,
        report_config: dict[str, Any],
        service: str,
        instance: str,
    ) -> dict[str, Any]:
        """
        Generate a comprehensive analytics report.

        Args:
            report_config: Configuration for the report
            service: Service name
            instance: Instance name

        Returns:
            Generated report data
        """
        self.logger.info("Generating analytics report")

        try:
            object_type = report_config.get("object_type_api_name")
            if not object_type:
                raise ValueError("object_type_api_name is required in report_config")

            # Get basic metrics
            metrics = await self.get_object_type_metrics(object_type, service, instance)

            # Get property-specific analytics if requested
            property_analytics = {}
            if "properties" in report_config:
                for prop_config in report_config["properties"]:
                    prop_name = prop_config["name"]
                    analytics_type = AnalyticsType(prop_config.get("type", "count"))

                    query = AnalyticsQuery(
                        id=f"report_{prop_name}_{analytics_type.value}",
                        object_type_api_name=object_type,
                        analytics_type=analytics_type,
                        property_name=prop_name,
                        filters=prop_config.get("filters", {}),
                        time_range=report_config.get("time_range"),
                        created_at=datetime.now(),
                    )

                    result = await self.execute_analytics_query(query, service, instance)
                    property_analytics[prop_name] = {
                        "type": analytics_type.value,
                        "result": result.result,
                        "execution_time_ms": result.execution_time_ms,
                    }

            # Generate report structure
            report = {
                "metadata": {
                    "object_type": object_type,
                    "generated_at": datetime.now().isoformat(),
                    "service": service,
                    "instance": instance,
                },
                "metrics": metrics,
                "property_analytics": property_analytics,
                "summary": {
                    "total_properties_analyzed": len(property_analytics),
                    "report_generation_time_ms": 0,  # Will be calculated below
                },
            }

            return report

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

    async def _execute_count_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> int:
        """Execute a count analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build count query
        sql = f"SELECT COUNT(*) as count FROM {table_name}{where_clause}"

        try:
            result = self.duckdb_repo.execute_scalar(sql, params, read_only=False)
            return int(result) if result is not None else 0

        except Exception as e:
            self.logger.error(f"Count query failed: {e}")
            raise

    async def _execute_sum_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> float:
        """Execute a sum analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for sum aggregation")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build sum query with validated identifier
        prop = self._safe_identifier(query.property_name)
        sql = f"SELECT SUM({prop}) as sum_value FROM {table_name}{where_clause}"

        try:
            result = self.duckdb_repo.execute_scalar(sql, params, read_only=False)
            return float(result) if result is not None else 0.0

        except Exception as e:
            self.logger.error(f"Sum query failed: {e}")
            raise

    async def _execute_average_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> float:
        """Execute an average analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for average aggregation")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build average query with validated identifier
        prop = self._safe_identifier(query.property_name)
        sql = f"SELECT AVG({prop}) as avg_value FROM {table_name}{where_clause}"

        try:
            result = self.duckdb_repo.execute_scalar(sql, params, read_only=False)
            return float(result) if result is not None else 0.0

        except Exception as e:
            self.logger.error(f"Average query failed: {e}")
            raise

    async def _execute_min_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> Any:
        """Execute a min analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for min aggregation")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build min query with validated identifier
        prop = self._safe_identifier(query.property_name)
        sql = f"SELECT MIN({prop}) as min_value FROM {table_name}{where_clause}"

        try:
            result = self.duckdb_repo.execute_scalar(sql, params, read_only=False)
            return float(result) if result is not None else 0.0

        except Exception as e:
            self.logger.error(f"Min query failed: {e}")
            raise

    async def _execute_max_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> Any:
        """Execute a max analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for max aggregation")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build max query with validated identifier
        prop = self._safe_identifier(query.property_name)
        sql = f"SELECT MAX({prop}) as max_value FROM {table_name}{where_clause}"

        try:
            result = self.duckdb_repo.execute_scalar(sql, params, read_only=False)
            return float(result) if result is not None else 0.0

        except Exception as e:
            self.logger.error(f"Max query failed: {e}")
            raise

    async def _execute_distribution_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> dict[str, int]:
        """Execute a distribution analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for distribution analysis")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Build distribution query with GROUP BY
        prop = self._safe_identifier(query.property_name)
        sql = f"SELECT {prop} as value, COUNT(*) as count FROM {table_name}{where_clause} GROUP BY {prop} ORDER BY count DESC"

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            # Convert to dictionary
            distribution = {}
            for row in rows:
                if isinstance(row, (list, tuple)) and len(row) >= 2:
                    value = str(row[0]) if row[0] is not None else "NULL"
                    count = int(row[1]) if row[1] is not None else 0
                    distribution[value] = count

            return distribution

        except Exception as e:
            self.logger.error(f"Distribution query failed: {e}")
            raise

    async def _execute_trend_query(
        self,
        query: AnalyticsQuery,
        service: str,
        instance: str,
    ) -> list[dict[str, Any]]:
        """Execute a trend analytics query."""
        if not self.duckdb_repo.is_available():
            raise RuntimeError("DuckDB is not available for analytics")

        if not query.property_name:
            raise ValueError("Property name is required for trend analysis")

        # Build table name based on object type (safe identifier)
        table_name = self._table_for_object_type(query.object_type_api_name)

        # Build WHERE clause from filters and time range
        where_clause = ""
        params = {}

        if query.filters:
            conditions = []
            for key, value in query.filters.items():
                conditions.append(f"{key} = ?")
                params[key] = value

            if conditions:
                where_clause = f" WHERE {' AND '.join(conditions)}"

        # Add time range filtering if provided
        if query.time_range:
            time_conditions = []
            start_time, end_time = query.time_range
            time_conditions.append("valid_from >= ?")
            time_conditions.append("valid_to <= ?")
            params["start_time"] = start_time.isoformat()
            params["end_time"] = end_time.isoformat()

            if where_clause:
                where_clause += f" AND {' AND '.join(time_conditions)}"
            else:
                where_clause = f" WHERE {' AND '.join(time_conditions)}"

        # Build trend query with time-based aggregation
        # Assuming we have a timestamp column for trend analysis
        prop = self._safe_identifier(query.property_name)
        sql = f"""
        SELECT
            DATE_TRUNC('day', valid_from) as period,
            AVG({prop}) as avg_value,
            MIN({prop}) as min_value,
            MAX({prop}) as max_value,
            COUNT(*) as count
        FROM {table_name}{where_clause}
        GROUP BY DATE_TRUNC('day', valid_from)
        ORDER BY period DESC
        LIMIT 30
        """

        try:
            rows = self.duckdb_repo.execute_query(sql, params, read_only=False)

            # Convert to list of dictionaries
            trend_data = []
            for row in rows:
                if isinstance(row, (list, tuple)) and len(row) >= 5:
                    trend_data.append(
                        {
                            "period": (
                                row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0])
                            ),
                            "avg_value": float(row[1]) if row[1] is not None else 0.0,
                            "min_value": float(row[2]) if row[2] is not None else 0.0,
                            "max_value": float(row[3]) if row[3] is not None else 0.0,
                            "count": int(row[4]) if row[4] is not None else 0,
                        }
                    )

            return trend_data

        except Exception as e:
            self.logger.error(f"Trend query failed: {e}")
            raise
