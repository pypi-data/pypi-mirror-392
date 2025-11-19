from __future__ import annotations

from collections import defaultdict
from typing import Any

from ontologia_api.services.instances_service import InstancesService
from ontologia_api.v2.schemas.instances import ObjectReadResponse
from ontologia_api.v2.schemas.search import (
    AggregateRequest,
    AggregateResponse,
    AggregateRow,
    AggregateSpec,
    WhereCondition,
)

__all__ = ["AnalyticsService"]


class AnalyticsService:
    """Lightweight analytics adapter providing aggregate operations for API v2."""

    def __init__(
        self,
        session,
        *,
        service: str = "ontology",
        instance: str = "default",
        principal: Any | None = None,
    ) -> None:
        self._service = service
        self._instance = instance
        self._instances = InstancesService(
            session,
            service=service,
            instance=instance,
            principal=principal,
        )

    def aggregate(self, request: AggregateRequest) -> AggregateResponse:
        data = self._instances.list_objects(
            request.objectTypeApiName,
            limit=10_000,
        ).data
        filtered = self._apply_where(data, request.where)
        rows = self._compute_groups(filtered, request.groupBy, request.metrics)
        return AggregateResponse(rows=rows)

    def _apply_where(
        self,
        items: list[ObjectReadResponse],
        conditions: list[WhereCondition],
    ) -> list[ObjectReadResponse]:
        if not conditions:
            return list(items)

        def matches(item: ObjectReadResponse) -> bool:
            props = item.properties or {}
            for cond in conditions:
                value = props.get(cond.property)
                op = cond.op
                expected = cond.value
                if op == "eq" and value != expected:
                    return False
                elif op == "ne" and value == expected:
                    return False
                elif op == "in":
                    if not isinstance(expected, (list, tuple, set)) or value not in expected:
                        return False
                elif op == "contains":
                    if (
                        not isinstance(value, str)
                        or not isinstance(expected, str)
                        or expected not in value
                    ):
                        return False
                elif op == "startswith":
                    if (
                        not isinstance(value, str)
                        or not isinstance(expected, str)
                        or not value.startswith(expected)
                    ):
                        return False
                elif op == "endswith":
                    if (
                        not isinstance(value, str)
                        or not isinstance(expected, str)
                        or not value.endswith(expected)
                    ):
                        return False
                elif op in {"gt", "gte", "lt", "lte"}:
                    if value is None:
                        return False
                    try:
                        if op == "gt" and not (value > expected):
                            return False
                        if op == "gte" and not (value >= expected):
                            return False
                        if op == "lt" and not (value < expected):
                            return False
                        if op == "lte" and not (value <= expected):
                            return False
                    except Exception:
                        return False
                elif op in {"isnull", "isnotnull"}:
                    is_null = value is None
                    if op == "isnull" and not is_null:
                        return False
                    if op == "isnotnull" and is_null:
                        return False
                # unsupported operators are ignored (treated as pass-through)
            return True

        return [item for item in items if matches(item)]

    def _compute_groups(
        self,
        items: list[ObjectReadResponse],
        group_by: list[str],
        metrics: list[AggregateSpec],
    ) -> list[AggregateRow]:
        if not metrics:
            return []

        groups = defaultdict(list)
        for item in items:
            props = item.properties or {}
            key = tuple((field, props.get(field)) for field in group_by)
            groups[key].append(props)

        rows: list[AggregateRow] = []
        for key, group_items in groups.items():
            group_dict = {field: value for field, value in key}
            metrics_map: dict[str, float | int] = {}

            for spec in metrics:
                metric_key = self._metric_key(spec)
                if spec.func == "count":
                    metrics_map[metric_key] = len(group_items)
                else:
                    values = [props.get(spec.property) for props in group_items]
                    numeric = [v for v in values if isinstance(v, (int, float))]
                    if spec.func == "sum":
                        metrics_map[metric_key] = float(sum(numeric))
                    elif spec.func == "avg":
                        metrics_map[metric_key] = (
                            float(sum(numeric) / len(numeric)) if numeric else 0.0
                        )

            rows.append(AggregateRow(group=group_dict, metrics=metrics_map))

        return rows

    @staticmethod
    def _metric_key(spec: AggregateSpec) -> str:
        if spec.func == "count":
            return "count"
        prop = spec.property or ""
        return f"{spec.func}({prop})"
