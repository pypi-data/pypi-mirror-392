"""
Query optimization utilities for the Ontologia SDK.

Provides intelligent query optimization including index suggestions,
query plan analysis, and performance recommendations.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .query_builder import FilterCondition, QueryBuilder, SortCondition

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of query optimizations."""

    INDEX_SUGGESTION = "index_suggestion"
    FILTER_REORDER = "filter_reorder"
    LIMIT_OPTIMIZATION = "limit_optimization"
    FIELD_SELECTION = "field_selection"
    JOIN_OPTIMIZATION = "join_optimization"
    CACHING_RECOMMENDATION = "caching_recommendation"


@dataclass
class OptimizationSuggestion:
    """Single optimization suggestion."""

    type: OptimizationType
    description: str
    impact: str  # "low", "medium", "high"
    estimated_improvement: float | None = None  # percentage
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryPlan:
    """Query execution plan with performance metrics."""

    object_type: str
    estimated_rows: int
    estimated_cost: float
    indexes_used: list[str] = field(default_factory=list)
    indexes_suggested: list[str] = field(default_factory=list)
    execution_time_ms: float | None = None
    optimizations: list[OptimizationSuggestion] = field(default_factory=list)


@dataclass
class IndexDefinition:
    """Index definition for optimization."""

    name: str
    fields: list[str]
    unique: bool = False
    partial_filter: dict[str, Any] | None = None
    estimated_selectivity: float | None = None


class QueryOptimizer:
    """
    Advanced query optimizer for Ontologia SDK.

    Analyzes queries and provides optimization suggestions
    based on data distribution and access patterns.
    """

    def __init__(self):
        self._index_cache: dict[str, list[IndexDefinition]] = {}
        self._stats_cache: dict[str, dict[str, Any]] = {}

    async def analyze_query(
        self, query_builder: QueryBuilder, session, include_execution_plan: bool = False
    ) -> QueryPlan:
        """
        Analyze a query and generate optimization suggestions.

        Args:
            query_builder: QueryBuilder instance to analyze
            session: ClientSession for metadata access
            include_execution_plan: Whether to include actual execution plan

        Returns:
            QueryPlan with analysis results
        """
        start_time = time.time()

        # Get object type metadata
        object_type = query_builder.object_type
        obj_type_def = await self._get_object_type_def(object_type, session)

        # Analyze filters
        filter_analysis = self._analyze_filters(query_builder.filters, obj_type_def)

        # Analyze sorting
        sort_analysis = self._analyze_sorting(query_builder.sorts, obj_type_def)

        # Analyze field selection
        field_analysis = self._analyze_field_selection(query_builder.selected_fields, obj_type_def)

        # Get existing indexes
        existing_indexes = await self._get_indexes(object_type, session)

        # Generate optimization suggestions
        optimizations = []
        optimizations.extend(filter_analysis.suggestions)
        optimizations.extend(sort_analysis.suggestions)
        optimizations.extend(field_analysis.suggestions)

        # Create query plan
        plan = QueryPlan(
            object_type=object_type,
            estimated_rows=filter_analysis.estimated_rows,
            estimated_cost=filter_analysis.cost + sort_analysis.cost,
            indexes_used=existing_indexes,
            indexes_suggested=self._suggest_indexes(query_builder, obj_type_def),
            optimizations=optimizations,
        )

        # Include execution time if requested
        if include_execution_plan:
            # Execute query with timing
            execution_start = time.time()
            try:
                from .query_builder import QueryExecutor

                executor = QueryExecutor(session)
                await executor.execute(query_builder)
                plan.execution_time_ms = (time.time() - execution_start) * 1000
            except Exception as e:
                logger.warning(f"Could not execute query for timing: {e}")

        # Cache the analysis
        self._cache_analysis(object_type, query_builder, plan)

        return plan

    def _analyze_filters(
        self, filters: list[FilterCondition], obj_type_def: dict[str, Any]
    ) -> FilterAnalysis:
        """Analyze filter conditions for optimization opportunities."""
        analysis = FilterAnalysis()

        # Get property definitions
        properties = {prop["name"]: prop for prop in obj_type_def.get("properties", [])}

        # Analyze each filter
        selective_filters = []
        for filter_cond in filters:
            prop_name = filter_cond.field
            if prop_name in properties:
                prop_def = properties[prop_name]
                selectivity = self._estimate_selectivity(filter_cond, prop_def)

                if selectivity < 0.1:  # Highly selective
                    selective_filters.append((filter_cond, selectivity))

                # Check for optimization opportunities
                if filter_cond.operator in ["=", "in"]:
                    if not self._has_index(prop_name, obj_type_def):
                        analysis.suggestions.append(
                            OptimizationSuggestion(
                                type=OptimizationType.INDEX_SUGGESTION,
                                description=f"Add index on '{prop_name}' for equality filtering",
                                impact="high",
                                estimated_improvement=50.0,
                                details={"field": prop_name, "operator": filter_cond.operator},
                            )
                        )

                # Check for range queries
                elif filter_cond.operator in [">", "<", ">=", "<=", "between"]:
                    if not self._has_composite_index(prop_name, obj_type_def):
                        analysis.suggestions.append(
                            OptimizationSuggestion(
                                type=OptimizationType.INDEX_SUGGESTION,
                                description=f"Add index on '{prop_name}' for range queries",
                                impact="medium",
                                estimated_improvement=30.0,
                                details={"field": prop_name, "operator": filter_cond.operator},
                            )
                        )

        # Suggest filter reordering
        if len(selective_filters) > 1:
            selective_filters.sort(key=lambda x: x[1])  # Sort by selectivity
            analysis.suggestions.append(
                OptimizationSuggestion(
                    type=OptimizationType.FILTER_REORDER,
                    description="Reorder filters by selectivity (most selective first)",
                    impact="medium",
                    estimated_improvement=20.0,
                    details={"optimal_order": [f[0].field for f in selective_filters]},
                )
            )

        # Estimate rows and cost
        analysis.estimated_rows = self._estimate_result_rows(filters, obj_type_def)
        analysis.cost = len(filters) * 10.0  # Base cost per filter

        return analysis

    def _analyze_sorting(
        self, sorts: list[SortCondition], obj_type_def: dict[str, Any]
    ) -> SortAnalysis:
        """Analyze sorting conditions for optimization."""
        analysis = SortAnalysis()

        if not sorts:
            return analysis

        properties = {prop["name"]: prop for prop in obj_type_def.get("properties", [])}

        for sort_cond in sorts:
            prop_name = sort_cond.field
            if prop_name in properties:
                # Check if sorting field is indexed
                if not self._has_index(prop_name, obj_type_def):
                    analysis.suggestions.append(
                        OptimizationSuggestion(
                            type=OptimizationType.INDEX_SUGGESTION,
                            description=f"Add index on '{prop_name}' for sorting optimization",
                            impact="medium",
                            estimated_improvement=40.0,
                            details={"field": prop_name, "direction": sort_cond.direction},
                        )
                    )

                # Check for composite index opportunity
                if len(sorts) > 1:
                    sort_fields = [s.field for s in sorts]
                    if not self._has_composite_index(sort_fields, obj_type_def):
                        analysis.suggestions.append(
                            OptimizationSuggestion(
                                type=OptimizationType.INDEX_SUGGESTION,
                                description=f"Add composite index on {sort_fields} for multi-field sorting",
                                impact="high",
                                estimated_improvement=60.0,
                                details={"fields": sort_fields},
                            )
                        )

        analysis.cost = len(sorts) * 15.0  # Higher cost for sorting
        return analysis

    def _analyze_field_selection(
        self, selected_fields: list[str] | None, obj_type_def: dict[str, Any]
    ) -> FieldAnalysis:
        """Analyze field selection for optimization."""
        analysis = FieldAnalysis()

        all_properties = obj_type_def.get("properties", [])
        all_fields = [prop["name"] for prop in all_properties]

        if selected_fields is None:
            # No field selection - suggest selecting only needed fields
            analysis.suggestions.append(
                OptimizationSuggestion(
                    type=OptimizationType.FIELD_SELECTION,
                    description="Select only required fields to reduce data transfer",
                    impact="medium",
                    estimated_improvement=25.0,
                    details={"available_fields": all_fields},
                )
            )
        else:
            # Check for large fields that could be excluded
            large_fields = []
            for prop in all_properties:
                if prop["name"] not in selected_fields:
                    prop_type = prop.get("type", "string")
                    if prop_type in ["text", "json", "blob"]:
                        large_fields.append(prop["name"])

            if large_fields:
                analysis.suggestions.append(
                    OptimizationSuggestion(
                        type=OptimizationType.FIELD_SELECTION,
                        description=f"Consider excluding large fields: {large_fields}",
                        impact="low",
                        estimated_improvement=15.0,
                        details={"large_fields": large_fields},
                    )
                )

        analysis.cost = len(selected_fields or all_fields) * 5.0
        return analysis

    def _suggest_indexes(
        self, query_builder: QueryBuilder, obj_type_def: dict[str, Any]
    ) -> list[str]:
        """Suggest indexes based on query patterns."""
        suggestions = []

        # Analyze filter patterns
        filter_fields = [f.field for f in query_builder.filters]
        if filter_fields:
            # Single field indexes
            for field in filter_fields:
                index_name = f"idx_{query_builder.object_type}_{field}"
                if index_name not in [
                    idx.name for idx in self._index_cache.get(query_builder.object_type, [])
                ]:
                    suggestions.append(index_name)

            # Composite indexes for multiple filters
            if len(filter_fields) > 1:
                composite_name = f"idx_{query_builder.object_type}_{'_'.join(filter_fields[:3])}"
                suggestions.append(composite_name)

        # Analyze sort patterns
        if query_builder.sorts:
            sort_fields = [s.field for s in query_builder.sorts]
            composite_name = f"idx_{query_builder.object_type}_sort_{'_'.join(sort_fields)}"
            suggestions.append(composite_name)

        return suggestions

    def _estimate_selectivity(
        self, filter_cond: FilterCondition, prop_def: dict[str, Any]
    ) -> float:
        """Estimate selectivity of a filter condition (0.0 to 1.0)."""
        # Base selectivity by operator
        operator_selectivity = {
            "=": 0.01,
            "in": 0.05,
            "like": 0.1,
            ">": 0.3,
            "<": 0.3,
            ">=": 0.4,
            "<=": 0.4,
            "between": 0.2,
            "is_null": 0.05,
            "is_not_null": 0.95,
        }

        base_selectivity = operator_selectivity.get(filter_cond.operator, 0.5)

        # Adjust based on property characteristics
        prop_type = prop_def.get("type", "string")

        if prop_type == "boolean":
            base_selectivity *= 0.5  # Boolean fields are less selective
        elif prop_type in ["integer", "float"]:
            base_selectivity *= 0.8  # Numeric fields are moderately selective
        elif prop_type == "string":
            if filter_cond.operator == "=" and len(str(filter_cond.value)) > 10:
                base_selectivity *= 0.5  # Long strings are more selective

        return min(max(base_selectivity, 0.001), 0.999)

    def _estimate_result_rows(
        self, filters: list[FilterCondition], obj_type_def: dict[str, Any]
    ) -> int:
        """Estimate number of rows returned by filters."""
        # Start with estimated total rows (could be from statistics)
        estimated_total = 10000  # Default estimate

        if not filters:
            return estimated_total

        # Apply selectivity for each filter
        result_rows = estimated_total
        for filter_cond in filters:
            properties = {prop["name"]: prop for prop in obj_type_def.get("properties", [])}
            if filter_cond.field in properties:
                prop_def = properties[filter_cond.field]
                selectivity = self._estimate_selectivity(filter_cond, prop_def)
                result_rows = int(result_rows * selectivity)

        return max(result_rows, 1)

    def _has_index(self, field: str, obj_type_def: dict[str, Any]) -> bool:
        """Check if field has an index."""
        indexes = obj_type_def.get("indexes", [])
        for index in indexes:
            if field in index.get("properties", []):
                return True
        return False

    def _has_composite_index(self, fields: str | list[str], obj_type_def: dict[str, Any]) -> bool:
        """Check if composite index exists for fields."""
        if isinstance(fields, str):
            fields = [fields]

        indexes = obj_type_def.get("indexes", [])
        for index in indexes:
            index_fields = index.get("properties", [])
            if index_fields == fields:
                return True
        return False

    async def _get_object_type_def(self, object_type: str, session) -> dict[str, Any]:
        """Get object type definition from session."""
        try:
            return await session.get_object_type(object_type) or {}
        except Exception as e:
            logger.warning(f"Could not get object type definition for {object_type}: {e}")
            return {}

    async def _get_indexes(self, object_type: str, session) -> list[str]:
        """Get existing indexes for object type."""
        if object_type in self._index_cache:
            return [idx.name for idx in self._index_cache[object_type]]

        try:
            # This would typically come from a system catalog or metadata API
            obj_type_def = await self._get_object_type_def(object_type, session)
            indexes = obj_type_def.get("indexes", [])

            # Cache the result
            self._index_cache[object_type] = [
                IndexDefinition(
                    name=f"idx_{object_type}_{'_'.join(idx.get('properties', []))}",
                    fields=idx.get("properties", []),
                    unique=idx.get("unique", False),
                )
                for idx in indexes
            ]

            return [idx.name for idx in self._index_cache[object_type]]
        except Exception as e:
            logger.warning(f"Could not get indexes for {object_type}: {e}")
            return []

    def _cache_analysis(self, object_type: str, query_builder: QueryBuilder, plan: QueryPlan):
        """Cache query analysis for future use."""
        # Simple in-memory cache - could be replaced with Redis or other cache
        cache_key = f"{object_type}_{hash(str(query_builder.build()))}"
        self._stats_cache[cache_key] = {"plan": plan, "timestamp": time.time()}

    async def create_optimized_query(
        self, original_query: QueryBuilder, optimizations: list[OptimizationSuggestion]
    ) -> QueryBuilder:
        """
        Create an optimized version of the query based on suggestions.

        Args:
            original_query: Original QueryBuilder
            optimizations: List of optimizations to apply

        Returns:
            Optimized QueryBuilder
        """
        optimized = original_query.copy()

        for optimization in optimizations:
            if optimization.type == OptimizationType.FILTER_REORDER:
                # Reorder filters by selectivity
                optimal_order = optimization.details.get("optimal_order", [])
                if optimal_order:
                    # This would require access to the actual filter objects
                    # For now, just log the suggestion
                    logger.info(f"Suggested filter order: {optimal_order}")

            elif optimization.type == OptimizationType.LIMIT_OPTIMIZATION:
                # Add or adjust limit based on suggestion
                suggested_limit = optimization.details.get("suggested_limit")
                if suggested_limit:
                    optimized.limit(suggested_limit)

        return optimized

    def get_optimization_summary(self, plan: QueryPlan) -> dict[str, Any]:
        """Get a summary of optimization suggestions."""
        summary: dict[str, Any] = {
            "total_suggestions": len(plan.optimizations),
            "high_impact": len([o for o in plan.optimizations if o.impact == "high"]),
            "medium_impact": len([o for o in plan.optimizations if o.impact == "medium"]),
            "low_impact": len([o for o in plan.optimizations if o.impact == "low"]),
            "estimated_improvement": 0.0,
            "categories": {},
        }

        # Calculate total estimated improvement
        for optimization in plan.optimizations:
            if optimization.estimated_improvement:
                summary["estimated_improvement"] += float(optimization.estimated_improvement)  # type: ignore[operator]

        # Group by optimization type
        for optimization in plan.optimizations:
            opt_type = optimization.type.value
            if opt_type not in summary["categories"]:  # type: ignore[operator]
                summary["categories"][opt_type] = []  # type: ignore[index]
            summary["categories"][opt_type].append(  # type: ignore[index]
                {
                    "description": optimization.description,
                    "impact": optimization.impact,
                    "estimated_improvement": optimization.estimated_improvement,
                }
            )

        return summary


@dataclass
class FilterAnalysis:
    """Analysis of filter conditions."""

    estimated_rows: int = 0
    cost: float = 0.0
    suggestions: list[OptimizationSuggestion] = field(default_factory=list)


@dataclass
class SortAnalysis:
    """Analysis of sorting conditions."""

    cost: float = 0.0
    suggestions: list[OptimizationSuggestion] = field(default_factory=list)


@dataclass
class FieldAnalysis:
    """Analysis of field selection."""

    cost: float = 0.0
    suggestions: list[OptimizationSuggestion] = field(default_factory=list)


# Convenience functions


async def optimize_query(
    query_builder: QueryBuilder, session, include_execution_plan: bool = False
) -> QueryPlan:
    """
    Optimize a query and return analysis.

    Args:
        query_builder: QueryBuilder to optimize
        session: ClientSession for metadata access
        include_execution_plan: Whether to include actual execution timing

    Returns:
        QueryPlan with optimization analysis
    """
    optimizer = QueryOptimizer()
    return await optimizer.analyze_query(query_builder, session, include_execution_plan)


def create_index_suggestion(
    object_type: str,
    fields: list[str],
    unique: bool = False,
    partial_filter: dict[str, Any] | None = None,
) -> IndexDefinition:
    """
    Create an index definition suggestion.

    Args:
        object_type: Object type name
        fields: Fields to index
        unique: Whether index should be unique
        partial_filter: Optional partial filter expression

    Returns:
        IndexDefinition for the suggested index
    """
    name_parts = ["idx", object_type] + fields
    if unique:
        name_parts.insert(1, "unique")

    return IndexDefinition(
        name="_".join(name_parts), fields=fields, unique=unique, partial_filter=partial_filter
    )
