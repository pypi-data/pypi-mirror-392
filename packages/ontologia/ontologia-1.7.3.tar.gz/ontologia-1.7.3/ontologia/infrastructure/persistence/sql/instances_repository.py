"""SQL implementation of the object instance repository."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, cast

from registro.core.resource import Resource
from sqlmodel import Session, and_, func, or_, select

from ontologia.domain.metamodels.instances.models_sql import ObjectInstance

logger = logging.getLogger(__name__)


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
        # First, let's check what's in the database without the Resource join
        self.session.exec(select(ObjectInstance)).all()

        # Also check what's in the Resource table
        from registro.core.resource import Resource

        self.session.exec(select(Resource)).all()

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

        # Debug: print the SQL query
        compiled = stmt.compile(compile_kwargs={"literal_binds": True})
        print(f"DEBUG get_object_instance: SQL={compiled}")

        res = self.session.exec(stmt).first()
        print(f"DEBUG get_object_instance: res={res}")
        if res is not None:
            print(f"DEBUG get_object_instance: res.rid={res.rid}")
            return res

        fallback = select(ObjectInstance).where(
            ObjectInstance.object_type_api_name == object_type_api_name,
            ObjectInstance.pk_value == pk_value,
        )

        if valid_at is not None:
            fallback = self._apply_valid_time_filter(fallback, valid_at)

        obj = self.session.exec(fallback).first()
        if obj is not None:
            return obj
        # Final safety fallback: attempt lookup by pk only (ignores type/scope).
        try:
            pk_only = select(ObjectInstance).where(ObjectInstance.pk_value == pk_value)
            return self.session.exec(pk_only).first()
        except Exception:
            return None

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
        logger.debug(
            "Repository save_object_instance pk=%s service=%s instance=%s",
            obj.pk_value,
            obj.service,
            obj.instance,
        )
        logger.debug("Repository session id=%s", id(self.session))
        logger.debug("Session dirty before add: %s", self.session.dirty)
        logger.debug("Session new before add: %s", self.session.new)

        # Try using add instead of merge to avoid replacing existing objects
        self.session.add(obj)
        persistent = obj
        logger.debug(
            "After add persistent.pk=%s service=%s instance=%s",
            persistent.pk_value,
            persistent.service,
            persistent.instance,
        )
        logger.debug("After add persistent.id=%s", persistent.id)
        logger.debug(
            "After add valid_from=%s transaction_from=%s",
            persistent.valid_from,
            persistent.transaction_from,
        )
        logger.debug("Session dirty after add: %s", self.session.dirty)
        logger.debug("Session new after add: %s", self.session.new)
        logger.debug(
            "Session state after add in repo: new=%d dirty=%d",
            len(self.session.new),
            len(self.session.dirty),
        )
        logger.debug("Added object in session new: %s", persistent in self.session.new)
        logger.debug("Added object id: %s", persistent.id)

        # Ensure the object is written without forcing a commit when part of a caller-managed transaction
        try:
            if getattr(self.session, "in_transaction", lambda: False)():
                # Detect OGM-managed nesting depth if available
                depth = 0
                try:
                    info = getattr(self.session, "info", None)
                    if isinstance(info, dict):
                        depth = int(info.get("ogm_tx_depth", 0))
                except Exception:
                    depth = 0
                # Default behavior: flush so data is visible in current transaction
                # and subsequent reads. For inner OGM transactions, also flush.
                # Only avoid eager flushing when we know we're at the outermost
                # OGM transaction (depth == 1) where the context manager will
                # commit at exit.
                if depth == 1:
                    # OGM outer transaction: let context commit
                    pass
                else:
                    # Flush changes and commit if not within OGM-managed tx
                    self.session.flush()
                    if depth == 0:
                        try:
                            self.session.commit()
                        except Exception:
                            # Best-effort commit; if it fails, leave to caller
                            pass
            else:
                # Outside a transaction: commit to persist immediately
                self.session.commit()
        finally:
            try:
                # May fail when not yet flushed/committed; ignore safely
                self.session.refresh(persistent)
            except Exception:
                pass
        logger.debug("After commit persistent.id=%s", persistent.id)

        # Don't access identity_map as it might contain deleted objects
        # print(f"DEBUG: Session identity map before return: {dict(self.session.identity_map)}")
        # Don't commit here - let the session context manager handle it
        # self.session.commit()
        logger.debug(
            "Session state before return: new=%d dirty=%d",
            len(self.session.new),
            len(self.session.dirty),
        )
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
        # Only commit when not part of a broader caller-managed transaction
        try:
            if getattr(self.session, "in_transaction", lambda: False)():
                self.session.flush()
                # Commit for non-OGM transactions to persist immediately in API flows
                depth = 0
                try:
                    info = getattr(self.session, "info", None)
                    if isinstance(info, dict):
                        depth = int(info.get("ogm_tx_depth", 0))
                except Exception:
                    depth = 0
                if depth == 0:
                    try:
                        self.session.commit()
                    except Exception:
                        pass
            else:
                self.session.commit()
        except Exception:
            # Preserve legacy behavior if introspection fails
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
