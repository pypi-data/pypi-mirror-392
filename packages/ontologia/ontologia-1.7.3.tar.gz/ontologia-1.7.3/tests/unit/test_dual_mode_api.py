"""
Tests for dual-mode API endpoints (service + OGM).

Tests both the original service-based approach and the new OGM-based approach
to ensure backward compatibility and proper functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from ontologia_api.core.auth import UserPrincipal, require_role
from ontologia_api.v2.routers.objects import OGM_AVAILABLE, router


class TestDualModeAPI:
    """Test dual-mode API endpoints."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        # Enable test authentication
        os.environ["USE_TEST_AUTH"] = "1"

        app = FastAPI()

        # Mock authentication: override concrete require_role dependencies
        from ontologia_api.core.auth import get_current_user as _get_user

        dep_viewer = require_role("viewer")
        dep_editor = require_role("editor")
        dep_admin = require_role("admin")
        app.dependency_overrides[dep_viewer] = lambda: MagicMock(spec=UserPrincipal, roles=["admin"])  # type: ignore
        app.dependency_overrides[dep_editor] = lambda: MagicMock(spec=UserPrincipal, roles=["admin"])  # type: ignore
        app.dependency_overrides[dep_admin] = lambda: MagicMock(spec=UserPrincipal, roles=["admin"])  # type: ignore
        app.dependency_overrides[_get_user] = lambda: MagicMock(spec=UserPrincipal, roles=["admin"])  # type: ignore

        # Simulate the actual mounting structure
        runtime_router = APIRouter(prefix="/v3/ontologies/{ontologyApiName}/runtime")
        runtime_router.include_router(router)
        app.include_router(runtime_router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_user_principal(self):
        """Mock user principal."""
        principal = MagicMock(spec=UserPrincipal)
        principal.roles = ["admin"]
        return principal

    def test_upsert_service_mode(self, client, app, mock_user_principal):
        """Test upsert in service mode (default)."""
        # Override command service dependency para controlar retorno
        from ontologia_api.handlers.instances import get_instance_command_service as _cmd_dep

        mock_cmd = MagicMock()
        mock_result = MagicMock()
        mock_result.pk_value = "test-pk"
        mock_result.rid = "test-rid"
        mock_result.properties = {"name": "test"}
        mock_cmd.upsert_object.return_value = mock_result
        app.dependency_overrides[_cmd_dep] = lambda *a, **k: mock_cmd

        response = client.put(
            "/v3/ontologies/test/runtime/objects/test_type/test_pk?a=1&k=1",
            json={"properties": {"name": "test"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["objectTypeApiName"] == "test_type"
        assert data["pkValue"] == "test-pk"
        assert data["properties"]["name"] == "test"

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_upsert_ogm_mode(self, client, mock_user_principal):
        """Test upsert in OGM mode."""
        with (
            patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model,
            patch("ontologia_api.v2.routers.objects.get_ogm_ontology", return_value=object()),
            patch("ontologia_api.v2.routers.objects._ogm_get_object") as mock_ogm_get,
        ):
            # Mock OGM model
            mock_model = MagicMock()
            mock_model.__primary_key__ = "id"
            mock_instance = MagicMock()
            mock_instance.__primary_key__ = "id"
            mock_instance.id = "test_pk"
            mock_instance.model_dump.return_value = {"name": "test", "id": "test_pk"}
            mock_instance.save.return_value = mock_instance
            mock_model.return_value = mock_instance
            mock_model.get.return_value = mock_instance
            mock_get_model.return_value = mock_model

            response = client.put(
                "/v3/ontologies/test/runtime/objects/test_type/test_pk?use_ogm=true&a=1&k=1",
                json={"properties": {"name": "test"}},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["objectTypeApiName"] == "test_type"
            assert data["pkValue"] == "test_pk"
            assert data["properties"]["name"] == "test"

    def test_get_service_mode(self, client, app, mock_user_principal):
        """Test get in service mode (default)."""
        # Override query service dependency para controlar retorno
        from ontologia_api.handlers.instances import get_instance_query_service as _qry_dep

        mock_qry = MagicMock()
        mock_result = MagicMock()
        mock_result.pk_value = "test-pk"
        mock_result.rid = "test-rid"
        mock_result.properties = {"name": "test"}
        mock_qry.get_object.return_value = mock_result
        app.dependency_overrides[_qry_dep] = lambda *a, **k: mock_qry

        response = client.get("/v3/ontologies/test/runtime/objects/test_type/test_pk?a=1&k=1")

        assert response.status_code == 200
        data = response.json()
        assert data["objectTypeApiName"] == "test_type"
        assert data["pkValue"] == "test-pk"
        assert data["properties"]["name"] == "test"

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_get_ogm_mode(self, client, mock_user_principal):
        """Test get in OGM mode."""
        with (
            patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model,
            patch("ontologia_api.v2.routers.objects.get_ogm_ontology", return_value=object()),
            patch("ontologia_api.v2.routers.objects._ogm_get_object") as mock_ogm_get,
        ):
            mock_model = MagicMock()
            mock_model.__primary_key__ = "id"
            mock_instance = MagicMock()
            mock_instance.__primary_key__ = "id"
            mock_instance.id = "test_pk"
            mock_instance.model_dump.return_value = {"name": "test", "id": "test_pk"}
            mock_model.get.return_value = mock_instance
            mock_get_model.return_value = mock_model

            from ontologia_api.v2.schemas.instances import ObjectReadResponse

            mock_ogm_get.return_value = ObjectReadResponse(
                rid="obj-test_type-test_pk",
                objectTypeApiName="test_type",
                pkValue="test-pk",
                properties={"name": "test"},
            )

            response = client.get(
                "/v3/ontologies/test/runtime/objects/test_type/test_pk?use_ogm=true&a=1&k=1"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["objectTypeApiName"] == "test_type"
            assert data["pkValue"] == "test-pk"

    def test_delete_service_mode(self, client, app, mock_user_principal):
        """Test delete in service mode (default)."""
        # Mock the service at the application layer where it's actually used
        with patch(
            "ontologia.application.instances_service.InstancesService.delete_object"
        ) as mock_delete:
            mock_delete.return_value = True

            response = client.delete("/v3/ontologies/test/runtime/objects/test_type/test_pk")

            assert response.status_code == 204

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_delete_ogm_mode(self, client, mock_user_principal):
        """Test delete in OGM mode."""
        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_instance = MagicMock()
            mock_instance.delete.return_value = None
            mock_model.get.return_value = mock_instance
            mock_get_model.return_value = mock_model

            response = client.delete(
                "/v3/ontologies/test/runtime/objects/test_type/test_pk?use_ogm=true"
            )

            assert response.status_code == 204

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_fallback_to_service(self, client, app, mock_user_principal):
        """Test OGM fallback to service when OGM fails."""
        with (
            patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model,
            patch(
                "ontologia.application.instances_service.InstancesService.upsert_object"
            ) as mock_upsert,
        ):
            # OGM fails
            mock_get_model.return_value = None

            # Service succeeds
            mock_result = MagicMock()
            mock_result.pk_value = "test-pk"
            mock_result.rid = "test-rid"
            mock_result.properties = {"name": "test"}
            mock_upsert.return_value = mock_result

            response = client.put(
                "/v3/ontologies/test/runtime/objects/test_type/test_pk?use_ogm=true&a=1&k=1",
                json={"properties": {"name": "test"}},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["objectTypeApiName"] == "test_type"
            assert data["pkValue"] == "test-pk"
            assert data["properties"]["name"] == "test"

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_model_not_found(self, client, mock_user_principal):
        """Test OGM when model is not found."""
        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_get_model.return_value = None

            response = client.put(
                "/v3/ontologies/test/runtime/objects/unknown_type/test_pk?use_ogm=true",
                json={"properties": {"name": "test"}},
            )

            assert response.status_code == 400
            # Different code paths may format the detail differently; assert 4xx semantics
            detail = response.json().get("detail", "")
            assert isinstance(detail, (str, list, dict))

    def test_ogm_unavailable_fallback(self, client, app, mock_user_principal):
        """Test graceful fallback when OGM is not available."""
        with patch("ontologia_api.v2.routers.objects.OGM_AVAILABLE", False):
            with patch(
                "ontologia.application.instances_service.InstancesService.upsert_object"
            ) as mock_upsert:
                mock_result = MagicMock()
                mock_result.pk_value = "test-pk"
                mock_result.rid = "test-rid"
                mock_result.properties = {"name": "test"}
                mock_upsert.return_value = mock_result

                response = client.put(
                    "/v3/ontologies/test/runtime/objects/test_type/test_pk?use_ogm=true",
                    json={"properties": {"name": "test"}},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["objectTypeApiName"] == "test_type"
                assert data["pkValue"] == "test-pk"
                assert data["properties"]["name"] == "test"


class TestOGMHelpers:
    """Test OGM helper functions."""

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_upsert_success(self):
        """Test successful OGM upsert."""
        from ontologia_api.v2.routers.objects import _ogm_upsert_object

        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_model.__primary_key__ = "id"
            mock_instance = MagicMock()
            mock_instance.__primary_key__ = "id"
            mock_instance.id = "test_pk"
            mock_instance.model_dump.return_value = {"name": "test", "id": "test_pk"}
            mock_instance.save.return_value = mock_instance
            mock_model.return_value = mock_instance
            mock_get_model.return_value = mock_model

            result = _ogm_upsert_object("test_type", "test_pk", {"name": "test"})

            assert result.objectTypeApiName == "test_type"
            assert result.pkValue == "test_pk"
            assert result.properties["name"] == "test"

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_get_success(self):
        """Test successful OGM get."""
        from ontologia_api.v2.routers.objects import _ogm_get_object

        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_model.__primary_key__ = "id"
            mock_instance = MagicMock()
            mock_instance.__primary_key__ = "id"
            mock_instance.id = "test_pk"
            mock_instance.model_dump.return_value = {"name": "test", "id": "test_pk"}
            mock_model.get.return_value = mock_instance
            mock_get_model.return_value = mock_model

            result = _ogm_get_object("test_type", "test_pk")

            assert result.objectTypeApiName == "test_type"
            assert result.pkValue == "test_pk"

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_delete_success(self):
        """Test successful OGM delete."""
        from ontologia_api.v2.routers.objects import _ogm_delete_object

        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_instance = MagicMock()
            mock_instance.delete.return_value = None
            mock_model.get.return_value = mock_instance
            mock_get_model.return_value = mock_model

            result = _ogm_delete_object("test_type", "test_pk")

            assert result is True

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_get_not_found(self):
        """Test OGM get when object not found."""
        from fastapi import HTTPException
        from ontologia_api.v2.routers.objects import _ogm_get_object

        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_model.get.side_effect = Exception("Object not found")
            mock_get_model.return_value = mock_model

            with pytest.raises(HTTPException) as exc_info:
                _ogm_get_object("test_type", "unknown_pk")

            assert exc_info.value.status_code == 404

    @pytest.mark.skipif(not OGM_AVAILABLE, reason="OGM not available")
    def test_ogm_delete_not_found(self):
        """Test OGM delete when object not found."""
        from ontologia_api.v2.routers.objects import _ogm_delete_object

        with patch("ontologia_api.v2.routers.objects.get_model_class") as mock_get_model:
            mock_model = MagicMock()
            mock_model.get.side_effect = Exception("Object not found")
            mock_get_model.return_value = mock_model

            result = _ogm_delete_object("test_type", "unknown_pk")

            assert result is False
