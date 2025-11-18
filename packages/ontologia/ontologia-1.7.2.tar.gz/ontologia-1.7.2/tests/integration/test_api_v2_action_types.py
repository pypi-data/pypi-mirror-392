import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Minimal environment for tests; global repo config in pytest.ini already sets most
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("ELASTICSEARCH_HOSTS", "[]")
os.environ.setdefault("ONTOLOGIA_CONFIG_ROOT", str(Path(__file__).parent.parent))

from ontologia_api.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_action_type_crud(client: TestClient):
    """Test CRUD operations for action types."""
    # First, get an authentication token
    token_response = client.post(
        "/v2/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["access_token"]

    # Include the token in the request headers
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # create ObjectType used by ActionType target
    r = client.put(
        "/v2/ontologies/default/objectTypes/expense",
        json={
            "displayName": "Expense",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "status": {"dataType": "string", "displayName": "Status", "required": False},
            },
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text

    # upsert action type
    body = {
        "displayName": "Approve Expense",
        "description": "Approve expense when pending",
        "targetObjectType": "expense",
        "parameters": {
            "message": {"dataType": "string", "displayName": "Message", "required": True}
        },
        "submissionCriteria": [
            {
                "description": "Only when pending",
                "ruleLogic": "target_object['properties']['status']=='PENDING'",
            }
        ],
        "validationRules": [],
        "executorKey": "system.log_message_test",
    }
    r2 = client.put(
        "/v2/ontologies/default/actionTypes/approve_expense", json=body, headers=headers
    )
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["apiName"] == "approve_expense"
    assert data["targetObjectType"] == "expense"
    assert data["version"] == 1
    assert data["isLatest"] is True

    # get it
    r3 = client.get("/v2/ontologies/default/actionTypes/approve_expense", headers=headers)
    assert r3.status_code == 200, r3.text

    # list
    r4 = client.get("/v2/ontologies/default/actionTypes", headers=headers)
    assert r4.status_code == 200, r4.text
    lst = r4.json()["data"]
    assert any(
        it["apiName"] == "approve_expense" and it["version"] == 1 for it in lst
    ), f"Action type 'approve_expense' not found in {lst}"

    # delete
    r5 = client.delete("/v2/ontologies/default/actionTypes/approve_expense", headers=headers)
    assert r5.status_code == 204, r5.text

    # Verify deletion
    r6 = client.get("/v2/ontologies/default/actionTypes/approve_expense", headers=headers)
    assert r6.status_code == 404, f"Expected 404, got {r6.status_code}: {r6.text}"
