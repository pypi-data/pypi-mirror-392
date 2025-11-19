"""Dependency injection providers for Ontologia services."""

from ontologia.dependencies.service_providers import (
    get_event_bus,
    get_instances_service,
    get_linked_objects_service,
    get_metamodel_service,
)

__all__ = [
    "get_instances_service",
    "get_metamodel_service",
    "get_linked_objects_service",
    "get_event_bus",
]
