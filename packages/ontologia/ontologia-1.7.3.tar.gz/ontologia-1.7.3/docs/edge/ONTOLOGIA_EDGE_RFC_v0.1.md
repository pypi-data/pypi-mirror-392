# Ontologia Edge RFC v0.1

Purpose: formalize the EdgeNode philosophy, message types, and a minimal contract for integrating edge devices (ESP32 or simulators) with the Ontologia core.

## 1. Philosophy

- Everything Is a Node: People, devices, sensors, places, processes — all as nodes with relationships and properties.
- Events Are Immutable: The network carries observations (EVENT). State is derived locally (STATE snapshots are summaries, not truth).
- Semantics First: Payloads are semantically structured; transport is pluggable (JSON/CBOR/Protobuf, Wi‑Fi/ESP‑NOW/MQTT/HTTP/WS).
- Graduated Autonomy: L0 (measure), L1 (semantic measure), L2 (local agent rules).
- Eventual Convergence: Mesh is imperfect; deduplication and TTL are mandatory.
- Strong Identity: Node identity = public key. Messages are signed.
- First‑Person Perspective: origin=node_id; “I observed…”

## 2. Roles & Responsibilities

- Core (Python): global graph, semantic fusion, AI/planning, durable storage, APIs.
- EdgeNode (ESP32/Sim): local perception & actuation, identity, simple rules, Ontologia Edge protocol.

## 3. Capability Levels

- L0 – Sensor: emits raw `sensor_value` style EVENTs.
- L1 – Semantic Sensor: converts readings to concepts (e.g., comfort/cold), emits semantic EVENTs; basic actuation.
- L2 – Edge Agent: local rule engine; operates degraded without core; peer‑to‑peer commands.

Each EdgeNode declares a level at boot in HELLO.capabilities.level.

## 4. Local Node State (minimal)

NodeState:
- node_id, public_key
- neighbors (mesh view), capabilities (sensors/actuators, level)
- facts_local (small set of assertions)
- config (thresholds/modes)

Persistence: compact key/value (CBOR/JSON/NVS/flash/SQLite). Rebuild state from local store + recent events.

## 5. Message Types (semantic)

- HELLO: presence + capabilities + key. Used for discovery and liveness.
- STATE: compact summary of local state for debugging/recovery.
- EVENT: immutable observation (primary stream).
- COMMAND: instruction to an edge node/actuator.
- ACK/ERROR: control feedback.

Required cross‑cutting fields per message:
- node_id (derived from public key), timestamp, nonce, signature
- msg_id (ULID) for deduplication; ttl for routing loops

JSON Schemas live at `docs/edge/schemas`.

## 6. Security & Identity

- On first boot, generate ECC (or Ed25519) keypair on device; store securely.
- node_id = ULID(public_key || device_seed) or hash of public key.
- All payloads include a detached signature covering canonical bytes (e.g., sorted JSON or CBOR Canonical).
- Core MUST verify signature using the registered public key for the node.

## 7. Transport Guidelines

- Mesh is transport‑agnostic. Start with HTTP/WS or UDP for core; ESP‑NOW for local broadcast.
- Always include `ttl` and `msg_id` for loop prevention/dedup.

## 8. Core Integration (current repo mapping)

- ontologia/edge: EdgeRuntime, SensorFusionEngine, SensorDetection, EntityStateStore.
- packages/ontologia_edge: EntityEvent (append‑only), EntityJournal backends, EntityManager, runtime helpers.
- Domain events bus: ontologia.domain.events (InMemory/InProcess/Kafka).

Fit:
- EVENT ↔ ontologia_edge.journal.EntityEvent (object_type, components, provenance, metadata, timestamps).
- Fusion ↔ ontologia.edge.fusion.SensorFusionEngine produces EntityEvent and publishes RuntimeEntityUpserted.
- COMMAND ↔ ontologia.edge.sdk.EdgeCommand (actuator execution).

Gaps to implement:
- Signed messages + public key registry (core verification middleware).
- HELLO/STATE endpoints and storage of capabilities/liveness.
- Optional peer‑to‑peer (mesh) dedup/ttl handling.

## 9. Minimal Contract (v0.1)

- Implement HELLO/STATE/EVENT schemas (docs/edge/schemas).
- Simulate edge behavior in Python (examples/edge/edge_node_sim.py) using EdgeRuntime.
- Defer hardware firmware; validate protocol in simulation.

## 10. Roadmap (phased)

0. Manifest + schemas (this RFC)
1. Python simulator and local fusion (done via EdgeRuntime)
2. Core API stubs: POST /edge/hello, POST /edge/state, POST /edge/event (signature verify placeholder)
3. Identity: public key registry + signature verification
4. Key rotation: admin endpoints for add/activate/revoke keys; multiple keys per node
5. Canonicalization: JSON canonical (default) + CBOR canonical (negotiated per request via `canonical` or header)
6. L1 semantics: threshold rules on device; EVENT semantics
7. L2 agent: local rules + peer COMMAND
