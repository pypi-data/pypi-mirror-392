# MicroPython EdgeNode stub demonstrating HELLO negotiation, EVENT/STATE, command pull, and ACK
# Note: This file is illustrative. Adjust imports (urequests/urequests2) based on your firmware.

import json
import os
import time

try:
    import urequests as requests  # MicroPython
except ImportError:  # CPython dev fallback
    import requests  # type: ignore


EDGE_TOKEN = os.getenv("EDGE_TOKEN") or "changeme"  # same as EDGE_SHARED_TOKEN on server
BASE = os.getenv("EDGE_BASE_URL") or "http://localhost:8001/v3/ontologies/default/streams"
NODE_ID = os.getenv("EDGE_NODE_ID") or "esp32-mpy-01"
ALGO = os.getenv("EDGE_SIG_ALGO") or "ecdsa"
KEY_PATH = os.getenv("EDGE_KEY_PATH") or "/tmp/edge_node_key"  # adjust for MicroPython FS

try:
    from .crypto_sign import ensure_keys, sign_canonical
except Exception:
    # Allow running when imported as script in CPython (same directory)
    from crypto_sign import ensure_keys, sign_canonical  # type: ignore


def _headers():
    return {"Content-Type": "application/json", "X-Edge-Token": EDGE_TOKEN}


def hello():
    algo, priv, pub = ensure_keys(KEY_PATH, ALGO)
    payload = {
        "type": "HELLO",
        "msg_id": str(int(time.time() * 1000)),
        "node_id": NODE_ID,
        "public_key": pub,  # PEM for ECDSA
        "capabilities": {
            "level": "L1",
            "sensors": ["temp"],
            "actuators": ["led"],
            "transports": ["http"],
            "crypto": {"algo": algo, "canonical": "json"},
        },
        "software": {"fw": "mpy-0.1"},
        "timestamp": int(time.time()),
        "ttl": 30,
        "nonce": str(int(time.time() * 1000)),
    }
    payload["signature"] = sign_canonical(payload, algo, priv, canonical="json")
    r = requests.post(BASE + "/edge/hello", data=json.dumps(payload), headers=_headers())
    try:
        return r.json()
    finally:
        r.close()


def emit_temp(value: float):
    algo, priv, pub = ensure_keys(KEY_PATH, ALGO)
    payload = {
        "type": "EVENT",
        "msg_id": str(int(time.time() * 1000)),
        "node_id": NODE_ID,
        "ont_type": "temperature",
        "subject": NODE_ID + ":room",
        "predicate": "has_temp",
        "object": value,
        "unit": "C",
        "components": {"reading": {"value": value, "unit": "C"}},
        "timestamp": int(time.time()),
        "ttl": 30,
        "nonce": str(int(time.time() * 1000)),
    }
    payload["signature"] = sign_canonical(payload, algo, priv, canonical="json")
    r = requests.post(BASE + "/edge/event", data=json.dumps(payload), headers=_headers())
    try:
        return r.json()
    finally:
        r.close()


def pull_commands(wait=25):
    r = requests.get(
        BASE + "/edge/commands/pull?nodeId=" + NODE_ID + "&waitSeconds=" + str(wait),
        headers=_headers(),
    )
    try:
        return r.json()
    finally:
        r.close()


def ack(ids):
    payload = {"nodeId": NODE_ID, "ids": ids}
    r = requests.post(BASE + "/edge/commands/ack", data=json.dumps(payload), headers=_headers())
    try:
        return r.json()
    finally:
        r.close()


def main():
    print("HELLO:", hello())
    print("EVENT:", emit_temp(26.8))
    while True:
        cmds = pull_commands(25) or []
        if cmds:
            print("Commands:", cmds)
            # Simulate execution then ACK
            ids = [c.get("id") for c in cmds if c.get("id")]
            if ids:
                print("ACK:", ack(ids))
        time.sleep(1)


if __name__ == "__main__":
    main()
