"""
services/instances_service.py
------------------------------
Camada de serviço para lógica de negócio das instâncias (Objects).
"""

import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import asc, desc, func
from sqlmodel import select

from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.instances.events import ObjectInstanceDeleted, ObjectInstanceUpserted
from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodels.aggregates.object_type import ObjectTypeAggregate
from ontologia.domain.metamodels.instances.dtos import ObjectInstanceDTO
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.repositories import MetamodelRepository
from ontologia.validators import (
    validate_non_empty_string,
    validate_properties,
    validate_service_instance,
)

# Note: concrete SQL repositories are injected elsewhere; avoid unused imports here

logger = logging.getLogger(__name__)

_UNSET = object()


# Simplified DTOs for core
class ObjectUpsertRequest(BaseModel):
    pk_value: str
    properties: dict[str, Any]


class ObjectReadResponse(BaseModel):
    pk_value: str
    properties: dict[str, Any]
    object_type_api_name: str
    created_at: datetime
    updated_at: datetime


class ObjectListResponse(BaseModel):
    objects: list[ObjectReadResponse]
    total: int


class SearchFilter(BaseModel):
    field: str
    operator: str  # eq, ne, lt, le, gt, ge, like, ilike, in
    value: Any


class SearchOrder(BaseModel):
    field: str
    direction: str  # asc, desc


class ObjectSearchRequest(BaseModel):
    filters: list[SearchFilter] = []
    order_by: list[SearchOrder] = []
    limit: int | None = None
    offset: int | None = None


class ObjectSearchResponse(BaseModel):
    objects: list[ObjectReadResponse]
    total: int


class InstancesService:
    """Service for managing object instances."""

    def __init__(
        self,
        instances_repository: ObjectInstanceRepository,
        metamodel_repository: MetamodelRepository,
        event_bus: DomainEventBus | None = None,
    ):
        """Initialize InstancesService with proper dependency injection.

        Args:
            instances_repository: Repository for object instances
            metamodel_repository: Repository for metamodel data
            event_bus: Event bus for publishing domain events

        Raises:
            ValueError: If required repositories are not provided
        """
        if instances_repository is None:
            raise ValueError("instances_repository is required")
        if metamodel_repository is None:
            raise ValueError("metamodel_repository is required")

        self.instances_repository = instances_repository
        self.metamodel_repository = metamodel_repository
        self.event_bus = event_bus or NullEventBus()

    def upsert_object(
        self, service: str, instance: str, object_type_api_name: str, request: ObjectUpsertRequest
    ) -> ObjectReadResponse:
        logger.debug("Domain upsert_object called with service=%s instance=%s", service, instance)
        """Upsert an object instance."""
        start_time = perf_counter()

        # Validate inputs using centralized validators
        try:
            service, instance = validate_service_instance(service, instance)
            object_type_api_name = validate_non_empty_string(
                object_type_api_name, "Object type API name"
            )
            pk_value = validate_non_empty_string(request.pk_value, "PK value")
            properties = validate_properties(request.properties)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
            ) from e

        logger.info(
            "Starting object upsert: service=%s, instance=%s, object_type=%s, pk=%s",
            service,
            instance,
            object_type_api_name,
            pk_value,
        )

        try:
            # Get object type
            object_type = self.metamodel_repository.get_object_type_by_api_name(
                service, instance, object_type_api_name
            )
            if not object_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ObjectType '{object_type_api_name}' not found",
                )

            # Create aggregate and normalize properties
            aggregate = ObjectTypeAggregate.from_model(object_type)
            normalized_properties = aggregate.normalize_instance_properties(pk_value, properties)
            has_valid_from = "valid_from" in normalized_properties
            has_valid_to = "valid_to" in normalized_properties
            valid_from_parsed = (
                self._parse_valid_timestamp(normalized_properties["valid_from"])
                if has_valid_from
                else _UNSET
            )
            valid_to_parsed = (
                self._parse_valid_timestamp(normalized_properties["valid_to"])
                if has_valid_to
                else _UNSET
            )

            existing = self.instances_repository.get_object_instance(object_type.rid, pk_value)
            logger.debug("Existing object found: %s", existing is not None)
            print(
                f"DEBUG upsert_object: looking for existing with object_type.rid={object_type.rid}, pk_value={pk_value}"
            )
            print(f"DEBUG upsert_object: existing={existing}")

            if existing:
                # Bitemporal logic: create new version instead of updating existing
                # Close the existing version's valid_to if it's still open
                if existing.valid_to is None:
                    existing.valid_to = datetime.now(UTC)
                    existing.updated_at = datetime.now(UTC)
                    self.instances_repository.save_object_instance(existing)

                # Create new version with updated properties
                valid_from_value = (
                    valid_from_parsed
                    if has_valid_from and valid_from_parsed is not _UNSET
                    else datetime.now(UTC)
                )
                valid_to_value = (
                    valid_to_parsed if has_valid_to and valid_to_parsed is not _UNSET else None
                )

                saved = self.instances_repository.save_object_instance(
                    ObjectInstance(
                        rid=None,  # New version gets new RID
                        service=service,
                        instance=instance,
                        api_name=f"{object_type_api_name}:{pk_value}",
                        display_name=f"{object_type.display_name} {pk_value}",
                        object_type_api_name=object_type.api_name,
                        object_type_rid=object_type.rid,
                        pk_value=pk_value,
                        data=normalized_properties,
                        valid_from=valid_from_value,
                        valid_to=valid_to_value,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                )
                logger.debug(
                    "Created ObjectInstance version (update) rid=%s pk=%s",
                    saved.object_type_rid,
                    saved.pk_value,
                )
                logger.info(
                    "Created new version of object: object_type=%s, pk=%s, duration=%.3fs",
                    object_type_api_name,
                    pk_value,
                    perf_counter() - start_time,
                )
            else:
                valid_from_value = (
                    valid_from_parsed
                    if has_valid_from and valid_from_parsed is not _UNSET
                    else datetime.now(UTC)
                )
                valid_to_value = (
                    valid_to_parsed if has_valid_to and valid_to_parsed is not _UNSET else None
                )
                print(
                    f"DEBUG upsert_object: creating new ObjectInstance with service={service}, instance={instance}"
                )
                # Avoid inserting into Resource table here to prevent write locks
                # during nested OGM transactions (especially on SQLite). Generate
                # a valid RID deterministically and rely on repository fallbacks
                # that don't require Resource joins when reading.
                try:
                    import uuid as _uuid

                    new_rid = f"ri.{service}.{instance}.{ObjectInstance.__resource_type__}.{_uuid.uuid4()}"
                except Exception:
                    new_rid = None
                saved = self.instances_repository.save_object_instance(
                    ObjectInstance(
                        rid=new_rid,
                        service=service,
                        instance=instance,
                        api_name=f"{object_type_api_name}:{pk_value}",
                        display_name=f"{object_type.display_name} {pk_value}",
                        object_type_api_name=object_type.api_name,
                        object_type_rid=object_type.rid,
                        pk_value=pk_value,
                        data=normalized_properties,
                        valid_from=valid_from_value,
                        valid_to=valid_to_value,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                )
                logger.debug(
                    "Created ObjectInstance (insert) rid=%s pk=%s",
                    saved.object_type_rid,
                    saved.pk_value,
                )
                # Check session state after save
                logger.debug(
                    "Session state after save: new=%d dirty=%d",
                    len(self.instances_repository._sql_repo.session.new),
                    len(self.instances_repository._sql_repo.session.dirty),
                )
                logger.info(
                    "Created object: object_type=%s, pk=%s, duration=%.3fs",
                    object_type_api_name,
                    pk_value,
                    perf_counter() - start_time,
                )

            # Publish event
            event = ObjectInstanceUpserted(
                service=service,
                instance=instance,
                object_type_api_name=object_type.api_name,
                primary_key_field=object_type.primary_key_field,
                primary_key_value=pk_value,
                payload=properties,
            )
            self.event_bus.publish(event)
            # Commit the session to persist the object only when not inside a caller-managed
            # transaction. This lets higher-level transaction contexts (e.g., OGM
            # ObjectModel.transaction()) control atomicity and rollbacks.
            try:
                sess = self.instances_repository._sql_repo.session
                if not getattr(sess, "in_transaction", lambda: False)():
                    sess.commit()
            except Exception:
                # If introspection fails, fall back to committing to preserve previous behavior
                self.instances_repository._sql_repo.session.commit()

            return ObjectReadResponse(
                pk_value=saved.pk_value,
                properties=dict(saved.data or {}),
                object_type_api_name=object_type_api_name,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            )
        except Exception:
            logger.error(
                "Failed to upsert object: service=%s, instance=%s, object_type=%s, pk=%s",
                service,
                instance,
                object_type_api_name,
                pk_value,
                exc_info=True,
            )
            raise

    def get_object(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        *,
        valid_at: datetime | None = None,
    ) -> ObjectReadResponse:
        """Get an object instance with bitemporal support."""

        # Get object type
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )

        # Prefer RID-based resolution to avoid service/instance mismatches and
        # allow repository adapters to derive correct scope from the metamodel.
        obj = self.instances_repository.get_object_instance(
            object_type.rid, pk_value, valid_at=valid_at
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object '{object_type_api_name}:{pk_value}' not found",
            )

        return ObjectReadResponse(
            pk_value=obj.pk_value,
            properties=dict(obj.data or {}),
            object_type_api_name=object_type_api_name,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    def get_object_dto(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
        *,
        valid_at: datetime | None = None,
    ) -> ObjectInstanceDTO:
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )

        obj = self.instances_repository.get_object_instance(
            object_type.rid, pk_value, valid_at=valid_at
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object '{object_type_api_name}:{pk_value}' not found",
            )

        return ObjectInstanceDTO.from_model(obj)

    def list_objects(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> ObjectListResponse:
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )
        items, total = self.instances_repository.list_object_instances(
            object_type.rid, limit=limit, offset=offset, valid_at=valid_at
        )
        objs = [
            ObjectReadResponse(
                pk_value=i.pk_value,
                properties=dict(i.data or {}),
                object_type_api_name=object_type_api_name,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in items
        ]
        return ObjectListResponse(objects=objs, total=total)

    def delete_object(
        self, service: str, instance: str, object_type_api_name: str, pk_value: str
    ) -> bool:
        start = perf_counter()
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )
        deleted = self.instances_repository.delete_object_instance(
            f"{service}:{instance}:{object_type_api_name}", pk_value
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object '{object_type_api_name}:{pk_value}' not found",
            )
        self.event_bus.publish(
            ObjectInstanceDeleted(
                service=service,
                instance=instance,
                object_type_api_name=object_type.api_name,
                primary_key_field=object_type.primary_key_field,
                primary_key_value=pk_value,
            )
        )
        logger.info(f"Deleted '{object_type_api_name}:{pk_value}' in {perf_counter()-start:.3f}s")
        return True

    def _parse_valid_timestamp(self, value: Any) -> datetime | None | object:
        if value is None:
            return None
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
            except ValueError:
                return _UNSET
        else:
            return _UNSET

        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    def count_objects(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
    ) -> int:
        """Count object instances."""
        # Get object type
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )

        # Count objects
        return self.instances_repository.count_object_instances(object_type.rid)

    def search_objects(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        request: ObjectSearchRequest,
    ) -> ObjectSearchResponse:
        """Search object instances with filters and ordering."""
        start_time = perf_counter()
        # Validate object type
        object_type = self.metamodel_repository.get_object_type_by_api_name(
            service, instance, object_type_api_name
        )
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )
        # Build base query
        stmt = select(ObjectInstance).where(ObjectInstance.object_type_rid == object_type.rid)
        # Apply filters
        for f in request.filters:
            col = (
                ObjectInstance.data[f.field].as_string()
                if f.field != "pk_value"
                else ObjectInstance.pk_value
            )
            op = f.operator.lower()
            if op == "eq":
                stmt = stmt.where(col == f.value)
            elif op == "ne":
                stmt = stmt.where(col != f.value)
            elif op == "lt":
                stmt = stmt.where(col < f.value)
            elif op == "le":
                stmt = stmt.where(col <= f.value)
            elif op == "gt":
                stmt = stmt.where(col > f.value)
            elif op == "ge":
                stmt = stmt.where(col >= f.value)
            elif op == "like":
                stmt = stmt.where(col.like(f.value))
            elif op == "ilike":
                stmt = stmt.where(col.ilike(f.value))
            elif op == "is_not":
                stmt = stmt.where(col != f.value)
            elif op == "is_not_null":
                stmt = stmt.where(col.isnot(None))
            elif op == "is_null":
                stmt = stmt.where(col.is_(None))
            else:
                raise ValueError(f"Unsupported filter operator: {op}")

        # Apply ordering
        for o in request.order_by:
            col = (
                ObjectInstance.data[o.field].as_string()
                if o.field != "pk_value"
                else ObjectInstance.pk_value
            )
            if o.direction.lower() == "desc":
                stmt = stmt.order_by(desc(col))
            else:
                stmt = stmt.order_by(asc(col))
        # Apply limit/offset
        if request.limit is not None:
            stmt = stmt.limit(request.limit)
        if request.offset is not None:
            stmt = stmt.offset(request.offset)
        # Execute
        # Use the repository's session for query execution
        session = self.instances_repository._sql_repo.session
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = session.exec(total_stmt).one()
        items = session.exec(stmt).all()
        objs = [
            ObjectReadResponse(
                pk_value=i.pk_value,
                properties=i.data,  # For now, data and properties are the same
                object_type_api_name=object_type.api_name,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in items
        ]
        logger.info(
            f"Searched {object_type_api_name} in {perf_counter()-start_time:.3f}s: total={total}, returned={len(objs)}"
        )
        return ObjectSearchResponse(objects=objs, total=total)


class ObjectInstanceCommandService:
    """
    Service for object instance command operations (create, update, delete).

    Handles write operations for object instances with proper validation,
    event publishing, and transaction management.
    """

    def __init__(
        self,
        instances_repository: ObjectInstanceRepository,
        metamodel_repository: MetamodelRepository,
        event_bus: DomainEventBus | None = None,
    ):
        """
        Initialize command service.

        Args:
            instances_repository: Repository for object instances
            metamodel_repository: Repository for metamodel data
            event_bus: Event bus for publishing domain events
        """
        self.instances_repository = instances_repository
        self.metamodel_repository = metamodel_repository
        self.event_bus = event_bus or NullEventBus()
        self.logger = logging.getLogger(__name__)

    async def create_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        properties: dict[str, Any],
        service: str,
        instance: str,
    ) -> ObjectReadResponse:
        """Create a new object instance."""
        # Implementation would go here
        raise NotImplementedError("Command service implementation pending")

    async def update_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        properties: dict[str, Any],
        service: str,
        instance: str,
    ) -> ObjectReadResponse:
        """Update an existing object instance."""
        # Implementation would go here
        raise NotImplementedError("Command service implementation pending")

    # Note: Async variants and a separate query service facade live in API layer
    # (packages/ontologia_api/services/instances_service.py). The application
    # layer exposes synchronous methods above to keep the domain simpler.
