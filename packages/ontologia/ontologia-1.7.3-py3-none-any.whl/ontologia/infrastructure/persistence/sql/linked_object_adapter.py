"""Adapter to align SQLLinkedObjectRepository with LinkedObjectRepository protocol."""

from __future__ import annotations

from typing import Any

from ontologia.domain.instances.repositories import LinkedObjectRepository
from ontologia.domain.metamodels.instances.models_sql import LinkedObject
from ontologia.infrastructure.persistence.sql.linked_objects_repository import (
    SQLLinkedObjectRepository,
)


class LinkedObjectRepositoryAdapter(LinkedObjectRepository):
    """Adapter that makes SQLLinkedObjectRepository conform to LinkedObjectRepository protocol."""

    def __init__(self, sql_repo: SQLLinkedObjectRepository, metamodel_repo: Any):
        """
        Initialize adapter with SQL repository and metamodel repository for RID resolution.

        Args:
            sql_repo: SQLLinkedObjectRepository instance
            metamodel_repo: Metamodel repository to resolve link_type_rid from api_name
        """
        self._sql_repo = sql_repo
        self._metamodel_repo = metamodel_repo

    def _resolve_link_type_rid(self, link_type_rid: str) -> tuple[str, str, str]:
        """
        Resolve a link type identifier into ``(service, instance, api_name)``.

        Supports the following inputs:
        - ``service:instance:api_name`` explicit tuple encoding
        - a resource ``rid`` (UUID-like) for the link type
        - a bare ``api_name`` (falls back to default scope)
        """
        # Explicit tuple encoding: service:instance:api_name
        if ":" in link_type_rid:
            parts = link_type_rid.split(":")
            if len(parts) >= 3:
                return parts[0], parts[1], parts[2]

        # Try to resolve using the metamodel repository/session, avoiding
        # accessing computed properties (e.g., link_type.service) that rely on
        # attached Resource state which may not be populated on a bare ORM row.
        try:
            # Prefer direct queries via the repository's session when available
            session = getattr(self._metamodel_repo, "session", None) or getattr(
                self._metamodel_repo, "_session", None
            )
            if session is not None:
                # Import locally to avoid hard dependency at module import time
                from registro.core.resource import Resource

                from ontologia.domain.metamodels.types.link_type import LinkType as _LT

                lt = session.exec(
                    __import__("sqlmodel").sqlmodel.select(_LT).where(_LT.rid == link_type_rid)
                ).first()
                if lt is not None:
                    res = session.exec(
                        __import__("sqlmodel")
                        .sqlmodel.select(Resource)
                        .where(Resource.rid == link_type_rid)
                    ).first()
                    if res is not None:
                        return str(res.service), str(res.instance), str(lt.api_name)

                # Fallback: treat identifier as api_name and resolve scope via Resource join
                lt2 = session.exec(
                    __import__("sqlmodel")
                    .sqlmodel.select(_LT, Resource)
                    .join(Resource, Resource.rid == _LT.rid)
                    .where(_LT.api_name == link_type_rid)
                ).first()
                if lt2 is not None:
                    lt_row, res_row = lt2
                    return (
                        str(getattr(res_row, "service", "ontology")),
                        str(getattr(res_row, "instance", "default")),
                        str(getattr(lt_row, "api_name", link_type_rid)),
                    )

            # Fallback to facade API if provided
            link_type = getattr(self._metamodel_repo, "get_link_type_by_rid", lambda *_: None)(
                link_type_rid
            )
            if link_type is not None:
                # Only use attributes guaranteed to exist
                api_name = getattr(link_type, "api_name", None)
                # If we can't reliably get service/instance from the model, fall through
                if api_name:
                    return "default", "default", str(api_name)
        except Exception:
            # Swallow and fall through to default
            pass

        # Last resort: treat identifier as api_name in ontology/default scope
        return "ontology", "default", link_type_rid

    def get_linked_object(
        self,
        link_type_rid: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> LinkedObject | None:
        service, instance, api_name = self._resolve_link_type_rid(link_type_rid)
        return self._sql_repo.get_linked_object(
            service, instance, api_name, source_pk_value, target_pk_value
        )

    def list_linked_objects(
        self,
        link_type_rid: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[LinkedObject], int]:
        service, instance, api_name = self._resolve_link_type_rid(link_type_rid)
        return self._sql_repo.list_linked_objects(service, instance, api_name, limit, offset)

    def save_linked_object(self, link: LinkedObject) -> LinkedObject:
        return self._sql_repo.save_linked_object(link)

    def delete_linked_object(
        self,
        link_type_rid: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> bool:
        service, instance, api_name = self._resolve_link_type_rid(link_type_rid)
        return self._sql_repo.delete_linked_object(
            service, instance, api_name, source_pk_value, target_pk_value
        )

    def traverse_outgoing(
        self,
        link_type_rid: str,
        source_pk_value: str,
        limit: int = 100,
    ) -> list[LinkedObject]:
        service, instance, api_name = self._resolve_link_type_rid(link_type_rid)
        return self._sql_repo.traverse_outgoing(service, instance, api_name, source_pk_value, limit)

    def traverse_incoming(
        self,
        link_type_rid: str,
        target_pk_value: str,
        limit: int = 100,
    ) -> list[LinkedObject]:
        service, instance, api_name = self._resolve_link_type_rid(link_type_rid)
        return self._sql_repo.traverse_incoming(service, instance, api_name, target_pk_value, limit)


__all__ = ["LinkedObjectRepositoryAdapter"]
