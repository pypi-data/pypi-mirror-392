"""
Graph persistence module for ontology system.

Provides graph database implementations for storing and querying
ontology instances and relationships using graph databases like
Neo4j, KuzuDB, or other graph storage systems.
"""

from .instances_repository import GraphInstancesRepository
from .linked_objects_repository import GraphLinkedObjectsRepository

__all__ = [
    "GraphInstancesRepository",
    "GraphLinkedObjectsRepository",
]
