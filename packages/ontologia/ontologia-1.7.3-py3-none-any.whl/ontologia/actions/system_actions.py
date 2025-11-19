"""system_actions.py
--------------------
Built-in system-level actions for ontology administration.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlmodel import Session, select

from ontologia.actions.registry import register_action
from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance

logger = logging.getLogger(__name__)


def _get_session(context: dict[str, Any]) -> Session:
    session = context.get("session")
    if not isinstance(session, Session):  # pragma: no cover - defensive guard
        raise ValueError("Action requires an active database session in context")
    return session


def _resolve_target_rid(context: dict[str, Any], params: dict[str, Any]) -> str:
    target_rid = params.get("target_rid")
    if target_rid:
        rid = str(target_rid)
    else:
        target = context.get("target_object")
        if target is not None:
            rid = getattr(target, "rid", None)
            if rid:
                rid = str(rid)
            else:
                raise ValueError("target object missing 'rid' attribute")
        else:
            raise ValueError("target_rid parameter is required when no target object is provided")
    if not rid or not rid.strip():
        raise ValueError("target_rid cannot be empty")
    return rid


def _validate_rid(rid: str, name: str) -> None:
    if not isinstance(rid, str) or not rid.strip():
        raise ValueError(f"{name} must be a non-empty string")
    # Simple validation for UUID-like RIDs (adjust if needed)
    if len(rid) < 10:
        raise ValueError(f"{name} appears to be invalid (too short)")


def _merge_properties(source: ObjectInstance, target: ObjectInstance) -> None:
    merged = dict(target.data or {})  # Start with target data (surviving object)
    merged.update(source.data or {})  # Update with source data (preserve source)
    target.data = merged


def _retarget_links(session: Session, source_rid: str, target_rid: str) -> None:
    # Resolve target and source instances to update pk fields consistently
    target_inst = session.exec(
        select(ObjectInstance).where(ObjectInstance.rid == target_rid)
    ).first()
    session.exec(select(ObjectInstance).where(ObjectInstance.rid == source_rid)).first()
    target_pk = getattr(target_inst, "pk_value", None) if target_inst is not None else None
    incoming = session.exec(
        select(LinkedObject).where(LinkedObject.to_object_rid == source_rid)
    ).all()
    for link in incoming:
        # If a link to the target already exists from the same source, drop this one.
        # Otherwise, simply deleting incoming-to-source avoids duplicates since
        # a pre-existing link to target typically exists in merge scenarios.
        session.delete(link)

    outgoing = session.exec(
        select(LinkedObject).where(LinkedObject.from_object_rid == source_rid)
    ).all()
    for link in outgoing:
        duplicate = session.exec(
            select(LinkedObject)
            .where(LinkedObject.link_type_rid == link.link_type_rid)
            .where(LinkedObject.from_object_rid == target_rid)
            .where(LinkedObject.to_object_rid == link.to_object_rid)
        ).first()
        if duplicate and duplicate.rid != link.rid:
            session.delete(link)
            continue
        link.from_object_rid = target_rid
        if target_pk:
            link.source_pk_value = target_pk
        session.add(link)

    # Final cleanup: remove any links that now point to target_rid but still
    # carry a stale target_pk_value (e.g., the source's pk). Keep only links
    # whose target_pk_value matches the target instance pk.
    if target_pk:
        stale_incoming = session.exec(
            select(LinkedObject)
            .where(LinkedObject.to_object_rid == target_rid)
            .where(LinkedObject.target_pk_value != target_pk)
        ).all()
        for link in stale_incoming:
            session.delete(link)


@register_action("system.merge_entities")
def merge_entities(context: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Merge a source entity into the target entity.

    Params:
        source_rid: RID of the entity to merge and delete (required)
        target_rid: RID of the surviving entity (optional if target object provided)
    """
    session = _get_session(context)

    source_rid_raw = params.get("source_rid")
    if not source_rid_raw:
        raise ValueError("'source_rid' parameter is required")
    source_rid = str(source_rid_raw)

    target_rid = _resolve_target_rid(context, params)

    # Validate RIDs
    _validate_rid(source_rid, "source_rid")
    _validate_rid(target_rid, "target_rid")

    if source_rid == target_rid:
        raise ValueError("source_rid and target_rid must be different")

    logger.info("Starting merge_entities: source=%s, target=%s", source_rid, target_rid)

    # Begin explicit transaction
    session.begin()

    try:
        source = session.get(ObjectInstance, source_rid)
        target = session.get(ObjectInstance, target_rid)
        if source is None:
            raise ValueError("Source entity not found")
        if target is None:
            raise ValueError("Target entity not found")

        _merge_properties(source, target)
        _retarget_links(session, source_rid, target_rid)

        session.delete(source)
        session.commit()
        session.refresh(target)

        logger.info(
            "Completed merge_entities: merged %s into %s, deleted source",
            source_rid,
            target_rid,
        )
        return {
            "status": "success",
            "mergedIntoRid": target_rid,
            "deletedRid": source_rid,
            "properties": dict(target.data or {}),
        }
    except Exception:
        session.rollback()
        logger.error(
            "Failed merge_entities: source=%s, target=%s",
            source_rid,
            target_rid,
            exc_info=True,
        )
        raise
