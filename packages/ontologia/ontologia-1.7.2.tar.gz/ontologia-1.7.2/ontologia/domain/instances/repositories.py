"""Repository interfaces for the instances bounded context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance


@dataclass(frozen=True, slots=True)
class VectorObject:
    """Object representation for vector storage and search."""

    object_rid: str
    object_type_api_name: str
    pk_value: str
    embedding: list[float]
    metadata: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Result from vector similarity search."""

    object_rid: str
    object_type_api_name: str
    pk_value: str
    score: float
    metadata: dict[str, str] | None = None


class ObjectInstanceRepository(Protocol):
    def get_object_instance(
        self,
        object_type_rid: str,
        pk_value: str,
        valid_at: datetime | None = None,
    ) -> ObjectInstance | None: ...

    def list_object_instances(
        self,
        object_type_rid: str,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> tuple[list[ObjectInstance], int]: ...

    def save_object_instance(self, obj: ObjectInstance) -> ObjectInstance: ...

    def delete_object_instance(
        self,
        object_type_rid: str,
        pk_value: str,
    ) -> bool: ...

    def count_object_instances(
        self,
        object_type_rid: str,
        valid_at: datetime | None = None,
    ) -> int: ...

    def get_object_instance_history(
        self,
        object_type_rid: str,
        pk_value: str,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        transaction_from: datetime | None = None,
        transaction_to: datetime | None = None,
    ) -> list[ObjectInstance]: ...


class LinkedObjectRepository(Protocol):
    def get_linked_object(
        self,
        link_type_rid: str,
        source_pk_value: str,
        target_pk_value: str,
        valid_at: datetime | None = None,
    ) -> LinkedObject | None: ...

    def list_linked_objects(
        self,
        link_type_rid: str,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> tuple[list[LinkedObject], int]: ...

    def save_linked_object(self, link: LinkedObject) -> LinkedObject: ...

    def delete_linked_object(
        self,
        link_type_rid: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> bool: ...

    def traverse_outgoing(
        self,
        link_type_rid: str,
        source_pk_value: str,
        limit: int = 100,
        valid_at: datetime | None = None,
    ) -> list[LinkedObject]: ...

    def traverse_incoming(
        self,
        link_type_rid: str,
        target_pk_value: str,
        limit: int = 100,
        valid_at: datetime | None = None,
    ) -> list[LinkedObject]: ...

    def get_linked_object_history(
        self,
        link_type_rid: str,
        source_pk_value: str,
        target_pk_value: str,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        transaction_from: datetime | None = None,
        transaction_to: datetime | None = None,
    ) -> list[LinkedObject]: ...


class VectorRepository(Protocol):
    """Repository interface for vector storage and similarity search operations."""

    async def upsert_vectors(self, objects: list[VectorObject]) -> bool: ...

    async def search_by_vector(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None,
        object_types: list[str] | None = None,
    ) -> list[SearchResult]: ...

    async def delete_vectors(self, object_rids: list[str]) -> bool: ...

    async def get_vector_stats(self) -> dict[str, int]: ...
