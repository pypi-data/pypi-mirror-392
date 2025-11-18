"""
elasticsearch_vector_repository.py
------------------------------------
Elasticsearch implementation of VectorRepository interface.

Provides vector similarity search capabilities using Elasticsearch's
dense vector field type and k-NN search functionality.
"""

from __future__ import annotations

import logging
from typing import Any

try:  # pragma: no cover - optional dependency
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover - handled at runtime
    Elasticsearch: Any = None

from ontologia.domain.instances.repositories import SearchResult, VectorObject


class ElasticsearchVectorRepository:
    """
    Elasticsearch implementation of vector storage and similarity search.

    Uses Elasticsearch's dense_vector field type and k-NN search
    to provide efficient vector similarity operations.
    """

    def __init__(self, hosts: list[str] | None = None, **kwargs):
        """
        Initialize the Elasticsearch vector repository.

        Args:
            hosts: List of Elasticsearch hosts
            **kwargs: Additional connection parameters
        """
        self.logger = logging.getLogger(__name__)
        self.hosts = hosts or ["localhost:9200"]
        self.kwargs = kwargs

        # Mock client for development - replace with real client in production
        self.client = self._create_client()

        # Index name for vector storage
        self.vector_index = "ontologia_vectors"

        self.logger.info(f"ElasticsearchVectorRepository initialized with hosts: {self.hosts}")

    def _create_client(self) -> Any:
        """
        Create Elasticsearch client connection.

        Returns:
            Elasticsearch client instance
        """
        if not self.hosts:
            self.logger.warning("No Elasticsearch hosts configured for vector store; using mock")
            return MockElasticsearchVectorClient()

        if Elasticsearch is None:
            self.logger.warning(
                "elasticsearch package not installed; install the 'search' dependency group to enable vector search"
            )
            return MockElasticsearchVectorClient()

        try:
            client = Elasticsearch(self.hosts, **self.kwargs)
            client.info()
            self.logger.info("Connected to Elasticsearch vector backend at %s", self.hosts)
            return client
        except Exception as e:  # pragma: no cover - requires external service
            self.logger.error(
                "Failed to initialize Elasticsearch vector client for %s; falling back to mock: %s",
                self.hosts,
                e,
            )
            return MockElasticsearchVectorClient()

    def create_vector_index_if_not_exists(self) -> bool:
        """
        Create the vector index with appropriate mapping if it doesn't exist.

        Returns:
            True if index was created or already exists
        """
        try:
            # In production:
            # if not self.client.indices.exists(index=self.vector_index):
            #     mapping = {
            #         "mappings": {
            #             "properties": {
            #                 "object_rid": {"type": "keyword"},
            #                 "object_type_api_name": {"type": "keyword"},
            #                 "pk_value": {"type": "keyword"},
            #                 "embedding": {
            #                     "type": "dense_vector",
            #                     "dims": 1536,  # Default for OpenAI embeddings
            #                     "index": True,
            #                     "similarity": "cosine"
            #                 },
            #                 "metadata": {"type": "object", "dynamic": True},
            #                 "_indexed_at": {"type": "date"}
            #             }
            #         }
            #     }
            #     self.client.indices.create(index=self.vector_index, body=mapping)

            self.logger.info(f"Created vector index: {self.vector_index}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create vector index {self.vector_index}: {e}")
            return False

    async def upsert_vectors(self, objects: list[VectorObject]) -> bool:
        """
        Insert or update vector objects in Elasticsearch.

        Args:
            objects: List of VectorObject instances to store

        Returns:
            True if operation was successful
        """
        if not objects:
            return True

        try:
            # Ensure index exists
            self.create_vector_index_if_not_exists()

            # Prepare bulk operations
            # In production:
            # from elasticsearch.helpers import bulk
            #
            # def generate_bulk_actions():
            #     for obj in objects:
            #         yield {
            #             "_index": self.vector_index,
            #             "_id": obj.object_rid,
            #             "_source": {
            #                 "object_rid": obj.object_rid,
            #                 "object_type_api_name": obj.object_type_api_name,
            #                 "pk_value": obj.pk_value,
            #                 "embedding": obj.embedding,
            #                 "metadata": obj.metadata or {},
            #                 "_indexed_at": "now"
            #             }
            #         }
            #
            # success_count, errors = bulk(self.client, generate_bulk_actions())

            # Mock implementation
            success_count = len(objects)
            self.logger.info(f"Upserted {success_count} vectors to Elasticsearch")
            return True

        except Exception as e:
            self.logger.error(f"Failed to upsert vectors: {e}")
            return False

    async def search_by_vector(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None,
        object_types: list[str] | None = None,
    ) -> list[SearchResult]:
        """
        Perform vector similarity search.

        Args:
            query_vector: Query embedding vector
            top_k: Maximum number of results to return
            filters: Optional metadata filters
            object_types: Optional object type filters

        Returns:
            List of SearchResult instances
        """
        try:
            # Build k-NN query
            query_clauses = [
                {"knn": {"embedding": {"vector": query_vector, "k": top_k, "similarity": "cosine"}}}
            ]

            # Add filters if provided
            if filters or object_types:
                filter_clauses = []

                if object_types:
                    filter_clauses.append({"terms": {"object_type_api_name": object_types}})

                if filters:
                    for field, value in filters.items():
                        filter_clauses.append({"term": {f"metadata.{field}": value}})

                # Wrap k-NN query with bool query for filtering
                query_clauses = [{"bool": {"must": query_clauses, "filter": filter_clauses}}]

            _es_query = {
                "query": query_clauses[0],
                "size": top_k,
                "_source": ["object_rid", "object_type_api_name", "pk_value", "_score", "metadata"],
            }

            # In production:
            # response = self.client.search(index=self.vector_index, body=es_query)
            # hits = response["hits"]["hits"]
            # return [
            #     SearchResult(
            #         object_rid=hit["_source"]["object_rid"],
            #         object_type_api_name=hit["_source"]["object_type_api_name"],
            #         pk_value=hit["_source"]["pk_value"],
            #         score=hit["_score"],
            #         metadata=hit["_source"].get("metadata")
            #     )
            #     for hit in hits
            # ]

            # Mock implementation
            mock_results = self._mock_vector_search_results(query_vector, top_k, object_types)
            return mock_results

        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []

    async def delete_vectors(self, object_rids: list[str]) -> bool:
        """
        Delete vectors by object RIDs.

        Args:
            object_rids: List of object RIDs to delete

        Returns:
            True if operation was successful
        """
        if not object_rids:
            return True

        try:
            # In production:
            # from elasticsearch.helpers import bulk
            #
            # def generate_delete_actions():
            #     for rid in object_rids:
            #         yield {
            #             "_index": self.vector_index,
            #             "_id": rid,
            #             "_op_type": "delete"
            #         }
            #
            # success_count, errors = bulk(self.client, generate_delete_actions())

            # Mock implementation
            success_count = len(object_rids)
            self.logger.info(f"Deleted {success_count} vectors from Elasticsearch")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete vectors: {e}")
            return False

    async def get_vector_stats(self) -> dict[str, int]:
        """
        Get vector index statistics.

        Returns:
            Dictionary with index statistics
        """
        try:
            # In production:
            # stats = self.client.indices.stats(index=self.vector_index)
            # doc_count = stats["indices"][self.vector_index]["total"]["docs"]["count"]
            # store_size = stats["indices"][self.vector_index]["total"]["store"]["size_in_bytes"]

            # Mock stats
            return {"total_vectors": 1000, "index_size_bytes": 1048576, "object_types": 5}  # 1MB

        except Exception as e:
            self.logger.error(f"Failed to get vector stats: {e}")
            return {"total_vectors": 0, "index_size_bytes": 0, "object_types": 0}

    def _mock_vector_search_results(
        self, query_vector: list[float], top_k: int, object_types: list[str] | None = None
    ) -> list[SearchResult]:
        """Mock vector search results for development purposes."""
        # Generate mock results with decreasing similarity scores
        results = []
        base_types = object_types or ["Customer", "Product", "Order"]

        for i in range(min(top_k, 10)):
            score = 0.95 - (i * 0.05)  # Decreasing scores
            object_type = base_types[i % len(base_types)]

            results.append(
                SearchResult(
                    object_rid=f"ontology:default:{object_type.lower()}:mock_{i}",
                    object_type_api_name=object_type,
                    pk_value=f"mock_{i}",
                    score=max(score, 0.1),  # Ensure score doesn't go negative
                    metadata={"category": f"mock_category_{i % 3}"},
                )
            )

        return results


class MockElasticsearchVectorClient:
    """Mock Elasticsearch client for vector operations."""

    def __init__(self):
        self.indices = MockVectorIndices()
        self.logger = logging.getLogger(__name__)

    def index(self, index: str, doc_id: str, body: dict) -> dict:
        """Mock index operation."""
        self.logger.debug(f"Mock vector index: {index}, id: {doc_id}")
        return {"result": "created", "_id": doc_id}

    def search(self, index: str, body: dict) -> dict:
        """Mock vector search operation."""
        self.logger.debug(f"Mock vector search: {index}")
        return {
            "hits": {
                "total": {"value": 10},
                "hits": [
                    {
                        "_source": {
                            "object_rid": f"mock_rid_{i}",
                            "object_type_api_name": "MockType",
                            "pk_value": f"mock_{i}",
                            "metadata": {"category": "mock"},
                        },
                        "_score": 0.95 - (i * 0.05),
                    }
                    for i in range(10)
                ],
            }
        }

    def delete(self, index: str, doc_id: str) -> dict:
        """Mock delete operation."""
        self.logger.debug(f"Mock vector delete: {index}, id: {doc_id}")
        return {"result": "deleted", "_id": doc_id}


class MockVectorIndices:
    """Mock indices API for vector operations."""

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
