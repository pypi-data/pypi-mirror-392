"""
Backward-compatible import for GraphInstancesRepository (moved to core infrastructure).
"""

from __future__ import annotations

from ontologia.infrastructure.persistence.graph.instances_repository import (
    GraphInstancesRepository,
)

__all__ = ["GraphInstancesRepository"]
