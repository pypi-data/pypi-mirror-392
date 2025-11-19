from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import cast, desc
from sqlmodel import Session, select

from ontologia_api.models.edge_commands_sql import CommandReceipt


def record_enqueued(
    session: Session,
    *,
    cmd_id: str,
    node_id: str,
    target: str,
    action: str,
    payload: dict,
) -> CommandReceipt:
    import os

    ack_timeout = int(os.getenv("EDGE_CMD_ACK_TIMEOUT", "30"))
    max_retries = int(os.getenv("EDGE_CMD_MAX_RETRIES", "3"))
    expires_sec = os.getenv("EDGE_CMD_EXPIRES_SEC")
    expires_at = None
    if expires_sec is not None:
        try:
            expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_sec))
        except ValueError:
            expires_at = None
    rec = CommandReceipt(
        id=cmd_id,
        node_id=node_id,
        target=target,
        action=action,
        payload=payload,
        status="queued",
        ack_timeout_seconds=ack_timeout,
        max_retries=max_retries,
        expires_at=expires_at,
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec


def record_delivered(session: Session, ids: Iterable[str]) -> int:
    now = datetime.now(UTC)
    count = 0
    for cmd_id in ids:
        rec = session.get(CommandReceipt, cmd_id)
        if rec is None:
            continue
        if rec.delivered_at is None:
            rec.delivered_at = now
        # If already delivered and acked, leave as is
        if rec.status == "queued":
            rec.status = "delivered"
        session.add(rec)
        count += 1
    session.commit()
    return count


def record_acked(session: Session, ids: Iterable[str]) -> int:
    now = datetime.now(UTC)
    count = 0
    for cmd_id in ids:
        rec = session.get(CommandReceipt, cmd_id)
        if rec is None:
            continue
        rec.acked_at = rec.acked_at or now
        rec.status = "acked"
        session.add(rec)
        count += 1
    session.commit()
    return count


def find_due_retries(session: Session, *, limit: int = 100) -> list[CommandReceipt]:
    now = datetime.now(UTC)
    rows = session.exec(
        select(CommandReceipt)
        .where(CommandReceipt.status == "delivered")
        .where(cast(Any, CommandReceipt.delivered_at).is_not(None))
    ).all()
    due: list[CommandReceipt] = []
    for r in rows:
        try:
            deadline = r.delivered_at + timedelta(seconds=r.ack_timeout_seconds)  # type: ignore[operator]
        except Exception:
            continue
        if r.acked_at is None and deadline <= now and r.retries < r.max_retries:
            due.append(r)
            if len(due) >= limit:
                break
    return due


def requeue(session: Session, ids: Iterable[str]) -> int:
    now = datetime.now(UTC)
    cnt = 0
    for cmd_id in ids:
        rec = session.get(CommandReceipt, cmd_id)
        if not rec:
            continue
        rec.retries += 1
        rec.status = "queued"
        rec.enqueued_at = now
        session.add(rec)
        cnt += 1
    session.commit()
    return cnt


def expire_overdue(session: Session) -> int:
    now = datetime.now(UTC)
    rows = session.exec(select(CommandReceipt)).all()
    cnt = 0
    for r in rows:
        if r.status in {"acked", "expired", "failed"}:
            continue
        expired = r.expires_at is not None and r.expires_at <= now
        exhausted = r.retries >= r.max_retries and r.status == "delivered"
        if expired or exhausted:
            r.status = "expired" if expired else "failed"
            session.add(r)
            cnt += 1
    session.commit()
    return cnt


def list_commands(
    session: Session, *, node_id: str | None = None, status: str | None = None, limit: int = 100
):
    stmt = select(CommandReceipt).order_by(desc(CommandReceipt.enqueued_at)).limit(limit)
    if node_id:
        stmt = stmt.where(CommandReceipt.node_id == node_id)
    if status:
        stmt = stmt.where(CommandReceipt.status == status)
    return session.exec(stmt).all()
