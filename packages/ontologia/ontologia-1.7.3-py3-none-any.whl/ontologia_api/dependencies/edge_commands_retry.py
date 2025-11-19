from __future__ import annotations

import asyncio
import logging
import os

from sqlmodel import Session

from ontologia_api.core.database import engine
from ontologia_api.core.edge_commands import EnqueuedCommand, get_command_queue
from ontologia_api.core.edge_metrics import (
    edge_commands_expired_total,
    edge_commands_retried_total,
)
from ontologia_api.repositories.edge_commands_repository import (
    expire_overdue,
    find_due_retries,
)
from ontologia_api.repositories.edge_commands_repository import (
    requeue as repo_requeue,
)

logger = logging.getLogger(__name__)


async def run_edge_command_retry_loop(stop_event: asyncio.Event) -> None:
    interval = int(os.getenv("EDGE_CMD_RETRY_INTERVAL", "5"))
    queue = get_command_queue()
    while not stop_event.is_set():
        try:
            with Session(engine) as session:
                due = find_due_retries(session, limit=100)
                if due:
                    ids: list[str] = [r.id for r in due]
                    # Re-enqueue commands
                    for r in due:
                        try:
                            await queue.enqueue(
                                EnqueuedCommand(
                                    id=r.id,
                                    node_id=r.node_id,
                                    target=r.target,
                                    action=r.action,
                                    payload=r.payload,
                                    timestamp=0.0,
                                ),
                                ttl=None,
                            )
                        except Exception:
                            logger.exception("Failed to enqueue retry for %s", r.id)
                    # Mark as requeued in DB (status/attempts)
                    try:
                        repo_requeue(session, ids)
                        edge_commands_retried_total.inc(len(ids))
                    except Exception:
                        logger.exception("Failed to mark requeue for %d commands", len(ids))
                # Expire overdue
                try:
                    cnt = expire_overdue(session)
                    if cnt:
                        logger.info("Expired/failed %d commands", cnt)
                        edge_commands_expired_total.inc(cnt)
                except Exception:
                    logger.exception("Expire overdue failed")
        except Exception:
            logger.exception("Edge command retry loop error")
        await asyncio.wait([asyncio.create_task(stop_event.wait())], timeout=interval)
