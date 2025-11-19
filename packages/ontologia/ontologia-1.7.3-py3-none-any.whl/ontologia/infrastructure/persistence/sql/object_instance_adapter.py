"""Adapter to align SQLObjectInstanceRepository with ObjectInstanceRepository protocol."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)

logger = logging.getLogger(__name__)


class ObjectInstanceRepositoryAdapter(ObjectInstanceRepository):
    """Adapter that makes SQLObjectInstanceRepository conform to ObjectInstanceRepository protocol."""

    def __init__(self, sql_repo: SQLObjectInstanceRepository, metamodel_repo: Any):
        """
        Initialize adapter with SQL repository and metamodel repository for RID resolution.

        Args:
            sql_repo: SQLObjectInstanceRepository instance
            metamodel_repo: Metamodel repository to resolve object_type_rid from api_name
        """
        self._sql_repo = sql_repo
        self._metamodel_repo = metamodel_repo

    def _resolve_object_type_rid(self, object_type_rid: str) -> tuple[str, str, str]:
        """
        Resolve an object type identifier into ``(service, instance, api_name)``.

        Supports the following inputs:
        - ``service:instance:api_name`` explicit tuple encoding
        - a resource ``rid`` for the object type
        - a bare ``api_name`` (falls back to default scope)
        """
        if ":" in object_type_rid:
            parts = object_type_rid.split(":")
            if len(parts) >= 3:
                return parts[0], parts[1], parts[2]

        # Try repo facade first
        try:
            obj = getattr(self._metamodel_repo, "get_object_type_by_rid", lambda *_: None)(
                object_type_rid
            )
        except Exception:
            obj = None

        # Attempt to read service/instance from Resource table using a session if available
        session = None
        try:
            session = getattr(self._metamodel_repo, "session", None) or getattr(
                self._metamodel_repo, "_session", None
            )
        except Exception:
            session = None
        # Fallback: use the SQL repo's session (always present)
        if session is None:
            try:
                session = self._sql_repo.session
            except Exception:
                session = None
        try:
            if session is not None:
                from registro.core.resource import Resource

                from ontologia.domain.metamodels.types.object_type import ObjectType as _OT

                ot = obj or session.exec(
                    __import__("sqlmodel").sqlmodel.select(_OT).where(_OT.rid == object_type_rid)
                ).first()
                if ot is not None:
                    res = session.exec(
                        __import__("sqlmodel").sqlmodel.select(Resource).where(Resource.rid == ot.rid)
                    ).first()
                    if res is not None:
                        return str(res.service), str(res.instance), str(ot.api_name)
        except Exception:
            pass

        if obj is not None:
            api = getattr(obj, "api_name", None)
            if api:
                return "default", "default", str(api)

        # Last resort: treat identifier as api_name in default scope
        return "default", "default", object_type_rid

    def get_object_instance(
        self,
        object_type_rid: str,
        pk_value: str,
        valid_at: datetime | None = None,
    ) -> ObjectInstance | None:
        service, instance, api_name = self._resolve_object_type_rid(object_type_rid)
        return self._sql_repo.get_object_instance(
            service, instance, api_name, pk_value, valid_at=valid_at
        )

    def list_object_instances(
        self,
        object_type_rid: str,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> tuple[list[ObjectInstance], int]:
        service, instance, api_name = self._resolve_object_type_rid(object_type_rid)
        instances, total = self._sql_repo.list_object_instances(
            service,
            instance,
            api_name,
            limit,
            offset,
            valid_at=valid_at,
        )
        return instances, total

    def save_object_instance(self, obj: ObjectInstance) -> ObjectInstance:
        logger.debug(
            "Adapter save_object_instance session_id=%s new_before=%d",
            id(self._sql_repo.session),
            len(self._sql_repo.session.new),
        )
        result = self._sql_repo.save_object_instance(obj)
        logger.debug("Adapter save_object_instance new_after=%d", len(self._sql_repo.session.new))
        return result

    def delete_object_instance(
        self,
        object_type_rid: str,
        pk_value: str,
    ) -> bool:
        service, instance, api_name = self._resolve_object_type_rid(object_type_rid)
        result = self._sql_repo.delete_object_instance(service, instance, api_name, pk_value)
        return result

    def count_object_instances(
        self,
        object_type_rid: str,
        valid_at: datetime | None = None,
    ) -> int:
        service, instance, api_name = self._resolve_object_type_rid(object_type_rid)
        return self._sql_repo.count_object_instances(service, instance, api_name, valid_at=valid_at)

    def get_object_instance_history(
        self,
        object_type_rid: str,
        pk_value: str,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        transaction_from: datetime | None = None,
        transaction_to: datetime | None = None,
    ) -> list[ObjectInstance]:
        service, instance, api_name = self._resolve_object_type_rid(object_type_rid)
        return self._sql_repo.get_object_instance_history(
            service,
            instance,
            api_name,
            pk_value,
            valid_from=valid_from,
            valid_to=valid_to,
            transaction_from=transaction_from,
            transaction_to=transaction_to,
        )


__all__ = ["ObjectInstanceRepositoryAdapter"]
