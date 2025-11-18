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


def _seed_action(
    client: TestClient, api_name: str, *, executor_key: str, rule_logic: str | None = None
):
    payload = {
        "displayName": api_name,
        "description": None,
        "targetObjectType": "expense",
        "parameters": {
            "message": {"dataType": "string", "displayName": "Message", "required": True}
        },
        "submissionCriteria": [],
        "validationRules": (
            [{"description": "rule", "ruleLogic": rule_logic}] if rule_logic is not None else []
        ),
        "executorKey": executor_key,
    }
    r = client.put(f"/v2/ontologies/default/actionTypes/{api_name}", json=payload)
    assert r.status_code == 200, r.text


def test_execute_missing_required_param_returns_400(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e1", "PENDING")
    _seed_action(client, "approve_expense", executor_key="system.log_message_test")

    r = client.post(
        "/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute",
        json={"parameters": {}},
    )
    assert r.status_code == 400, r.text


def test_execute_with_unknown_executor_returns_501(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e2", "PENDING")
    _seed_action(client, "ghost_action", executor_key="system.unknown")

    r = client.post(
        "/v2/ontologies/default/objects/expense/e2/actions/ghost_action/execute",
        json={"parameters": {"message": "hi"}},
    )
    assert r.status_code == 501, r.text


def test_execute_validation_rule_failure_returns_400(client: TestClient, session):
    _put_expense_object_type(client)
    _put_expense(client, "e3", "PENDING")
    _seed_action(
        client,
        "validate_msg_ok",
        executor_key="system.log_message_test",
        rule_logic="params['message'] == 'ok'",
    )

    r = client.post(
        "/v2/ontologies/default/objects/expense/e3/actions/validate_msg_ok/execute",
        json={"parameters": {"message": "nope"}},
    )
    assert r.status_code == 400, r.text
