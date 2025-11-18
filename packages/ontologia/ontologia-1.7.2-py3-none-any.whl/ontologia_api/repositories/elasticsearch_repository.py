"""
Backward-compatible shim. Use ontologia.infrastructure.elasticsearch_repository.
"""

from __future__ import annotations

from ontologia.infrastructure.elasticsearch_repository import ElasticsearchRepository

__all__ = ["ElasticsearchRepository"]
