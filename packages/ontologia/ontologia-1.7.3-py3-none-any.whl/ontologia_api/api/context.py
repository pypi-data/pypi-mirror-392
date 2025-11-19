"""DDD-aware API composition primitives."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from fastapi import APIRouter, FastAPI


@dataclass(slots=True)
class BoundedContext:
    """Container that groups routers belonging to the same bounded context."""

    name: str
    router: APIRouter
    summary: str


def mount_contexts(app: FastAPI, contexts: Iterable[BoundedContext]) -> None:
    """Include the routers for every bounded context on the FastAPI app."""

    for context in contexts:
        app.include_router(context.router)


__all__ = ["BoundedContext", "mount_contexts"]
