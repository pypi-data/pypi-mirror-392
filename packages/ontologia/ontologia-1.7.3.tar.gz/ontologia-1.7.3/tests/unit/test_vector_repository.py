"""
Test vector repository implementation and embedding event handlers.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ontologia.domain.events import ObjectInstanceDeleted, ObjectInstanceUpserted
from ontologia.domain.instances.repositories import SearchResult, VectorObject
from ontologia.event_handlers.embedding import EmbeddingEventHandler, search_similar_objects
from ontologia.infrastructure.elasticsearch_vector_repository import ElasticsearchVectorRepository


class TestVectorRepository:
    """Test vector repository implementations."""

    def test_elasticsearch_vector_repository_init(self):
        """Test Elasticsearch vector repository initialization."""
        repo = ElasticsearchVectorRepository(hosts=["http://localhost:9200"])
        assert repo.hosts == ["http://localhost:9200"]
        assert repo.vector_index == "ontologia_vectors"
        assert repo.client is not None

    @pytest.mark.asyncio
    async def test_upsert_vectors_success(self):
        """Test successful vector upsert operation."""
        repo = ElasticsearchVectorRepository()

        vectors = [
            VectorObject(
                object_rid="test:object:1",
                object_type_api_name="TestObject",
                pk_value="1",
                embedding=[0.1, 0.2, 0.3] * 512,  # 1536 dimensions
                metadata={"name": "test"},
            )
        ]

        result = await repo.upsert_vectors(vectors)
        assert result is True

    @pytest.mark.asyncio
    async def test_upsert_vectors_empty(self):
        """Test upsert operation with empty vector list."""
        repo = ElasticsearchVectorRepository()
        result = await repo.upsert_vectors([])
        assert result is True

    @pytest.mark.asyncio
    async def test_search_by_vector(self):
        """Test vector similarity search."""
        repo = ElasticsearchVectorRepository()

        query_vector = [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        results = await repo.search_by_vector(
            query_vector=query_vector,
            top_k=5,
            filters={"category": "test"},
            object_types=["TestObject"],
        )

        assert len(results) <= 5
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.object_type_api_name == "TestObject"
            assert result.score >= 0.0
            assert result.score <= 1.0

    @pytest.mark.asyncio
    async def test_delete_vectors(self):
        """Test vector deletion operation."""
        repo = ElasticsearchVectorRepository()

        object_rids = ["test:object:1", "test:object:2"]
        result = await repo.delete_vectors(object_rids)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_vector_stats(self):
        """Test getting vector index statistics."""
        repo = ElasticsearchVectorRepository()
        stats = await repo.get_vector_stats()

        assert "total_vectors" in stats
        assert "index_size_bytes" in stats
        assert "object_types" in stats
        assert isinstance(stats["total_vectors"], int)


class TestEmbeddingEventHandler:
    """Test embedding event handler functionality."""

    def test_embedding_handler_init(self):
        """Test embedding handler initialization."""
        mock_repo = MagicMock()
        handler = EmbeddingEventHandler(mock_repo)
        assert handler._vector_repo is mock_repo

    def test_should_process_embeddings_disabled(self):
        """Test that embedding processing is disabled when configured."""
        mock_repo = MagicMock()
        handler = EmbeddingEventHandler(mock_repo)

        # Mock config to disable embeddings
        with patch.object(handler._config.features, "enable_vector_embeddings", new=False):
            assert handler._should_process_embeddings() is False

    def test_should_process_embeddings_no_repo(self):
        """Test that embedding processing is disabled when no repo available."""
        handler = EmbeddingEventHandler(None)
        assert handler._should_process_embeddings() is False

    def test_handle_object_instance_upserted_disabled(self):
        """Test handling upsert event when embeddings are disabled."""
        mock_repo = MagicMock()
        handler = EmbeddingEventHandler(mock_repo)

        # Mock config to disable embeddings
        with patch.object(handler._config.features, "enable_vector_embeddings", new=False):
            event = ObjectInstanceUpserted(
                service="test_service",
                instance="test_instance",
                object_type_api_name="TestObject",
                primary_key_field="id",
                primary_key_value="1",
                payload={"name": "test"},
            )

            handler.handle_object_instance_upserted(event)
            assert handler._counters["skipped_operations"] == 1

    def test_handle_object_instance_upserted_no_repo(self):
        """Test handling upsert event when no vector repo available."""
        handler = EmbeddingEventHandler(None)

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={"name": "test"},
        )

        handler.handle_object_instance_upserted(event)
        # When no repo is available, _should_process_embeddings() returns False
        # so it increments skipped_operations, not failed_operations
        assert handler._counters.get("skipped_operations", 0) == 1

    def test_handle_object_instance_upserted_success(self):
        """Test successful handling of upsert event."""
        mock_repo = AsyncMock()
        mock_repo.upsert_vectors.return_value = True

        handler = EmbeddingEventHandler(mock_repo)

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={"name": "test object", "description": "test description"},
        )

        handler.handle_object_instance_upserted(event)
        assert handler._counters["embedding_operations"] == 1  # type: ignore[index]

    def test_handle_object_instance_deleted_disabled(self):
        """Test handling delete event when embeddings are disabled."""
        mock_repo = MagicMock()
        handler = EmbeddingEventHandler(mock_repo)

        # Mock config to disable embeddings
        with patch.object(handler._config.features, "enable_vector_embeddings", enable_vector_embeddings=False):  # type: ignore[attr-defined]
            event = ObjectInstanceDeleted(
                service="test_service",
                instance="test_instance",
                object_type_api_name="TestObject",
                primary_key_field="id",
                primary_key_value="1",
            )

            handler.handle_object_instance_deleted(event)

    def test_handle_object_instance_deleted_success(self):
        """Test successful handling of delete event."""
        mock_repo = AsyncMock()
        mock_repo.delete_vectors.return_value = True

        handler = EmbeddingEventHandler(mock_repo)

        event = ObjectInstanceDeleted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
        )

        handler.handle_object_instance_deleted(event)

    def test_generate_embedding_no_primary_key(self):
        """Test embedding generation fails without primary key."""
        handler = EmbeddingEventHandler()

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value=None,  # type: ignore[arg-type]
            payload={"name": "test"},
        )

        result = handler._generate_embedding(event)
        assert result is None

    def test_generate_embedding_no_payload(self):
        """Test embedding generation with no payload."""
        handler = EmbeddingEventHandler()

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={},
        )

        result = handler._generate_embedding(event)
        assert result is None

    def test_generate_embedding_success(self):
        """Test successful embedding generation."""
        handler = EmbeddingEventHandler()

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={"name": "test object", "description": "test description"},
        )

        result = handler._generate_embedding(event)
        assert result is not None
        assert isinstance(result, VectorObject)
        assert result.object_rid == "ontology:default:TestObject:1"
        assert result.object_type_api_name == "TestObject"
        assert result.pk_value == "1"
        assert len(result.embedding) == 1536  # OpenAI embedding dimensions

    def test_prepare_text_content_with_text_fields(self):
        """Test text content preparation with common text fields."""
        handler = EmbeddingEventHandler()

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={
                "name": "Test Name",
                "description": "Test Description",
                "content": "Test Content",
                "other_field": "other value",
            },
        )

        content = handler._prepare_text_content(event)
        assert "Test Name" in content
        assert "Test Description" in content
        assert "Test Content" in content
        assert "other value" in content

    def test_prepare_text_content_empty_payload(self):
        """Test text content preparation with empty payload."""
        handler = EmbeddingEventHandler()

        event = ObjectInstanceUpserted(
            service="test_service",
            instance="test_instance",
            object_type_api_name="TestObject",
            primary_key_field="id",
            primary_key_value="1",
            payload={},
        )

        content = handler._prepare_text_content(event)
        assert content == ""

    def test_generate_text_embedding_empty_text(self):
        """Test embedding generation with empty text."""
        handler = EmbeddingEventHandler()

        result = handler._generate_text_embedding("")
        assert result is None

    def test_generate_text_embedding_success(self):
        """Test successful text embedding generation."""
        handler = EmbeddingEventHandler()

        result = handler._generate_text_embedding("test text for embedding")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)

    def test_get_stats(self):
        """Test getting handler statistics."""
        handler = EmbeddingEventHandler()
        stats = handler.get_stats()

        assert "embedding_operations" in stats
        assert "delete_operations" in stats
        assert "failed_operations" in stats
        assert "skipped_operations" in stats
        assert all(isinstance(v, int) for v in stats.values())


class TestVectorSearchUtility:
    """Test vector search utility functions."""

    @pytest.mark.asyncio
    async def test_search_similar_objects_no_repo(self):
        """Test search similar objects with no repository."""
        result = await search_similar_objects(vector_repo=None, query_text="test query", top_k=5)  # type: ignore[arg-type]
        assert result == []

    @pytest.mark.asyncio
    async def test_search_similar_objects_success(self):
        """Test successful search similar objects."""
        mock_repo = AsyncMock()
        mock_results = [
            SearchResult(
                object_rid="test:object:1",
                object_type_api_name="TestObject",
                pk_value="1",
                score=0.95,
                metadata={"name": "test"},
            )
        ]
        mock_repo.search_by_vector.return_value = mock_results

        result = await search_similar_objects(
            vector_repo=mock_repo,
            query_text="test query",
            top_k=5,
            filters={"category": "test"},
            object_types=["TestObject"],
        )

        assert len(result) == 1
        assert result[0]["object_rid"] == "test:object:1"  # type: ignore[index]
        assert result[0]["similarity_score"] == 0.95  # type: ignore[index]
        assert result[0]["object_type_api_name"] == "TestObject"  # type: ignore[index]

    @pytest.mark.asyncio
    async def test_search_similar_objects_no_embedding(self):
        """Test search similar objects when embedding generation fails."""
        mock_repo = AsyncMock()

        # Mock the handler to return None for embedding
        with patch(
            "ontologia.event_handlers.embedding.EmbeddingEventHandler"
        ) as mock_handler_class:
            mock_handler = MagicMock()
            mock_handler._generate_text_embedding.return_value = None
            mock_handler_class.return_value = mock_handler

            result = await search_similar_objects(
                vector_repo=mock_repo, query_text="test query", top_k=5
            )

            assert result == []


class TestVectorStoreFactory:
    """Test vector store factory functionality."""

    def test_create_vector_repository_disabled(self):
        """Test factory when vector embeddings are disabled."""
        with patch("ontologia.infrastructure.vector_store_factory.load_config") as mock_load_config:
            mock_config = MagicMock()
            mock_config.features.enable_vector_embeddings = False  # type: ignore[attr-defined]
            mock_load_config.return_value = mock_config

            from ontologia.infrastructure.vector_store_factory import create_vector_repository

            result = create_vector_repository()
            assert result is None

    def test_create_vector_repository_no_config(self):
        """Test factory when vector store config is missing."""
        with patch("ontologia.infrastructure.vector_store_factory.load_config") as mock_load_config:
            mock_config = MagicMock()
            mock_config.features.enable_vector_embeddings = True  # type: ignore[attr-defined]
            mock_config.vector_store = None  # type: ignore[attr-defined]
            mock_load_config.return_value = mock_config

            from ontologia.infrastructure.vector_store_factory import create_vector_repository

            result = create_vector_repository()
            assert result is None

    def test_create_vector_repository_elasticsearch(self):
        """Test factory creating Elasticsearch repository."""
        with patch("ontologia.infrastructure.vector_store_factory.load_config") as mock_load_config:
            mock_config = MagicMock()
            mock_config.features.enable_vector_embeddings = True  # type: ignore[attr-defined]
            mock_config.vector_store.provider = "elasticsearch"  # type: ignore[attr-defined]
            mock_config.vector_store.address = "http://localhost:9200"  # type: ignore[attr-defined]
            mock_load_config.return_value = mock_config

            from ontologia.infrastructure.vector_store_factory import create_vector_repository

            result = create_vector_repository()
            assert result is not None
            assert isinstance(result, ElasticsearchVectorRepository)

    def test_get_vector_repository_info_enabled(self):
        """Test getting vector repository info when enabled."""
        with patch("ontologia.infrastructure.vector_store_factory.load_config") as mock_load_config:
            mock_config = MagicMock()
            mock_config.features.enable_vector_embeddings = True  # type: ignore[attr-defined]
            mock_config.vector_store.provider = "elasticsearch"  # type: ignore[attr-defined]
            mock_config.vector_store.address = "http://localhost:9200"  # type: ignore[attr-defined]
            mock_config.vector_store.embedding_dimensions = 1536  # type: ignore[attr-defined]
            mock_config.vector_store.similarity_metric = "cosine"  # type: ignore[attr-defined]
            mock_config.vector_store.index_name = "ontologia_vectors"  # type: ignore[attr-defined]
            mock_load_config.return_value = mock_config

            from ontologia.infrastructure.vector_store_factory import get_vector_repository_info

            info = get_vector_repository_info()

            assert info["enabled"] is True
            assert info["provider"] == "elasticsearch"
            assert info["address"] == "http://localhost:9200"
            assert info["embedding_dimensions"] == 1536

    def test_get_vector_repository_info_disabled(self):
        """Test getting vector repository info when disabled."""
        with patch("ontologia.infrastructure.vector_store_factory.load_config") as mock_load_config:
            mock_config = MagicMock()
            mock_config.features.enable_vector_embeddings = False  # type: ignore[attr-defined]
            mock_load_config.return_value = mock_config

            from ontologia.infrastructure.vector_store_factory import get_vector_repository_info

            info = get_vector_repository_info()

            assert info["enabled"] is False
            assert "reason" in info
