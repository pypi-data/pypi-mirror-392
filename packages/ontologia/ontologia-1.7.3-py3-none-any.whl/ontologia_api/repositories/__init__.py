"""Repositories for data access."""

from ontologia_api.repositories.kuzudb_repository import KuzuDBRepository, get_kuzu_repo
from ontologia_api.repositories.metamodel_repository import MetamodelRepository

__all__ = ["KuzuDBRepository", "get_kuzu_repo", "MetamodelRepository"]
