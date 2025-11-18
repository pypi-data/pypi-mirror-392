# Ontologia Edge Deployment Guide

This guide summarizes how to deploy the Edge ingestion stack in production with secure identity, reliable command delivery, and observability.

## 1. Core Services

- Ontologia API (FastAPI): start with `uvicorn ontologia_api.main:app --host 0.0.0.0 --port 8001`.
- Redis: required for dedup, command queues, and long-poll.

Environment variables (recommended):
- `REDIS_URL=redis://<host>:6379`
- `EDGE_SHARED_TOKEN=<edge-clients-shared-secret>`
- `EDGE_ADMIN_TOKEN=<admin-secret>`
- `EDGE_VERIFY_SIGNATURES=1` (enforce signature verification)
- `EDGE_SIG_ALGO=ed25519` (global default, nodes can negotiate their own)
- `EDGE_CMD_ACK_TIMEOUT=30`, `EDGE_CMD_MAX_RETRIES=3`, `EDGE_CMD_RETRY_INTERVAL=5`
- `EDGE_CMD_EXPIRES_SEC=<optional>` (expire queued commands)
- `EDGE_SYNC_TO_ONTOLOGY=1` (optional: sync nodes as objects)
- `EDGE_NODE_OBJECT_TYPE=edge_node` (object type used by sync)

## 2. Endpoints Summary

- Ingestion (token-protected):
  - `POST /v3/{ontology}/streams/edge/hello` — presence, capabilities, key
  - `POST /v3/{ontology}/streams/edge/state` — compact node state
  - `POST /v3/{ontology}/streams/edge/event` — ontological event (immutable)
- Commands (token-protected):
  - `POST /v3/{ontology}/streams/edge/commands` — enqueue
  - `GET  /v3/{ontology}/streams/edge/commands/pull?nodeId=...&waitSeconds=25` — long-poll fetch
  - `POST /v3/{ontology}/streams/edge/commands/ack` — acknowledge
- Admin (admin-token protected):
  - `POST /v3/{ontology}/streams/edge/nodes/{nodeId}/keys` — add key
  - `POST /v3/{ontology}/streams/edge/nodes/{nodeId}/keys/{keyId}/activate` — activate
  - `POST /v3/{ontology}/streams/edge/nodes/{nodeId}/keys/{keyId}/revoke` — revoke
  - `GET  /v3/{ontology}/streams/edge/nodes/{nodeId}/keys` — list keys
  - `GET  /v3/{ontology}/streams/edge/commands?nodeId=&status=&limit=` — list receipts
- Observability:
  - `GET /v3/{ontology}/streams/edge/metrics` — JSON snapshot
  - `GET /v3/{ontology}/streams/edge/dashboard` — simple HTML view
  - `GET /metrics` — Prometheus exposition (scrape from Prometheus)

## 3. Identity & Signatures

- Nodes generate and store private keys in hardware (ESP32 NVS or secure element).
- HELLO negotiates `capabilities.crypto.algo` (ed25519|ecdsa) and `canonical` (json|cbor).
- API verifies signatures using registered public keys (ed25519 via PyNaCl/cryptography; ECDSA via cryptography).


### cURL examples (ECDSA/JSON)

1) Generate keys (dev only):
```bash
python -c "from examples.edge.crypto_sign import ensure_keys; print(ensure_keys('/tmp/edge_key','ecdsa')[1])" > /tmp/pub.pem
```

2) HELLO payload signing (Python):
```python
from examples.edge.crypto_sign import ensure_keys, sign_canonical
import json, time, base64
algo, priv, pub = ensure_keys('/tmp/edge_key','ecdsa')
hello = {
  'type':'HELLO','msg_id':str(int(time.time()*1000)),'node_id':'node-1',
  'public_key': pub,'capabilities':{'level':'L1','crypto':{'algo':algo,'canonical':'json'}},
  'timestamp': int(time.time()), 'ttl': 30, 'nonce': str(int(time.time()*1000))
}
hello['signature'] = sign_canonical(hello, algo, priv, 'json')
print(json.dumps(hello))
```

3) Send HELLO:
```bash
curl -sS -X POST "$BASE/v3/$ONTO/streams/edge/hello" \
  -H "Content-Type: application/json" -H "X-Edge-Token: $EDGE_SHARED_TOKEN" \
  -d "$(python hello_sign.py)"
```

4) EVENT signing mirrors HELLO; sign canonical JSON without the `signature` field.

## 4. Docker Quickstart

Bring up a local stack (API + Redis + Prometheus + Grafana):

```bash
cd config/edge
docker compose up --build
```

Then:
- API: http://localhost:8001 (docs at /docs)
- Prometheus: http://localhost:9090 (scrapes /metrics)
- Grafana: http://localhost:3000 (admin/admin) with Edge dashboard pre-loaded

The compose file sets:
- `EDGE_SHARED_TOKEN=changeme`
- `EDGE_VERIFY_SIGNATURES=1`
- `REDIS_URL=redis://redis:6379`

To POST a signed HELLO against the containerized API (from host):

```bash
export BASE=http://localhost:8001
export ONTO=default
export EDGE_SHARED_TOKEN=changeme
python - <<'PY'
from examples.edge.crypto_sign import ensure_keys, sign_canonical
import json, time
algo, priv, pub = ensure_keys('/tmp/edge_key','ecdsa')
hello = {
  'type':'HELLO','msg_id':str(int(time.time()*1000)),'node_id':'node-1',
  'public_key': pub,'capabilities':{'level':'L1','crypto':{'algo':algo,'canonical':'json'}},
  'timestamp': int(time.time()), 'ttl': 30, 'nonce': str(int(time.time()*1000))
}
hello['signature'] = sign_canonical(hello, algo, priv, 'json')
print(json.dumps(hello))
PY
```

```bash
curl -sS -X POST "$BASE/v3/ontologies/$ONTO/streams/edge/hello" \
  -H "Content-Type: application/json" -H "X-Edge-Token: $EDGE_SHARED_TOKEN" \
  -d @<(python - <<'PY'
from examples.edge.crypto_sign import ensure_keys, sign_canonical
import json, time
algo, priv, pub = ensure_keys('/tmp/edge_key','ecdsa')
hello={'type':'HELLO','msg_id':str(int(time.time()*1000)),'node_id':'node-1','public_key':pub,'capabilities':{'level':'L1','crypto':{'algo':algo,'canonical':'json'}},'timestamp':int(time.time()),'ttl':30,'nonce':str(int(time.time()*1000))}
hello['signature']=sign_canonical(hello,algo,priv,'json')
print(json.dumps(hello))
PY)
```


## 4. Reliability

- Dedup: Redis SETNX + TTL (fallback SQL/in-memory) by `msg_id`.
- Command queue: Redis list per node, long-poll BLPOP.
- Receipts: SQL records — queued, delivered, acked; background retry loop re-enqueues after timeout; expiry policy.

## 5. Dashboards & Metrics

- Scrape `/metrics` from Prometheus; import the sample Grafana JSON at `docs/edge/grafana_dashboard.json`.
- Built-in HTML dashboard provides a lightweight live view for quick checks.

## 6. Reference Client

- MicroPython stub: `examples/edge/micropython_stub.py` (HELLO/EVENT/pull/ACK).
- For ESP32-IDF, start from `examples/edge/esp32_idf/README.md`.


## 5. Access Control (ACL) & Rate Limiting

### ACL for Enqueue (Per Node)

- By default, enqueue is open for all callers.
- To restrict, add principals to a node's ACL (admin token required):
  - List: `GET /v3/{ontology}/streams/edge/nodes/{nodeId}/acl`
  - Add: `POST /v3/{ontology}/streams/edge/nodes/{nodeId}/acl` with `{ "principal": "svc:ci" }`
  - Remove: `DELETE /v3/{ontology}/streams/edge/nodes/{nodeId}/acl/{principal}`
- Callers must send `X-Edge-Principal: <principal>` to be allowed when ACL exists.

### Rate Limits (defaults per node)

- HELLO: 5/minute — `EDGE_RL_HELLO_CAP`, `EDGE_RL_HELLO_WIN`
- STATE: 30/minute — `EDGE_RL_STATE_CAP`, `EDGE_RL_STATE_WIN`
- EVENT: 60/minute — `EDGE_RL_EVENT_CAP`, `EDGE_RL_EVENT_WIN`
- ENQUEUE: 30/minute — `EDGE_RL_ENQ_CAP`, `EDGE_RL_ENQ_WIN`
- PULL: 120/minute — `EDGE_RL_PULL_CAP`, `EDGE_RL_PULL_WIN`
- Backed by Redis sliding window; falls back to in-memory in single-instance mode.
