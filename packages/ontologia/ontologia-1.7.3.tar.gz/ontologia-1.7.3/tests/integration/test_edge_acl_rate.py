import os
import time

import pytest
from fastapi.testclient import TestClient
from ontologia_api.main import app


@pytest.mark.integration
def test_rate_limit_event_and_acl_enqueue():
    # Configure strict limits for the test
    os.environ["EDGE_VERIFY_SIGNATURES"] = "0"  # disable crypto to focus on rate/acl
    os.environ["EDGE_RL_EVENT_CAP"] = "1"
    os.environ["EDGE_RL_EVENT_WIN"] = "60"
    os.environ["EDGE_RL_ENQ_CAP"] = "1"
    os.environ["EDGE_RL_ENQ_WIN"] = "60"
    os.environ["EDGE_SHARED_TOKEN"] = "test-token"

    client = TestClient(app)
    headers = {"X-Edge-Token": "test-token"}
    base = "/v3/ontologies/default/streams/edge"

    # Post two EVENTs quickly; second should 429
    evt = {
        "type": "EVENT",
        "msg_id": "e1",
        "node_id": "node-rl",
        "ont_type": "temperature",
        "subject": "node-rl:room",
        "predicate": "has_temp",
        "object": 22.0,
        "timestamp": int(time.time()),
        "ttl": 30,
        "nonce": "n1",
        "signature": "-",
    }
    r1 = client.post(base + "/event", json=evt, headers=headers)
    assert r1.status_code == 200
    evt["msg_id"] = "e2"
    r2 = client.post(base + "/event", json=evt, headers=headers)
    assert r2.status_code == 429

    # ACL tests for enqueue: add ACL for svc:ci and ensure no-other principal is blocked
    admin_headers = {"X-Edge-Admin-Token": "admin"}
    os.environ["EDGE_ADMIN_TOKEN"] = "admin"
    racl = client.post(
        "/v3/ontologies/default/streams/edge/nodes/node-rl/acl",
        json={"principal": "svc:ci"},
        headers=admin_headers,
    )
    assert racl.status_code == 200

    # Enqueue without principal -> 403
    cmd = {"nodeId": "node-rl", "target": "led", "action": "on", "payload": {}}
    r3 = client.post(base + "/commands", json=cmd, headers=headers)
    assert r3.status_code == 403

    # Enqueue with allowed principal -> 200 (first)
    headers_princ = {**headers, "X-Edge-Principal": "svc:ci"}
    r4 = client.post(base + "/commands", json=cmd, headers=headers_princ)
    assert r4.status_code == 200

    # Enqueue again (rate limited at 1/min) -> 429
    r5 = client.post(base + "/commands", json=cmd, headers=headers_princ)
    assert r5.status_code == 429
