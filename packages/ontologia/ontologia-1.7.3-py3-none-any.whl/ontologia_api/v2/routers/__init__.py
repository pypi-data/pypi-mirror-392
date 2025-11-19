"""FastAPI routers for API v2."""

from ontologia_api.v2.routers import (
    action_types,
    actions,
    datasets,
    edge,
    interfaces,
    link_types,
    linked_objects,
    object_types,
    objects,
    query_types,
    realtime,
)

__all__ = [
    "object_types",
    "link_types",
    "objects",
    "linked_objects",
    "interfaces",
    "actions",
    "action_types",
    "datasets",
    "edge",
    "realtime",
    "query_types",
]
