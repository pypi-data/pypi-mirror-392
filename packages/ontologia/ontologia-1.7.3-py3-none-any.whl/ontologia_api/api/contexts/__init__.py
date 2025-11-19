"""Bounded context registry for the Ontologia API."""

from __future__ import annotations

from typing import List

from ontologia_api.api.context import BoundedContext
from ontologia_api.api.contexts.ontology import build_contexts as build_ontology_contexts
from ontologia_api.api.contexts.system import build_contexts as build_system_contexts


def get_default_contexts() -> list[BoundedContext]:
    """Return the bounded contexts that make up the public API surface."""

    contexts: list[BoundedContext] = []
    contexts.extend(build_ontology_contexts())
    contexts.extend(build_system_contexts())
    return contexts


__all__ = ["get_default_contexts"]
