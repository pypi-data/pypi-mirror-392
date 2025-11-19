"""
vector_store_factory.py
------------------------
Factory for creating vector repository instances based on configuration.

Provides a centralized way to create vector repositories based on the
provider specified in configuration, supporting multiple backends.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia.config import load_config
from ontologia.domain.instances.repositories import VectorRepository

logger = logging.getLogger(__name__)


def create_vector_repository() -> VectorRepository | None:
    """
    Create a vector repository instance based on configuration.

    Returns:
        VectorRepository instance or None if vector store is disabled
    """
    config = load_config()

    # Check if vector embeddings are enabled
    if (
        not hasattr(config.features, "enable_vector_embeddings")
        or not config.features.enable_vector_embeddings
    ):
        logger.info("Vector embeddings are disabled in configuration")
        return None

    # Get vector store configuration
    vector_config = getattr(config, "vector_store", None)
    if not vector_config:
        logger.warning("Vector store configuration not found")
        return None

    provider = getattr(vector_config, "provider", "elasticsearch")
    # address is currently unused; retained for future providers

    logger.info(f"Creating vector repository with provider: {provider}")

    try:
        if provider == "elasticsearch":
            return _create_elasticsearch_repository(vector_config)
        elif provider == "qdrant":
            return _create_qdrant_repository(vector_config)
        elif provider == "chroma":
            return _create_chroma_repository(vector_config)
        else:
            logger.error(f"Unsupported vector store provider: {provider}")
            return None

    except Exception as e:
        logger.error(f"Failed to create vector repository: {e}")
        return None


def _create_elasticsearch_repository(config: Any) -> VectorRepository:
    """Create Elasticsearch vector repository."""
    from ontologia.infrastructure.elasticsearch_vector_repository import (
        ElasticsearchVectorRepository,
    )

    hosts = getattr(config, "address", "http://localhost:9200")
    if isinstance(hosts, str):
        hosts = [hosts]

    # Additional configuration options
    kwargs = {}
    if hasattr(config, "username"):
        kwargs["http_auth"] = (config.username, getattr(config, "password", ""))
    if hasattr(config, "verify_certs"):
        kwargs["verify_certs"] = config.verify_certs

    repository = ElasticsearchVectorRepository(hosts=hosts, **kwargs)

    # Create index if it doesn't exist
    repository.create_vector_index_if_not_exists()

    logger.info(f"Elasticsearch vector repository created with hosts: {hosts}")
    return repository


def _create_qdrant_repository(config: Any) -> VectorRepository:
    """Create Qdrant vector repository."""
    # Placeholder for future Qdrant implementation
    logger.warning("Qdrant repository not yet implemented")
    raise NotImplementedError("Qdrant repository implementation pending")


def _create_chroma_repository(config: Any) -> VectorRepository:
    """Create ChromaDB vector repository."""
    # Placeholder for future ChromaDB implementation
    logger.warning("ChromaDB repository not yet implemented")
    raise NotImplementedError("ChromaDB repository implementation pending")


def get_vector_repository_info() -> dict[str, Any]:
    """
    Get information about the current vector repository configuration.

    Returns:
        Dictionary with configuration details
    """
    config = load_config()

    # Check if enabled
    if (
        not hasattr(config.features, "enable_vector_embeddings")
        or not config.features.enable_vector_embeddings
    ):
        return {"enabled": False, "reason": "Vector embeddings disabled in configuration"}

    vector_config = getattr(config, "vector_store", None)
    if not vector_config:
        return {"enabled": False, "reason": "Vector store configuration not found"}

    return {
        "enabled": True,
        "provider": getattr(vector_config, "provider", "elasticsearch"),
        "address": getattr(vector_config, "address", "http://localhost:9200"),
        "embedding_dimensions": getattr(vector_config, "embedding_dimensions", 1536),
        "similarity_metric": getattr(vector_config, "similarity_metric", "cosine"),
        "index_name": getattr(vector_config, "index_name", "ontologia_vectors"),
    }
