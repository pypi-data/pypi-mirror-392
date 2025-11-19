"""
embedding.py
-----------
Event handlers for maintaining vector embeddings and similarity search.

Handles generating embeddings for object instances and maintaining
vector indexes for semantic search capabilities.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia.config import load_config
from ontologia.domain.events import (
    InProcessEventBus,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
    SubscribableEventBus,
)
from ontologia.domain.instances.repositories import VectorObject, VectorRepository
from ontologia.tracing import trace_operation

logger = logging.getLogger(__name__)
# Global registry to prevent duplicate registrations
_registered_buses: dict[int, EmbeddingEventHandler] = {}


class EmbeddingEventHandler:
    """
    Handles domain events for maintaining vector embeddings.

    This handler ensures that object instances are converted to vector
    embeddings and stored in the vector database when they are created
    or updated, and removed when deleted.
    """

    def __init__(self, vector_repo: VectorRepository | None = None) -> None:
        """
        Initialize the embedding event handler.

        Args:
            vector_repo: Vector repository instance
        """
        self._vector_repo = vector_repo
        self._config = load_config()
        self._logger = logging.getLogger(__name__)
        # Counters for observability
        self._counters = {
            "embedding_operations": 0,
            "delete_operations": 0,
            "failed_operations": 0,
            "skipped_operations": 0,
        }

    def _should_process_embeddings(self) -> bool:
        """
        Check if embedding processing should be performed based on configuration.

        Returns:
            True if embedding processing is enabled and vector repo is available
        """
        if not self._vector_repo:
            return False

        # Check if vector features are enabled in configuration
        if hasattr(self._config.features, "enable_vector_embeddings"):
            return self._config.features.enable_vector_embeddings

        # Default to enabled for development
        return True

    @trace_operation("embedding_upsert", event_type="ObjectInstanceUpserted")
    def handle_object_instance_upserted(self, event: ObjectInstanceUpserted) -> None:
        """
        Handle object instance upsert events by generating and storing embeddings.

        Args:
            event: ObjectInstanceUpserted event
        """
        object_type = event.object_type_api_name
        pk_value = str(event.primary_key_value)

        if not self._should_process_embeddings():
            self._counters["skipped_operations"] += 1
            self._logger.debug(
                "Vector embeddings disabled, skipping upsert for object_type=%s, pk=%s",
                object_type,
                pk_value,
            )
            return

        if not self._vector_repo:
            self._counters["failed_operations"] += 1
            self._logger.warning(
                "Vector repository not available, skipping embedding for object_type=%s, pk=%s",
                object_type,
                pk_value,
            )
            return

        try:
            # Generate embedding for the object
            vector_object = self._generate_embedding(event)
            if not vector_object:
                self._counters["skipped_operations"] += 1
                self._logger.debug(
                    "No embedding generated for object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
                return

            # Store the vector
            import asyncio

            success = asyncio.run(self._vector_repo.upsert_vectors([vector_object]))

            if success:
                self._counters["embedding_operations"] += 1
                self._logger.info(
                    "Generated and stored embedding for object: object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
            else:
                self._counters["failed_operations"] += 1
                self._logger.warning(
                    "Failed to store embedding for object: object_type=%s, pk=%s",
                    object_type,
                    pk_value,
                )
        except Exception:
            self._counters["failed_operations"] += 1
            self._logger.error(
                "Error processing embedding for object: object_type=%s, pk=%s",
                object_type,
                pk_value,
                exc_info=True,
            )

    @trace_operation("embedding_delete", event_type="ObjectInstanceDeleted")
    def handle_object_instance_deleted(self, event: ObjectInstanceDeleted) -> None:
        """
        Handle object instance deletion events by removing from vector store.

        Args:
            event: ObjectInstanceDeleted event
        """
        if not self._should_process_embeddings():
            self._logger.debug("Vector embeddings disabled, skipping delete handler")
            return

        if not self._vector_repo:
            self._logger.warning("Vector repository not available, skipping deletion")
            return

        try:
            # Generate object RID for deletion
            object_rid = f"ontology:default:{event.object_type_api_name}:{event.primary_key_value}"

            # Delete from vector store
            import asyncio

            success = asyncio.run(self._vector_repo.delete_vectors([object_rid]))

            if success:
                self._logger.info(
                    f"Deleted embedding for object {event.object_type_api_name}:{event.primary_key_value} from vector store"
                )
            else:
                self._logger.warning(
                    f"Failed to delete embedding for object {event.object_type_api_name}:{event.primary_key_value} from vector store"
                )

        except Exception as e:
            self._logger.error(
                f"Error deleting embedding for object {event.object_type_api_name}:{event.primary_key_value}: {e}"
            )

    def get_stats(self) -> dict[str, int]:
        """Return current embedding processing statistics."""
        return dict(self._counters)

    def _generate_embedding(self, event: ObjectInstanceUpserted) -> VectorObject | None:
        """
        Generate vector embedding for an object instance.

        Args:
            event: ObjectInstanceUpserted event

        Returns:
            VectorObject instance or None if generation fails
        """
        if not event.primary_key_value:
            self._logger.warning(
                f"Object missing primary key value, skipping embedding generation: {event.object_type_api_name}"
            )
            return None

        # Prepare text content for embedding generation
        text_content = self._prepare_text_content(event)
        if not text_content:
            self._logger.debug(
                f"No text content available for embedding generation: {event.object_type_api_name}"
            )
            return None

        # Generate embedding (mock implementation)
        embedding = self._generate_text_embedding(text_content)
        if not embedding:
            return None

        # Build object RID
        object_rid = f"ontology:default:{event.object_type_api_name}:{event.primary_key_value}"

        # Prepare metadata
        metadata = {
            "object_type": event.object_type_api_name,
            "primary_key": str(event.primary_key_value),
            "indexed_at": event.occurred_at.isoformat(),
        }

        # Add some payload fields as metadata if available
        if event.payload:
            for key, value in event.payload.items():
                if isinstance(value, str) and len(value) < 200:  # Limit metadata size
                    metadata[key] = value

        return VectorObject(
            object_rid=object_rid,
            object_type_api_name=event.object_type_api_name,
            pk_value=str(event.primary_key_value),
            embedding=embedding,
            metadata=metadata,
        )

    def _prepare_text_content(self, event: ObjectInstanceUpserted) -> str:
        """
        Prepare text content for embedding generation from object payload.

        Args:
            event: ObjectInstanceUpserted event

        Returns:
            Concatenated text content suitable for embedding
        """
        if not event.payload:
            return ""

        # Extract text fields from payload
        text_parts = []

        # Common field names that might contain text
        text_fields = [
            "name",
            "title",
            "description",
            "content",
            "text",
            "summary",
            "notes",
            "comments",
            "details",
            "remarks",
        ]

        for field in text_fields:
            if field in event.payload and isinstance(event.payload[field], str):
                text_parts.append(event.payload[field])

        # Also include any string fields that aren't too long
        for key, value in event.payload.items():
            if isinstance(value, str) and key not in text_fields and len(value) < 500:
                text_parts.append(f"{key}: {value}")

        # Join with spaces and limit total length
        content = " ".join(text_parts)
        return content[:2000] if content else ""  # Limit to 2000 chars

    def _generate_text_embedding(self, text: str) -> list[float] | None:
        """
        Generate vector embedding from text content.

        Args:
            text: Text content to embed

        Returns:
            Vector embedding or None if generation fails
        """
        if not text.strip():
            return None

        try:
            # Mock embedding generation for development
            # In production, this would call an embedding service like OpenAI:
            # from openai import OpenAI
            # client = OpenAI()
            # response = client.embeddings.create(
            #     model="text-embedding-ada-002",
            #     input=text
            # )
            # return response.data[0].embedding

            # Generate mock embedding (1536 dimensions for OpenAI compatibility)
            import hashlib
            import math

            # Create deterministic but pseudo-random embedding based on text
            hash_obj = hashlib.sha256(text.encode())
            hash_hex = hash_obj.hexdigest()

            # Convert hash to floating point values
            embedding = []
            for i in range(0, len(hash_hex), 2):
                hex_pair = hash_hex[i : i + 2]
                val = int(hex_pair, 16) / 255.0  # Normalize to [0, 1]
                # Convert to [-1, 1] range and apply some transformation
                transformed = 2.0 * val - 1.0
                embedding.append(transformed)

            # Pad or truncate to 1536 dimensions (OpenAI standard)
            while len(embedding) < 1536:
                # Add some variation based on position
                pos_val = math.sin(len(embedding) * 0.1) * 0.1
                embedding.append(pos_val)

            return embedding[:1536]

        except Exception as e:
            self._logger.error(f"Failed to generate embedding for text: {e}")
            return None


def register_embedding_event_handlers(
    bus: SubscribableEventBus, vector_repo: VectorRepository | None = None
) -> EmbeddingEventHandler:
    """
    Register embedding event handlers with the event bus.

    Args:
        bus: Event bus to register handlers with
        vector_repo: Vector repository instance

    Returns:
        The registered EmbeddingEventHandler instance for metrics
    """
    if not isinstance(bus, InProcessEventBus):
        raise ValueError("Expected InProcessEventBus")

    key = id(bus)
    if key in _registered_buses:
        logger.warning("Embedding handlers already registered for this bus, skipping")
        return _registered_buses[key]

    handler = EmbeddingEventHandler(vector_repo)

    bus.subscribe(ObjectInstanceUpserted, handler.handle_object_instance_upserted)
    bus.subscribe(ObjectInstanceDeleted, handler.handle_object_instance_deleted)

    _registered_buses[key] = handler
    logger.info("Embedding event handlers registered with event bus")

    # Register metrics from the actual instance
    from ontologia.bootstrap import register_handler_metrics_from_instances

    register_handler_metrics_from_instances(embedding_handler=handler)

    return handler


async def search_similar_objects(
    vector_repo: VectorRepository,
    query_text: str,
    top_k: int = 10,
    filters: dict[str, str] | None = None,
    object_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Utility function to search for similar objects using text query.

    Args:
        vector_repo: Vector repository instance
        query_text: Text query to search for
        top_k: Maximum number of results
        filters: Optional metadata filters
        object_types: Optional object type filters

    Returns:
        List of similar objects with their metadata
    """
    if not vector_repo:
        return []

    try:
        # Generate embedding for query text
        handler = EmbeddingEventHandler()
        query_embedding = handler._generate_text_embedding(query_text)

        if not query_embedding:
            return []

        # Search by vector
        results = await vector_repo.search_by_vector(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filters,
            object_types=object_types,
        )

        # Convert to dict format
        return [
            {
                "object_rid": result.object_rid,
                "object_type_api_name": result.object_type_api_name,
                "pk_value": result.pk_value,
                "similarity_score": result.score,
                "metadata": result.metadata,
            }
            for result in results
        ]

    except Exception as e:
        logger.error(f"Failed to search similar objects: {e}")
        return []
