"""Bounded context catalogue for the version 2 API surface."""

from __future__ import annotations

from ontologia_api.core.ddd import BoundedContext
from ontologia_api.v2.routers import (
    action_types,
    actions,
    analytics,
    auth,
    change_sets,
    datasets,
    interfaces,
    link_types,
    linked_objects,
    migrations,
    object_types,
    objects,
    query_types,
    realtime,
)

ONTOLOGY_MODELING_CONTEXT = BoundedContext(
    name="ontology_modeling",
    summary="Ontology schema and interface governance.",
    description=(
        "Operations that evolve the ontology metamodel, including object"
        " types, link types, query types, and interface contracts."
    ),
    mount_path="/v2/ontologies/{ontologyApiName}",
    routers=(
        object_types.router,
        link_types.router,
        query_types.router,
        interfaces.router,
    ),
    order=10,
)

ONTOLOGY_RUNTIME_CONTEXT = BoundedContext(
    name="ontology_runtime",
    summary="Operational endpoints for interacting with ontology instances.",
    description=(
        "Action discovery/execution, CRUD over objects and linked objects,"
        " and realtime subscriptions for runtime experiences."
    ),
    mount_path="/v2/ontologies/{ontologyApiName}",
    routers=(
        actions.router,
        action_types.router,
        objects.router,
        linked_objects.router,
        realtime.router,
    ),
    order=20,
)

ONTOLOGY_ANALYTICS_CONTEXT = BoundedContext(
    name="ontology_analytics",
    summary="Analytics and data products derived from the ontology graph.",
    mount_path="/v2/ontologies/{ontologyApiName}",
    routers=(analytics.router, datasets.router),
    order=30,
)

ONTOLOGY_CHANGE_MANAGEMENT_CONTEXT = BoundedContext(
    name="ontology_change_management",
    summary="Change sets, migrations, and lifecycle orchestration.",
    mount_path="/v2/ontologies/{ontologyApiName}",
    routers=(change_sets.router, migrations.router),
    order=40,
)

IDENTITY_AND_ACCESS_CONTEXT = BoundedContext(
    name="identity_and_access",
    summary="Authentication and token issuance for Ontologia clients.",
    mount_path="/v2/auth",
    routers=(auth.router,),
    order=5,
)

BOUNDED_CONTEXTS: tuple[BoundedContext, ...] = (
    IDENTITY_AND_ACCESS_CONTEXT,
    ONTOLOGY_MODELING_CONTEXT,
    ONTOLOGY_RUNTIME_CONTEXT,
    ONTOLOGY_ANALYTICS_CONTEXT,
    ONTOLOGY_CHANGE_MANAGEMENT_CONTEXT,
)

__all__ = ["BOUNDED_CONTEXTS"]
