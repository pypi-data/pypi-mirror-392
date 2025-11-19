from __future__ import annotations

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from ontologia_api.core.ddd import APIBootstrapper, BoundedContext


def _make_router(name: str) -> APIRouter:
    router = APIRouter()

    @router.get("/ping", name=f"{name}_ping")
    def ping() -> dict[str, str]:
        return {"status": "ok", "router": name}

    return router


def test_bootstrapper_mounts_contexts() -> None:
    app = FastAPI()
    bootstrapper = APIBootstrapper()
    bootstrapper.register(
        BoundedContext(
            name="alpha",
            summary="Alpha context",
            mount_path="/v1/alpha",
            routers=(_make_router("alpha"),),
        )
    )
    bootstrapper.mount(app)

    assert app.url_path_for("alpha_ping") == "/v1/alpha/ping"


def test_bootstrapper_preserves_mount_order() -> None:
    app = FastAPI()
    bootstrapper = APIBootstrapper()
    bootstrapper.register_many(
        (
            BoundedContext(
                name="first",
                summary="First context",
                mount_path="/v1/common",
                routers=(_make_router("first"),),
                order=10,
            ),
            BoundedContext(
                name="second",
                summary="Second context",
                mount_path="/v1/common",
                routers=(_make_router("second"),),
                order=20,
            ),
        )
    )
    bootstrapper.mount(app)

    # Routes with overlapping prefixes remain accessible and ordered
    assert app.url_path_for("first_ping") == "/v1/common/ping"
    assert app.url_path_for("second_ping") == "/v1/common/ping"
    route_names = [route.name for route in app.routes if isinstance(route, APIRoute)]
    assert route_names.index("first_ping") < route_names.index("second_ping")


def test_registering_duplicate_contexts_is_rejected() -> None:
    bootstrapper = APIBootstrapper()
    bootstrapper.register(
        BoundedContext(
            name="duplicate",
            summary="Duplicate",
            mount_path="/v1/duplicate",
            routers=(_make_router("duplicate"),),
        )
    )

    with pytest.raises(ValueError):
        bootstrapper.register(
            BoundedContext(
                name="duplicate",
                summary="Duplicate",
                mount_path="/v1/duplicate",
                routers=(_make_router("duplicate"),),
            )
        )
