from __future__ import annotations

# Ensure models are imported so startup create_all sees all tables
import registro.core.resource  # noqa: F401
import schemathesis
from fastapi.testclient import TestClient
from ontologia_api.main import app

import ontologia.domain.metamodels.types.action_type  # noqa: F401
import ontologia.domain.metamodels.types.link_type  # noqa: F401
import ontologia.domain.metamodels.types.object_type  # noqa: F401
import ontologia.domain.metamodels.types.property_type  # noqa: F401

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


def _seed_baseline() -> None:
    with TestClient(app) as client:
        client.put(
            "/v2/ontologies/default/objectTypes/employee",
            json={
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )


def test_openapi_spec_is_valid():
    schema.validate()


def test_openapi_contract_object_types():
    _seed_baseline()
    with TestClient(app) as client:
        response = client.get("/v2/ontologies/default/objectTypes")
        operation = schema["/v2/ontologies/{ontologyApiName}/objectTypes"]["get"]
        st_response = schemathesis.Response.from_any(response)
        schema.validate_response(operation, st_response)


def test_openapi_contract_objects():
    with TestClient(app) as client:
        client.put(
            "/v2/ontologies/default/objectTypes/employee",
            json={
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                },
            },
        )
        client.put(
            "/v2/ontologies/default/objects/employee/e1",
            json={"properties": {"id": "e1"}},
        )
        response = client.get(
            "/v2/ontologies/default/objects",
            params={"objectType": "employee"},
        )
        operation = schema["/v2/ontologies/{ontologyApiName}/objects"]["get"]
        st_response = schemathesis.Response.from_any(response)
        schema.validate_response(operation, st_response)
