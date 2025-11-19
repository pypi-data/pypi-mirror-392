"""
linked_objects_repository.py
-------------------------------
Graph-based repository for linked objects (relationships).

Provides high-performance graph operations for managing relationships
between object instances using graph databases.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from ontologia.domain.instances.repositories import LinkedObjectRepository
from ontologia.domain.metamodels.instances.models_sql import LinkedObject

logger = logging.getLogger(__name__)


class GraphLinkedObjectsRepository(LinkedObjectRepository):
    """
    Graph database implementation for linked objects (relationships).

    Optimized for storing and querying relationships between object instances
    using graph database capabilities for efficient traversal and pattern matching.
    """

    def __init__(self, graph_client: Any, session_factory: Any):
        """
        Initialize graph linked objects repository.

        Args:
            graph_client: Graph database client (Neo4j, KuzuDB, etc.)
            session_factory: Session factory for database operations
        """
        self.graph_client = graph_client
        self.session_factory = session_factory
        self.logger = logging.getLogger(__name__)

    async def create(self, linked_object: LinkedObject) -> LinkedObject:
        """
        Create a new linked object (relationship).

        Args:
            linked_object: Linked object to create

        Returns:
            Created linked object
        """
        client = self._graph_client()
        if client is None:
            raise RuntimeError("Graph database not available")

        try:
            # Create relationship between source and target nodes
            query = """
            MATCH (source:Object {pkValue: $source_pk}), (target:Object {pkValue: $target_pk})
            CREATE (source)-[r:LINKED {
                linkTypeApiName: $link_type_api_name,
                linkTypeRid: $link_type_rid,
                properties: $properties,
                validFrom: $valid_from,
                validTo: $valid_to,
                transactionFrom: $transaction_from,
                transactionTo: $transaction_to
            }]->(target)
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            """

            import json
            from datetime import datetime

            params = {
                "source_pk": linked_object.source_pk_value,
                "target_pk": linked_object.target_pk_value,
                "link_type_api_name": linked_object.link_type_api_name,
                "link_type_rid": linked_object.link_type_rid,
                "properties": json.dumps(linked_object.data or {}),
                "valid_from": datetime.now(UTC).isoformat(),
                "valid_to": None,
                "transaction_from": datetime.now(UTC).isoformat(),
                "transaction_to": None,
            }

            rows = self._run_query(query, params)
            if rows:
                self.logger.info(f"Created linked object: {linked_object.link_type_api_name}")
                return linked_object
            else:
                raise RuntimeError(
                    f"Failed to create linked object: {linked_object.link_type_api_name}"
                )

        except Exception as e:
            self.logger.error(f"Failed to create linked object: {e}")
            raise

    async def get_by_pk(
        self,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> LinkedObject | None:
        """
        Get linked object by primary key.

        Args:
            link_type_api_name: API name of the link type
            source_pk_value: Primary key of the source object
            target_pk_value: Primary key of the target object

        Returns:
            Linked object or None if not found
        """
        client = self._graph_client()
        if client is None:
            return None

        try:
            query = """
            MATCH (source:Object {pkValue: $source_pk})-[r:LINKED {linkTypeApiName: $link_type_api_name}]->(target:Object {pkValue: $target_pk})
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            LIMIT 1
            """

            params = {
                "source_pk": source_pk_value,
                "target_pk": target_pk_value,
                "link_type_api_name": link_type_api_name,
            }

            rows = self._run_query(query, params)
            linked_objects = self._rows_to_linked_objects(rows)

            if linked_objects:
                self.logger.info(f"Found linked object: {link_type_api_name}")
                return linked_objects[0]
            else:
                self.logger.info(f"Linked object not found: {link_type_api_name}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to get linked object: {e}")
            return None

    async def update(self, linked_object: LinkedObject) -> LinkedObject:
        """
        Update an existing linked object.

        Args:
            linked_object: Linked object to update

        Returns:
            Updated linked object
        """
        client = self._graph_client()
        if client is None:
            raise RuntimeError("Graph database not available")

        try:
            # Update relationship properties
            query = """
            MATCH (source:Object {pkValue: $source_pk})-[r:LINKED {linkTypeApiName: $link_type_api_name}]->(target:Object {pkValue: $target_pk})
            SET r.properties = $properties,
                r.linkTypeRid = $link_type_rid,
                r.transactionTo = $transaction_to
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            """

            import json
            from datetime import datetime

            params = {
                "source_pk": linked_object.source_pk_value,
                "target_pk": linked_object.target_pk_value,
                "link_type_api_name": linked_object.link_type_api_name,
                "link_type_rid": linked_object.link_type_rid,
                "properties": json.dumps(linked_object.data or {}),
                "transaction_to": datetime.now(UTC).isoformat(),
            }

            rows = self._run_query(query, params)
            if rows:
                self.logger.info(f"Updated linked object: {linked_object.link_type_api_name}")
                return linked_object
            else:
                raise RuntimeError(
                    f"Failed to update linked object: {linked_object.link_type_api_name}"
                )

        except Exception as e:
            self.logger.error(f"Failed to update linked object: {e}")
            raise

    async def delete(
        self,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> bool:
        """
        Delete a linked object.

        Args:
            link_type_api_name: API name of the link type
            source_pk_value: Primary key of the source object
            target_pk_value: Primary key of the target object

        Returns:
            True if deleted, False if not found
        """
        client = self._graph_client()
        if client is None:
            return False

        try:
            # Delete relationship
            query = """
            MATCH (source:Object {pkValue: $source_pk})-[r:LINKED {linkTypeApiName: $link_type_api_name}]->(target:Object {pkValue: $target_pk})
            DELETE r
            RETURN count(r) AS deleted_count
            """

            params = {
                "source_pk": source_pk_value,
                "target_pk": target_pk_value,
                "link_type_api_name": link_type_api_name,
            }

            rows = self._run_query(query, params)
            deleted_count = rows[0].get("deleted_count", 0) if rows else 0

            if deleted_count > 0:
                self.logger.info(f"Deleted linked object: {link_type_api_name}")
                return True
            else:
                self.logger.warning(f"Linked object not found for deletion: {link_type_api_name}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete linked object: {e}")
            return False

    async def list_by_source(
        self,
        link_type_api_name: str,
        source_pk_value: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LinkedObject]:
        """
        List linked objects by source object.

        Args:
            link_type_api_name: API name of the link type
            source_pk_value: Primary key of the source object
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of linked objects
        """
        client = self._graph_client()
        if client is None:
            return []

        try:
            query = """
            MATCH (source:Object {pkValue: $source_pk})-[r:LINKED {linkTypeApiName: $link_type_api_name}]->(target:Object)
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            ORDER BY target.pkValue
            SKIP $offset
            LIMIT $limit
            """

            params = {
                "source_pk": source_pk_value,
                "link_type_api_name": link_type_api_name,
                "offset": offset,
                "limit": limit,
            }

            rows = self._run_query(query, params)
            linked_objects = self._rows_to_linked_objects(rows)

            self.logger.info(
                f"Listed {len(linked_objects)} linked objects by source: {source_pk_value}"
            )
            return linked_objects

        except Exception as e:
            self.logger.error(f"Failed to list linked objects by source: {e}")
            return []

    async def list_by_target(
        self,
        link_type_api_name: str,
        target_pk_value: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LinkedObject]:
        """
        List linked objects by target object.

        Args:
            link_type_api_name: API name of the link type
            target_pk_value: Primary key of the target object
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of linked objects
        """
        client = self._graph_client()
        if client is None:
            return []

        try:
            query = """
            MATCH (source:Object)-[r:LINKED {linkTypeApiName: $link_type_api_name}]->(target:Object {pkValue: $target_pk})
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            ORDER BY source.pkValue
            SKIP $offset
            LIMIT $limit
            """

            params = {
                "target_pk": target_pk_value,
                "link_type_api_name": link_type_api_name,
                "offset": offset,
                "limit": limit,
            }

            rows = self._run_query(query, params)
            linked_objects = self._rows_to_linked_objects(rows)

            self.logger.info(
                f"Listed {len(linked_objects)} linked objects by target: {target_pk_value}"
            )
            return linked_objects

        except Exception as e:
            self.logger.error(f"Failed to list linked objects by target: {e}")
            return []

    async def find_relationships(
        self,
        source_type: str,
        source_pk: str,
        relationship_types: list[str] | None = None,
        max_depth: int = 2,
    ) -> list[LinkedObject]:
        """
        Find relationships from a source object.

        Args:
            source_type: API name of the source object type
            source_pk: Primary key of the source object
            relationship_types: Optional list of relationship types to filter
            max_depth: Maximum traversal depth

        Returns:
            List of linked objects representing relationships
        """
        client = self._graph_client()
        if client is None:
            return []

        try:
            # Build relationship type filter
            rel_filter = ""
            if relationship_types:
                rel_filter = f"|{'|'.join(relationship_types)}"

            query = f"""
            MATCH (source:Object {{pkValue: $source_pk, objectTypeApiName: $source_type}})-[r:LINKED{rel_filter}*1..{max_depth}]-(target:Object)
            RETURN DISTINCT r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            ORDER BY source.pkValue, target.pkValue
            LIMIT 1000
            """

            params = {"source_pk": source_pk, "source_type": source_type}

            rows = self._run_query(query, params)
            linked_objects = self._rows_to_linked_objects(rows)

            self.logger.info(
                f"Found {len(linked_objects)} relationships from: {source_type}:{source_pk}"
            )
            return linked_objects

        except Exception as e:
            self.logger.error(f"Failed to find relationships: {e}")
            return []

    async def traverse_outgoing(
        self,
        link_type_rid: str,
        source_pk_value: str,
        limit: int = 100,
        valid_at: datetime | None = None,
    ) -> list[LinkedObject]:
        """
        Traverse outgoing relationships from a source object.

        Args:
            link_type_rid: RID of the link type
            source_pk_value: Primary key value of the source object
            limit: Maximum number of results
            valid_at: Valid datetime for temporal queries (optional)

        Returns:
            List of linked objects representing outgoing relationships
        """
        client = self._graph_client()
        if client is None:
            return []

        try:
            # Build Cypher query for outgoing traversal
            query = """
            MATCH (source:Object)-[r:LINKED]->(target:Object)
            WHERE source.pkValue = $source_pk AND r.linkTypeRid = $link_type_rid
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            ORDER BY target.pkValue
            LIMIT $limit
            """

            params = {"source_pk": source_pk_value, "link_type_rid": link_type_rid, "limit": limit}

            if valid_at:
                # Add temporal filtering if valid_at is provided
                query = """
                MATCH (source:Object)-[r:LINKED]->(target:Object)
                WHERE source.pkValue = $source_pk
                  AND r.linkTypeRid = $link_type_rid
                  AND r.validFrom <= $valid_at
                  AND (r.validTo IS NULL OR r.validTo > $valid_at)
                RETURN r.linkTypeApiName AS linkTypeApiName,
                       r.linkTypeRid AS linkTypeRid,
                       source.pkValue AS sourcePkValue,
                       target.pkValue AS targetPkValue,
                       r.properties AS properties,
                       r.rid AS rid
                ORDER BY target.pkValue
                LIMIT $limit
                """
                params["valid_at"] = valid_at.isoformat()

            rows = self._run_query(query, params)
            return self._rows_to_linked_objects(rows)

        except Exception as e:
            self.logger.error(f"Failed to traverse outgoing relationships: {e}")
            return []

    async def traverse_incoming(
        self,
        link_type_rid: str,
        target_pk_value: str,
        limit: int = 100,
        valid_at: datetime | None = None,
    ) -> list[LinkedObject]:
        """
        Traverse incoming relationships to a target object.

        Args:
            link_type_rid: RID of the link type
            target_pk_value: Primary key value of the target object
            limit: Maximum number of results
            valid_at: Valid datetime for temporal queries (optional)

        Returns:
            List of linked objects representing incoming relationships
        """
        client = self._graph_client()
        if client is None:
            return []

        try:
            # Build Cypher query for incoming traversal
            query = """
            MATCH (source:Object)-[r:LINKED]->(target:Object)
            WHERE target.pkValue = $target_pk AND r.linkTypeRid = $link_type_rid
            RETURN r.linkTypeApiName AS linkTypeApiName,
                   r.linkTypeRid AS linkTypeRid,
                   source.pkValue AS sourcePkValue,
                   target.pkValue AS targetPkValue,
                   r.properties AS properties,
                   r.rid AS rid
            ORDER BY source.pkValue
            LIMIT $limit
            """

            params = {"target_pk": target_pk_value, "link_type_rid": link_type_rid, "limit": limit}

            if valid_at:
                # Add temporal filtering if valid_at is provided
                query = """
                MATCH (source:Object)-[r:LINKED]->(target:Object)
                WHERE target.pkValue = $target_pk
                  AND r.linkTypeRid = $link_type_rid
                  AND r.validFrom <= $valid_at
                  AND (r.validTo IS NULL OR r.validTo > $valid_at)
                RETURN r.linkTypeApiName AS linkTypeApiName,
                       r.linkTypeRid AS linkTypeRid,
                       source.pkValue AS sourcePkValue,
                       target.pkValue AS targetPkValue,
                       r.properties AS properties,
                       r.rid AS rid
                ORDER BY source.pkValue
                LIMIT $limit
                """
                params["valid_at"] = valid_at.isoformat()

            rows = self._run_query(query, params)
            return self._rows_to_linked_objects(rows)

        except Exception as e:
            self.logger.error(f"Failed to traverse incoming relationships: {e}")
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _graph_client(self) -> Any | None:
        """Get the graph client instance."""
        client = self.graph_client
        if client is None or not hasattr(client, "execute"):
            return None
        availability = getattr(client, "is_available", None)
        if callable(availability):
            try:
                if not availability():
                    return None
            except Exception:
                self.logger.debug("Graph availability probe failed", exc_info=True)
                return None
        return client

    def _run_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a graph query and return rows."""
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
        """Convert query result to list of dictionaries."""
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
            except Exception:
                self.logger.debug("Graph row fetch failed at index %s", idx, exc_info=True)
                continue
            rows.append(self._row_to_dict(row_obj, columns))
        return rows

    @staticmethod
    def _row_to_dict(row_obj: Any, columns: list[str]) -> dict[str, Any]:
        """Convert row object to dictionary."""
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
        return data

    def _rows_to_linked_objects(self, rows: list[dict[str, Any]]) -> list[LinkedObject]:
        """Convert query rows to LinkedObject instances."""
        linked_objects: list[LinkedObject] = []
        for row in rows:
            # Check if row has required fields with non-None values
            if not all(
                key in row and row[key] is not None
                for key in ["linkTypeApiName", "linkTypeRid", "sourcePkValue", "targetPkValue"]
            ):
                self.logger.warning(f"Skipping row missing required fields: {row}")
                continue
            try:
                data = self._parse_properties(row.get("data"))
                linked_object = LinkedObject(
                    link_type_api_name=row.get("linkTypeApiName"),
                    link_type_rid=row.get("linkTypeRid"),
                    source_pk_value=row.get("sourcePkValue"),
                    target_pk_value=row.get("targetPkValue"),
                    data=data,
                    rid=row.get("rid"),
                )
                linked_objects.append(linked_object)
            except Exception as e:
                self.logger.warning(f"Failed to convert row to LinkedObject: {e}")
                continue
        return linked_objects

    @staticmethod
    def _parse_properties(properties_value: Any) -> dict[str, Any]:
        """Parse properties from graph query result."""
        if properties_value is None:
            return {}
        if isinstance(properties_value, dict):
            return dict(properties_value)
        if isinstance(properties_value, str):
            try:
                import json

                return json.loads(properties_value)
            except json.JSONDecodeError:
                return {}
        return {}

    async def get_relationship_graph(
        self,
        object_type_api_name: str,
        pk_value: str,
        depth: int = 2,
        include_properties: bool = True,
    ) -> dict[str, Any]:
        """
        Get relationship graph for an object instance.

        Args:
            object_type_api_name: API name of the object type
            pk_value: Primary key value
            depth: Traversal depth
            include_properties: Whether to include object properties

        Returns:
            Graph representation with nodes and edges
        """
        client = self._graph_client()
        if client is None:
            return {"nodes": [], "edges": []}

        try:
            # Build query to get nodes and edges
            node_props = "properties(n)" if include_properties else "null"
            edge_props = "properties(r)" if include_properties else "null"

            query = f"""
            MATCH path = (start:Object {{pkValue: $pk_value, objectTypeApiName: $object_type}})-[*1..{depth}]-(end:Object)
            WITH nodes(path) AS path_nodes, relationships(path) AS path_rels
            UNWIND path_nodes AS node
            UNWIND path_rels AS rel
            RETURN DISTINCT
                node.pkValue AS id,
                node.objectTypeApiName AS type,
                {node_props} AS properties,
                rel.linkTypeApiName AS edge_type,
                startNode(rel).pkValue AS source,
                endNode(rel).pkValue AS target,
                {edge_props} AS edge_properties
            """

            params = {"pk_value": pk_value, "object_type": object_type_api_name}

            rows = self._run_query(query, params)

            # Build graph structure
            nodes = {}
            edges = []

            for row in rows:
                # Add node if not already added
                node_id = row.get("id")
                if node_id and node_id not in nodes:
                    nodes[node_id] = {
                        "id": node_id,
                        "type": row.get("type"),
                        "properties": self._parse_properties(row.get("properties")),
                    }

                # Add edge if it has all required fields
                if all(row.get(field) for field in ["edge_type", "source", "target"]):
                    edges.append(
                        {
                            "type": row.get("edge_type"),
                            "source": row.get("source"),
                            "target": row.get("target"),
                            "properties": self._parse_properties(row.get("edge_properties")),
                        }
                    )

            graph = {
                "nodes": list(nodes.values()),
                "edges": edges,
                "metadata": {"depth": depth, "node_count": len(nodes), "edge_count": len(edges)},
            }

            self.logger.info(
                f"Generated relationship graph with {len(nodes)} nodes and {len(edges)} edges"
            )
            return graph

        except Exception as e:
            self.logger.error(f"Failed to get relationship graph: {e}")
            return {"nodes": [], "edges": []}
