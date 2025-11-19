"""Domain-driven API composition primitives.

This module introduces explicit bounded-context registration for the public API.
It allows the FastAPI application to be assembled in a declarative, DDD-friendly
fashion where presentation routers are grouped by domain boundaries and wired
consistently during startup.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import dataclass, field

from fastapi import APIRouter, FastAPI

LifecycleHook = Callable[[FastAPI], Awaitable[None] | None]


@dataclass(frozen=True)
class BoundedContext:
    """Metadata describing a bounded context exposed through the API layer.

    Attributes:
        name: Human-friendly identifier used for diagnostics and documentation.
        mount_path: Absolute URL prefix where the routers should be exposed.
        routers: Collection of routers belonging to this bounded context.
        summary: Short description used for documentation and discovery.
        description: Optional extended description for architectural overviews.
        tags: Optional tags applied to every router when included.
        startup_hooks: Lifecycle hooks executed on application startup.
        shutdown_hooks: Lifecycle hooks executed on application shutdown.
        order: Ordering weight that controls how routers sharing the same
            ``mount_path`` are mounted. Lower numbers are mounted first which is
            important when routers have overlapping static and parametrised
            paths.
    """

    name: str
    mount_path: str
    routers: Sequence[APIRouter]
    summary: str
    description: str | None = None
    tags: Sequence[str] | None = None
    startup_hooks: Sequence[LifecycleHook] = field(default_factory=tuple)
    shutdown_hooks: Sequence[LifecycleHook] = field(default_factory=tuple)
    order: int = 100

    def __post_init__(self) -> None:  # pragma: no cover - defensive programming
        if not self.mount_path.startswith("/"):
            msg = "BoundedContext.mount_path must be absolute (start with '/')."
            raise ValueError(msg)
        if not self.routers:
            msg = "BoundedContext.routers cannot be empty."
            raise ValueError(msg)


class APIBootstrapper:
    """Registers bounded contexts and mounts them onto a FastAPI application."""

    def __init__(self, *, base_path: str = "") -> None:
        self._base_path = base_path.rstrip("/")
        self._contexts: dict[str, BoundedContext] = {}

    @property
    def base_path(self) -> str:
        """Base API prefix applied to every bounded context."""

        return self._base_path

    @property
    def contexts(self) -> Sequence[BoundedContext]:
        """Return the registered contexts in mounting order."""

        return tuple(sorted(self._contexts.values(), key=lambda ctx: ctx.order))

    def register(self, context: BoundedContext) -> None:
        """Register a bounded context.

        Raises:
            ValueError: if a context with the same name has already been
                registered.
        """

        if context.name in self._contexts:
            msg = f"Bounded context '{context.name}' already registered."
            raise ValueError(msg)
        self._contexts[context.name] = context

    def register_many(self, contexts: Iterable[BoundedContext]) -> None:
        """Register multiple contexts in order."""

        for context in contexts:
            self.register(context)

    def mount(self, app: FastAPI) -> None:
        """Wire the registered contexts into the provided FastAPI app."""

        for context in self.contexts:
            mount_path = f"{self._base_path}{context.mount_path}" or "/"
            tags = list(context.tags) if context.tags else None
            for router in context.routers:
                app.include_router(router, prefix=mount_path, tags=tags)
            for hook in context.startup_hooks:
                app.add_event_handler("startup", self._wrap_hook(app, hook))
            for hook in context.shutdown_hooks:
                app.add_event_handler("shutdown", self._wrap_hook(app, hook))

    @staticmethod
    def _wrap_hook(app: FastAPI, hook: LifecycleHook) -> Callable[[], Awaitable[None] | None]:
        """Normalise lifecycle hooks to callables accepted by FastAPI."""

        async def _run() -> None:
            result = hook(app)
            if inspect.isawaitable(result):
                await result

        return _run


__all__ = ["APIBootstrapper", "BoundedContext", "LifecycleHook"]
