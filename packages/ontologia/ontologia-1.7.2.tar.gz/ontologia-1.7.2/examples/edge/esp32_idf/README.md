# ESP32-IDF EdgeNode Skeleton

This reference shows how to implement Ontologia EdgeNode on ESP-IDF (ESP32/ESP32-C6).

Features:
- Generate device keypair (Ed25519 recommended)
- HELLO with capabilities and crypto negotiation (algo + canonical)
- EVENT (temperature, button) and STATE (local snapshot)
- Command pull + ACK loop (HTTP long-poll)

## Steps

1) Create ESP-IDF project and add components: `mbedtls`, `esp_http_client`, `json` (cJSON or jsmn), `ed25519` (third-party or mbedtls if available).
2) On first boot, generate/store keypair in NVS; expose the public key.
3) Implement `http_post_json(url, payload, headers)` and `http_get(url, headers)` wrappers.
4) Build HELLO payload:
```
{
  "type": "HELLO",
  "msg_id": "<ulid>",
  "node_id": "esp32-...",
  "public_key": "<PEM or base64>",
  "capabilities": {
    "level": "L1",
    "sensors": ["temp"],
    "actuators": ["led"],
    "transports": ["http"],
    "crypto": {"algo": "ed25519", "canonical": "json"}
  },
  "timestamp": 1731700000,
  "ttl": 30,
  "nonce": "<ulid>",
  "signature": "<sign(canonical_json_without_signature)>"
}
```
5) Periodically post EVENTs and a STATE snapshot; include `X-Edge-Token` header.
6) Start a long-poll GET to `/v3/{ontology}/streams/edge/commands/pull?nodeId=<id>&waitSeconds=25`; on response, execute commands and POST ACK with command IDs.

See `examples/edge/micropython_stub.py` for a compact, working reference.
