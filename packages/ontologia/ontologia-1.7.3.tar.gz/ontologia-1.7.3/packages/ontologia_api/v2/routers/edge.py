from __future__ import annotations

import logging
from datetime import timedelta
from time import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from ontologia_edge.entity_manager import EntityManager
from sqlmodel import Session, select

from ontologia_api.core.database import get_session
from ontologia_api.core.edge_auth import require_edge_admin, require_edge_token
from ontologia_api.core.edge_canonical import canonicalize
from ontologia_api.core.edge_commands import (
    EnqueuedCommand,
    get_command_queue,
    new_command_id,
)
from ontologia_api.core.edge_dedup import get_dedup_backend
from ontologia_api.core.edge_metrics import (
    edge_acl_denied_total,
    edge_commands_acked_total,
    edge_commands_enqueued_total,
    edge_event_total,
    edge_hello_total,
    edge_rate_limit_rejections_total,
    edge_signature_failures_total,
    edge_state_total,
)
from ontologia_api.core.edge_models import EdgeEvent, EdgeHello, EdgeState
from ontologia_api.core.edge_presence import get_presence_backend
from ontologia_api.core.edge_ratelimit import rate_limit
from ontologia_api.core.edge_security import (
    InMemoryDedupStore,
    SignatureVerifier,
)
from ontologia_api.dependencies.realtime import get_entity_manager
from ontologia_api.models.edge_models_sql import EdgeNode, EdgeNodeState
from ontologia_api.repositories.edge_acl_repository import (
    is_allowed as acl_is_allowed,
)
from ontologia_api.repositories.edge_acl_repository import (
    list_acl as acl_list,
)
from ontologia_api.repositories.edge_acl_repository import (
    remove_acl as acl_remove,
)
from ontologia_api.repositories.edge_acl_repository import (
    upsert_acl as acl_upsert,
)
from ontologia_api.repositories.edge_commands_repository import (
    list_commands as repo_list_commands,
)
from ontologia_api.repositories.edge_commands_repository import (
    record_acked,
    record_delivered,
    record_enqueued,
)
from ontologia_api.repositories.edge_repository import (
    ensure_message_not_seen,
    get_public_key,
    save_edge_state,
    upsert_edge_node,
)

router = APIRouter(tags=["Edge"])
logger = logging.getLogger(__name__)

_dedup = InMemoryDedupStore()  # local fallback
_redis_dedup = get_dedup_backend()
_verifier = SignatureVerifier()


def _canonical_bytes(payload: dict[str, Any], *, mode: str | None) -> bytes:
    return canonicalize(payload, mode=(mode or "json"))


@router.post(
    "/edge/hello", summary="Edge presence announcement", dependencies=[Depends(require_edge_token)]
)
async def edge_hello(
    ontologyApiName: str,
    message: EdgeHello,
    session=Depends(get_session),
    canonical: str | None = None,
):
    # Rate limit per node or IP
    key = f"hello:{message.node_id}"
    if not await rate_limit(key, prefix="HELLO", default_capacity=5, default_window=60):
        edge_rate_limit_rejections_total.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    # SQL dedup (preferred)
    # Prefer Redis dedup if available
    try:
        if not await _redis_dedup.is_new(message.msg_id, node_id=message.node_id, ttl=message.ttl):
            return {"status": "duplicate", "msgId": message.msg_id}
    except Exception:
        try:
            is_new = ensure_message_not_seen(
                session, msg_id=message.msg_id, node_id=message.node_id, ttl=message.ttl
            )
            if not is_new:
                return {"status": "duplicate", "msgId": message.msg_id}
        except Exception:
            if await _dedup.seen(message.msg_id):
                return {"status": "duplicate", "msgId": message.msg_id}
            await _dedup.remember(message.msg_id, message.ttl)

    # Persist/update node presence and capabilities
    try:
        upsert_edge_node(
            session,
            node_id=message.node_id,
            public_key=message.public_key,
            capabilities=message.capabilities,
            software=message.software,
            hw=message.hw,
        )
    except Exception:
        logger.exception("Failed to upsert edge node")

    # Derive canonical mode from capabilities if not provided
    if canonical is None:
        caps = message.capabilities or {}
        crypto = caps.get("crypto") or caps.get("sig") or {}
        if isinstance(crypto, dict):
            cand = crypto.get("canonical") or crypto.get("mode")
            if isinstance(cand, str) and cand:
                canonical = cand

    # Optionally bootstrap EdgeNode ObjectType and upsert instance into ontology
    import os as _os

    if _os.getenv("EDGE_SYNC_TO_ONTOLOGY", "0") in {"1", "true", "True"}:
        try:
            from ontologia_api.services.metamodel_service import MetamodelService as _MetaSvc
            from ontologia_api.v2.schemas.metamodel import (
                ObjectTypePutRequest as _OTReq,
            )
            from ontologia_api.v2.schemas.metamodel import (
                PropertyDefinition as _Prop,
            )

            _ot_name = _os.getenv("EDGE_NODE_OBJECT_TYPE", "edge_node")
            _m = _MetaSvc(session, service="ontology", instance=ontologyApiName)
            try:
                _m.get_object_type(_ot_name)
            except Exception:
                # Create minimal type if missing
                _req = _OTReq(
                    displayName="Edge Node",
                    primaryKey="id",
                    properties={
                        "id": _Prop(dataType="string", displayName="ID", required=True),
                        "public_key": _Prop(dataType="string", displayName="Public Key"),
                        "level": _Prop(dataType="string", displayName="Level"),
                        "sig_algo": _Prop(dataType="string", displayName="Signature Algorithm"),
                        "canonical_mode": _Prop(dataType="string", displayName="Canonical Mode"),
                        "last_seen": _Prop(dataType="timestamp", displayName="Last Seen"),
                    },
                )
                _m.upsert_object_type(_ot_name, _req)
            # Upsert instance with selected properties
            from ontologia_api.services.instances_service import InstancesService as _InstSvc

            _i = _InstSvc(session, service="ontology", instance=ontologyApiName)
            _props = {
                "id": message.node_id,
                "public_key": message.public_key,
                "level": (message.capabilities or {}).get("level"),
                "sig_algo": (
                    ((message.capabilities or {}).get("crypto") or {}).get("algo")
                    if isinstance((message.capabilities or {}).get("crypto"), dict)
                    else (message.capabilities or {}).get("sigAlgo")
                ),
                "canonical_mode": (
                    ((message.capabilities or {}).get("crypto") or {}).get("canonical")
                    if isinstance((message.capabilities or {}).get("crypto"), dict)
                    else (message.capabilities or {}).get("canonical")
                ),
                "last_seen": message.timestamp,
            }
            _i.upsert_object(_ot_name, message.node_id, body={"properties": _props})
        except Exception:
            logger.exception("Failed to sync edge node to ontology")

    # Register key in verifier and (optionally) verify signature
    await _verifier.ensure_key(message.node_id, message.public_key)
    ok = await _verifier.verify(
        message.node_id,
        _canonical_bytes(message.model_dump(mode="json"), mode=canonical),
        message.signature,
        algo=(
            ((message.capabilities or {}).get("crypto") or {}).get("algo")
            if isinstance((message.capabilities or {}).get("crypto"), dict)
            else (message.capabilities or {}).get("sigAlgo")
        ),
    )
    if not ok:
        edge_signature_failures_total.inc()
        edge_signature_failures_total.inc()
        edge_signature_failures_total.inc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # Presence backend (Redis if configured)
    try:
        backend = get_presence_backend()
        await backend.upsert(
            message.node_id,
            {
                "capabilities": message.capabilities,
                "software": message.software or {},
                "hw": message.hw or {},
            },
            ttl=message.ttl,
        )
    except Exception:
        logger.exception("Presence backend upsert failed")

    logger.info(
        "HELLO from %s level=%s sensors=%s actuators=%s",
        message.node_id,
        (message.capabilities or {}).get("level"),
        (message.capabilities or {}).get("sensors"),
        (message.capabilities or {}).get("actuators"),
    )
    edge_hello_total.inc()

    # Optional: sync to ontology object instance
    import os

    if os.getenv("EDGE_SYNC_TO_ONTOLOGY", "0") in {"1", "true", "True"}:
        try:
            from ontologia_api.services.instances_service import InstancesService

            ot_name = os.getenv("EDGE_NODE_OBJECT_TYPE", "edge_node")
            svc = InstancesService(session, service="ontology", instance=ontologyApiName)
            # Upsert minimal object (id only if schema not present)
            svc.upsert_object(
                ot_name, message.node_id, body={"properties": {"id": message.node_id}}
            )
        except Exception:
            logger.exception("Failed to sync edge node object")
    return {"status": "ok", "nodeId": message.node_id}


@router.post(
    "/edge/state", summary="Edge local state snapshot", dependencies=[Depends(require_edge_token)]
)
async def edge_state(
    ontologyApiName: str,
    message: EdgeState,
    session=Depends(get_session),
    canonical: str | None = None,
):
    if not await rate_limit(
        f"state:{message.node_id}", prefix="STATE", default_capacity=30, default_window=60
    ):
        edge_rate_limit_rejections_total.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    try:
        if not await _redis_dedup.is_new(message.msg_id, node_id=message.node_id, ttl=message.ttl):
            return {"status": "duplicate", "msgId": message.msg_id}
    except Exception:
        try:
            is_new = ensure_message_not_seen(
                session, msg_id=message.msg_id, node_id=message.node_id, ttl=message.ttl
            )
            if not is_new:
                return {"status": "duplicate", "msgId": message.msg_id}
        except Exception:
            if await _dedup.seen(message.msg_id):
                return {"status": "duplicate", "msgId": message.msg_id}
            await _dedup.remember(message.msg_id, message.ttl)

    # Use node's negotiated canonical mode if not provided
    if canonical is None:
        node = session.get(EdgeNode, message.node_id)
        if node and node.canonical_mode:
            canonical = node.canonical_mode

    ok = await _verifier.verify(
        message.node_id,
        _canonical_bytes(message.model_dump(mode="json"), mode=canonical),
        message.signature,
        algo=(
            session.get(EdgeNode, message.node_id).sig_algo
            if session.get(EdgeNode, message.node_id)
            else None
        ),
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # Persist latest state for observability
    try:
        save_edge_state(session, node_id=message.node_id, payload=message.state)
    except Exception:
        logger.exception("Failed to persist edge state")
    logger.info("STATE from %s keys=%s", message.node_id, sorted(message.state.keys()))
    edge_state_total.inc()
    return {"status": "ok", "nodeId": message.node_id}


@router.post(
    "/edge/event",
    summary="Ingest ontological EVENT into real-time manager",
    dependencies=[Depends(require_edge_token)],
)
async def edge_event(
    ontologyApiName: str,
    message: EdgeEvent,
    manager: EntityManager = Depends(get_entity_manager),
    session=Depends(get_session),
    canonical: str | None = None,
):
    if not await rate_limit(
        f"event:{message.node_id}", prefix="EVENT", default_capacity=60, default_window=60
    ):
        edge_rate_limit_rejections_total.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    try:
        if not await _redis_dedup.is_new(message.msg_id, node_id=message.node_id, ttl=message.ttl):
            return {"status": "duplicate", "msgId": message.msg_id}
    except Exception:
        try:
            is_new = ensure_message_not_seen(
                session, msg_id=message.msg_id, node_id=message.node_id, ttl=message.ttl
            )
            if not is_new:
                return {"status": "duplicate", "msgId": message.msg_id}
        except Exception:
            if await _dedup.seen(message.msg_id):
                return {"status": "duplicate", "msgId": message.msg_id}
            await _dedup.remember(message.msg_id, message.ttl)

    # Load key from DB if present to prime verifier
    try:
        key = get_public_key(session, message.node_id)
        if key:
            await _verifier.ensure_key(message.node_id, key)
    except Exception:
        logger.exception("Failed to load public key for node %s", message.node_id)

    # Use negotiated canonical mode if param missing
    if canonical is None:
        node = session.get(EdgeNode, message.node_id)
        if node and node.canonical_mode:
            canonical = node.canonical_mode

    ok = await _verifier.verify(
        message.node_id,
        _canonical_bytes(message.model_dump(mode="json"), mode=canonical),
        message.signature,
        algo=(
            session.get(EdgeNode, message.node_id).sig_algo
            if session.get(EdgeNode, message.node_id)
            else None
        ),
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    # Map EVENT → EntityManager.upsert
    # Heuristic: subject becomes entity_id; ont_type → object_type; provenance=node_id
    entity_id = message.subject if message.subject else f"{message.node_id}:{message.ont_type}"
    object_type = message.ont_type
    ttl_seconds = message.ttl if message.ttl and message.ttl > 0 else 30
    components = message.to_components()
    metadata = dict(message.metadata or {})
    metadata.update(
        {
            "predicate": message.predicate,
            "unit": message.unit,
            "origin": message.node_id,
            "msg_id": message.msg_id,
        }
    )

    snapshot = await manager.upsert(
        entity_id,
        object_type=object_type,
        provenance=message.node_id,
        ttl=timedelta(seconds=ttl_seconds),
        components=components,
        metadata=metadata,
    )
    edge_event_total.inc()
    return {
        "status": "ok",
        "entityId": snapshot.entity_id,
        "objectType": snapshot.object_type,
        "expiresAt": snapshot.expires_at,
        "updatedAt": snapshot.updated_at,
    }


# --- Key management (admin) ---
from pydantic import BaseModel

from ontologia_api.repositories.edge_repository import (
    activate_edge_key,
    add_edge_key,
    list_edge_keys,
    revoke_edge_key,
)


class _KeyCreate(BaseModel):
    public_key: str
    make_active: bool = True


@router.post(
    "/edge/nodes/{nodeId}/keys",
    summary="Add a public key for node (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def add_node_key(
    ontologyApiName: str, nodeId: str, payload: _KeyCreate, session: Session = Depends(get_session)
):
    rec = add_edge_key(
        session, node_id=nodeId, public_key=payload.public_key, make_active=payload.make_active
    )
    return {
        "keyId": rec.key_id,
        "active": rec.active,
        "createdAt": rec.created_at,
        "revokedAt": rec.revoked_at,
    }


@router.post(
    "/edge/nodes/{nodeId}/keys/{keyId}/activate",
    summary="Activate a key (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def activate_node_key(
    ontologyApiName: str, nodeId: str, keyId: str, session: Session = Depends(get_session)
):
    rec = activate_edge_key(session, node_id=nodeId, key_id=keyId)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    return {"keyId": rec.key_id, "active": rec.active}


@router.post(
    "/edge/nodes/{nodeId}/keys/{keyId}/revoke",
    summary="Revoke a key (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def revoke_node_key(
    ontologyApiName: str, nodeId: str, keyId: str, session: Session = Depends(get_session)
):
    rec = revoke_edge_key(session, node_id=nodeId, key_id=keyId)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    return {"keyId": rec.key_id, "active": rec.active, "revokedAt": rec.revoked_at}


@router.get(
    "/edge/nodes/{nodeId}/keys",
    summary="List node keys (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def list_node_keys(
    ontologyApiName: str, nodeId: str, session: Session = Depends(get_session)
):
    rows = list_edge_keys(session, node_id=nodeId)
    try:
        record_delivered(session, [it.key_id for it in rows])
    except Exception:
        logger.exception("Failed to persist command (delivered)")
    return [
        {
            "keyId": r.key_id,
            "active": r.active,
            "revokedAt": r.revoked_at,
            "createdAt": r.created_at,
        }
        for r in rows
    ]


@router.get("/edge/nodes", summary="List registered edge nodes")
async def list_edge_nodes(ontologyApiName: str, session: Session = Depends(get_session)):
    nodes = session.exec(select(EdgeNode)).all()
    return [
        {
            "nodeId": n.node_id,
            "level": n.level,
            "sensors": n.sensors,
            "actuators": n.actuators,
            "transports": n.transports,
            "lastSeen": n.last_seen,
        }
        for n in nodes
    ]


@router.get("/edge/metrics", summary="Edge metrics (JSON)")
async def edge_metrics(session: Session = Depends(get_session)):
    total_nodes = session.exec(select(EdgeNode)).all()
    total = len(total_nodes)
    import datetime
    from datetime import UTC

    now = datetime.datetime.now(UTC)
    stale = [n for n in total_nodes if (now - n.last_seen).total_seconds() > 60]

    from ontologia_api.models.edge_commands_sql import CommandReceipt

    receipts = session.exec(select(CommandReceipt)).all()
    by_status: dict[str, int] = {}
    for r in receipts:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    return {
        "nodes": {
            "total": total,
            "stale60s": len(stale),
        },
        "commands": by_status,
    }


@router.get("/edge/dashboard", response_class=HTMLResponse, summary="Simple Edge dashboard")
async def edge_dashboard(ontologyApiName: str):
    # Inline HTML/JS that calls the API endpoints to render live view
    return HTMLResponse(
        r"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Ontologia Edge Dashboard</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 20px; }
      h1 { margin-bottom: 0; }
      .meta { color: #666; margin-top: 4px; }
      .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
      .card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
      table { width: 100%; border-collapse: collapse; }
      th, td { padding: 6px; border-bottom: 1px solid #eee; text-align: left; }
      .status { font-size: 12px; padding: 2px 6px; border-radius: 4px; }
      .queued { background: #eef; }
      .delivered { background: #efe; }
      .acked { background: #efe; }
      .failed, .expired { background: #fee; }
      .pill { display: inline-block; background: #f6f6f6; padding: 2px 8px; border-radius: 999px; margin-right: 6px; font-size: 12px; }
    </style>
  </head>
  <body>
    <h1>Ontologia Edge</h1>
    <div class="meta">Live overview for ontology: <strong id="onto"></strong></div>

    <div class="grid">
      <div class="card">
        <h3>Metrics</h3>
        <div id="metrics">Loading…</div>
      </div>
      <div class="card">
        <h3>Commands (latest)</h3>
        <div id="commands">Loading…</div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h3>Nodes</h3>
      <div id="nodes">Loading…</div>
    </div>

    <script>
      const onto = document.getElementById('onto');
      onto.textContent = decodeURIComponent(window.location.pathname.split('/')[3] || 'default');

      async function fetchJSON(path) {
        const res = await fetch(path);
        return await res.json();
      }

      function renderMetrics(m) {
        const el = document.getElementById('metrics');
        const pills = Object.entries(m.commands || {}).map(([k,v]) => `<span class="pill">${k}: ${v}</span>`).join(' ');
        el.innerHTML = `
          <div>Nodes total: <strong>${m.nodes.total}</strong> · stale(>60s): <strong>${m.nodes.stale60s}</strong></div>
          <div style="margin-top:8px;">Commands by status: ${pills || '—'}</div>
        `;
      }

      function renderNodes(rows) {
        const el = document.getElementById('nodes');
        const html = [`<table><thead><tr><th>Node</th><th>Level</th><th>Sensors</th><th>Actuators</th><th>Transports</th><th>Last Seen</th></tr></thead><tbody>`]
        for (const n of rows) {
          html.push(`<tr><td>${n.nodeId}</td><td>${n.level||''}</td><td>${(n.sensors||[]).join(', ')}</td><td>${(n.actuators||[]).join(', ')}</td><td>${(n.transports||[]).join(', ')}</td><td>${n.lastSeen}</td></tr>`);
        }
        html.push('</tbody></table>');
        el.innerHTML = html.join('');
      }

      function renderCommands(rows) {
        const el = document.getElementById('commands');
        const html = [`<table><thead><tr><th>ID</th><th>Node</th><th>Target</th><th>Action</th><th>Status</th><th>Retries</th></tr></thead><tbody>`]
        for (const r of rows) {
          html.push(`<tr><td>${r.id}</td><td>${r.nodeId}</td><td>${r.target}</td><td>${r.action}</td><td><span class="status ${r.status}">${r.status}</span></td><td>${r.retries}</td></tr>`);
        }
        html.push('</tbody></table>');
        el.innerHTML = html.join('');
      }

      async function refresh() {
        const base = window.location.pathname.replace(/\/dashboard$/, '');
        const [metrics, nodes, cmds] = await Promise.all([
          fetchJSON(base + '/metrics'),
          fetchJSON(base + '/nodes'),
          fetchJSON(base + '/commands?limit=50'),
        ]);
        renderMetrics(metrics);
        renderNodes(nodes);
        renderCommands(cmds);
      }

      refresh();
      setInterval(refresh, 5000);
    </script>
  </body>
  </html>
        """
    )


@router.get("/edge/nodes/{nodeId}", summary="Get edge node details")
async def get_edge_node(ontologyApiName: str, nodeId: str, session: Session = Depends(get_session)):
    node = session.get(EdgeNode, nodeId)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return {
        "nodeId": node.node_id,
        "publicKey": node.public_key,
        "level": node.level,
        "sensors": node.sensors,
        "actuators": node.actuators,
        "transports": node.transports,
        "software": node.software,
        "hw": node.hw,
        "lastSeen": node.last_seen,
    }


@router.get("/edge/nodes/{nodeId}/state", summary="Get latest reported state for a node")
async def get_edge_node_state(
    ontologyApiName: str, nodeId: str, session: Session = Depends(get_session)
):
    state = session.get(EdgeNodeState, nodeId)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
    return {"nodeId": nodeId, "state": state.payload, "updatedAt": state.updated_at}


# --- Commands downstream ---
from pydantic import BaseModel, Field


class _EnqueueCommand(BaseModel):
    node_id: str = Field(..., alias="nodeId")
    target: str = Field(...)
    action: str = Field(...)
    payload: dict[str, Any] = Field(default_factory=dict)
    ttl: int | None = Field(default=300, ge=1)


@router.post(
    "/edge/commands",
    summary="Enqueue a command for an edge node",
    dependencies=[Depends(require_edge_token)],
    response_model=None,
)
async def enqueue_command(
    request: Request,
    ontologyApiName: str,
    cmd: _EnqueueCommand,
    session: Session = Depends(get_session),
):
    # Extract principal from request headers
    principal = request.headers.get("X-Edge-Principal")

    # Check ACL first
    if not acl_is_allowed(session, cmd.node_id, principal):
        edge_acl_denied_total.inc()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for target node"
        )

    # Rate limit enqueue per target node
    if not await rate_limit(
        f"enqueue:{cmd.node_id}", prefix="ENQ", default_capacity=30, default_window=60
    ):
        edge_rate_limit_rejections_total.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    queue = get_command_queue()
    record = EnqueuedCommand(
        id=new_command_id(),
        node_id=cmd.node_id,
        target=cmd.target,
        action=cmd.action,
        payload=cmd.payload,
        timestamp=time(),
    )
    try:
        record_enqueued(
            session,
            cmd_id=record.id,
            node_id=record.node_id,
            target=record.target,
            action=record.action,
            payload=record.payload,
        )
    except Exception:
        logger.exception("Failed to persist command (queued)")
    await queue.enqueue(record, ttl=cmd.ttl)
    edge_commands_enqueued_total.inc()
    return {"status": "queued", "commandId": record.id}


@router.get(
    "/edge/commands/pull",
    summary="Pull pending commands for a node",
    dependencies=[Depends(require_edge_token)],
)
async def pull_commands(
    ontologyApiName: str,
    nodeId: str,
    max_count: int = 10,
    waitSeconds: int = 0,
    session: Session = Depends(get_session),
):
    if not await rate_limit(
        f"pull:{nodeId}", prefix="PULL", default_capacity=120, default_window=60
    ):
        edge_rate_limit_rejections_total.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )
    queue = get_command_queue()
    items = (
        await queue.pull_blocking(nodeId, timeout=waitSeconds, max_items=max_count)
        if (waitSeconds and waitSeconds > 0)
        else await queue.pull(nodeId, max_items=max_count)
    )
    return [
        {
            "id": it.id,
            "target": it.target,
            "action": it.action,
            "payload": it.payload,
            "timestamp": it.timestamp,
        }
        for it in items
    ]


# --- Command acknowledgements (optional) ---
class _AckCommands(BaseModel):
    node_id: str
    ids: list[str]


@router.post(
    "/edge/commands/ack",
    summary="Acknowledge processed commands",
    dependencies=[Depends(require_edge_token)],
)
async def ack_commands(
    ontologyApiName: str, payload: _AckCommands, session: Session = Depends(get_session)
):
    # For now, no durable store is required. Stub for future metrics.
    try:
        count = record_acked(session, payload.ids)
    except Exception:
        logger.exception("Failed to persist command (acked)")
        count = 0
    logger.info("ACK from %s: %s", payload.node_id, ",".join(payload.ids))
    if count:
        edge_commands_acked_total.inc(count)
    return {"status": "ok", "count": count}


@router.get(
    "/edge/commands",
    summary="List command receipts (admin/observability)",
    dependencies=[Depends(require_edge_admin)],
)
async def list_commands(
    ontologyApiName: str,
    nodeId: str | None = None,
    status: str | None = None,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    rows = repo_list_commands(session, node_id=nodeId, status=status, limit=limit)
    return [
        {
            "id": r.id,
            "nodeId": r.node_id,
            "target": r.target,
            "action": r.action,
            "status": r.status,
            "retries": r.retries,
            "enqueuedAt": r.enqueued_at,
            "deliveredAt": r.delivered_at,
            "ackedAt": r.acked_at,
        }
        for r in rows
    ]


# --- ACL management (admin) ---
class _ACLItem(BaseModel):
    principal: str


@router.get(
    "/edge/nodes/{nodeId}/acl",
    summary="List node ACL (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def list_node_acl(ontologyApiName: str, nodeId: str, session: Session = Depends(get_session)):
    return {"nodeId": nodeId, "principals": acl_list(session, nodeId)}


@router.post(
    "/edge/nodes/{nodeId}/acl",
    summary="Add principal to ACL (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def add_node_acl(
    ontologyApiName: str, nodeId: str, item: _ACLItem, session: Session = Depends(get_session)
):
    acl_upsert(session, nodeId, item.principal)
    return {"status": "ok"}


@router.delete(
    "/edge/nodes/{nodeId}/acl/{principal}",
    summary="Remove principal from ACL (admin)",
    dependencies=[Depends(require_edge_admin)],
)
async def remove_node_acl(
    ontologyApiName: str, nodeId: str, principal: str, session: Session = Depends(get_session)
):
    ok = acl_remove(session, nodeId, principal)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Principal not found")
    return {"status": "ok"}
