"""Factory functions for creating core services with proper dependency injection."""

from __future__ import annotations

import logging
from typing import Any

from ontologia.application.instances_service import InstancesService
from ontologia.application.metamodel_service import MetamodelService
from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.instances.repositories import LinkedObjectRepository, ObjectInstanceRepository
from ontologia.domain.metamodels.repositories import MetamodelRepository
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.linked_object_adapter import (
    LinkedObjectRepositoryAdapter,
)
from ontologia.infrastructure.persistence.sql.linked_objects_repository import (
    SQLLinkedObjectRepository,
)
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)
from ontologia.infrastructure.persistence.sql.object_instance_adapter import (
    ObjectInstanceRepositoryAdapter,
)

logger = logging.getLogger(__name__)


def create_metamodel_repository(session: Any) -> MetamodelRepository:
    """Create a metamodel repository with SQL implementation.
    
    Args:
        session: SQLModel/SQLAlchemy session
        
    Returns:
        MetamodelRepository implementation
    """
    # Cast to Protocol since SQLMetamodelRepository structurally satisfies it
    return SQLMetamodelRepository(session)  # type: ignore[return-value]


def create_object_instance_repository(
    session: Any, 
    metamodel_repository: MetamodelRepository
) -> ObjectInstanceRepository:
    """Create an object instance repository with SQL implementation.
    
    Args:
        session: SQLModel/SQLAlchemy session
        metamodel_repository: Repository for metamodel data
        
    Returns:
        ObjectInstanceRepository implementation
    """
    sql_repo = SQLObjectInstanceRepository(session)
    return ObjectInstanceRepositoryAdapter(sql_repo, metamodel_repository)  # type: ignore[return-value]


def create_linked_object_repository(
    session: Any,
    metamodel_repository: MetamodelRepository
) -> LinkedObjectRepository:
    """Create a linked object repository with SQL implementation.
    
    Args:
        session: SQLModel/SQLAlchemy session
        metamodel_repository: Repository for metamodel data
        
    Returns:
        LinkedObjectRepository implementation
    """
    sql_repo = SQLLinkedObjectRepository(session)
    return LinkedObjectRepositoryAdapter(sql_repo, metamodel_repository)  # type: ignore[return-value]


def create_metamodel_service(
    metamodel_repository: MetamodelRepository
) -> MetamodelService:
    """Create a metamodel service with repository injection.
    
    Args:
        metamodel_repository: Repository for metamodel operations
        
    Returns:
        MetamodelService instance
    """
    return MetamodelService(metamodel_repository)


def create_instances_service(
    instances_repository: ObjectInstanceRepository,
    metamodel_repository: MetamodelRepository,
    event_bus: DomainEventBus | None = None
) -> InstancesService:
    """Create an instances service with repository and event bus injection.
    
    Args:
        instances_repository: Repository for object instances
        metamodel_repository: Repository for metamodel data
        event_bus: Event bus for domain events (optional)
        
    Returns:
        InstancesService instance
    """
    return InstancesService(
        instances_repository=instances_repository,
        metamodel_repository=metamodel_repository,
        event_bus=event_bus or NullEventBus()
    )


def create_core_services(session: Any) -> dict[str, Any]:
    """Create all core services with proper dependency injection.
    
    This factory function creates a complete set of core services
    with all dependencies properly wired. Useful for testing and
    bootstrapping the application.
    
    Args:
        session: SQLModel/SQLAlchemy session
        
    Returns:
        Dictionary containing all core services
    """
    # Create repositories
    metamodel_repo = create_metamodel_repository(session)
    instances_repo = create_object_instance_repository(session, metamodel_repo)
    linked_objects_repo = create_linked_object_repository(session, metamodel_repo)
    
    # Create services
    metamodel_service = create_metamodel_service(metamodel_repo)
    instances_service = create_instances_service(instances_repo, metamodel_repo)
    
    return {
        "metamodel_repository": metamodel_repo,
        "instances_repository": instances_repo,
        "linked_objects_repository": linked_objects_repo,
        "metamodel_service": metamodel_service,
        "instances_service": instances_service,
    }


__all__ = [
    "create_metamodel_repository",
    "create_object_instance_repository", 
    "create_linked_object_repository",
    "create_metamodel_service",
    "create_instances_service",
    "create_core_services",
]