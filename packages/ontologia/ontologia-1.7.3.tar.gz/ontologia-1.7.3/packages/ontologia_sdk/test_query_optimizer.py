"""
Tests for the query optimizer implementation.
"""

from unittest.mock import AsyncMock

import pytest

from ontologia_sdk.query_builder import FilterCondition, QueryBuilder, SortCondition
from ontologia_sdk.query_optimizer import (
    FieldAnalysis,
    FilterAnalysis,
    IndexDefinition,
    OptimizationSuggestion,
    OptimizationType,
    QueryOptimizer,
    QueryPlan,
    SortAnalysis,
    create_index_suggestion,
    optimize_query,
)


class TestQueryOptimizer:
    """Test QueryOptimizer functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.optimizer = QueryOptimizer()
        self.mock_session = AsyncMock()

    @pytest.mark.asyncio
    async def test_analyze_query_basic(self):
        """Test basic query analysis."""
        # Create a simple query
        query = QueryBuilder("person")
        query.where("name", "=", "John")

        # Mock object type definition
        obj_type_def = {
            "api_name": "person",
            "properties": [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}],
            "indexes": [],
        }

        self.mock_session.get_object_type = AsyncMock(return_value=obj_type_def)

        # Analyze query
        plan = await self.optimizer.analyze_query(query, self.mock_session)

        assert plan.object_type == "person"
        assert isinstance(plan, QueryPlan)
        assert plan.estimated_rows > 0
        assert plan.estimated_cost > 0
        assert len(plan.optimizations) > 0

    @pytest.mark.asyncio
    async def test_analyze_query_with_indexes(self):
        """Test query analysis with existing indexes."""
        query = QueryBuilder("person")
        query.where("name", "=", "John")

        # Mock object type with existing index
        obj_type_def = {
            "api_name": "person",
            "properties": [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}],
            "indexes": [{"properties": ["name"], "unique": False}],
        }

        self.mock_session.get_object_type = AsyncMock(return_value=obj_type_def)

        plan = await self.optimizer.analyze_query(query, self.mock_session)

        # Should have fewer suggestions since index exists
        index_suggestions = [
            o for o in plan.optimizations if o.type == OptimizationType.INDEX_SUGGESTION
        ]
        assert len(index_suggestions) == 0 or not any(
            "name" in o.description for o in index_suggestions
        )

    @pytest.mark.asyncio
    async def test_analyze_complex_query(self):
        """Test analysis of complex query with multiple conditions."""
        query = QueryBuilder("person")
        query.where("age", ">", 25)
        query.and_where("status", "=", "active")
        query.order_by("name", "asc")
        query.limit(10)

        obj_type_def = {
            "api_name": "person",
            "properties": [
                {"name": "name", "type": "string"},
                {"name": "age", "type": "integer"},
                {"name": "status", "type": "string"},
                {"name": "bio", "type": "text"},
            ],
            "indexes": [],
        }

        self.mock_session.get_object_type = AsyncMock(return_value=obj_type_def)

        plan = await self.optimizer.analyze_query(query, self.mock_session)

        # Should have multiple optimization suggestions
        assert len(plan.optimizations) >= 2

        # Check for different types of optimizations
        optimization_types = {o.type for o in plan.optimizations}
        assert OptimizationType.INDEX_SUGGESTION in optimization_types

    @pytest.mark.asyncio
    async def test_analyze_query_with_execution_plan(self):
        """Test query analysis including execution timing."""
        query = QueryBuilder("person")
        query.where("name", "=", "John")

        obj_type_def = {
            "api_name": "person",
            "properties": [{"name": "name", "type": "string"}],
            "indexes": [],
        }

        self.mock_session.get_object_type = AsyncMock(return_value=obj_type_def)

        # Mock successful query execution
        with pytest.MonkeyPatch().context() as m:
            mock_executor = AsyncMock()
            mock_executor.execute = AsyncMock(return_value=[])

            # Import QueryExecutor from the correct module

            m.setattr("ontologia_sdk.query_builder.QueryExecutor", lambda session: mock_executor)

            plan = await self.optimizer.analyze_query(
                query, self.mock_session, include_execution_plan=True
            )

            assert plan.execution_time_ms is not None
            assert plan.execution_time_ms > 0

    def test_analyze_filters_equality(self):
        """Test filter analysis for equality conditions."""
        filters = [FilterCondition(field="name", operator="=", value="John")]

        obj_type_def = {"properties": [{"name": "name", "type": "string"}]}

        analysis = self.optimizer._analyze_filters(filters, obj_type_def)

        assert analysis.estimated_rows > 0
        assert len(analysis.suggestions) > 0

        # Should suggest index for equality filter
        index_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.INDEX_SUGGESTION
        ]
        assert len(index_suggestions) > 0
        assert "name" in index_suggestions[0].description

    def test_analyze_filters_range(self):
        """Test filter analysis for range conditions."""
        filters = [FilterCondition(field="age", operator=">", value=25)]

        obj_type_def = {"properties": [{"name": "age", "type": "integer"}]}

        analysis = self.optimizer._analyze_filters(filters, obj_type_def)

        # Should suggest index for range query
        index_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.INDEX_SUGGESTION
        ]
        assert len(index_suggestions) > 0
        assert "range" in index_suggestions[0].description.lower()

    def test_analyze_filters_multiple_selective(self):
        """Test filter analysis with multiple selective filters."""
        filters = [
            FilterCondition(field="email", operator="=", value="john@example.com"),
            FilterCondition(field="status", operator="=", value="active"),
        ]

        obj_type_def = {
            "properties": [
                {"name": "email", "type": "string"},
                {"name": "status", "type": "string"},
            ]
        }

        analysis = self.optimizer._analyze_filters(filters, obj_type_def)

        # Should suggest filter reordering
        reorder_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.FILTER_REORDER
        ]
        assert len(reorder_suggestions) > 0

    def test_analyze_sorting_single_field(self):
        """Test sorting analysis for single field."""
        sorts = [SortCondition(field="name", direction="asc")]

        obj_type_def = {"properties": [{"name": "name", "type": "string"}]}

        analysis = self.optimizer._analyze_sorting(sorts, obj_type_def)

        # Should suggest index for sorting
        index_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.INDEX_SUGGESTION
        ]
        assert len(index_suggestions) > 0
        assert "sorting" in index_suggestions[0].description.lower()

    def test_analyze_sorting_multiple_fields(self):
        """Test sorting analysis for multiple fields."""
        sorts = [
            SortCondition(field="department", direction="asc"),
            SortCondition(field="name", direction="asc"),
        ]

        obj_type_def = {
            "properties": [
                {"name": "department", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }

        analysis = self.optimizer._analyze_sorting(sorts, obj_type_def)

        # Should suggest composite index
        composite_suggestions = [
            o for o in analysis.suggestions if "composite" in o.description.lower()
        ]
        assert len(composite_suggestions) > 0

    def test_analyze_field_selection_no_selection(self):
        """Test field analysis when no fields are selected."""
        selected_fields = None

        obj_type_def = {
            "properties": [
                {"name": "name", "type": "string"},
                {"name": "bio", "type": "text"},
                {"name": "age", "type": "integer"},
            ]
        }

        analysis = self.optimizer._analyze_field_selection(selected_fields, obj_type_def)

        # Should suggest field selection
        field_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.FIELD_SELECTION
        ]
        assert len(field_suggestions) > 0

    def test_analyze_field_selection_with_large_fields(self):
        """Test field analysis with large fields excluded."""
        selected_fields = ["name", "age"]

        obj_type_def = {
            "properties": [
                {"name": "name", "type": "string"},
                {"name": "bio", "type": "text"},  # Large field
                {"name": "data", "type": "json"},  # Large field
                {"name": "age", "type": "integer"},
            ]
        }

        analysis = self.optimizer._analyze_field_selection(selected_fields, obj_type_def)

        # Should suggest excluding large fields
        field_suggestions = [
            o for o in analysis.suggestions if o.type == OptimizationType.FIELD_SELECTION
        ]
        assert len(field_suggestions) > 0
        assert any("large" in o.description.lower() for o in field_suggestions)

    def test_estimate_selectivity_equality(self):
        """Test selectivity estimation for equality operators."""
        filter_cond = FilterCondition(field="name", operator="=", value="John")
        prop_def = {"type": "string"}

        selectivity = self.optimizer._estimate_selectivity(filter_cond, prop_def)

        assert 0 < selectivity < 1
        assert selectivity < 0.1  # Equality should be highly selective

    def test_estimate_selectivity_range(self):
        """Test selectivity estimation for range operators."""
        filter_cond = FilterCondition(field="age", operator=">", value=25)
        prop_def = {"type": "integer"}

        selectivity = self.optimizer._estimate_selectivity(filter_cond, prop_def)

        assert 0 < selectivity < 1
        assert selectivity > 0.1  # Range should be less selective than equality

    def test_estimate_selectivity_boolean(self):
        """Test selectivity estimation for boolean fields."""
        filter_cond = FilterCondition(field="active", operator="=", value=True)
        prop_def = {"type": "boolean"}

        selectivity = self.optimizer._estimate_selectivity(filter_cond, prop_def)

        assert 0 < selectivity < 1

    def test_estimate_result_rows_no_filters(self):
        """Test result row estimation with no filters."""
        filters = []
        obj_type_def = {"properties": []}

        rows = self.optimizer._estimate_result_rows(filters, obj_type_def)

        assert rows > 0  # Should return estimated total

    def test_estimate_result_rows_with_filters(self):
        """Test result row estimation with filters."""
        filters = [FilterCondition(field="name", operator="=", value="John")]
        obj_type_def = {"properties": [{"name": "name", "type": "string"}]}

        rows = self.optimizer._estimate_result_rows(filters, obj_type_def)

        assert rows > 0
        assert rows < 10000  # Should be less than estimated total

    def test_has_index(self):
        """Test index detection."""
        obj_type_def = {"indexes": [{"properties": ["name"]}, {"properties": ["age", "status"]}]}

        assert self.optimizer._has_index("name", obj_type_def)
        assert self.optimizer._has_index("age", obj_type_def)
        assert not self.optimizer._has_index("email", obj_type_def)

    def test_has_composite_index(self):
        """Test composite index detection."""
        obj_type_def = {"indexes": [{"properties": ["age", "status"]}, {"properties": ["name"]}]}

        assert self.optimizer._has_composite_index(["age", "status"], obj_type_def)
        assert not self.optimizer._has_composite_index(["status", "age"], obj_type_def)
        assert not self.optimizer._has_composite_index(["email"], obj_type_def)

    @pytest.mark.asyncio
    async def test_get_indexes_caching(self):
        """Test index caching functionality."""
        object_type = "person"

        # First call should fetch from session
        obj_type_def = {"indexes": [{"properties": ["name"], "unique": False}]}

        self.mock_session.get_object_type = AsyncMock(return_value=obj_type_def)

        indexes1 = await self.optimizer._get_indexes(object_type, self.mock_session)
        assert len(indexes1) > 0

        # Second call should use cache
        indexes2 = await self.optimizer._get_indexes(object_type, self.mock_session)
        assert indexes1 == indexes2

    @pytest.mark.asyncio
    async def test_create_optimized_query(self):
        """Test creating optimized query from suggestions."""
        original_query = QueryBuilder("person")
        original_query.where("name", "=", "John")

        optimizations = [
            OptimizationSuggestion(
                type=OptimizationType.LIMIT_OPTIMIZATION,
                description="Add limit",
                impact="medium",
                details={"suggested_limit": 100},
            )
        ]

        optimized = await self.optimizer.create_optimized_query(original_query, optimizations)

        assert optimized is not original_query  # Should be a copy
        # Note: The actual optimization would require more complex implementation

    def test_get_optimization_summary(self):
        """Test optimization summary generation."""
        plan = QueryPlan(
            object_type="person",
            estimated_rows=100,
            estimated_cost=50.0,
            optimizations=[
                OptimizationSuggestion(
                    type=OptimizationType.INDEX_SUGGESTION,
                    description="Add index on name",
                    impact="high",
                    estimated_improvement=50.0,
                ),
                OptimizationSuggestion(
                    type=OptimizationType.FIELD_SELECTION,
                    description="Select specific fields",
                    impact="medium",
                    estimated_improvement=25.0,
                ),
            ],
        )

        summary = self.optimizer.get_optimization_summary(plan)

        assert summary["total_suggestions"] == 2
        assert summary["high_impact"] == 1
        assert summary["medium_impact"] == 1
        assert summary["low_impact"] == 0
        assert summary["estimated_improvement"] == 75.0
        assert "index_suggestion" in summary["categories"]
        assert "field_selection" in summary["categories"]


class TestOptimizationSuggestion:
    """Test OptimizationSuggestion dataclass."""

    def test_optimization_suggestion_creation(self):
        """Test creating optimization suggestion."""
        suggestion = OptimizationSuggestion(
            type=OptimizationType.INDEX_SUGGESTION,
            description="Add index on name",
            impact="high",
            estimated_improvement=50.0,
            details={"field": "name"},
        )

        assert suggestion.type == OptimizationType.INDEX_SUGGESTION
        assert suggestion.description == "Add index on name"
        assert suggestion.impact == "high"
        assert suggestion.estimated_improvement == 50.0
        assert suggestion.details["field"] == "name"


class TestQueryPlan:
    """Test QueryPlan dataclass."""

    def test_query_plan_creation(self):
        """Test creating query plan."""
        optimizations = [
            OptimizationSuggestion(
                type=OptimizationType.INDEX_SUGGESTION, description="Add index", impact="high"
            )
        ]

        plan = QueryPlan(
            object_type="person",
            estimated_rows=100,
            estimated_cost=50.0,
            indexes_used=["idx_name"],
            indexes_suggested=["idx_email"],
            optimizations=optimizations,
        )

        assert plan.object_type == "person"
        assert plan.estimated_rows == 100
        assert plan.estimated_cost == 50.0
        assert len(plan.indexes_used) == 1
        assert len(plan.indexes_suggested) == 1
        assert len(plan.optimizations) == 1


class TestIndexDefinition:
    """Test IndexDefinition dataclass."""

    def test_index_definition_creation(self):
        """Test creating index definition."""
        index = IndexDefinition(
            name="idx_person_name",
            fields=["name"],
            unique=True,
            partial_filter={"status": "active"},
        )

        assert index.name == "idx_person_name"
        assert index.fields == ["name"]
        assert index.unique is True
        assert index.partial_filter == {"status": "active"}


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_optimize_query_function(self):
        """Test optimize_query convenience function."""
        query = QueryBuilder("person")
        query.where("name", "=", "John")

        mock_session = AsyncMock()
        mock_session.get_object_type = AsyncMock(
            return_value={"properties": [{"name": "name", "type": "string"}], "indexes": []}
        )

        plan = await optimize_query(query, mock_session)

        assert isinstance(plan, QueryPlan)
        assert plan.object_type == "person"

    def test_create_index_suggestion_function(self):
        """Test create_index_suggestion convenience function."""
        index = create_index_suggestion(
            "person", ["name", "email"], unique=True, partial_filter={"status": "active"}
        )

        assert isinstance(index, IndexDefinition)
        assert "idx_unique_person_name_email" == index.name
        assert index.fields == ["name", "email"]
        assert index.unique is True
        assert index.partial_filter == {"status": "active"}


class TestFilterAnalysis:
    """Test FilterAnalysis dataclass."""

    def test_filter_analysis_creation(self):
        """Test creating filter analysis."""
        suggestions = [
            OptimizationSuggestion(
                type=OptimizationType.INDEX_SUGGESTION, description="Add index", impact="high"
            )
        ]

        analysis = FilterAnalysis(estimated_rows=100, cost=25.0, suggestions=suggestions)

        assert analysis.estimated_rows == 100
        assert analysis.cost == 25.0
        assert len(analysis.suggestions) == 1


class TestSortAnalysis:
    """Test SortAnalysis dataclass."""

    def test_sort_analysis_creation(self):
        """Test creating sort analysis."""
        suggestions = [
            OptimizationSuggestion(
                type=OptimizationType.INDEX_SUGGESTION,
                description="Add index for sorting",
                impact="medium",
            )
        ]

        analysis = SortAnalysis(cost=15.0, suggestions=suggestions)

        assert analysis.cost == 15.0
        assert len(analysis.suggestions) == 1


class TestFieldAnalysis:
    """Test FieldAnalysis dataclass."""

    def test_field_analysis_creation(self):
        """Test creating field analysis."""
        suggestions = [
            OptimizationSuggestion(
                type=OptimizationType.FIELD_SELECTION,
                description="Select specific fields",
                impact="low",
            )
        ]

        analysis = FieldAnalysis(cost=10.0, suggestions=suggestions)

        assert analysis.cost == 10.0
        assert len(analysis.suggestions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
