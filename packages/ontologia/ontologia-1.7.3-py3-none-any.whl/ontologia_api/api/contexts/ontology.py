"""DDD bounded contexts for ontology-centric capabilities."""

from __future__ import annotations

from fastapi import APIRouter
from ontologia_api.api.context import BoundedContext
from ontologia_api.v2.routers import (
    action_types,
    actions,
    analytics,
    change_sets,
    datasets,
    edge,
    interfaces,
    link_types,
    linked_objects,
    migrations,
    object_types,
    objects,
    query_types,
    realtime,
)


def build_contexts() -> list[BoundedContext]:
    """Assemble ontology-facing bounded contexts built on top of the core routers."""

    metamodel_router = APIRouter(
        prefix="/v3/ontologies/{ontologyApiName}/metamodel",
        tags=["Metamodel"],
    )
    metamodel_router.include_router(object_types.router, tags=["Metamodel"])
    metamodel_router.include_router(link_types.router, tags=["Metamodel"])
    metamodel_router.include_router(interfaces.router, tags=["Metamodel"])
    metamodel_router.include_router(query_types.router, tags=["Metamodel"])
    metamodel_router.include_router(action_types.router, tags=["Metamodel"])

    runtime_router = APIRouter(
        prefix="/v3/ontologies/{ontologyApiName}/runtime",
        tags=["Runtime"],
    )
    runtime_router.include_router(objects.router, tags=["Runtime"])
    runtime_router.include_router(linked_objects.router, tags=["Runtime"])
    runtime_router.include_router(actions.router, tags=["Runtime"])
    runtime_router.include_router(analytics.router, tags=["Runtime"])

    governance_router = APIRouter(
        prefix="/v3/ontologies/{ontologyApiName}/governance",
        tags=["Governance"],
    )
    governance_router.include_router(datasets.router, tags=["Governance"])
    governance_router.include_router(change_sets.router, tags=["Governance"])
    governance_router.include_router(migrations.router, tags=["Governance"])

    streams_router = APIRouter(
        prefix="/v3/ontologies/{ontologyApiName}/streams",
        tags=["Streams"],
    )
    streams_router.include_router(realtime.router, tags=["Streams"])
    streams_router.include_router(edge.router, tags=["Streams"])  # Edge ingestion endpoints

    return [
        BoundedContext(
            name="Ontology Metamodel",
            router=metamodel_router,
            summary="Schema authoring, type registries, and ontology interfaces.",
        ),
        BoundedContext(
            name="Ontology Runtime",
            router=runtime_router,
            summary="Operational graph runtime handling instances, queries, and actions.",
        ),
        BoundedContext(
            name="Ontology Governance",
            router=governance_router,
            summary="Lifecycle management for datasets, change sets, and migrations.",
        ),
        BoundedContext(
            name="Ontology Streams",
            router=streams_router,
            summary="Hybrid real-time projections and websocket streaming APIs.",
        ),
    ]


__all__ = ["build_contexts"]
