from fastapi.testclient import TestClient


def _put_expense_object_type(client: TestClient):
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
    )
    assert r.status_code == 200, r.text


def _put_expense(client: TestClient, pk: str, status: str):
    r = client.put(
        f"/v2/ontologies/default/objects/expense/{pk}",
        json={"properties": {"id": pk, "status": status}},
    )
    assert r.status_code == 200, r.text


def _seed_action(client: TestClient):
    r = client.put(
        "/v2/ontologies/default/actionTypes/approve_expense",
        json={
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
            "executorKey": "system.log_message",
        },
    )
    assert r.status_code == 200, r.text


def test_actions_discovery_and_execute(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(client)

    # Discover
    r = client.get("/v2/ontologies/default/objects/expense/e1/actions")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert [a["apiName"] for a in data] == ["approve_expense"]

    # Execute
    r2 = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute",
        json={"parameters": {"message": "approved"}},
    )
    assert r2.status_code == 200, r2.text
    payload = r2.json()
    assert payload.get("status") == "success"
    assert payload.get("message") == "approved"


def test_actions_unavailable_when_criteria_fail(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e2", "DRAFT")
    _seed_action(client)

    # Discover: none
    r = client.get("/v2/ontologies/default/objects/expense/e2/actions")
    assert r.status_code == 200, r.text
    assert r.json()["data"] == []

    # Execute: 403
    r2 = client.post(
        "/v2/ontologies/default/objects/expense/e2/actions/approve_expense/execute",
        json={"parameters": {"message": "nope"}},
    )
    assert r2.status_code == 403
