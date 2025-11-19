"""
instances_repository.py
------------------------
Graph-based repository for object instances using graph databases.

Provides high-performance graph operations for object instances with
relationship traversal, pattern matching, and graph analytics capabilities.
"""

from __future__ import annotations

import builtins
import json
import logging
import os
from typing import Any

from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance

logger = logging.getLogger(__name__)

_TRUTHY = {"1", "true", "yes", "on", "t", "y"}

try:  # Local import to avoid heavy configuration lookups during tests
    from ontologia.config import use_unified_graph_enabled as _config_unified_enabled
except Exception:  # pragma: no cover - defensive fallback for minimal environments

    def _config_unified_enabled() -> bool:
        return True


class GraphInstancesRepository(ObjectInstanceRepository):
    """
    Graph database implementation for object instance storage and retrieval.

    Leverages graph databases for efficient relationship traversal and
    complex pattern matching queries across object instances.
    """

    def __init__(
        self,
        graph_client: Any | None = None,
        session_factory: Any | None = None,
        **legacy_kwargs: Any,
    ):
        """
        Initialize graph instances repository.

        Args:
            graph_client: Graph database client (Neo4j, KuzuDB, etc.)
            session_factory: Session factory for database operations
        """
        if graph_client is None:
            graph_client = legacy_kwargs.get("kuzu_repo") or legacy_kwargs.get("graph_client")
        if session_factory is None:
            session_factory = legacy_kwargs.get("session") or legacy_kwargs.get("session_factory")

        self.graph_client = graph_client
        self.session_factory = session_factory
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _graph_client(self) -> Any | None:
        client = self.graph_client
        if client is None or not hasattr(client, "execute"):
            return None
        availability = getattr(client, "is_available", None)
        if callable(availability):
            try:
                if not availability():
                    return None
            except Exception:  # pragma: no cover - defensive logging
                self.logger.debug("Graph availability probe failed", exc_info=True)
                return None
        return client

    def is_available(self) -> bool:
        return self._graph_client() is not None

    def _unified_graph_enabled(self) -> bool:
        env_override = os.getenv("USE_UNIFIED_GRAPH")
        if env_override is not None:
            return env_override.strip().lower() in _TRUTHY
        try:
            return bool(_config_unified_enabled())
        except Exception:  # pragma: no cover - defensive fallback
            return True

    @staticmethod
    def _quote_identifier(name: str) -> str:
        if not name:
            return "id"
        safe = name.strip()
        if safe.isidentifier():
            return safe
        escaped = safe.replace("`", "``")
        return f"`{escaped}`"

    @staticmethod
    def _label_expr(label: str) -> str:
        if not label:
            return "Object"
        safe = label.strip()
        if safe.isidentifier():
            return safe
        escaped = safe.replace("`", "``")
        return f"`{escaped}`"

    def _run_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        client = self._graph_client()
        if client is None:
            return []
        try:
            if params is None:
                result = client.execute(query)
            else:
                try:
                    result = client.execute(query, params)
                except TypeError:
                    # Some clients (older kuzu builds) do not accept params
                    result = client.execute(query)
        except Exception:
            self.logger.debug("Graph query failed: %s", query, exc_info=True)
            return []
        return self._rows_from_result(result)

    def _rows_from_result(self, result: Any) -> list[dict[str, Any]]:
        if result is None:
            return []
        df = None
        get_df = getattr(result, "get_as_df", None)
        if callable(get_df):
            df = get_df()
        elif hasattr(result, "df"):
            df = result.df
        if df is None:
            return []
        try:
            length = len(df)
        except TypeError:
            shape = getattr(df, "shape", None)
            length = shape[0] if shape else 0
        columns = list(getattr(df, "columns", []) or [])
        rows: list[dict[str, Any]] = []
        for idx in range(length or 0):
            try:
                row_obj = df[idx]
            except Exception:  # pragma: no cover - defensive logging
                self.logger.debug("Graph row fetch failed at index %s", idx, exc_info=True)
                continue
            rows.append(self._row_to_dict(row_obj, columns))
        return rows

    @staticmethod
    def _row_to_dict(row_obj: Any, columns: list[str]) -> dict[str, Any]:
        if isinstance(row_obj, dict):
            return dict(row_obj)
        data: dict[str, Any] = {}
        getter = getattr(row_obj, "get", None)
        if callable(getter):
            for col in columns:
                data[col] = getter(col)
            return data
        for col in columns:
            if hasattr(row_obj, col):
                data[col] = getattr(row_obj, col)
            elif hasattr(row_obj, "__getitem__"):
                try:
                    data[col] = row_obj[col]
                except Exception:
                    data[col] = None
            else:
                data[col] = None
        return data

    @staticmethod
    def _parse_properties(raw: Any) -> dict[str, Any]:
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return dict(raw)
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}
        if hasattr(raw, "to_dict"):
            try:
                return dict(raw.to_dict())  # type: ignore[arg-type]
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

    def _payloads_from_rows(
        self,
        rows: list[dict[str, Any]],
        *,
        default_type: str | None = None,
    ) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for row in rows:
            payloads.append(self._hydrate_row(row, default_type=default_type))
        return payloads

    def _hydrate_row(
        self,
        row: dict[str, Any],
        *,
        default_type: str | None = None,
    ) -> dict[str, Any]:
        props = self._parse_properties(row.get("properties"))
        rid = row.get("rid") or row.get("objectRid") or row.get("object_rid")
        if rid is None and "ogmRid" in row:
            rid = row.get("ogmRid")
        pk_value = row.get("pkValue") or row.get("pk_value")
        if pk_value is None:
            pk_value = row.get("primary_key_value")
        if pk_value is None:
            pk_value = props.get("pkValue") or props.get("pk_value")
        inferred_type = row.get("objectTypeApiName")
        if inferred_type is None:
            inferred_type = self._extract_type_from_labels(row.get("labels") or row.get("_labels"))
        if inferred_type is None:
            inferred_type = default_type
        payload = {
            "objectTypeApiName": inferred_type,
            "pkValue": pk_value,
            "properties": props,
            "rid": rid,
        }
        return payload

    @staticmethod
    def _extract_type_from_labels(labels_value: Any) -> str | None:
        labels: list[str] = []
        if isinstance(labels_value, (list, tuple, set)):
            labels = [str(label) for label in labels_value]
        elif isinstance(labels_value, str):
            labels = [labels_value]
        if not labels:
            return None
        for label in labels:
            # Prefer non-generic labels (anything other than Object/Interface)
            if label and label not in {"Object", "Interface"}:
                return label
        return labels[0]

    def _edge_payloads_from_rows(
        self,
        rows: list[dict[str, Any]],
        *,
        default_source: str | None = None,
        default_target: str | None = None,
        property_names: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        filtered_keys = set(property_names or ())
        payloads: list[dict[str, Any]] = []
        for row in rows:
            props = self._parse_properties(row.get("properties"))
            if filtered_keys:
                props = {key: value for key, value in props.items() if key in filtered_keys}
            link_rid = row.get("rid") or row.get("edgeRid")
            payloads.append(
                {
                    "fromObjectType": row.get("fromObjectType") or default_source,
                    "toObjectType": row.get("toObjectType") or default_target,
                    "fromPk": row.get("fromPk") or props.get("fromPk"),
                    "toPk": row.get("toPk") or props.get("toPk"),
                    "properties": props,
                    "rid": link_rid,
                    "linkProperties": props,
                    "linkRid": link_rid,
                }
            )
        return payloads

    def _link_target_payloads_from_rows(
        self,
        rows: list[dict[str, Any]],
        *,
        default_anchor_type: str | None,
        default_neighbor_type: str | None,
        anchor_pk_value: str | None,
        direction: str,
    ) -> list[dict[str, Any]]:
        inverse = str(direction or "forward").lower() in {"inverse", "incoming", "reverse"}
        payloads: list[dict[str, Any]] = []
        for row in rows:
            anchor_type = row.get("anchorType") or default_anchor_type
            neighbor_type = row.get("neighborType") or default_neighbor_type
            anchor_pk = row.get("anchorPk") or anchor_pk_value
            neighbor_pk = row.get("neighborPk") or row.get("pkValue")
            if neighbor_pk is None:
                continue
            node_props = self._parse_properties(
                row.get("neighborProperties") or row.get("properties")
            )
            edge_props = self._parse_properties(row.get("edgeProperties"))
            neighbor_rid = row.get("neighborRid") or row.get("rid")
            link_rid = row.get("edgeRid") or row.get("rid")
            payloads.append(
                {
                    "objectTypeApiName": neighbor_type,
                    "pkValue": neighbor_pk,
                    "properties": node_props,
                    "rid": neighbor_rid,
                    "fromObjectType": neighbor_type if inverse else anchor_type,
                    "fromPk": neighbor_pk if inverse else anchor_pk,
                    "toObjectType": anchor_type if inverse else neighbor_type,
                    "toPk": anchor_pk if inverse else neighbor_pk,
                    "linkProperties": edge_props,
                    "linkRid": link_rid,
                }
            )
        return payloads

    def list_by_interface(
        self,
        interface_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List object instances implementing a given interface using graph data."""

        queries: list[tuple[str, dict[str, Any]]] = []
        if self._unified_graph_enabled():
            queries.append(
                (
                    "MATCH (o:Object)\n"
                    "WHERE $interface IN o.labels\n"
                    "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties, o.objectRid AS rid, o.labels AS labels\n"
                    "ORDER BY o.pkValue\n"
                    "SKIP $offset\n"
                    "LIMIT $limit",
                    {"interface": interface_api_name, "limit": limit, "offset": offset},
                )
            )

        # Fallback: treat interface as additional label on the node
        label = self._label_expr(interface_api_name)
        queries.append(
            (
                f"MATCH (o:{label})\n"
                "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, properties(o) AS properties, coalesce(o.rid, o.objectRid) AS rid, labels(o) AS _labels\n"
                "ORDER BY COALESCE(o.pkValue, o.id)\n"
                "SKIP $offset\n"
                "LIMIT $limit",
                {"offset": offset, "limit": limit},
            )
        )

        rows: list[dict[str, Any]] = []
        for query, params in queries:
            rows = self._run_query(query, params)
            if rows:
                break

        if not rows:
            return []

        return self._payloads_from_rows(rows)

    def list_by_type(
        self,
        object_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if not self.is_available():
            return []

        queries: list[tuple[str, dict[str, Any]]] = []
        if self._unified_graph_enabled():
            queries.append(
                (
                    "MATCH (o:Object)\n"
                    "WHERE o.objectTypeApiName = $objectType\n"
                    "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties, o.objectRid AS rid\n"
                    "ORDER BY o.pkValue\n"
                    "SKIP $offset\n"
                    "LIMIT $limit",
                    {
                        "objectType": object_type_api_name,
                        "limit": limit,
                        "offset": offset,
                    },
                )
            )

        label = self._label_expr(object_type_api_name)
        pk_field = self._quote_identifier("id")
        queries.append(
            (
                f"MATCH (o:{label})\n"
                f"RETURN $objectType AS objectTypeApiName, COALESCE(o.pkValue, o.{pk_field}) AS pkValue, properties(o) AS properties, coalesce(o.rid, o.objectRid) AS rid\n"
                f"ORDER BY COALESCE(o.pkValue, o.{pk_field})\n"
                "SKIP $offset\n"
                "LIMIT $limit",
                {
                    "objectType": object_type_api_name,
                    "limit": limit,
                    "offset": offset,
                },
            )
        )

        rows: list[dict[str, Any]] = []
        for query, params in queries:
            rows = self._run_query(query, params)
            if rows:
                break

        if not rows:
            return []

        return self._payloads_from_rows(rows, default_type=object_type_api_name)

    def get_linked_objects(
        self,
        from_label: str,
        from_pk_field: str,
        from_pk_value: str,
        link_label: str,
        to_label: str,
        direction: str = "forward",
        *,
        limit: int = 100,
        offset: int = 0,
        property_names: Any | None = None,  # backward compat signature
    ) -> list[dict[str, Any]]:
        if not self.is_available():
            return []

        inverse = str(direction or "forward").lower() in {"inverse", "incoming", "reverse"}

        queries: list[tuple[str, dict[str, Any]]] = []
        rel = self._label_expr(link_label)
        anchor_type_value = to_label if inverse else from_label
        neighbor_type_value = from_label if inverse else to_label
        if self._unified_graph_enabled():
            if inverse:
                queries.append(
                    (
                        f"MATCH (anchor:Object)<-[r:{rel}]-(neighbor:Object)\n"
                        "WHERE anchor.objectTypeApiName = $anchorType AND anchor.pkValue = $anchorPk\n"
                        "  AND neighbor.objectTypeApiName = $neighborType\n"
                        "RETURN anchor.objectTypeApiName AS anchorType, anchor.pkValue AS anchorPk,\n"
                        "       neighbor.objectTypeApiName AS neighborType, neighbor.pkValue AS neighborPk,\n"
                        "       neighbor.properties AS neighborProperties, neighbor.objectRid AS neighborRid,\n"
                        "       r.properties AS edgeProperties, r.rid AS edgeRid\n"
                        "ORDER BY neighbor.pkValue\n"
                        "SKIP $offset\n"
                        "LIMIT $limit",
                        {
                            "anchorType": anchor_type_value,
                            "neighborType": neighbor_type_value,
                            "anchorPk": from_pk_value,
                            "offset": offset,
                            "limit": limit,
                        },
                    )
                )
            else:
                queries.append(
                    (
                        f"MATCH (anchor:Object)-[r:{rel}]->(neighbor:Object)\n"
                        "WHERE anchor.objectTypeApiName = $anchorType AND anchor.pkValue = $anchorPk\n"
                        "  AND neighbor.objectTypeApiName = $neighborType\n"
                        "RETURN anchor.objectTypeApiName AS anchorType, anchor.pkValue AS anchorPk,\n"
                        "       neighbor.objectTypeApiName AS neighborType, neighbor.pkValue AS neighborPk,\n"
                        "       neighbor.properties AS neighborProperties, neighbor.objectRid AS neighborRid,\n"
                        "       r.properties AS edgeProperties, r.rid AS edgeRid\n"
                        "ORDER BY neighbor.pkValue\n"
                        "SKIP $offset\n"
                        "LIMIT $limit",
                        {
                            "anchorType": anchor_type_value,
                            "neighborType": neighbor_type_value,
                            "anchorPk": from_pk_value,
                            "offset": offset,
                            "limit": limit,
                        },
                    )
                )

        anchor_label = self._label_expr(anchor_type_value)
        neighbor_label = self._label_expr(neighbor_type_value)
        pk_identifier = self._quote_identifier(from_pk_field or "id")
        neighbor_pk_field = self._quote_identifier((from_pk_field if inverse else None) or "id")
        if inverse:
            pattern = (
                f"MATCH (anchor:{anchor_label})<-[:{rel}]-(neighbor:{neighbor_label})\n"
                f"WHERE anchor.{pk_identifier} = $anchorPk\n"
            )
        else:
            pattern = (
                f"MATCH (anchor:{anchor_label})-[:{rel}]->(neighbor:{neighbor_label})\n"
                f"WHERE anchor.{pk_identifier} = $anchorPk\n"
            )
        queries.append(
            (
                pattern
                + "RETURN $anchorType AS anchorType, $anchorPk AS anchorPk,\n"
                + "       $neighborType AS neighborType, COALESCE(neighbor.pkValue, neighbor."
                + neighbor_pk_field
                + ") AS neighborPk,\n"
                + "       properties(neighbor) AS neighborProperties, coalesce(neighbor.rid, neighbor.objectRid) AS neighborRid,\n"
                + "       rel.properties AS edgeProperties, rel.rid AS edgeRid\n"
                + "ORDER BY neighborPk\n"
                + "SKIP $offset\n"
                + "LIMIT $limit",
                {
                    "anchorType": anchor_type_value,
                    "neighborType": neighbor_type_value,
                    "anchorPk": from_pk_value,
                    "offset": offset,
                    "limit": limit,
                },
            )
        )

        rows: list[dict[str, Any]] = []
        for query, params in queries:
            rows = self._run_query(query, params)
            if rows:
                break

        if not rows:
            return []

        return self._link_target_payloads_from_rows(
            rows,
            default_anchor_type=anchor_type_value,
            default_neighbor_type=neighbor_type_value,
            anchor_pk_value=from_pk_value,
            direction=direction,
        )

    def list_edges(
        self,
        link_label: str,
        source_label: str | None = None,
        target_label: str | None = None,
        source_pk_field: str | None = None,
        target_pk_field: str | None = None,
        *,
        limit: int = 100,
        offset: int = 0,
        property_names: tuple[str, ...] | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not self.is_available():
            return []

        props_filter: tuple[str, ...] | None = None
        if property_names:
            if isinstance(property_names, tuple):
                props_filter = property_names
            else:
                props_filter = tuple(property_names)

        queries: list[tuple[str, dict[str, Any]]] = []
        rel = self._label_expr(link_label)
        if self._unified_graph_enabled():
            queries.append(
                (
                    f"MATCH (source:Object)-[rel:{rel}]->(target:Object)\n"
                    "WHERE ($sourceLabel IS NULL OR source.objectTypeApiName = $sourceLabel)\n"
                    "  AND ($targetLabel IS NULL OR target.objectTypeApiName = $targetLabel)\n"
                    "RETURN source.objectTypeApiName AS fromObjectType, source.pkValue AS fromPk,\n"
                    "       target.objectTypeApiName AS toObjectType, target.pkValue AS toPk,\n"
                    "       rel.properties AS properties, rel.rid AS rid\n"
                    "ORDER BY fromPk, toPk\n"
                    "SKIP $offset\n"
                    "LIMIT $limit",
                    {
                        "sourceLabel": source_label,
                        "targetLabel": target_label,
                        "offset": offset,
                        "limit": limit,
                    },
                )
            )

        source_pk = self._quote_identifier(source_pk_field or "id")
        target_pk = self._quote_identifier(target_pk_field or "id")
        source_label_value = source_label or "Object"
        target_label_value = target_label or "Object"
        source_node_label = self._label_expr(source_label_value)
        target_node_label = self._label_expr(target_label_value)
        queries.append(
            (
                f"MATCH (source:{source_node_label})-[rel:{rel}]->(target:{target_node_label})\n"
                f"RETURN $sourceLabel AS fromObjectType, source.{source_pk} AS fromPk,\n"
                f"       $targetLabel AS toObjectType, target.{target_pk} AS toPk,\n"
                "       rel.properties AS properties, rel.rid AS rid\n"
                f"ORDER BY COALESCE(source.pkValue, source.{source_pk}), COALESCE(target.pkValue, target.{target_pk})\n"
                "SKIP $offset\n"
                "LIMIT $limit",
                {
                    "sourceLabel": source_label_value,
                    "targetLabel": target_label_value,
                    "offset": offset,
                    "limit": limit,
                },
            )
        )

        rows: list[dict[str, Any]] = []
        for query, params in queries:
            rows = self._run_query(query, params)
            if rows:
                break

        if not rows:
            return []

        return self._edge_payloads_from_rows(
            rows,
            default_source=source_label_value,
            default_target=target_label_value,
            property_names=props_filter,
        )

    def list_links(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return self.list_edges(*args, **kwargs)

    async def create(self, instance: ObjectInstance) -> ObjectInstance:
        """
        Create a new object instance in the graph database.

        Args:
            instance: Object instance to create

        Returns:
            Created object instance
        """
        if not self.is_available():
            raise RuntimeError("Graph database not available")

        label = self._label_expr(instance.object_type.api_name)
        pk_field = self._quote_identifier(instance.object_type.pk_field or "id")
        pk_value = getattr(instance, instance.object_type.pk_field or "id")

        # Convert properties to JSON
        properties = {}
        if hasattr(instance, "properties"):
            properties = dict(instance.properties or {})

        # Add metadata
        properties["objectTypeApiName"] = instance.object_type.api_name
        properties["pkValue"] = pk_value

        query = f"""
        CREATE (node:{label} {{{pk_field}: $pkValue, properties: $properties, objectTypeApiName: $objectType, pkValue: $pkValue}})
        RETURN node.{pk_field} AS pkValue, properties(node) AS properties, node.objectTypeApiName AS objectTypeApiName
        """

        params = {
            "pkValue": pk_value,
            "properties": json.dumps(properties),
            "objectType": instance.object_type.api_name,
        }

        rows = self._run_query(query, params)
        if rows:
            self.logger.info(f"Created object instance: {instance.object_type.api_name}:{pk_value}")
            return instance
        else:
            raise RuntimeError(
                f"Failed to create object instance: {instance.object_type.api_name}:{pk_value}"
            )

    async def get_by_pk(
        self,
        object_type_api_name: str,
        pk_or_field: str,
        pk_value: str | None = None,
        *,
        pk_field: str | None = None,
    ) -> dict[str, Any] | ObjectInstance | None:
        """Get object instance by primary key, with unified and legacy fallbacks."""

        if not self.is_available():
            return None

        if pk_value is None:
            pk_value = pk_or_field
        else:
            pk_field = pk_field or pk_or_field

        pk_field = pk_field or "id"

        queries: list[tuple[str, dict[str, Any]]] = []
        if self._unified_graph_enabled():
            queries.append(
                (
                    "MATCH (o:Object)\n"
                    "WHERE o.objectTypeApiName = $objectType AND o.pkValue = $pkValue\n"
                    "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties, o.objectRid AS rid\n"
                    "LIMIT 1",
                    {"objectType": object_type_api_name, "pkValue": pk_value},
                )
            )

        label = self._label_expr(object_type_api_name)
        pk_identifier = self._quote_identifier(pk_field)
        queries.append(
            (
                f"MATCH (o:{label})\n"
                f"WHERE o.{pk_identifier} = $pkValue\n"
                f"RETURN $objectType AS objectTypeApiName, o.{pk_identifier} AS pkValue, properties(o) AS properties, coalesce(o.rid, o.objectRid) AS rid\n"
                "LIMIT 1",
                {"objectType": object_type_api_name, "pkValue": pk_value},
            )
        )

        rows: list[dict[str, Any]] = []
        for query, params in queries:
            rows = self._run_query(query, params)
            if rows:
                break

        payloads = self._payloads_from_rows(rows, default_type=object_type_api_name)
        return payloads[0] if payloads else None

    async def update(self, instance: ObjectInstance) -> ObjectInstance:
        """
        Update an existing object instance.

        Args:
            instance: Object instance to update

        Returns:
            Updated object instance
        """
        if not self.is_available():
            raise RuntimeError("Graph database not available")

        label = self._label_expr(instance.object_type.api_name)
        pk_field = self._quote_identifier(instance.object_type.pk_field or "id")
        pk_value = getattr(instance, instance.object_type.pk_field or "id")

        # Convert properties to JSON
        properties = {}
        if hasattr(instance, "properties"):
            properties = dict(instance.properties or {})

        # Add metadata
        properties["objectTypeApiName"] = instance.object_type.api_name
        properties["pkValue"] = pk_value

        query = f"""
        MATCH (node:{label} {{{pk_field}: $pkValue}})
        SET node.properties = $properties, node.objectTypeApiName = $objectType, node.pkValue = $pkValue
        RETURN node.{pk_field} AS pkValue, properties(node) AS properties, node.objectTypeApiName AS objectTypeApiName
        """

        params = {
            "pkValue": pk_value,
            "properties": json.dumps(properties),
            "objectType": instance.object_type.api_name,
        }

        rows = self._run_query(query, params)
        if rows:
            self.logger.info(f"Updated object instance: {instance.object_type.api_name}:{pk_value}")
            return instance
        else:
            raise RuntimeError(
                f"Failed to update object instance: {instance.object_type.api_name}:{pk_value}"
            )

    async def delete(self, object_type_api_name: str, pk_value: str) -> bool:
        """
        Delete an object instance.

        Args:
            object_type_api_name: API name of the object type
            pk_value: Primary key value

        Returns:
            True if deleted, False if not found
        """
        if not self.is_available():
            return False

        label = self._label_expr(object_type_api_name)
        pk_field = self._quote_identifier("id")  # Default to id field

        query = f"""
        MATCH (node:{label} {{{pk_field}: $pkValue}})
        DETACH DELETE node
        RETURN count(node) AS deleted_count
        """

        params = {"pkValue": pk_value}

        rows = self._run_query(query, params)
        deleted_count = rows[0].get("deleted_count", 0) if rows else 0

        if deleted_count > 0:
            self.logger.info(f"Deleted object instance: {object_type_api_name}:{pk_value}")
            return True
        else:
            self.logger.warning(
                f"Object instance not found for deletion: {object_type_api_name}:{pk_value}"
            )
            return False

    async def list(
        self,
        object_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> builtins.list[ObjectInstance]:
        """
        List object instances with pagination and filtering.

        Args:
            object_type_api_name: API name of the object type
            limit: Maximum number of results
            offset: Number of results to skip
            filters: Optional filters to apply

        Returns:
            List of object instances
        """
        if not self.is_available():
            return []

        label = self._label_expr(object_type_api_name)
        pk_field = self._quote_identifier("id")  # Default to id field

        # Build WHERE clause from filters
        where_clauses = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if filters:
            for key, value in filters.items():
                if key == "properties":
                    # Handle property filters
                    if isinstance(value, dict):
                        for prop_key, prop_value in value.items():
                            param_name = f"prop_{prop_key}"
                            where_clauses.append(f"node.properties.{prop_key} = ${param_name}")
                            params[param_name] = prop_value
                else:
                    # Handle direct field filters
                    param_name = f"filter_{key}"
                    where_clauses.append(f"node.{key} = ${param_name}")
                    params[param_name] = value

        where_clause = "\nWHERE " + "\n  AND ".join(where_clauses) if where_clauses else ""

        query = f"""
        MATCH (node:{label})
        {where_clause}
        RETURN node.{pk_field} AS pkValue, properties(node) AS properties, node.objectTypeApiName AS objectTypeApiName
        ORDER BY node.{pk_field}
        SKIP $offset
        LIMIT $limit
        """

        rows = self._run_query(query, params)
        payloads = self._payloads_from_rows(rows, default_type=object_type_api_name)

        self.logger.info(f"Listed {len(payloads)} object instances: {object_type_api_name}")
        return payloads

    async def search(
        self,
        object_type_api_name: str,
        query: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> builtins.list[ObjectInstance]:
        """
        Search object instances using full-text search.

        Args:
            object_type_api_name: API name of the object type
            query: Search query
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching object instances
        """
        if not self.is_available():
            return []

        label = self._label_expr(object_type_api_name)
        pk_field = self._quote_identifier("id")  # Default to id field

        # Search in properties and object type
        query = f"""
        MATCH (node:{label})
        WHERE node.objectTypeApiName CONTAINS $searchQuery
           OR node.properties CONTAINS $searchQuery
        RETURN node.{pk_field} AS pkValue, properties(node) AS properties, node.objectTypeApiName AS objectTypeApiName
        ORDER BY node.{pk_field}
        SKIP $offset
        LIMIT $limit
        """

        params = {"searchQuery": query, "limit": limit, "offset": offset}

        rows = self._run_query(query, params)
        payloads = self._payloads_from_rows(rows, default_type=object_type_api_name)

        self.logger.info(
            f"Searched and found {len(payloads)} object instances: {object_type_api_name}"
        )
        return payloads

    async def traverse_relationships(
        self,
        object_type_api_name: str,
        pk_value: str,
        relationship_type: str | None = None,
        direction: str = "outgoing",
        depth: int = 1,
    ) -> builtins.list[ObjectInstance]:
        """
        Traverse relationships from an object instance.

        Args:
            object_type_api_name: API name of the object type
            pk_value: Primary key value of the source object
            relationship_type: Type of relationship to traverse
            direction: Direction of traversal ("incoming", "outgoing", "both")
            depth: Maximum traversal depth

        Returns:
            List of connected object instances
        """
        if not self.is_available():
            return []

        label = self._label_expr(object_type_api_name)
        pk_field = self._quote_identifier("id")  # Default to id field

        # Build relationship pattern based on direction
        if direction == "incoming":
            rel_pattern = "<-"
        elif direction == "outgoing":
            rel_pattern = "->"
        else:  # both
            rel_pattern = "-"

        rel_filter = f":{relationship_type}" if relationship_type else ""

        query = f"""
        MATCH (start:{label} {{{pk_field}: $pkValue}})
        {rel_pattern}[{rel_filter}]{{1,{depth}}}]-(end)
        RETURN DISTINCT end.id AS pkValue, properties(end) AS properties, end.objectTypeApiName AS objectTypeApiName
        ORDER BY end.id
        LIMIT 1000
        """

        params = {"pkValue": pk_value}

        rows = self._run_query(query, params)
        payloads = self._payloads_from_rows(rows)

        self.logger.info(
            f"Traversed relationships from: {object_type_api_name}:{pk_value}, found {len(payloads)} connections"
        )
        return payloads

    async def find_path(
        self,
        source_type: str,
        source_pk: str,
        target_type: str,
        target_pk: str,
        max_depth: int = 5,
    ) -> builtins.list[ObjectInstance]:
        """
        Find shortest path between two object instances.

        Args:
            source_type: API name of the source object type
            source_pk: Primary key of the source object
            target_type: API name of the target object type
            target_pk: Primary key of the target object
            max_depth: Maximum path depth to search

        Returns:
            List of object instances representing the path
        """
        if not self.is_available():
            return []

        source_label = self._label_expr(source_type)
        target_label = self._label_expr(target_type)
        pk_field = self._quote_identifier("id")  # Default to id field

        query = f"""
        MATCH (start:{source_label} {{{pk_field}: $sourcePk}}), (end:{target_label} {{{pk_field}: $targetPk}})
        MATCH path = shortestPath((start)-[*1..{max_depth}]-(end))
        RETURN [node in nodes(path) | node.id AS pkValue, properties(node) AS properties, node.objectTypeApiName AS objectTypeApiName] AS path_nodes
        LIMIT 1
        """

        params = {"sourcePk": source_pk, "targetPk": target_pk}

        rows = self._run_query(query, params)
        if rows and rows[0].get("path_nodes"):
            path_nodes = rows[0]["path_nodes"]
            self.logger.info(
                f"Found path with {len(path_nodes)} nodes: {source_type}:{source_pk} -> {target_type}:{target_pk}"
            )
            return path_nodes
        else:
            self.logger.info(
                f"No path found: {source_type}:{source_pk} -> {target_type}:{target_pk}"
            )
            return []
