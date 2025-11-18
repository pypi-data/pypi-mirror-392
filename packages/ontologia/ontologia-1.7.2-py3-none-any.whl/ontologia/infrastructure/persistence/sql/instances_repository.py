"""SQL implementation of the object instance repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from registro.core.resource import Resource
from sqlmodel import Session, and_, func, or_, select

from ontologia.domain.metamodels.instances.models_sql import ObjectInstance


class SQLObjectInstanceRepository:
    """Persist object instances using SQLModel persistence with bitemporal support."""

    def __init__(self, session: Session):
        self.session = session

    def get_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        valid_at: datetime | None = None,
    ) -> ObjectInstance | None:
        stmt = (
            select(ObjectInstance)
            .join(Resource, Resource.rid == ObjectInstance.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ObjectInstance.object_type_api_name == object_type_api_name,
                ObjectInstance.pk_value == pk_value,
            )
        )

        # Apply bitemporal filtering if valid_at is specified
        if valid_at is not None:
            stmt = self._apply_valid_time_filter(stmt, valid_at)

        res = self.session.exec(stmt).first()
        if res is not None:
            return res

        fallback = select(ObjectInstance).where(
            ObjectInstance.object_type_api_name == object_type_api_name,
            ObjectInstance.pk_value == pk_value,
        )

        if valid_at is not None:
            fallback = self._apply_valid_time_filter(fallback, valid_at)

        return self.session.exec(fallback).first()

    def list_object_instances(
        self,
        service: str,
        instance: str,
        object_type_api_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> tuple[list[ObjectInstance], int]:
        try:
            stmt = (
                select(ObjectInstance)
                .join(Resource, Resource.rid == ObjectInstance.rid)
                .where(Resource.service == service, Resource.instance == instance)
            )
            count_stmt = (
                select(func.count())
                .select_from(ObjectInstance)
                .join(Resource, Resource.rid == ObjectInstance.rid)
                .where(Resource.service == service, Resource.instance == instance)
            )

            if object_type_api_name:
                stmt = stmt.where(ObjectInstance.object_type_api_name == object_type_api_name)
                count_stmt = count_stmt.where(
                    ObjectInstance.object_type_api_name == object_type_api_name
                )

            # Apply bitemporal filtering if valid_at is specified
            if valid_at is not None:
                stmt = self._apply_valid_time_filter(stmt, valid_at)
                count_stmt = self._apply_valid_time_filter(count_stmt, valid_at)

            # Get total count
            total = self.session.exec(count_stmt).one()

            # Get paginated results
            stmt = stmt.limit(limit).offset(offset)
            results = list(self.session.exec(stmt).all())

            if results:
                return results, total
        except Exception:
            pass

        # Fallback without Resource join
        fallback = select(ObjectInstance)
        count_fallback = select(func.count()).select_from(ObjectInstance)

        if object_type_api_name:
            fallback = fallback.where(ObjectInstance.object_type_api_name == object_type_api_name)
            count_fallback = count_fallback.where(
                ObjectInstance.object_type_api_name == object_type_api_name
            )

        if valid_at is not None:
            fallback = self._apply_valid_time_filter(fallback, valid_at)
            count_fallback = self._apply_valid_time_filter(count_fallback, valid_at)

        total = self.session.exec(count_fallback).one()
        fallback = fallback.limit(limit).offset(offset)
        results = list(self.session.exec(fallback).all())

        return results, total

    def save_object_instance(self, obj: ObjectInstance) -> ObjectInstance:
        print(f"DEBUG: Repository save_object_instance called with pk={obj.pk_value}, service={obj.service}, instance={obj.instance}")
        print(f"DEBUG: Repository session ID: {id(self.session)}")
        print(f"DEBUG: Session dirty before merge: {self.session.dirty}")
        print(f"DEBUG: Session new before merge: {self.session.new}")
        
        # Try using add instead of merge to avoid replacing existing objects
        self.session.add(obj)
        persistent = obj
        print(f"DEBUG: After add, persistent.pk={persistent.pk_value}, service={persistent.service}, instance={persistent.instance}")
        print(f"DEBUG: After add, persistent.id={persistent.id}")
        print(f"DEBUG: After add, persistent.valid_from={persistent.valid_from}, transaction_from={persistent.transaction_from}")
        print(f"DEBUG: Session dirty after add: {self.session.dirty}")
        print(f"DEBUG: Session new after add: {self.session.new}")
        print(f"DEBUG: Session state after add in repo: new={len(self.session.new)}, dirty={len(self.session.dirty)}")
        print(f"DEBUG: Added object in session new: {persistent in self.session.new}")
        print(f"DEBUG: Added object id: {persistent.id}")
        # Don't access identity_map as it might contain deleted objects
        # print(f"DEBUG: Session identity map before return: {dict(self.session.identity_map)}")
        # Don't commit here - let the session context manager handle it
        # self.session.commit()
        print(f"DEBUG: Session state before return: new={len(self.session.new)}, dirty={len(self.session.dirty)}")
        return persistent

    def delete_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
    ) -> bool:
        obj = self.get_object_instance(service, instance, object_type_api_name, pk_value)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True

    def count_object_instances(
        self,
        service: str,
        instance: str,
        object_type_api_name: str | None = None,
        valid_at: datetime | None = None,
    ) -> int:
        """Count object instances matching the criteria."""
        try:
            count_stmt = (
                select(func.count())
                .select_from(ObjectInstance)
                .join(Resource, Resource.rid == ObjectInstance.rid)
                .where(Resource.service == service, Resource.instance == instance)
            )

            if object_type_api_name:
                count_stmt = count_stmt.where(
                    ObjectInstance.object_type_api_name == object_type_api_name
                )

            # Apply bitemporal filtering if valid_at is specified
            if valid_at is not None:
                count_stmt = self._apply_valid_time_filter(count_stmt, valid_at)

            return self.session.exec(count_stmt).one()
        except Exception:
            pass

        # Fallback without Resource join
        count_fallback = select(func.count()).select_from(ObjectInstance)
        if object_type_api_name:
            count_fallback = count_fallback.where(
                ObjectInstance.object_type_api_name == object_type_api_name
            )

        # Apply bitemporal filtering if valid_at is specified
        if valid_at is not None:
            count_fallback = self._apply_valid_time_filter(count_fallback, valid_at)

        return self.session.exec(count_fallback).one()

    def get_object_instance_history(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        transaction_from: datetime | None = None,
        transaction_to: datetime | None = None,
    ) -> list[ObjectInstance]:
        """Get the complete history of an object instance with temporal filtering."""
        stmt = (
            select(ObjectInstance)
            .join(Resource, Resource.rid == ObjectInstance.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ObjectInstance.object_type_api_name == object_type_api_name,
                ObjectInstance.pk_value == pk_value,
            )
        )

        # Apply temporal range filtering
        if valid_from is not None:
            from typing import Any
            from typing import cast as _cast

            vf = _cast(Any, ObjectInstance.valid_from)
            stmt = stmt.where(vf >= valid_from)
        if valid_to is not None:
            from typing import Any
            from typing import cast as _cast

            vt = _cast(Any, ObjectInstance.valid_to)
            stmt = stmt.where(or_(vt <= valid_to, vt.is_(None)))
        if transaction_from is not None:
            from typing import Any
            from typing import cast as _cast

            tf = _cast(Any, ObjectInstance.transaction_from)
            stmt = stmt.where(tf >= transaction_from)
        if transaction_to is not None:
            from typing import Any
            from typing import cast as _cast

            tt = _cast(Any, ObjectInstance.transaction_to)
            stmt = stmt.where(or_(tt <= transaction_to, tt.is_(None)))

        # Order by valid time then transaction time for consistent history view
        stmt = stmt.order_by(
            ObjectInstance.valid_from.desc(), ObjectInstance.transaction_from.desc()
        )

        return list(self.session.exec(stmt).all())

    def _apply_valid_time_filter(self, stmt, valid_at: datetime):
        """Apply valid time filter for point-in-time queries."""
        vf = cast(Any, ObjectInstance.valid_from)
        vt = cast(Any, ObjectInstance.valid_to)
        return stmt.where(
            and_(
                vf <= valid_at,
                or_(vt > valid_at, vt.is_(None)),
            )
        )


__all__ = ["SQLObjectInstanceRepository"]
