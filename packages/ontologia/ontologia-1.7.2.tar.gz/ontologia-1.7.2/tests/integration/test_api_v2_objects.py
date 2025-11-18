from fastapi.testclient import TestClient
from ontologia_api.core.auth import create_access_token
from ontologia_api.core.database import get_session


def _create_object_type(client: TestClient, api_name: str, pk: str = "id"):
    resp = client.put(
        f"/v2/ontologies/default/objectTypes/{api_name}",
        json={
            "displayName": api_name.title(),
            "primaryKey": pk,
            "properties": {
                pk: {"dataType": "string", "displayName": pk.upper(), "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
        },
    )
    assert resp.status_code == 200, resp.text


def test_upsert_get_list_delete_object_instance(client: TestClient):
    _create_object_type(client, "asset", pk="asset_id")

    # Upsert instance
    put_resp = client.put(
        "/v2/ontologies/default/objects/asset/A123",
        json={"properties": {"name": "Laptop"}},
    )
    assert put_resp.status_code == 200, put_resp.text
    body = put_resp.json()
    assert body["objectTypeApiName"] == "asset"
    assert body["pkValue"] == "A123"
    assert body["properties"]["asset_id"] == "A123"
    assert body["properties"]["name"] == "Laptop"

    # Get instance
    get_resp = client.get("/v2/ontologies/default/objects/asset/A123")
    assert get_resp.status_code == 200
    assert get_resp.json()["properties"]["name"] == "Laptop"

    # List by query filter
    list_q = client.get("/v2/ontologies/default/objects", params={"objectType": "asset"})
    assert list_q.status_code == 200
    assert len(list_q.json()["data"]) == 1

    # List by path
    list_p = client.get("/v2/ontologies/default/objects/asset")
    assert list_p.status_code == 200
    assert len(list_p.json()["data"]) == 1

    # Delete
    del_resp = client.delete("/v2/ontologies/default/objects/asset/A123")
    assert del_resp.status_code == 204

    # Now 404
    get_404 = client.get("/v2/ontologies/default/objects/asset/A123")
    assert get_404.status_code == 404


def test_upsert_object_unknown_object_type_returns_400(client: TestClient):
    resp = client.put(
        "/v2/ontologies/default/objects/unknown/1",
        json={"properties": {"name": "X"}},
    )
    assert resp.status_code == 400
    assert "ObjectType 'unknown' not found" in resp.json()["detail"]


def test_upsert_replaces_properties_semantics(client: TestClient):
    _create_object_type(client, "person", pk="person_id")

    # Create with both fields
    r1 = client.put(
        "/v2/ontologies/default/objects/person/1",
        json={"properties": {"name": "Alice"}},
    )
    assert r1.status_code == 200
    assert r1.json()["properties"]["name"] == "Alice"

    # Replace with only PK enforced and different name
    r2 = client.put(
        "/v2/ontologies/default/objects/person/1",
        json={"properties": {"name": "Alice Smith"}},
    )
    assert r2.status_code == 200
    props = r2.json()["properties"]
    # Only 'person_id' and 'name' are expected; semantics are replace, not merge
    assert props["person_id"] == "1"
    assert props["name"] == "Alice Smith"


def test_abac_property_filtering():
    # This test needs its own client without authentication override
    from fastapi.testclient import TestClient
    from ontologia_api.main import app
    from sqlmodel import Session, SQLModel, create_engine
    from sqlmodel.pool import StaticPool

    # Create test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Override only database session, keep authentication
        def get_session_override():
            yield session

        app.dependency_overrides[get_session] = get_session_override

        with TestClient(app) as client:
            # Create tokens for admin and viewer
            admin_token = create_access_token(subject="admin", roles=["admin"], tenants={})
            viewer_token = create_access_token(subject="viewer", roles=["viewer"], tenants={})

            # Use admin token for creation
            headers = {"Authorization": f"Bearer {admin_token}"}

            # Create an ObjectType with a sensitive property
            client.put(
                "/v2/ontologies/default/objectTypes/user",
                json={
                    "displayName": "User",
                    "primaryKey": "id",
                    "properties": {
                        "id": {"dataType": "string", "required": True, "displayName": "ID"},
                        "name": {"dataType": "string", "displayName": "Name"},
                        "ssn": {
                            "dataType": "string",
                            "displayName": "SSN",
                            "securityTags": ["PII"],
                        },
                    },
                },
                headers=headers,
            )

            # Create an instance
            client.put(
                "/v2/ontologies/default/objects/user/u1",
                json={"properties": {"name": "Test User", "ssn": "123-456-7890"}},
                headers=headers,
            )

            # 1. Admin should see the PII property
            resp_admin = client.get(
                "/v2/ontologies/default/objects/user/u1",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp_admin.status_code == 200
            assert "ssn" in resp_admin.json()["properties"]
            assert resp_admin.json()["properties"]["ssn"] == "123-456-7890"

            # 2. Viewer should NOT see the PII property
            resp_viewer = client.get(
                "/v2/ontologies/default/objects/user/u1",
                headers={"Authorization": f"Bearer {viewer_token}"},
            )
            assert resp_viewer.status_code == 200
            assert "ssn" not in resp_viewer.json()["properties"]
            assert "name" in resp_viewer.json()["properties"]

        app.dependency_overrides.clear()
