import os
import time

import pytest
from fastapi.testclient import TestClient
from ontologia_api.main import app


def _setup_env():
    os.environ["EDGE_SHARED_TOKEN"] = "test-token"
    os.environ["EDGE_VERIFY_SIGNATURES"] = "1"
    # Avoid Redis dependency for tests; dedup and presence will fallback
    os.environ.pop("REDIS_URL", None)


def _sign_hello(node_id: str, algo: str = "ed25519") -> dict:
    from examples.edge.crypto_sign import ensure_keys, sign_canonical

    msg = {
        "type": "HELLO",
        "msg_id": str(int(time.time() * 1000)),
        "node_id": node_id,
        "public_key": None,  # filled below
        "capabilities": {
            "level": "L1",
            "crypto": {"algo": algo, "canonical": "json"},
        },
        "timestamp": int(time.time()),
        "ttl": 30,
        "nonce": str(int(time.time() * 1000)),
    }
    algo, priv, pub = ensure_keys("/tmp/e2e_edge_key", algo)
    msg["public_key"] = pub
    msg["signature"] = sign_canonical(msg, algo, priv, canonical="json")
    return msg


def _sign_event(node_id: str, algo: str = "ed25519") -> dict:
    from examples.edge.crypto_sign import ensure_keys, sign_canonical

    msg = {
        "type": "EVENT",
        "msg_id": str(int(time.time() * 1000)),
        "node_id": node_id,
        "ont_type": "temperature",
        "subject": f"{node_id}:room",
        "predicate": "has_temp",
        "object": 23.5,
        "unit": "C",
        "components": {"reading": {"value": 23.5, "unit": "C"}},
        "timestamp": int(time.time()),
        "ttl": 30,
        "nonce": str(int(time.time() * 1000)),
    }
    algo, priv, pub = ensure_keys("/tmp/e2e_edge_key", algo)
    msg["signature"] = sign_canonical(msg, algo, priv, canonical="json")
    return msg


@pytest.mark.integration
def test_edge_e2e_signed_hello_and_event():
    _setup_env()
    client = TestClient(app)
    headers = {"X-Edge-Token": "test-token"}
    base = "/v3/ontologies/default/streams/edge"

    # Signed HELLO
    hello = _sign_hello("test-node-1", algo="ed25519")
    r = client.post(base + "/hello", json=hello, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "ok"

    # Duplicate HELLO (same msg_id)
    r2 = client.post(base + "/hello", json=hello, headers=headers)
    assert r2.status_code == 200
    assert r2.json().get("status") in {"duplicate", "ok"}

    # Signed EVENT
    event = _sign_event("test-node-1", algo="ed25519")
    r3 = client.post(base + "/event", json=event, headers=headers)
    assert r3.status_code == 200, r3.text
    assert r3.json().get("status") == "ok"

    # Realtime events list (sanity)
    r4 = client.get("/v3/ontologies/default/streams/realtime/events")
    assert r4.status_code == 200
    assert isinstance(r4.json(), list)
