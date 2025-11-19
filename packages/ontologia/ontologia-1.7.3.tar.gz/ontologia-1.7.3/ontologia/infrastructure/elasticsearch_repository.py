"""
elasticsearch_repository.py
----------------------------
Repository for full-text search capabilities using Elasticsearch.

Provides fast text-based searching across all ObjectInstance properties,
supporting advanced search features like relevance scoring, faceting,
and aggregation capabilities.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, cast

try:  # pragma: no cover - optional dependency
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover - handled at runtime
    Elasticsearch: Any = None


class ElasticsearchRepository:
    """
    Repository for managing full-text search operations with Elasticsearch.

    This repository handles indexing of ObjectInstance data and provides
    fast text-based search capabilities across all object properties.
    """

    def __init__(self, hosts: list[str] | None = None, **kwargs):
        """
        Initialize the Elasticsearch repository.

        Args:
            hosts: List of Elasticsearch hosts
            **kwargs: Additional connection parameters
        """
        self.logger = logging.getLogger(__name__)
        self.hosts = hosts or ["localhost:9200"]
        self.kwargs = kwargs

        # Try to create real client, fall back to mock
        self.client = self._create_client()

        # Default index name pattern
        self.index_pattern = "ontologia_objects"

        self.logger.info(f"ElasticsearchRepository initialized with hosts: {self.hosts}")

    def _create_client(self) -> Any:
        """
        Create Elasticsearch client connection.

        Returns:
            Elasticsearch client instance
        """
        if not self.hosts:
            raise ValueError("Elasticsearch hosts must be configured")

        if Elasticsearch is None:
            self.logger.warning("elasticsearch package not installed; falling back to mock client")
            return MockElasticsearchClient()

        try:
            client = Elasticsearch(self.hosts, **self.kwargs)
            info = client.info()
            cluster_name = (
                info.get("cluster_name", "unknown") if isinstance(info, dict) else "unknown"
            )
            self.logger.info("Connected to Elasticsearch cluster: %s", cluster_name)
            return client
        except Exception as e:  # pragma: no cover - requires Elasticsearch instance
            self.logger.warning(
                "Failed to connect to Elasticsearch (%s): %s; falling back to mock client",
                self.hosts,
                e,
            )
            return MockElasticsearchClient()

    def is_available(self) -> bool:
        """
        Check if Elasticsearch is available and connected.

        Returns:
            True if Elasticsearch client is available and connected
        """
        try:
            if hasattr(self.client, "ping"):
                return self.client.ping()
            elif hasattr(self.client, "info"):
                self.client.info()
                return True
            return False
        except Exception:
            return False

    def create_index(self, object_type_api_name: str, properties: dict[str, Any]) -> bool:
        """
        Create index for a specific object type.

        Args:
            object_type_api_name: API name of the object type
            properties: Dictionary of property definitions and their types

        Returns:
            True if index created successfully
        """
        index_name = f"{self.index_pattern}_{object_type_api_name}"

        # Build Elasticsearch mapping
        mapping = self._build_mapping(properties)
        self.logger.debug(
            "Elasticsearch mapping built",
            extra={"index": index_name, "mapping_keys": list(mapping.keys())[:5]},
        )

        try:
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(
                    index=index_name, body={"mappings": {"properties": mapping}}
                )

            self.logger.info(f"Created Elasticsearch index: {index_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create index {index_name}: {e}")
            return False

    def _build_mapping(self, properties: dict[str, Any]) -> dict[str, Any]:
        """
        Build Elasticsearch mapping from property definitions.

        Args:
            properties: Dictionary of property definitions

        Returns:
            Elasticsearch mapping configuration
        """
        mapping = {
            "objectTypeApiName": {"type": "keyword"},
            "pkValue": {"type": "keyword"},
            "rid": {"type": "keyword"},
            "labels": {"type": "keyword"},
            "_indexed_at": {"type": "date"},
        }

        # Map common ontologia types to Elasticsearch types
        type_mapping = {
            "string": "text",
            "integer": "integer",
            "int": "integer",
            "long": "long",
            "double": "double",
            "float": "float",
            "boolean": "boolean",
            "bool": "boolean",
            "date": "date",
            "timestamp": "date",
        }

        for prop_name, prop_type in properties.items():
            es_type = type_mapping.get(str(prop_type).lower(), "text")

            if es_type == "text":
                # Text fields get both text and keyword versions
                mapping[prop_name] = {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                }
            else:
                mapping[prop_name] = {"type": es_type}

        return mapping

    def index_object(self, object_data: Mapping[str, Any] | Any) -> bool:
        """
        Index a single object instance.

        Args:
            object_data: Dictionary containing object data or Pydantic model

        Returns:
            True if indexed successfully
        """
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(object_data, "model_dump"):
                data_dict = cast(Any, object_data).model_dump()
            elif hasattr(object_data, "dict"):
                data_dict = cast(Any, object_data).dict()
            else:
                data_dict = object_data

            object_type = data_dict.get("objectTypeApiName") or data_dict.get(
                "object_type_api_name"
            )
            if not object_type:
                self.logger.warning("Object missing objectTypeApiName, skipping indexing")
                return False

            # Prepare document for Elasticsearch
            doc = {
                **data_dict,
                "_indexed_at": "now",  # Elasticsearch will convert to timestamp
            }

            self.client.index(
                index=f"{self.index_pattern}_{object_type}",
                id=data_dict.get("pk_value") or data_dict.get("rid") or data_dict.get("id"),
                body=doc,
            )

            self.logger.debug(f"Indexed object: {data_dict.get('rid')}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to index object: {e}")
            return False

    def index_objects_batch(self, objects: list[dict[str, Any]]) -> int:
        """
        Index multiple objects in bulk.

        Args:
            objects: List of object dictionaries

        Returns:
            Number of successfully indexed objects
        """
        if not objects:
            return 0

        try:
            from elasticsearch.helpers import bulk

            def generate_bulk_actions():
                for obj in objects:
                    object_type = obj.get("objectTypeApiName")
                    if object_type:
                        index_name = f"{self.index_pattern}_{object_type}"
                        yield {
                            "_index": index_name,
                            "_id": obj.get("rid"),
                            "_source": {**obj, "_indexed_at": "now"},
                        }

            success_count, errors = bulk(self.client, generate_bulk_actions())

            self.logger.info(f"Bulk indexed {success_count} objects")
            if errors:
                errors_list = list(errors) if isinstance(errors, (list, tuple)) else [errors]
                self.logger.warning(f"Bulk indexing had {len(errors_list)} errors")
            return success_count

        except Exception as e:
            self.logger.error(f"Bulk indexing failed: {e}")
            return 0

    def search_by_text(
        self,
        object_type: str,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Perform text search across all properties of an object type.

        Args:
            object_type: API name of the object type to search
            query: Text query string
            filters: Additional field filters
            limit: Maximum number of results
            offset: Results offset for pagination

        Returns:
            List of document dictionaries matching the search
        """
        try:
            # Build bool query block and optional filters first (to satisfy type checker)
            filter_clauses: list[dict[str, Any]] = []
            if filters:
                for field, value in filters.items():
                    if isinstance(value, str):
                        filter_clauses.append({"term": {f"{field}.keyword": value}})
                    else:
                        filter_clauses.append({"term": {field: value}})

            bool_query: dict[str, Any] = {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["*"],  # Search all fields
                            "type": "best_fields",
                            "fuzziness": "AUTO",  # Allow some fuzzy matching
                        }
                    }
                ]
            }
            if filter_clauses:
                bool_query["filter"] = filter_clauses

            # Build Elasticsearch query
            es_query: dict[str, Any] = {
                "query": {"bool": bool_query},
                "size": limit,
                "from": offset,
            }
            # reference es_query to avoid unused variable lint and aid debugging
            self.logger.debug(
                "Built ES text query",
                extra={"has_filter": "filter" in bool_query, "keys": list(es_query.keys())},
            )

            # In production:
            index_name = f"{self.index_pattern}_{object_type}"
            response = self.client.search(index=index_name, body=es_query)
            hits = response["hits"]["hits"]
            return [hit["_source"] for hit in hits]

        except Exception as e:
            self.logger.error(f"Text search failed: {e}")
            return []

    def search_with_filters(
        self,
        object_type: str,
        filters: dict[str, Any],
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        """
        Search objects using exact field filters (no text search).

        Args:
            object_type: API name of the object type
            filters: Dictionary of field filters
            limit: Maximum number of results
            offset: Results offset

        Returns:
            List of pkValue strings matching the filters
        """
        try:
            # Build exact match query
            filters_list: list[dict[str, Any]] = []
            es_query: dict[str, Any] = {
                "query": {"bool": {"filter": filters_list}},
                "size": limit,
                "from": offset,
                "_source": ["pkValue", "objectTypeApiName"],
            }
            # reference es_query to avoid unused variable lint and aid debugging
            self.logger.debug(
                "Built ES filter query",
                extra={"filters": len(filters_list), "keys": list(es_query.keys())},
            )

            # Add filter clauses
            for field, value in filters.items():
                if isinstance(value, str):
                    filters_list.append({"term": {f"{field}.keyword": value}})
                elif isinstance(value, list):
                    filters_list.append({"terms": {f"{field}.keyword": value}})
                else:
                    filters_list.append({"term": {field: value}})

            index_name = f"{self.index_pattern}_{object_type}"
            response = self.client.search(index=index_name, body=es_query)
            hits = response["hits"]["hits"]
            return [hit["_source"]["pkValue"] for hit in hits]

        except Exception as e:
            self.logger.error(f"Filter search failed for {object_type}: {e}")
            return []

    def _mock_search_results(
        self, object_type: str, query: str, limit: int
    ) -> list[dict[str, Any]]:
        """Mock search results for development purposes."""
        # This would be replaced by actual Elasticsearch results
        return [
            {"pkValue": f"mock_result_{i}", "objectTypeApiName": object_type}
            for i in range(min(limit, 10))  # Return up to 10 mock results
        ]

    def _mock_filter_results(
        self, object_type: str, filters: dict[str, Any], limit: int
    ) -> list[dict[str, Any]]:
        """Mock filter results for development purposes."""
        return [
            {"pkValue": f"mock_filtered_{i}", "objectTypeApiName": object_type}
            for i in range(min(limit, 5))  # Return up to 5 mock results
        ]

    def delete_object(self, object_type: str, pk_value: str) -> bool:
        """
        Delete an object from the search index.

        Args:
            object_type: API name of the object type
            pk_value: Primary key value of the object

        Returns:
            True if deleted successfully
        """
        try:
            index_name = f"{self.index_pattern}_{object_type}"

            # Find all documents by pk_value
            search_result = self.client.search(
                index=index_name,
                body={"query": {"term": {"pk_value": pk_value}}, "_source": ["_id"]},
            )

            hits = search_result.get("hits", {}).get("hits", [])
            if not hits:
                self.logger.warning(f"Object {pk_value} not found in index {index_name}")
                return False

            # Delete all documents with this pk_value
            for hit in hits:
                doc_id = hit["_id"]
                self.client.delete(index=index_name, id=doc_id)

            self.logger.info(f"Deleted {len(hits)} documents for pk_value {pk_value}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete object {pk_value}: {e}")
            return False

    def get_index_stats(self, object_type: str) -> dict[str, Any]:
        """
        Get statistics for an object type index.

        Args:
            object_type: API name of the object type

        Returns:
            Dictionary with index statistics
        """
        index_name = f"{self.index_pattern}_{object_type}"

        try:
            stats = self.client.indices.stats(index=index_name)
            return {
                "doc_count": stats["indices"][index_name]["total"]["docs"]["count"],
                "store_size": stats["indices"][index_name]["total"]["store"]["size_in_bytes"],
                "index_name": index_name,
            }

        except Exception as e:
            self.logger.error(f"Failed to get index stats for {object_type}: {e}")
            return {}


class MockElasticsearchClient:
    """Mock Elasticsearch client for development purposes."""

    def __init__(self):
        self.indices = MockIndices()
        self.logger = logging.getLogger(__name__)

    def index(self, index: str, doc_id: str, body: dict) -> dict:
        """Mock index operation."""
        self.logger.debug(f"Mock index: {index}, id: {doc_id}")
        return {"result": "created", "_id": doc_id}

    def search(self, index: str, body: dict) -> dict:
        """Mock search operation."""
        self.logger.debug(f"Mock search: {index}")
        return {
            "hits": {
                "total": {"value": 10},
                "hits": [{"_source": {"pkValue": f"mock_{i}"}} for i in range(10)],
            }
        }

    def delete(self, index: str, doc_id: str) -> dict:
        """Mock delete operation."""
        self.logger.debug(f"Mock delete: {index}, id: {doc_id}")
        return {"result": "deleted", "_id": doc_id}


class MockIndices:
    """Mock indices API for development."""

    def exists(self, index: str) -> bool:
        return False

    def create(self, index: str, body: dict) -> dict:
        return {"acknowledged": True}

    def stats(self, index: str) -> dict:
        return {
            "indices": {
                index: {
                    "total": {
                        "docs": {"count": 1000},
                        "store": {"size_in_bytes": 1048576},
                    }
                }
            }
        }
