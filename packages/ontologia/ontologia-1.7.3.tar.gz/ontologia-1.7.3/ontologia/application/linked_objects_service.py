"""
services/linked_objects_service.py
------------------------------
Camada de serviço para lógica de negócio dos linked objects.
"""

import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.instances.events import LinkCreated, LinkDeleted
from ontologia.domain.instances.repositories import LinkedObjectRepository
from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
from ontologia.domain.metamodels.repositories import MetamodelRepository
from ontologia.domain.metamodels.types.link_type import Cardinality

# Note: avoid importing concrete SQL repositories here; service depends on protocols
from ontologia.validators import (
    validate_api_name,
    validate_different_values,
    validate_non_empty_string,
    validate_properties,
    validate_service_instance,
)

logger = logging.getLogger(__name__)


# Simplified DTOs for core
class LinkedObjectUpsertRequest(BaseModel):
    source_pk_value: str
    target_pk_value: str
    properties: dict[str, Any] = Field(default_factory=dict)


class LinkedObjectReadResponse(BaseModel):
    source_pk_value: str
    target_pk_value: str
    properties: dict[str, Any]
    link_type_api_name: str
    source_object_type_api_name: str
    target_object_type_api_name: str
    created_at: datetime
    updated_at: datetime


class LinkedObjectListResponse(BaseModel):
    linked_objects: list[LinkedObjectReadResponse]
    total: int


class LinkedObjectsService:
    """Service for managing linked objects."""

    def __init__(
        self,
        linked_objects_repository: LinkedObjectRepository,
        metamodel_repository: MetamodelRepository,
        event_bus: DomainEventBus | None = None,
    ):
        """Initialize LinkedObjectsService with proper dependency injection.

        Args:
            linked_objects_repository: Repository for linked objects
            metamodel_repository: Repository for metamodel data
            event_bus: Event bus for publishing domain events

        Raises:
            ValueError: If required repositories are not provided
        """
        if linked_objects_repository is None:
            raise ValueError("linked_objects_repository is required")
        if metamodel_repository is None:
            raise ValueError("metamodel_repository is required")

        self.linked_objects_repository = linked_objects_repository
        self.metamodel_repository = metamodel_repository
        self.event_bus = event_bus or NullEventBus()

    def upsert_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        request: LinkedObjectUpsertRequest,
    ) -> LinkedObjectReadResponse:
        """Create or update a linked object."""
        start_time = perf_counter()

        # Validate inputs using centralized validators
        service, instance = validate_service_instance(service, instance)
        link_type_api_name = validate_non_empty_string(link_type_api_name, "Link type API name")
        source_pk = validate_non_empty_string(request.source_pk_value, "Source PK value")
        target_pk = validate_non_empty_string(request.target_pk_value, "Target PK value")
        validate_different_values(source_pk, target_pk, "Source PK value", "Target PK value")
        properties = validate_properties(request.properties)

        logger.info(
            "Starting linked object upsert: service=%s, instance=%s, link_type=%s, source=%s, target=%s",
            service,
            instance,
            link_type_api_name,
            source_pk,
            target_pk,
        )

        try:
            link_type = self.metamodel_repository.get_link_type_by_api_name(
                service, instance, link_type_api_name
            )
            if not link_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LinkType '{link_type_api_name}' not found",
                )

            # Get source and target object types (nomes corretos + repo helper por RID)
            source_ot = (
                self.metamodel_repository.get_object_type_by_rid(link_type.from_object_type_rid)
                if getattr(link_type, "from_object_type_rid", None)
                else None
            )
            if source_ot is None:
                source_ot = self.metamodel_repository.get_object_type_by_api_name(
                    service, instance, link_type.from_object_type_api_name
                )

            target_ot = (
                self.metamodel_repository.get_object_type_by_rid(link_type.to_object_type_rid)
                if getattr(link_type, "to_object_type_rid", None)
                else None
            )
            if target_ot is None:
                target_ot = self.metamodel_repository.get_object_type_by_api_name(
                    service, instance, link_type.to_object_type_api_name
                )

            if not source_ot or not target_ot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Source or target ObjectType not found",
                )

            existing = self.linked_objects_repository.get_linked_object(
                link_type.rid, source_pk, target_pk
            )

            cardinality = getattr(link_type, "cardinality", Cardinality.MANY_TO_MANY)
            try:
                cardinality = Cardinality(cardinality)
            except ValueError:
                cardinality = Cardinality.MANY_TO_MANY

            if existing is None:
                self._enforce_cardinality_constraints(
                    service, instance, link_type, cardinality, source_pk, target_pk
                )

            if existing is not None:
                if cardinality is Cardinality.ONE_TO_ONE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cardinality violation: ONE_TO_ONE link already exists",
                    )

            if existing:
                # Bitemporal logic: create new version instead of updating existing
                # Close the existing version's valid_to if it's still open
                if getattr(existing, "valid_to", None) is None:
                    existing.valid_to = datetime.now(UTC)
                    existing.updated_at = datetime.now(UTC)
                    self.linked_objects_repository.save_linked_object(existing)

                # Create new version with updated properties
                if getattr(existing, "from_object_rid", None) is None:
                    from_object_rid = self._resolve_object_instance_rid(source_ot.rid, source_pk)
                else:
                    from_object_rid = existing.from_object_rid

                if getattr(existing, "to_object_rid", None) is None:
                    to_object_rid = self._resolve_object_instance_rid(target_ot.rid, target_pk)
                else:
                    to_object_rid = existing.to_object_rid

                saved = self.linked_objects_repository.save_linked_object(
                    LinkedObject(
                        rid=None,  # New version gets new RID
                        service=service,
                        instance=instance,
                        api_name=f"{link_type_api_name}:{source_pk}->{target_pk}",
                        display_name=f"{link_type.display_name} {source_pk}→{target_pk}",
                        link_type_api_name=link_type.api_name,
                        link_type_rid=link_type.rid,
                        from_object_rid=from_object_rid,
                        to_object_rid=to_object_rid,
                        source_pk_value=source_pk,
                        target_pk_value=target_pk,
                        data=properties,  # Store properties in the data field
                        valid_from=datetime.now(UTC),  # New version starts now
                        valid_to=None,  # Open-ended validity
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                )
                logger.info(
                    "Created new version of linked object: link_type=%s, source=%s, target=%s, duration=%.3fs",
                    link_type_api_name,
                    source_pk,
                    target_pk,
                    perf_counter() - start_time,
                )
            else:
                source_instance_rid = self._resolve_object_instance_rid(source_ot.rid, source_pk)
                target_instance_rid = self._resolve_object_instance_rid(target_ot.rid, target_pk)
                # Ensure a Resource row exists for the LinkedObject so joins work
                try:
                    res = self.metamodel_repository.create_resource(
                        LinkedObject.__resource_type__,
                        service,
                        instance,
                        f"{link_type.display_name} {source_pk}→{target_pk}",
                    )
                    new_rid = getattr(res, "rid", None)
                except Exception:
                    new_rid = None

                saved = self.linked_objects_repository.save_linked_object(
                    LinkedObject(
                        rid=new_rid,
                        service=service,
                        instance=instance,
                        api_name=f"{link_type_api_name}:{source_pk}->{target_pk}",
                        display_name=f"{link_type.display_name} {source_pk}→{target_pk}",
                        link_type_api_name=link_type.api_name,
                        link_type_rid=link_type.rid,
                        from_object_rid=source_instance_rid,
                        to_object_rid=target_instance_rid,
                        source_pk_value=source_pk,
                        target_pk_value=target_pk,
                        data=properties,  # Store properties in the data field
                        valid_from=datetime.now(UTC),  # New version starts now
                        valid_to=None,  # Open-ended validity
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                )

                # Publish LinkCreated event
                link_event = LinkCreated(
                    service=service,
                    instance=instance,
                    link_type_api_name=link_type_api_name,
                    from_object_type=source_ot.api_name,
                    from_primary_key_field=source_ot.primary_key_field or "pk",
                    from_pk=source_pk,
                    to_object_type=target_ot.api_name,
                    to_primary_key_field=target_ot.primary_key_field or "pk",
                    to_pk=target_pk,
                    properties=properties,
                )
                self.event_bus.publish(link_event)

                logger.info(
                    "Created linked object: link_type=%s, source=%s, target=%s, duration=%.3fs",
                    link_type_api_name,
                    source_pk,
                    target_pk,
                    perf_counter() - start_time,
                )

            return LinkedObjectReadResponse(
                source_pk_value=saved.source_pk_value,
                target_pk_value=saved.target_pk_value,
                properties=saved.properties,
                link_type_api_name=link_type_api_name,
                source_object_type_api_name=source_ot.api_name,
                target_object_type_api_name=target_ot.api_name,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            )
        except Exception:
            logger.error(
                "Failed to upsert linked object: service=%s, instance=%s, link_type=%s, source=%s, target=%s",
                service,
                instance,
                link_type_api_name,
                source_pk,
                target_pk,
                exc_info=True,
            )
            raise

    def _resolve_object_instance_rid(self, object_type_rid: str, pk_value: str) -> str | None:
        session = self._get_sql_session()
        if session is None:
            return None
        stmt = select(ObjectInstance).where(
            ObjectInstance.object_type_rid == object_type_rid,
            ObjectInstance.pk_value == pk_value,
        )
        obj = session.exec(stmt).first()
        return getattr(obj, "rid", None) if obj else None

    def _get_sql_session(self) -> Session | None:
        session = getattr(self.linked_objects_repository, "session", None)
        if session is not None:
            return session
        sql_repo = getattr(self.linked_objects_repository, "_sql_repo", None)
        if sql_repo is not None:
            return getattr(sql_repo, "session", None)
        return None

    def _enforce_cardinality_constraints(
        self,
        service: str,
        instance: str,
        link_type: Any,
        cardinality: Cardinality,
        source_pk: str,
        target_pk: str,
    ) -> None:
        if cardinality is Cardinality.MANY_TO_MANY:
            return

        # Forward constraints: limit outgoing degree from source
        if cardinality in (Cardinality.ONE_TO_ONE, Cardinality.MANY_TO_ONE):
            lt_ident = f"{service}:{instance}:{link_type.api_name}"
            existing_forward = self.linked_objects_repository.traverse_outgoing(
                lt_ident, source_pk, 1
            )
            # Debug: print counts during tests
            try:
                import os

                if os.getenv("TESTING") in {"1", "true", "True"}:
                    try:
                        details = ", ".join(
                            f"{getattr(x, 'link_type_api_name', '?')}:{getattr(x, 'source_pk_value', '?')}->{getattr(x, 'target_pk_value', '?')}"
                            for x in (existing_forward or [])
                        )
                    except Exception:
                        details = "?"
                    print(
                        f"DEBUG cardinality forward check lt={lt_ident} source={source_pk} count={len(existing_forward)} details=[{details}]"
                    )
            except Exception:
                pass
            if existing_forward:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cardinality violation: forward degree exceeded",
                )

        # Inverse constraints: limit incoming degree to target
        if cardinality in (Cardinality.ONE_TO_ONE, Cardinality.ONE_TO_MANY):
            lt_ident = f"{service}:{instance}:{link_type.api_name}"
            existing_inverse = self.linked_objects_repository.traverse_incoming(
                lt_ident, target_pk, 1
            )
            try:
                import os

                if os.getenv("TESTING") in {"1", "true", "True"}:
                    print(
                        f"DEBUG cardinality inverse check lt={lt_ident} target={target_pk} count={len(existing_inverse)}"
                    )
            except Exception:
                pass
            if existing_inverse:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cardinality violation: inverse degree exceeded",
                )

    def get_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> LinkedObjectReadResponse:
        """Get a linked object."""
        # Validate inputs
        service, instance = validate_service_instance(service, instance)
        link_type_api_name = validate_api_name(link_type_api_name, "Link type API name")
        validate_non_empty_string(source_pk_value, "Source PK value")
        validate_non_empty_string(target_pk_value, "Target PK value")

        link_type = self.metamodel_repository.get_link_type_by_api_name(
            service, instance, link_type_api_name
        )
        if not link_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        source_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.from_object_type_rid)
            if getattr(link_type, "from_object_type_rid", None)
            else None
        )
        target_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.to_object_type_rid)
            if getattr(link_type, "to_object_type_rid", None)
            else None
        )

        if not source_ot or not target_ot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target ObjectType not found",
            )

        linked_obj = self.linked_objects_repository.get_linked_object(
            link_type.rid, source_pk_value, target_pk_value
        )
        if not linked_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkedObject '{link_type_api_name}:"
                f"{source_pk_value}->{target_pk_value}' not found",
            )

        return LinkedObjectReadResponse(
            source_pk_value=linked_obj.source_pk_value,
            target_pk_value=linked_obj.target_pk_value,
            properties=linked_obj.properties,
            link_type_api_name=link_type_api_name,
            source_object_type_api_name=source_ot.api_name,
            target_object_type_api_name=target_ot.api_name,
            created_at=linked_obj.created_at,
            updated_at=linked_obj.updated_at,
        )

    def delete_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> None:
        """Delete a linked object."""
        start_time = perf_counter()

        # Validate inputs
        service, instance = validate_service_instance(service, instance)
        link_type_api_name = validate_api_name(link_type_api_name, "Link type API name")
        source_pk = validate_non_empty_string(source_pk_value, "Source PK value")
        target_pk = validate_non_empty_string(target_pk_value, "Target PK value")

        link_type = self.metamodel_repository.get_link_type_by_api_name(
            service, instance, link_type_api_name
        )
        if not link_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        # Idempotent delete: if link is not present, proceed without raising 404

        # Get source and target object types for event
        source_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.from_object_type_rid)
            if getattr(link_type, "from_object_type_rid", None)
            else None
        )
        if source_ot is None:
            source_ot = self.metamodel_repository.get_object_type_by_api_name(
                service, instance, link_type.from_object_type_api_name
            )

        target_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.to_object_type_rid)
            if getattr(link_type, "to_object_type_rid", None)
            else None
        )
        if target_ot is None:
            target_ot = self.metamodel_repository.get_object_type_by_api_name(
                service, instance, link_type.to_object_type_api_name
            )

        # Attempt repository-scoped delete first; fall back to direct SQL by api_name
        deleted_ok = False
        try:
            res = self.linked_objects_repository.delete_linked_object(
                link_type.rid, source_pk, target_pk
            )
            # Some adapters return a boolean; treat truthy as success
            deleted_ok = bool(res)
        except Exception:
            deleted_ok = False

        if not deleted_ok:
            try:
                session = self._get_sql_session()
                if session is not None:
                    from sqlmodel import select as _select

                    obj = session.exec(
                        _select(LinkedObject)
                        .where(LinkedObject.link_type_api_name == link_type.api_name)
                        .where(LinkedObject.source_pk_value == source_pk)
                        .where(LinkedObject.target_pk_value == target_pk)
                    ).first()
                    if obj is not None:
                        session.delete(obj)
                        session.commit()
                        deleted_ok = True
            except Exception:
                # Best-effort fallback
                pass

        # Publish LinkDeleted event
        link_event = LinkDeleted(
            service=service,
            instance=instance,
            link_type_api_name=link_type_api_name,
            from_object_type=source_ot.api_name,
            from_primary_key_field=source_ot.primary_key_field or "pk",
            from_pk=source_pk,
            to_object_type=target_ot.api_name,
            to_primary_key_field=target_ot.primary_key_field or "pk",
            to_pk=target_pk,
        )
        self.event_bus.publish(link_event)

        logger.info(
            "Deleted linked object: link_type=%s, source=%s, target=%s, duration=%.3fs",
            link_type_api_name,
            source_pk,
            target_pk,
            perf_counter() - start_time,
        )

    def list_linked_objects(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> LinkedObjectListResponse:
        """List linked objects."""
        # Validate inputs
        service, instance = validate_service_instance(service, instance)
        link_type_api_name = validate_api_name(link_type_api_name, "Link type API name")
        if limit < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be non-negative"
            )
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Offset must be non-negative"
            )
        if limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit cannot exceed 1000"
            )

        link_type = self.metamodel_repository.get_link_type_by_api_name(
            service, instance, link_type_api_name
        )
        if not link_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        source_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.from_object_type_rid)
            if getattr(link_type, "from_object_type_rid", None)
            else None
        )
        target_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.to_object_type_rid)
            if getattr(link_type, "to_object_type_rid", None)
            else None
        )

        if not source_ot or not target_ot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target ObjectType not found",
            )

        # List linked objects
        linked_objects, total = self.linked_objects_repository.list_linked_objects(
            link_type.rid, limit=limit, offset=offset
        )

        # Fallback for minimal environments where Resource rows may be absent
        # or adapters cannot fully resolve scope. Query directly by api_name.
        if total == 0 or not linked_objects:
            try:
                session = self._get_sql_session()
                if session is not None:
                    stmt = (
                        select(LinkedObject)
                        .where(LinkedObject.link_type_api_name == link_type.api_name)
                        .limit(limit)
                        .offset(offset)
                    )
                    linked_objects = list(session.exec(stmt).all())
                    total = len(linked_objects)
            except Exception:
                pass

        return LinkedObjectListResponse(
            linked_objects=[
                LinkedObjectReadResponse(
                    source_pk_value=obj.source_pk_value,
                    target_pk_value=obj.target_pk_value,
                    properties=obj.properties,
                    link_type_api_name=link_type_api_name,
                    source_object_type_api_name=source_ot.api_name,
                    target_object_type_api_name=target_ot.api_name,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                )
                for obj in linked_objects
            ],
            total=total,
        )

    def traverse_linked_objects(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        link_type_api_name: str,
        *,
        direction: str = "outgoing",
        limit: int = 100,
    ) -> LinkedObjectListResponse:
        """Traverse linked objects from a source object."""
        start_time = perf_counter()

        # Validate inputs
        service, instance = validate_service_instance(service, instance)
        object_type_api_name = validate_api_name(object_type_api_name, "Object type API name")
        pk_value = validate_non_empty_string(pk_value, "PK value")
        link_type_api_name = validate_api_name(link_type_api_name, "Link type API name")
        if direction not in ("outgoing", "incoming"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direction must be 'outgoing' or 'incoming'",
            )
        if limit < 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 0 and 1000"
            )

        # Get object type
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )

        # Get link type
        link_type = self.metamodel_repository.get_link_type_by_api_name(
            service, instance, link_type_api_name
        )
        if not link_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        # Get source and target object types
        source_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.from_object_type_rid)
            if getattr(link_type, "from_object_type_rid", None)
            else None
        )
        target_ot = (
            self.metamodel_repository.get_object_type_by_rid(link_type.to_object_type_rid)
            if getattr(link_type, "to_object_type_rid", None)
            else None
        )

        if not source_ot or not target_ot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target ObjectType not found",
            )

        # Traverse linked objects
        if direction == "outgoing":
            linked_objects = self.linked_objects_repository.traverse_outgoing(
                link_type.rid, pk_value, limit=limit
            )
        elif direction == "incoming":
            linked_objects = self.linked_objects_repository.traverse_incoming(
                link_type.rid, pk_value, limit=limit
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direction must be 'outgoing' or 'incoming'",
            )

        logger.info(
            "Traversed linked objects: object_type=%s, pk=%s, link_type=%s, direction=%s, count=%d, duration=%.3fs",
            object_type_api_name,
            pk_value,
            link_type_api_name,
            direction,
            len(linked_objects),
            perf_counter() - start_time,
        )

        return LinkedObjectListResponse(
            linked_objects=[
                LinkedObjectReadResponse(
                    source_pk_value=obj.source_pk_value,
                    target_pk_value=obj.target_pk_value,
                    properties=obj.properties,
                    link_type_api_name=link_type_api_name,
                    source_object_type_api_name=source_ot.api_name,
                    target_object_type_api_name=target_ot.api_name,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                )
                for obj in linked_objects
            ],
            total=len(linked_objects),
        )


class LinkedObjectsCommandService:
    """
    Service for linked objects command operations (create, update, delete).

    Handles write operations for linked objects with proper validation,
    event publishing, and transaction management.
    """

    def __init__(
        self,
        linked_objects_repository,
        metamodel_repository,
        event_bus=None,
    ):
        """
        Initialize command service.

        Args:
            linked_objects_repository: Repository for linked objects
            metamodel_repository: Repository for metamodel data
            event_bus: Event bus for publishing domain events
        """
        self.linked_objects_repository = linked_objects_repository
        self.metamodel_repository = metamodel_repository
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)

    async def create_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        request,
    ) -> LinkedObjectReadResponse:
        """Create a new linked object."""
        # Implementation would go here
        raise NotImplementedError("Command service implementation pending")

    async def update_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
        properties: dict,
    ) -> LinkedObjectReadResponse:
        """Update an existing linked object."""
        # Implementation would go here
        raise NotImplementedError("Command service implementation pending")

    async def delete_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> bool:
        """Delete a linked object."""
        # Implementation would go here
        raise NotImplementedError("Command service implementation pending")


class LinkedObjectsQueryService:
    """
    Service for linked objects query operations (read, search, traverse).

    Handles read operations for linked objects with optimized querying,
    relationship traversal, and graph analytics support.
    """

    def __init__(
        self,
        linked_objects_repository,
        metamodel_repository,
    ):
        """
        Initialize query service.

        Args:
            linked_objects_repository: Repository for linked objects
            metamodel_repository: Repository for metamodel data
        """
        self.linked_objects_repository = linked_objects_repository
        self.metamodel_repository = metamodel_repository
        self.logger = logging.getLogger(__name__)

    async def get_linked_object(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        source_pk_value: str,
        target_pk_value: str,
    ) -> LinkedObjectReadResponse | None:
        """Get a specific linked object."""
        # Implementation would go here
        raise NotImplementedError("Query service implementation pending")

    async def list_linked_objects(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
        filters: dict | None = None,
    ) -> LinkedObjectListResponse:
        """List linked objects with pagination."""
        # Implementation would go here
        raise NotImplementedError("Query service implementation pending")

    async def traverse_linked_objects(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        link_type_api_name: str,
        direction: str = "outgoing",
        *,
        limit: int = 100,
        depth: int = 1,
    ) -> LinkedObjectListResponse:
        """Traverse linked objects in specified direction."""
        # Implementation would go here
        raise NotImplementedError("Query service implementation pending")
