from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime
from typing import Any, cast

from sqlmodel import Session, select

from ontologia_api.models.edge_keys_sql import EdgeNodeKey
from ontologia_api.models.edge_models_sql import (
    EdgeMessageReceipt,
    EdgeNode,
    EdgeNodeState,
)


def upsert_edge_node(
    session: Session,
    *,
    node_id: str,
    public_key: str | None,
    capabilities: dict[str, Any] | None,
    software: dict[str, Any] | None,
    hw: dict[str, Any] | None,
) -> EdgeNode:
    level = (capabilities or {}).get("level")
    sensors = (capabilities or {}).get("sensors")
    actuators = (capabilities or {}).get("actuators")
    transports = (capabilities or {}).get("transports")
    existing = session.get(EdgeNode, node_id)
    now = datetime.now(UTC)
    if existing is None:
        node = EdgeNode(
            node_id=node_id,
            public_key=public_key,
            level=level,
            sensors=sensors,
            actuators=actuators,
            transports=transports,
            software=software,
            hw=hw,
            sig_algo=_extract_sig_algo(capabilities),
            canonical_mode=_extract_canonical_mode(capabilities),
            last_seen=now,
        )
        session.add(node)
        session.commit()
        session.refresh(node)
        return node
    # Merge/update
    if public_key and not existing.public_key:
        existing.public_key = public_key
    existing.level = level or existing.level
    existing.sensors = sensors or existing.sensors
    existing.actuators = actuators or existing.actuators
    existing.transports = transports or existing.transports
    existing.software = software or existing.software
    existing.hw = hw or existing.hw
    # Update negotiation preferences if provided
    sig_algo = _extract_sig_algo(capabilities)
    canonical_mode = _extract_canonical_mode(capabilities)
    existing.sig_algo = sig_algo or existing.sig_algo
    existing.canonical_mode = canonical_mode or existing.canonical_mode
    existing.last_seen = now
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


def _extract_sig_algo(capabilities: dict[str, Any] | None) -> str | None:
    if not capabilities:
        return None
    crypto = capabilities.get("crypto") or capabilities.get("sig") or {}
    if isinstance(crypto, dict):
        algo = crypto.get("algo") or crypto.get("algorithm")
        if isinstance(algo, str) and algo:
            return algo
    # Also accept direct field
    algo = capabilities.get("sigAlgo")
    return str(algo) if isinstance(algo, str) and algo else None


def _extract_canonical_mode(capabilities: dict[str, Any] | None) -> str | None:
    if not capabilities:
        return None
    crypto = capabilities.get("crypto") or capabilities.get("sig") or {}
    if isinstance(crypto, dict):
        canonical = crypto.get("canonical") or crypto.get("mode")
        if isinstance(canonical, str) and canonical:
            return canonical
    mode = capabilities.get("canonical")
    return str(mode) if isinstance(mode, str) and mode else None


def save_edge_state(session: Session, *, node_id: str, payload: dict[str, Any]) -> EdgeNodeState:
    state = session.get(EdgeNodeState, node_id)
    now = datetime.now(UTC)
    if state is None:
        state = EdgeNodeState(node_id=node_id, payload=payload, updated_at=now)
        session.add(state)
    else:
        state.payload = payload
        state.updated_at = now
        session.add(state)
    session.commit()
    session.refresh(state)
    return state


def ensure_message_not_seen(
    session: Session, *, msg_id: str, node_id: str | None, ttl: int | None
) -> bool:
    """Returns True if message is new and records it; False if duplicate (already seen and not expired)."""
    receipt = session.get(EdgeMessageReceipt, msg_id)
    now = datetime.now(UTC)
    if receipt is not None and receipt.expires_at > now:
        return False
    # Insert/update
    expiry = EdgeMessageReceipt.compute_expiry(ttl)
    entry = EdgeMessageReceipt(msg_id=msg_id, node_id=node_id, received_at=now, expires_at=expiry)
    session.add(entry)
    session.commit()
    return True


def get_public_key(session: Session, node_id: str) -> str | None:
    # Prefer active key from EdgeNodeKey; fallback to EdgeNode.public_key
    stmt = (
        select(EdgeNodeKey)
        .where(EdgeNodeKey.node_id == node_id, EdgeNodeKey.active)
        .limit(1)
    )  # noqa: E712
    row = session.exec(stmt).first()
    if row and row.public_key:
        return row.public_key
    node = session.get(EdgeNode, node_id)
    return node.public_key if node else None


def _key_id_for(public_key: str) -> str:
    h = hashlib.sha256(public_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(h).decode("utf-8").rstrip("=")


def add_edge_key(
    session: Session, node_id: str, public_key: str, *, make_active: bool = False
) -> EdgeNodeKey:
    key_id = _key_id_for(public_key)
    existing = session.get(EdgeNodeKey, key_id)
    if existing is None:
        record = EdgeNodeKey(key_id=key_id, node_id=node_id, public_key=public_key, active=False)
        session.add(record)
    else:
        record = existing
    if make_active:
        # Deactivate current active keys
        for row in session.exec(
            select(EdgeNodeKey).where(EdgeNodeKey.node_id == node_id, EdgeNodeKey.active)
        ).all():  # noqa: E712
            row.active = False
            session.add(row)
        record.active = True
    session.add(record)
    # also persist to EdgeNode for back-compat if empty
    node = session.get(EdgeNode, node_id)
    if node and not node.public_key:
        node.public_key = public_key
        session.add(node)
    session.commit()
    session.refresh(record)
    return record


def list_edge_keys(session: Session, node_id: str) -> list[EdgeNodeKey]:
    rows = session.exec(select(EdgeNodeKey).where(EdgeNodeKey.node_id == node_id)).all()
    return cast(list[EdgeNodeKey], list(rows))


def activate_edge_key(session: Session, node_id: str, key_id: str) -> EdgeNodeKey | None:
    record = session.get(EdgeNodeKey, key_id)
    if record is None or record.node_id != node_id:
        return None
    # Deactivate others
    for row in session.exec(
        select(EdgeNodeKey).where(EdgeNodeKey.node_id == node_id, EdgeNodeKey.active)
    ).all():  # noqa: E712
        row.active = False
        session.add(row)
    record.active = True
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def revoke_edge_key(session: Session, node_id: str, key_id: str) -> EdgeNodeKey | None:
    record = session.get(EdgeNodeKey, key_id)
    if record is None or record.node_id != node_id:
        return None
    record.active = False
    from datetime import UTC, datetime

    record.revoked_at = datetime.now(UTC)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
