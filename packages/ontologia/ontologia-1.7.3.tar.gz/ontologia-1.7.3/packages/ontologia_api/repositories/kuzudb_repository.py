"""
Backward-compatible import for Kuzu repository (moved to core infrastructure).
"""

from __future__ import annotations

from ontologia.infrastructure.persistence.kuzu import KuzuDBRepository, get_kuzu_repo

__all__ = ["KuzuDBRepository", "get_kuzu_repo"]
