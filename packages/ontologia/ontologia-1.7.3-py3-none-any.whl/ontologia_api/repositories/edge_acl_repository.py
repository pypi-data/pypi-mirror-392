from __future__ import annotations

from sqlmodel import Session, select

from ontologia_api.models.edge_acl_sql import EdgeNodeACL


def list_acl(session: Session, node_id: str) -> list[str]:
    rows = session.exec(select(EdgeNodeACL).where(EdgeNodeACL.node_id == node_id)).all()
    return [r.principal for r in rows]


def upsert_acl(session: Session, node_id: str, principal: str) -> None:
    row = session.get(EdgeNodeACL, (node_id, principal))
    if row is None:
        row = EdgeNodeACL(node_id=node_id, principal=principal)
        session.add(row)
        session.commit()


def remove_acl(session: Session, node_id: str, principal: str) -> bool:
    row = session.get(EdgeNodeACL, (node_id, principal))
    if not row:
        return False
    session.delete(row)
    session.commit()
    return True


def is_allowed(session: Session, node_id: str, principal: str | None) -> bool:
    rows = list_acl(session, node_id)
    if not rows:
        return True  # open by default
    if not principal:
        return False
    return principal in rows
