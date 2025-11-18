"""
Tests for the fluent QueryBuilder implementation.
"""

import pytest

from ontologia_sdk.query_builder import (
    FilterCondition,
    PaginationInfo,
    QueryBuilder,
    QueryExecutor,
    RelationshipInclude,
    SortCondition,
    build_filter_dict,
    query,
)


class TestFilterCondition:
    """Test FilterCondition dataclass."""

    def test_filter_condition_creation(self):
        """Test creating a filter condition."""
        condition = FilterCondition(field="name", operator="=", value="John", logical_op="AND")

        assert condition.field == "name"
        assert condition.operator == "="
        assert condition.value == "John"
        assert condition.logical_op == "AND"


class TestSortCondition:
    """Test SortCondition dataclass."""

    def test_sort_condition_creation(self):
        """Test creating a sort condition."""
        sort = SortCondition(field="name", direction="desc")

        assert sort.field == "name"
        assert sort.direction == "desc"


class TestPaginationInfo:
    """Test PaginationInfo dataclass."""

    def test_pagination_creation(self):
        """Test creating pagination info."""
        pagination = PaginationInfo(offset=10, limit=20)

        assert pagination.offset == 10
        assert pagination.limit == 20


class TestRelationshipInclude:
    """Test RelationshipInclude dataclass."""

    def test_relationship_include_creation(self):
        """Test creating a relationship include."""
        include = RelationshipInclude(
            link_type="friend_of", direction="outgoing", fields=["name", "email"]
        )

        assert include.link_type == "friend_of"
        assert include.direction == "outgoing"
        assert include.fields == ["name", "email"]


class TestQueryBuilder:
    """Test QueryBuilder functionality."""

    def test_query_builder_init(self):
        """Test QueryBuilder initialization."""
        builder = QueryBuilder("person")

        assert builder.object_type == "person"
        assert len(builder.filters) == 0
        assert len(builder.sorts) == 0
        assert builder.pagination is None
        assert len(builder.includes) == 0
        assert builder.selected_fields is None

    def test_where_basic(self):
        """Test basic WHERE condition."""
        builder = QueryBuilder("person")
        result = builder.where("name", "=", "John")

        assert result is builder  # Should return self
        assert len(builder.filters) == 1

        filter_condition = builder.filters[0]
        assert filter_condition.field == "name"
        assert filter_condition.operator == "="
        assert filter_condition.value == "John"
        assert filter_condition.logical_op == "AND"

    def test_where_invalid_operator(self):
        """Test WHERE with invalid operator."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Invalid operator"):
            builder.where("name", "invalid_op", "John")

    def test_and_where(self):
        """Test AND WHERE condition."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")
        builder.and_where("age", ">", 25)

        assert len(builder.filters) == 2

        # Second filter should have AND logical operator
        second_filter = builder.filters[1]
        assert second_filter.logical_op == "AND"

    def test_or_where(self):
        """Test OR WHERE condition."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")
        builder.or_where("name", "=", "Jane")

        assert len(builder.filters) == 2

        # Second filter should have OR logical operator
        second_filter = builder.filters[1]
        assert second_filter.logical_op == "OR"

    def test_not_where(self):
        """Test NOT WHERE condition."""
        builder = QueryBuilder("person")
        builder.not_where("status", "=", "inactive")

        assert len(builder.filters) == 1

        filter_condition = builder.filters[0]
        assert filter_condition.logical_op == "NOT"

    def test_where_in(self):
        """Test WHERE IN condition."""
        builder = QueryBuilder("person")
        builder.where_in("status", ["active", "pending"])

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "in"
        assert filter_condition.value == ["active", "pending"]

    def test_where_not_in(self):
        """Test WHERE NOT IN condition."""
        builder = QueryBuilder("person")
        builder.where_not_in("status", ["deleted", "archived"])

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "not_in"

    def test_where_like(self):
        """Test WHERE LIKE condition."""
        builder = QueryBuilder("person")
        builder.where_like("name", "John%")

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "like"
        assert filter_condition.value == "John%"

    def test_where_between(self):
        """Test WHERE BETWEEN condition."""
        builder = QueryBuilder("person")
        builder.where_between("age", 25, 35)

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "between"
        assert filter_condition.value == [25, 35]

    def test_where_null(self):
        """Test WHERE IS NULL condition."""
        builder = QueryBuilder("person")
        builder.where_null("deleted_at")

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "is_null"
        assert filter_condition.value is None

    def test_where_not_null(self):
        """Test WHERE IS NOT NULL condition."""
        builder = QueryBuilder("person")
        builder.where_not_null("email")

        assert len(builder.filters) == 1
        filter_condition = builder.filters[0]
        assert filter_condition.operator == "is_not_null"
        assert filter_condition.value is None

    def test_order_by(self):
        """Test ORDER BY clause."""
        builder = QueryBuilder("person")
        result = builder.order_by("name", "desc")

        assert result is builder
        assert len(builder.sorts) == 1

        sort_condition = builder.sorts[0]
        assert sort_condition.field == "name"
        assert sort_condition.direction == "desc"

    def test_order_by_invalid_direction(self):
        """Test ORDER BY with invalid direction."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Invalid direction"):
            builder.order_by("name", "invalid")

    def test_order_by_asc(self):
        """Test ORDER BY ASC shortcut."""
        builder = QueryBuilder("person")
        builder.order_by_asc("name")

        assert len(builder.sorts) == 1
        assert builder.sorts[0].direction == "asc"

    def test_order_by_desc(self):
        """Test ORDER BY DESC shortcut."""
        builder = QueryBuilder("person")
        builder.order_by_desc("age")

        assert len(builder.sorts) == 1
        assert builder.sorts[0].direction == "desc"

    def test_multiple_order_by(self):
        """Test multiple ORDER BY clauses."""
        builder = QueryBuilder("person")
        builder.order_by("name", "asc").order_by("age", "desc")

        assert len(builder.sorts) == 2
        assert builder.sorts[0].field == "name"
        assert builder.sorts[0].direction == "asc"
        assert builder.sorts[1].field == "age"
        assert builder.sorts[1].direction == "desc"

    def test_limit(self):
        """Test LIMIT clause."""
        builder = QueryBuilder("person")
        result = builder.limit(10)

        assert result is builder
        assert builder.pagination is not None
        assert builder.pagination.limit == 10
        assert builder.pagination.offset == 0

    def test_limit_invalid(self):
        """Test LIMIT with invalid value."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Limit must be positive"):
            builder.limit(0)

        with pytest.raises(ValueError, match="Limit must be positive"):
            builder.limit(-5)

    def test_offset(self):
        """Test OFFSET clause."""
        builder = QueryBuilder("person")
        builder.offset(20)

        assert builder.pagination is not None
        assert builder.pagination.offset == 20
        assert builder.pagination.limit is None

    def test_offset_invalid(self):
        """Test OFFSET with invalid value."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Offset cannot be negative"):
            builder.offset(-1)

    def test_paginate(self):
        """Test paginate method."""
        builder = QueryBuilder("person")
        builder.paginate(page=2, per_page=10)

        assert builder.pagination is not None
        assert builder.pagination.offset == 10  # (2-1) * 10
        assert builder.pagination.limit == 10

    def test_paginate_invalid(self):
        """Test paginate with invalid values."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Page must be >= 1"):
            builder.paginate(page=0, per_page=10)

        with pytest.raises(ValueError, match="Per page must be positive"):
            builder.paginate(page=1, per_page=0)

    def test_select(self):
        """Test field selection."""
        builder = QueryBuilder("person")
        result = builder.select("name", "email", "age")

        assert result is builder
        assert builder.selected_fields == ["name", "email", "age"]

    def test_select_empty(self):
        """Test SELECT with no fields."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="At least one field"):
            builder.select()

    def test_include_related(self):
        """Test including related objects."""
        builder = QueryBuilder("person")
        result = builder.include_related(
            "friend_of", direction="outgoing", fields=["name", "email"]
        )

        assert result is builder
        assert len(builder.includes) == 1

        include = builder.includes[0]
        assert include.link_type == "friend_of"
        assert include.direction == "outgoing"
        assert include.fields == ["name", "email"]

    def test_include_related_invalid_direction(self):
        """Test include_related with invalid direction."""
        builder = QueryBuilder("person")

        with pytest.raises(ValueError, match="Invalid direction"):
            builder.include_related("friend_of", "invalid")

    def test_include_outgoing(self):
        """Test include_outgoing shortcut."""
        builder = QueryBuilder("person")
        builder.include_outgoing("friend_of", ["name"])

        assert len(builder.includes) == 1
        include = builder.includes[0]
        assert include.direction == "outgoing"
        assert include.fields == ["name"]

    def test_include_incoming(self):
        """Test include_incoming shortcut."""
        builder = QueryBuilder("person")
        builder.include_incoming("member_of", ["title"])

        assert len(builder.includes) == 1
        include = builder.includes[0]
        assert include.direction == "incoming"
        assert include.fields == ["title"]

    def test_build_basic(self):
        """Test building basic query."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")

        query = builder.build()

        assert query["object_type"] == "person"
        assert len(query["filters"]) == 1
        assert query["filters"][0]["field"] == "name"
        assert query["filters"][0]["operator"] == "="
        assert query["filters"][0]["value"] == "John"

    def test_build_complex(self):
        """Test building complex query."""
        builder = QueryBuilder("person")
        builder.where("age", ">", 25).order_by("name", "asc").limit(10)

        query = builder.build()

        assert query["object_type"] == "person"
        assert len(query["filters"]) == 1
        assert len(query["sort"]) == 1
        assert query["sort"][0]["field"] == "name"
        assert query["sort"][0]["direction"] == "asc"
        assert query["pagination"]["limit"] == 10

    def test_build_sql_basic(self):
        """Test building SQL-like string."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")

        sql = builder.build_sql()

        assert "SELECT * FROM person" in sql
        assert "WHERE name = 'John'" in sql

    def test_build_sql_complex(self):
        """Test building complex SQL-like string."""
        builder = QueryBuilder("person")
        builder.where("age", ">", 25).order_by("name", "desc").limit(10)

        sql = builder.build_sql()

        assert "SELECT * FROM person" in sql
        assert "WHERE age > 25" in sql
        assert "ORDER BY name DESC" in sql
        assert "LIMIT 10" in sql

    def test_build_sql_special_operators(self):
        """Test SQL generation with special operators."""
        builder = QueryBuilder("person")
        builder.where_in("status", ["active", "pending"])
        builder.where_null("deleted_at")
        builder.where_between("age", 25, 35)

        sql = builder.build_sql()

        assert "status IN ('active', 'pending')" in sql
        assert "deleted_at IS NULL" in sql
        assert "age BETWEEN 25 AND 35" in sql

    def test_copy(self):
        """Test copying query builder."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John").order_by("age", "desc").limit(10)

        copy = builder.copy()

        # Should be equal but not the same object
        assert copy is not builder
        assert copy.object_type == builder.object_type
        assert len(copy.filters) == len(builder.filters)
        assert len(copy.sorts) == len(builder.sorts)
        assert copy.pagination.limit == builder.pagination.limit

    def test_reset(self):
        """Test resetting query builder."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John").order_by("age", "desc").limit(10)

        result = builder.reset()

        assert result is builder
        assert len(builder.filters) == 0
        assert len(builder.sorts) == 0
        assert builder.pagination is None
        assert builder.selected_fields is None
        assert len(builder.includes) == 0

    def test_str_representation(self):
        """Test string representation."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")

        str_repr = str(builder)
        assert "SELECT * FROM person" in str_repr
        assert "WHERE name = 'John'" in str_repr

    def test_repr_representation(self):
        """Test detailed representation."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John").order_by("age", "desc")

        repr_str = repr(builder)
        assert "QueryBuilder(object_type='person'" in repr_str
        assert "filters=1" in repr_str
        assert "sorts=1" in repr_str


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_query_function(self):
        """Test query() convenience function."""
        builder = query("person")

        assert isinstance(builder, QueryBuilder)
        assert builder.object_type == "person"

    def test_build_filter_dict(self):
        """Test build_filter_dict function."""
        filter_dict = build_filter_dict("name", "=", "John")

        expected = {"field": "name", "operator": "=", "value": "John"}

        assert filter_dict == expected


class TestQueryExecutor:
    """Test QueryExecutor functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session."""
        from unittest.mock import AsyncMock

        session = AsyncMock()
        session.list_objects = AsyncMock(return_value=[])
        return session

    @pytest.fixture
    def executor(self, mock_session):
        """Create QueryExecutor with mock session."""
        return QueryExecutor(mock_session)

    @pytest.mark.asyncio
    async def test_executor_execute_basic(self, executor, mock_session):
        """Test basic query execution."""
        builder = QueryBuilder("person")
        builder.where("name", "=", "John")

        await executor.execute(builder)

        # Verify session was called
        mock_session.list_objects.assert_called_once()
        call_args = mock_session.list_objects.call_args
        assert call_args[0][0] == "person"  # object_type
        assert "name" in call_args[1]  # filter

    @pytest.mark.asyncio
    async def test_executor_execute_with_pagination(self, executor, mock_session):
        """Test query execution with pagination."""
        builder = QueryBuilder("person")
        builder.limit(10).offset(20)

        await executor.execute(builder)

        # Verify pagination was passed
        call_args = mock_session.list_objects.call_args
        assert call_args[1]["limit"] == 10
        assert call_args[1]["offset"] == 20

    @pytest.mark.asyncio
    async def test_executor_count(self, executor, mock_session):
        """Test counting query results."""
        # Mock return data
        mock_session.list_objects.return_value = [{"pk": "1"}, {"pk": "2"}, {"pk": "3"}]

        builder = QueryBuilder("person")
        builder.where("status", "=", "active")

        count = await executor.count(builder)

        assert count == 3
        # Should have called without pagination
        call_args = mock_session.list_objects.call_args
        assert "limit" not in call_args[1]
        assert "offset" not in call_args[1]


class TestQueryBuilderChaining:
    """Test method chaining functionality."""

    def test_complex_chaining(self):
        """Test complex method chaining."""
        builder = (
            query("person")
            .where("status", "=", "active")
            .and_where("age", ">=", 18)
            .or_where("special_status", "=", "vip")
            .order_by_asc("name")
            .order_by_desc("created_at")
            .limit(20)
            .offset(10)
            .select("name", "email", "age")
            .include_outgoing("friend_of", ["name"])
        )

        # Verify all conditions were applied
        assert len(builder.filters) == 3
        assert len(builder.sorts) == 2
        assert builder.pagination.limit == 20
        assert builder.pagination.offset == 10
        assert builder.selected_fields == ["name", "email", "age"]
        assert len(builder.includes) == 1

        # Verify logical operators
        assert builder.filters[0].logical_op == "AND"
        assert builder.filters[1].logical_op == "AND"
        assert builder.filters[2].logical_op == "OR"

    def test_chaining_with_copy_and_reset(self):
        """Test chaining with copy and reset operations."""
        builder = query("person").where("status", "=", "active").limit(10)

        # Copy and modify
        copy_builder = builder.copy().and_where("age", ">", 25).order_by("name")

        # Original should be unchanged
        assert len(builder.filters) == 1
        assert len(builder.sorts) == 0

        # Copy should have additional conditions
        assert len(copy_builder.filters) == 2
        assert len(copy_builder.sorts) == 1

        # Reset and rebuild
        reset_result = copy_builder.reset().where("department", "=", "engineering").limit(5)

        assert reset_result is copy_builder
        assert len(copy_builder.filters) == 1
        assert copy_builder.filters[0].field == "department"
        assert copy_builder.pagination.limit == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
