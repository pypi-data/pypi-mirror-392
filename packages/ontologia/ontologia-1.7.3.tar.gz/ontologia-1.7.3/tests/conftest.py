"""Test configuration and helpers.

Provides a minimal async test runner fallback when pytest-asyncio is not
available in the environment. This ensures unit tests marked as asyncio
can still execute in constrained environments (e.g., CI sandboxes) without
altering test semantics.
"""

from __future__ import annotations

# Ensure test-friendly environment before any app imports
import os

# Force an isolated in-memory SQLite database per test process (override any prior value)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("TESTING", "1")
# Disable external integrations during tests unless explicitly enabled
os.environ.setdefault("ELASTICSEARCH_HOSTS", "")

import asyncio
import importlib.util
import inspect
from collections.abc import Callable
from typing import Any

import pytest

_HAS_PYTEST_ASYNCIO = importlib.util.find_spec("pytest_asyncio") is not None

# Provide minimal stubs for optional heavy deps to prevent import-time failures
# in modules that only check for their presence.
import sys
import types

for _opt in ("polars",):
    if _opt not in sys.modules:
        sys.modules[_opt] = types.ModuleType(_opt)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: Any) -> bool | None:
    """Run coroutine test functions via asyncio when pytest-asyncio is missing.

    If pytest-asyncio is installed, defer to its behavior. Otherwise, detect
    coroutine test functions and execute them with asyncio.run.
    """
    if _HAS_PYTEST_ASYNCIO:
        return None

    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        params = set(inspect.signature(testfunction).parameters.keys())
        kwargs = {k: v for k, v in getattr(pyfuncitem, "funcargs", {}).items() if k in params}
        asyncio.run(testfunction(**kwargs))
        return True
    return None


# Import the enhanced fixtures so they're discovered by pytest.
# This mirrors a standard conftest layout while keeping this file minimal.
try:
    from tests.fixtures.enhanced_conftest import *  # type: ignore[unused-ignore]  # noqa: F401,F403
except Exception:  # pragma: no cover - optional in constrained envs
    # Optional fixtures require extra dev dependencies (e.g., factory-boy).
    # Provide minimal fallbacks for common fixtures used by unit tests.
    import os
    from collections.abc import Iterator

    import pytest
    from fastapi.testclient import TestClient
    from ontologia_api.core.auth import (  # type: ignore
        UserPrincipal,
        get_current_user,
    )
    from ontologia_api.core.database import get_session  # type: ignore
    from ontologia_api.main import app  # type: ignore
    from sqlmodel import Session as SQLSession
    from sqlmodel import SQLModel, create_engine

    @pytest.fixture
    def session() -> Iterator[SQLSession]:
        engine = create_engine(
            "sqlite:///file:pytest_shared?mode=memory&cache=shared",
            connect_args={"check_same_thread": False, "uri": True},
        )
        try:
            import ontologia.domain.metamodels.instances.models_sql  # noqa: F401
        except Exception:
            pass
        SQLModel.metadata.create_all(engine)
        with SQLSession(engine) as s:
            yield s

    @pytest.fixture
    def client(session: SQLSession) -> Iterator[TestClient]:
        def get_session_override() -> Iterator[SQLSession]:
            yield session

        tenant_key = f"ontology/{os.getenv('ONTOLOGY', 'default')}"
        test_principal = UserPrincipal(
            user_id="test_user",
            roles=["admin"],
            tenants={tenant_key: "admin"},
        )

        def get_current_user_override() -> UserPrincipal:  # type: ignore[reportGeneralTypeIssues]
            return test_principal

        app.dependency_overrides[get_session] = get_session_override
        app.dependency_overrides[get_current_user] = get_current_user_override

        c = TestClient(app)
        try:
            yield c
        finally:
            app.dependency_overrides.clear()


# --- Global per-test DB isolation for API dependencies ---
# Avoids cross-test unique constraint collisions by providing a fresh in-memory
# database for FastAPI dependency `get_session` when tests access the app.
try:
    import ontologia_api.main as _api_main
    from ontologia_api.core import database as _api_db
    from ontologia_api.core.database import get_session as _api_get_session
    from ontologia_api.main import app as _api_app
    from sqlmodel import Session as SQLSession
    from sqlmodel import SQLModel, create_engine

    try:
        # Clear cached dependencies to avoid stale singletons across tests
        from ontologia_api.dependencies.events import reset_dependencies_caches as _reset_deps
    except Exception:  # pragma: no cover
        _reset_deps: Callable[[], Any] | None = None

    @pytest.fixture(autouse=True)
    def _isolate_api_db_per_test(request):
        """Ensure FastAPI uses the same DB as the test session when available.

        - If a `session` fixture is requested by the test, reuse its engine so
          API calls and direct DB access operate on the same database.
        - Otherwise, provide a fresh in-memory engine with all models created.
        """
        # Skip per-test isolation for contract and playground tests
        fspath = str(getattr(request, "fspath", ""))
        if "tests/contracts" in fspath or "playground" in fspath:
            yield
            return

        engine = None
        # Try to reuse the test's `session` fixture engine, if present
        try:
            sess = request.getfixturevalue("session")  # type: ignore[assignment]
            try:
                engine = sess.get_bind()  # type: ignore[attr-defined]
            except Exception:
                engine = None
        except Exception:
            engine = None

        # Otherwise fall back to a dedicated in-memory engine
        if engine is None:
            from sqlalchemy.pool import StaticPool as _StaticPool

            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=_StaticPool,
            )
            # Ensure models are imported so metadata includes all tables
            try:
                import registro.core.resource  # noqa: F401

                import ontologia.domain.metamodels.types.action_type  # noqa: F401
                import ontologia.domain.metamodels.types.link_type  # noqa: F401
                import ontologia.domain.metamodels.types.object_type  # noqa: F401
                import ontologia.domain.metamodels.types.property_type  # noqa: F401
            except Exception:
                pass
        # Always reset schema to guarantee clean state per test
        try:
            SQLModel.metadata.drop_all(engine)
        except Exception:
            pass
        SQLModel.metadata.create_all(engine)

        # For auth-focused tests, ensure any auth overrides are cleared so that
        # Authorization headers (or their absence) are respected.
        if "tests/integration/test_auth_jwt.py" in fspath:
            try:
                from ontologia_api.core.auth import get_current_user as _api_get_user

                _api_app.dependency_overrides.pop(_api_get_user, None)
            except Exception:
                pass

        # Clear dependency caches now that the engine is established
        try:
            if _reset_deps:
                _reset_deps()
        except Exception:
            pass

        # Also patch the API's global engine so any direct engine usage
        # (e.g., during app startup/bootstrap) uses the same per-test DB.
        _api_db.engine = engine
        # Patch the already-imported engine reference used by the FastAPI app
        # so startup and any direct engine usage operate on the same in-memory DB.
        try:
            _api_main.engine = engine
        except Exception:
            pass

        def _override():
            with SQLSession(engine) as s:
                yield s

        _api_app.dependency_overrides[_api_get_session] = _override
        try:
            yield
        finally:
            _api_app.dependency_overrides.pop(_api_get_session, None)

except Exception:
    # If API modules are not importable in a given test run, skip isolation
    pass

# --- Auth-aware client fixtures ---
try:
    from fastapi.testclient import TestClient as _TestClient
    from ontologia_api.core.database import get_session as _api_get_session2
    from ontologia_api.main import app as _app_for_auth
    from sqlmodel import Session as _SQLSession

    @pytest.fixture
    def auth_client(request) -> _TestClient:  # type: ignore[override]
        """Client that exercises real auth (no get_current_user override).

        Still benefits from per-test DB isolation via the autouse fixture.
        If a `session` fixture exists in the requesting test, ensure the API uses it.
        """
        engine = None
        try:
            sess = request.getfixturevalue("session")  # type: ignore[assignment]
            try:
                engine = sess.get_bind()  # type: ignore[attr-defined]
            except Exception:
                engine = None
        except Exception:
            engine = None

        if engine is not None:

            def _override():
                with _SQLSession(engine) as s:
                    yield s

            _app_for_auth.dependency_overrides[_api_get_session2] = _override

        try:
            with _TestClient(_app_for_auth) as c:
                yield c
        finally:
            _app_for_auth.dependency_overrides.pop(_api_get_session2, None)

except Exception:
    pass

# Provide a deterministic `client` fixture that ensures per-test DB and admin principal,
# overriding any similarly-named fixture from auxiliary modules.
try:
    import importlib

    from fastapi.testclient import TestClient as _TestClient2
    from ontologia_api.core.auth import (
        UserPrincipal as _UserPrincipal,
    )
    from ontologia_api.core.auth import (
        get_current_user as _get_current_user,
    )
    from ontologia_api.core.database import get_session as _get_session_dep
    from sqlmodel import Session as _Sess

    try:
        from ontologia_api.dependencies.events import reset_dependencies_caches as _reset_deps2
    except Exception:  # pragma: no cover
        _reset_deps2: Callable[[], Any] | None = None

    @pytest.fixture
    def client(request) -> _TestClient2:  # type: ignore[override]
        # Reuse the per-test engine established by the autouse isolation
        # fixture to guarantee a clean database for every test.
        try:
            import ontologia_api.core.database as _api_db2
            import ontologia_api.main as _api_main2
            from sqlmodel import create_engine as _create_engine
        except Exception as _e:  # pragma: no cover - unlikely
            raise RuntimeError("API modules not importable for client fixture") from _e

        # Prefer the calling test's `session` engine if available to ensure
        # API operations and direct DB access see the same state.
        eng = None
        try:
            _sess_for_client = request.getfixturevalue("session")  # type: ignore[assignment]
            try:
                eng = _sess_for_client.get_bind()  # type: ignore[attr-defined]
            except Exception:
                eng = None
        except Exception:
            eng = None
        if eng is None:
            # Create a brand-new in-memory engine for this client, ensuring
            # complete isolation even if drop_all cannot resolve FK cycles.
            from sqlalchemy.pool import StaticPool as _StaticPool2

            eng = _create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=_StaticPool2,
            )
        # Ensure models are imported and force a clean schema on the fresh engine
        try:
            import registro.core.resource as _reg_res  # noqa: F401

            import ontologia.domain.metamodels.instances.models_sql as _models  # noqa: F401
            import ontologia.domain.metamodels.types.action_type as _act  # noqa: F401
            import ontologia.domain.metamodels.types.link_type as _lt  # noqa: F401
            import ontologia.domain.metamodels.types.object_type as _ot  # noqa: F401
            import ontologia.domain.metamodels.types.property_type as _pt  # noqa: F401
        except Exception:
            pass
        try:
            from sqlmodel import SQLModel as _SQLM

            try:
                _SQLM.metadata.drop_all(eng)
            except Exception:
                pass
            _SQLM.metadata.create_all(eng)
        except Exception:
            pass
        # Reset dependency caches to ensure consistency with the new engine
        try:
            if _reset_deps2:
                _reset_deps2()
        except Exception:
            pass
        _api_db2.engine = eng
        _api_main2.engine = eng

        # Create a fresh FastAPI app instance to avoid global state leaks between tests
        try:
            import ontologia_api.main as _main_mod

            _main_mod = importlib.reload(_main_mod)  # type: ignore[assignment]
            _app_for_client = _main_mod.app  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            from ontologia_api.main import app as _app_for_client  # fallback

        def _session_override():
            with _Sess(eng) as s:
                yield s

        test_principal = _UserPrincipal(
            user_id="test_user",
            roles=["admin"],
            tenants={"ontology/default": "admin", "*": "admin"},
        )

        def _user_override():
            return test_principal

        _app_for_client.dependency_overrides[_get_session_dep] = _session_override
        _app_for_client.dependency_overrides[_get_current_user] = _user_override
        try:
            with _TestClient2(_app_for_client) as c:
                # Purge any pre-seeded link types/links in the default scope to ensure
                # deterministic integration tests regardless of prior state.
                try:
                    # Prefer raw SQL for robustness against dependency ordering
                    with eng.connect() as conn:
                        try:
                            conn.exec_driver_sql("DELETE FROM linkedobject")
                        except Exception:
                            pass
                        try:
                            conn.exec_driver_sql("DELETE FROM linkpropertytype")
                        except Exception:
                            pass
                        try:
                            conn.exec_driver_sql("DELETE FROM linktype")
                        except Exception:
                            pass
                        try:
                            conn.exec_driver_sql(
                                "DELETE FROM resource WHERE resource_type IN ('link-type','link-property-type','linked-object')"
                            )
                        except Exception:
                            pass
                        try:
                            conn.commit()
                        except Exception:
                            pass
                    from registro.core.resource import Resource as _Res
                    from sqlmodel import select as _select

                    from ontologia.domain.metamodels.instances.models_sql import (
                        LinkedObject as _LO,
                    )
                    from ontologia.domain.metamodels.types.link_property_type import (
                        LinkPropertyType as _LPT,
                    )
                    from ontologia.domain.metamodels.types.link_type import (
                        LinkType as _LT,
                    )

                    with _Sess(eng) as _s:
                        # Delete linked objects (all)
                        try:
                            for lo in _s.exec(_select(_LO)).all():
                                _s.delete(lo)
                            _s.commit()
                        except Exception:
                            _s.rollback()
                        # Delete link property types for current instance
                        try:
                            rows = _s.exec(
                                _select(_LPT)
                                .join(_LT, _LT.api_name == _LPT.link_type_api_name)
                                .join(_Res, _Res.rid == _LT.rid)
                                .where(
                                    _Res.service == "ontology",
                                    _Res.instance == "default",
                                )
                            ).all()
                            for r in rows or []:
                                _s.delete(r)
                            if rows:
                                _s.commit()
                        except Exception:
                            _s.rollback()
                        # Delete link types for current instance
                        try:
                            lts = _s.exec(
                                _select(_LT)
                                .join(_Res, _Res.rid == _LT.rid)
                                .where(
                                    _Res.service == "ontology",
                                    _Res.instance == "default",
                                )
                            ).all()
                            for lt in lts or []:
                                _s.delete(lt)
                            if lts:
                                _s.commit()
                        except Exception:
                            _s.rollback()
                except Exception:
                    pass
                yield c
        finally:
            _app_for_client.dependency_overrides.clear()

except Exception:
    pass


def pytest_collection_modifyitems(config, items):  # pragma: no cover - test harness behavior
    """Skip benchmark tests unless explicitly enabled via RUN_BENCHMARK=true."""
    import os as _os

    if _os.getenv("RUN_BENCHMARK") == "true":
        return
    for item in items:
        if item.get_closest_marker("benchmark") is not None:
            item.add_marker(
                pytest.mark.skip(reason="Benchmarks disabled; set RUN_BENCHMARK=true to enable")
            )
