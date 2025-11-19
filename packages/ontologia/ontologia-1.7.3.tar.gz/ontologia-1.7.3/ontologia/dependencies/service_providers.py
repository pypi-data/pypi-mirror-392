"""Service provider functions for dependency injection."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from ontologia.application.instances_service import InstancesService
from ontologia.application.linked_objects_service import LinkedObjectsService
from ontologia.application.metamodel_service import MetamodelService
from ontologia.application.sync_service import OntologySyncService
from ontologia.dependencies.factories import (
    create_instances_service,
    create_linked_object_repository,
    create_metamodel_repository,
    create_metamodel_service,
    create_object_instance_repository,
)
from ontologia.domain.events import DomainEventBus
from ontologia.domain.instances.repositories import LinkedObjectRepository, ObjectInstanceRepository
from ontologia.domain.metamodels.repositories import MetamodelRepository
from ontologia.event_bus import get_event_bus

# Import get_session from existing dependencies
try:
    from ontologia.infrastructure.database import get_session
except ImportError:
    # Fallback for environments where the import might differ
    def get_session() -> Session:
        """Fallback session provider - should be overridden by actual implementation."""
        raise NotImplementedError("Session provider not properly configured")


def get_metamodel_repository(
    session: Annotated[Session, Depends(get_session)],
) -> MetamodelRepository:
    """Provide metamodel repository with session injection."""
    return create_metamodel_repository(session)


def get_instances_repository(
    session: Annotated[Session, Depends(get_session)],
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
) -> ObjectInstanceRepository:
    """Provide instances repository with session and metamodel repository injection."""
    return create_object_instance_repository(session, metamodel_repository)


def get_linked_objects_repository(
    session: Annotated[Session, Depends(get_session)],
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
) -> LinkedObjectRepository:
    """Provide linked objects repository with session and metamodel repository injection."""
    return create_linked_object_repository(session, metamodel_repository)


def get_metamodel_service(
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
) -> MetamodelService:
    """Provide metamodel service with repository injection."""
    return create_metamodel_service(metamodel_repository)


def get_event_bus_production() -> DomainEventBus:
    """Provide EventBus with production configuration."""
    from ontologia.event_bus import get_event_bus as event_bus_factory

    return event_bus_factory()


def get_instances_service(
    instances_repository: Annotated[ObjectInstanceRepository, Depends(get_instances_repository)],
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
    event_bus: Annotated[DomainEventBus, Depends(get_event_bus)],
) -> InstancesService:
    """Provide instances service with repository and event bus injection."""
    return create_instances_service(instances_repository, metamodel_repository, event_bus)


def get_linked_objects_service(
    linked_objects_repository: Annotated[
        LinkedObjectRepository, Depends(get_linked_objects_repository)
    ],
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
    event_bus: Annotated[DomainEventBus, Depends(get_event_bus)],
) -> LinkedObjectsService:
    """Provide linked objects service with repository and event bus injection."""
    return LinkedObjectsService(linked_objects_repository, metamodel_repository, event_bus)


def get_sync_service(
    metamodel_repository: Annotated[MetamodelRepository, Depends(get_metamodel_repository)],
    # Note: Kuzu and DuckDB connections would need to be provided separately
    # as they are not standard database sessions
) -> OntologySyncService:
    """Provide sync service with metamodel repository injection.

    Note: Kuzu and DuckDB connections need to be provided separately
    as they are not standard SQLModel sessions.
    """
    return OntologySyncService(metamodel_repository)
