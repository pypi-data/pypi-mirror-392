"""
Fluent QueryBuilder for constructing complex ontology queries.

Provides a type-safe, chainable interface for building queries
with support for filtering, sorting, pagination, and relationships.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FilterCondition:
    """Represents a single filter condition."""

    field: str
    operator: str
    value: Any
    logical_op: str = "AND"  # AND, OR, NOT


@dataclass
class SortCondition:
    """Represents a sorting condition."""

    field: str
    direction: str = "asc"  # asc, desc


@dataclass
class PaginationInfo:
    """Represents pagination parameters."""

    offset: int = 0
    limit: int | None = None


@dataclass
class RelationshipInclude:
    """Represents a relationship to include in results."""

    link_type: str
    direction: str = "outgoing"  # outgoing, incoming, both
    fields: list[str] | None = None


class QueryBuilder:
    """
    Fluent query builder for ontology operations.

    Provides a chainable interface for building complex queries
    with type safety and validation.
    """

    def __init__(self, object_type: str):
        """
        Initialize query builder for a specific object type.

        Args:
            object_type: The API name of the object type to query
        """
        self.object_type = object_type
        self.filters: list[FilterCondition] = []
        self.sorts: list[SortCondition] = []
        self.pagination: PaginationInfo | None = None
        self.includes: list[RelationshipInclude] = []
        self.selected_fields: list[str] | None = None
        self._current_logical_op = "AND"

    def where(self, field: str, operator: str, value: Any) -> QueryBuilder:
        """
        Add a WHERE condition to the query.

        Args:
            field: Field name to filter on
            operator: Comparison operator (=, !=, >, <, >=, <=, like, in, not_in)
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        # Validate operator
        valid_operators = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "like",
            "ilike",
            "in",
            "not_in",
            "is_null",
            "is_not_null",
            "between",
        }

        if operator not in valid_operators:
            raise ValueError(f"Invalid operator: {operator}. Valid operators: {valid_operators}")

        condition = FilterCondition(
            field=field, operator=operator, value=value, logical_op=self._current_logical_op
        )

        self.filters.append(condition)
        self._current_logical_op = "AND"  # Reset to default

        return self

    def and_where(self, field: str, operator: str, value: Any) -> QueryBuilder:
        """
        Add an AND WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_logical_op = "AND"
        return self.where(field, operator, value)

    def or_where(self, field: str, operator: str, value: Any) -> QueryBuilder:
        """
        Add an OR WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_logical_op = "OR"
        return self.where(field, operator, value)

    def not_where(self, field: str, operator: str, value: Any) -> QueryBuilder:
        """
        Add a NOT WHERE condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._current_logical_op = "NOT"
        return self.where(field, operator, value)

    def where_in(self, field: str, values: list[Any]) -> QueryBuilder:
        """
        Add a WHERE field IN (values) condition.

        Args:
            field: Field name to filter on
            values: List of values to match

        Returns:
            Self for method chaining
        """
        return self.where(field, "in", values)

    def where_not_in(self, field: str, values: list[Any]) -> QueryBuilder:
        """
        Add a WHERE field NOT IN (values) condition.

        Args:
            field: Field name to filter on
            values: List of values to exclude

        Returns:
            Self for method chaining
        """
        return self.where(field, "not_in", values)

    def where_like(self, field: str, pattern: str) -> QueryBuilder:
        """
        Add a WHERE field LIKE pattern condition.

        Args:
            field: Field name to filter on
            pattern: SQL LIKE pattern (use % for wildcards)

        Returns:
            Self for method chaining
        """
        return self.where(field, "like", pattern)

    def where_between(self, field: str, start: Any, end: Any) -> QueryBuilder:
        """
        Add a WHERE field BETWEEN start AND end condition.

        Args:
            field: Field name to filter on
            start: Start value (inclusive)
            end: End value (inclusive)

        Returns:
            Self for method chaining
        """
        return self.where(field, "between", [start, end])

    def where_null(self, field: str) -> QueryBuilder:
        """
        Add a WHERE field IS NULL condition.

        Args:
            field: Field name to check for null

        Returns:
            Self for method chaining
        """
        return self.where(field, "is_null", None)

    def where_not_null(self, field: str) -> QueryBuilder:
        """
        Add a WHERE field IS NOT NULL condition.

        Args:
            field: Field name to check for not null

        Returns:
            Self for method chaining
        """
        return self.where(field, "is_not_null", None)

    def order_by(self, field: str, direction: str = "asc") -> QueryBuilder:
        """
        Add ORDER BY clause to the query.

        Args:
            field: Field name to sort by
            direction: Sort direction ("asc" or "desc")

        Returns:
            Self for method chaining
        """
        if direction not in ["asc", "desc"]:
            raise ValueError(f"Invalid direction: {direction}. Use 'asc' or 'desc'")

        sort = SortCondition(field=field, direction=direction)
        self.sorts.append(sort)

        return self

    def order_by_asc(self, field: str) -> QueryBuilder:
        """
        Add ORDER BY field ASC clause.

        Args:
            field: Field name to sort ascending

        Returns:
            Self for method chaining
        """
        return self.order_by(field, "asc")

    def order_by_desc(self, field: str) -> QueryBuilder:
        """
        Add ORDER BY field DESC clause.

        Args:
            field: Field name to sort descending

        Returns:
            Self for method chaining
        """
        return self.order_by(field, "desc")

    def limit(self, count: int) -> QueryBuilder:
        """
        Set LIMIT clause for the query.

        Args:
            count: Maximum number of results to return

        Returns:
            Self for method chaining
        """
        if count <= 0:
            raise ValueError("Limit must be positive")

        if self.pagination is None:
            self.pagination = PaginationInfo()

        self.pagination.limit = count
        return self

    def offset(self, count: int) -> QueryBuilder:
        """
        Set OFFSET clause for the query.

        Args:
            count: Number of results to skip

        Returns:
            Self for method chaining
        """
        if count < 0:
            raise ValueError("Offset cannot be negative")

        if self.pagination is None:
            self.pagination = PaginationInfo()

        self.pagination.offset = count
        return self

    def paginate(self, page: int, per_page: int) -> QueryBuilder:
        """
        Set pagination using page-based parameters.

        Args:
            page: Page number (1-based)
            per_page: Results per page

        Returns:
            Self for method chaining
        """
        if page < 1:
            raise ValueError("Page must be >= 1")
        if per_page <= 0:
            raise ValueError("Per page must be positive")

        offset = (page - 1) * per_page

        if self.pagination is None:
            self.pagination = PaginationInfo()

        self.pagination.offset = offset
        self.pagination.limit = per_page

        return self

    def select(self, *fields: str) -> QueryBuilder:
        """
        Set fields to select in the query.

        Args:
            *fields: Field names to include in results

        Returns:
            Self for method chaining
        """
        if not fields:
            raise ValueError("At least one field must be specified")

        self.selected_fields = list(fields)
        return self

    def include_related(
        self, link_type: str, direction: str = "outgoing", fields: list[str] | None = None
    ) -> QueryBuilder:
        """
        Include related objects in the query results.

        Args:
            link_type: Type of link to follow
            direction: Direction to follow links ("outgoing", "incoming", "both")
            fields: Optional list of fields to include from related objects

        Returns:
            Self for method chaining
        """
        if direction not in ["outgoing", "incoming", "both"]:
            raise ValueError(
                f"Invalid direction: {direction}. Use 'outgoing', 'incoming', or 'both'"
            )

        include = RelationshipInclude(link_type=link_type, direction=direction, fields=fields)

        self.includes.append(include)
        return self

    def include_outgoing(self, link_type: str, fields: list[str] | None = None) -> QueryBuilder:
        """
        Include outgoing related objects.

        Args:
            link_type: Type of link to follow
            fields: Optional fields to include from related objects

        Returns:
            Self for method chaining
        """
        return self.include_related(link_type, "outgoing", fields)

    def include_incoming(self, link_type: str, fields: list[str] | None = None) -> QueryBuilder:
        """
        Include incoming related objects.

        Args:
            link_type: Type of link to follow
            fields: Optional fields to include from related objects

        Returns:
            Self for method chaining
        """
        return self.include_related(link_type, "incoming", fields)

    def build(self) -> dict[str, Any]:
        """
        Build the query into a dictionary format.

        Returns:
            Query dictionary ready for execution
        """
        query = {
            "object_type": self.object_type,
        }

        # Add filters
        if self.filters:
            query["filters"] = [
                {
                    "field": f.field,
                    "operator": f.operator,
                    "value": f.value,
                    "logical_op": f.logical_op,
                }
                for f in self.filters
            ]

        # Add sorting
        if self.sorts:
            query["sort"] = [{"field": s.field, "direction": s.direction} for s in self.sorts]

        # Add pagination
        if self.pagination:
            query["pagination"] = {"offset": self.pagination.offset, "limit": self.pagination.limit}

        # Add field selection
        if self.selected_fields:
            query["fields"] = self.selected_fields

        # Add relationship includes
        if self.includes:
            query["includes"] = [
                {"link_type": inc.link_type, "direction": inc.direction, "fields": inc.fields}
                for inc in self.includes
            ]

        return query

    def build_sql(self) -> str:
        """
        Build the query as a SQL-like string (for debugging).

        Returns:
            SQL-like representation of the query
        """
        parts = [f"SELECT * FROM {self.object_type}"]

        # WHERE clause
        if self.filters:
            where_parts = []
            for f in self.filters:
                if f.operator == "is_null":
                    condition = f"{f.field} IS NULL"
                elif f.operator == "is_not_null":
                    condition = f"{f.field} IS NOT NULL"
                elif f.operator == "in":
                    values_str = ", ".join(repr(v) for v in f.value)
                    condition = f"{f.field} IN ({values_str})"
                elif f.operator == "not_in":
                    values_str = ", ".join(repr(v) for v in f.value)
                    condition = f"{f.field} NOT IN ({values_str})"
                elif f.operator == "between":
                    condition = f"{f.field} BETWEEN {repr(f.value[0])} AND {repr(f.value[1])}"
                else:
                    condition = f"{f.field} {f.operator} {repr(f.value)}"

                if f.logical_op != "AND":
                    condition = f"{f.logical_op} {condition}"

                where_parts.append(condition)

            parts.append(f"WHERE {' '.join(where_parts)}")

        # ORDER BY clause
        if self.sorts:
            sort_parts = [f"{s.field} {s.direction.upper()}" for s in self.sorts]
            parts.append(f"ORDER BY {', '.join(sort_parts)}")

        # LIMIT and OFFSET
        if self.pagination:
            if self.pagination.limit:
                parts.append(f"LIMIT {self.pagination.limit}")
            if self.pagination.offset > 0:
                parts.append(f"OFFSET {self.pagination.offset}")

        return " ".join(parts)

    def copy(self) -> QueryBuilder:
        """
        Create a copy of the query builder.

        Returns:
            New QueryBuilder instance with same conditions
        """
        new_builder = QueryBuilder(self.object_type)
        new_builder.filters = self.filters.copy()
        new_builder.sorts = self.sorts.copy()
        new_builder.pagination = self.pagination
        new_builder.includes = self.includes.copy()
        new_builder.selected_fields = self.selected_fields.copy() if self.selected_fields else None
        new_builder._current_logical_op = self._current_logical_op

        return new_builder

    def reset(self) -> QueryBuilder:
        """
        Reset the query builder to initial state.

        Returns:
            Self for method chaining
        """
        self.filters.clear()
        self.sorts.clear()
        self.pagination = None
        self.includes.clear()
        self.selected_fields = None
        self._current_logical_op = "AND"

        return self

    def __str__(self) -> str:
        """String representation of the query."""
        return self.build_sql()

    def __repr__(self) -> str:
        """Detailed representation of the query builder."""
        return f"QueryBuilder(object_type='{self.object_type}', filters={len(self.filters)}, sorts={len(self.sorts)})"


# Convenience functions


def query(object_type: str) -> QueryBuilder:
    """
    Create a new QueryBuilder for the given object type.

    Args:
        object_type: API name of the object type to query

    Returns:
        New QueryBuilder instance
    """
    return QueryBuilder(object_type)


def build_filter_dict(field: str, operator: str, value: Any) -> dict[str, Any]:
    """
    Build a filter dictionary for use with ClientSession.

    Args:
        field: Field name to filter on
        operator: Comparison operator
        value: Value to compare against

    Returns:
        Filter dictionary
    """
    return {"field": field, "operator": operator, "value": value}


# Query execution helper


class QueryExecutor:
    """
    Helper class for executing queries with a ClientSession.

    Provides methods to execute QueryBuilder instances and handle results.
    """

    def __init__(self, session):
        """
        Initialize executor with a ClientSession.

        Args:
            session: ClientSession instance for executing queries
        """
        self.session = session

    async def execute(self, query_builder: QueryBuilder) -> list[dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            query_builder: QueryBuilder instance

        Returns:
            List of query results
        """
        query = query_builder.build()

        # Convert QueryBuilder format to session format
        filters = {}
        for filter_dict in query.get("filters", []):
            field = filter_dict["field"]
            operator = filter_dict["operator"]
            value = filter_dict["value"]

            # Convert to session filter format
            if operator == "=":
                filters[field] = value
            elif operator == "in":
                filters[f"{field}__in"] = value
            elif operator == "like":
                filters[f"{field}__like"] = value
            else:
                # For other operators, use a more complex format
                filters[f"{field}__{operator}"] = value

        # Add pagination to filters
        if query.get("pagination"):
            filters.update(query["pagination"])

        return await self.session.list_objects(query["object_type"], **filters)

    async def count(self, query_builder: QueryBuilder) -> int:
        """
        Execute a query and return count of results.

        Args:
            query_builder: QueryBuilder instance

        Returns:
            Number of matching results
        """
        # Remove pagination for count
        count_query = query_builder.copy()
        count_query.pagination = None

        results = await self.execute(count_query)
        return len(results)
