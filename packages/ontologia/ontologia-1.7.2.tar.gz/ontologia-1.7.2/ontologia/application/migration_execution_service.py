"""Execute generated schema migration tasks by mutating object instances."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)

logger = logging.getLogger(__name__)


class MigrationExecutionService:
    """Apply `MigrationTask` plans to stored object instances."""

    def __init__(self, session_or_service: Any, *, metamodel_service: Any | None = None) -> None:
        if isinstance(session_or_service, Session):
            self._session = session_or_service
            self._metamodel_service = metamodel_service
        else:
            self._metamodel_service = session_or_service
            repo = getattr(self._metamodel_service, "repo", None)
            session = getattr(repo, "session", None)
            if session is None:
                raise ValueError("MigrationExecutionService requires a SQLModel session")
            self._session = session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_task(
        self,
        service: str,
        instance: str,
        task_rid: str,
        *,
        dry_run: bool = False,
        batch_size: int | None = None,
    ) -> dict[str, Any]:
        task = self._session.get(MigrationTask, task_rid)
        if task is None:
            raise ValueError(f"MigrationTask '{task_rid}' not found")

        plan = task.plan or {}
        operations = plan.get("operations", [])

        instances = self._session.exec(
            select(ObjectInstance).where(
                ObjectInstance.object_type_api_name == task.object_type_api_name
            )
        ).all()

        total_instances = len(instances or [])
        updated_count = 0
        failed_count = 0
        errors: list[str] = []

        for instance_record in instances or []:
            try:
                updated = self._apply_operations(instance_record, operations, dry_run=dry_run)
                if updated and not dry_run:
                    instance_record.updated_at = datetime.now(UTC)
                    self._session.add(instance_record)
                    updated_count += 1
            except Exception as exc:  # pragma: no cover - defensive
                failed_count += 1
                errors.append(f"{instance_record.pk_value}: {exc}")

        if not dry_run:
            if failed_count:
                task.status = MigrationTaskStatus.FAILED
                task.error_message = errors[0] if errors else "Migration failed"
            else:
                task.status = MigrationTaskStatus.COMPLETED
                task.error_message = None
            self._session.add(task)
            self._session.commit()
            self._session.refresh(task)

        return {
            "taskRid": task.rid,
            "objectTypeApiName": task.object_type_api_name,
            "dryRun": dry_run,
            "totalInstances": total_instances,
            "updatedCount": 0 if dry_run else updated_count,
            "failedCount": failed_count,
            "errors": errors,
            "operationsPlanned": len(operations),
            "taskStatus": (
                task.status.value
                if isinstance(task.status, MigrationTaskStatus)
                else str(task.status)
            ),
        }

    def run_pending_tasks(
        self,
        service: str,
        instance: str,
        *,
        dry_run: bool = False,
        limit: int | None = None,
        batch_size: int | None = None,
    ) -> list[dict[str, Any]]:
        stmt = select(MigrationTask).where(MigrationTask.status == MigrationTaskStatus.PENDING)
        if limit is not None:
            stmt = stmt.limit(limit)
        tasks = self._session.exec(stmt).all()

        results: list[dict[str, Any]] = []
        for task in tasks or []:
            results.append(
                self.run_task(
                    service,
                    instance,
                    task.rid,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
            )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_operations(
        self,
        instance_record: ObjectInstance,
        operations: list[dict[str, Any]],
        *,
        dry_run: bool,
    ) -> bool:
        if not operations:
            return False

        data = dict(instance_record.data or {})
        original_data = dict(data)
        updated = False

        for operation in operations:
            op_type = (operation or {}).get("operation")
            if op_type == "change_type":
                property_name = operation.get("property")
                target_type = operation.get("to")
                if property_name not in data:
                    continue
                converted, changed = self._convert_value(data[property_name], target_type)
                if changed:
                    if not dry_run:
                        data[property_name] = converted
                    updated = updated or not dry_run
            elif op_type == "drop_property":
                property_name = operation.get("property")
                if property_name in data and not dry_run:
                    data.pop(property_name, None)
                    updated = True

        if not dry_run and updated:
            instance_record.data = data
        else:
            instance_record.data = original_data if dry_run else instance_record.data

        return updated

    def _convert_value(self, value: Any, target_type: Any) -> tuple[Any, bool]:
        if target_type in (None, "string", "STRING"):
            new_value = None if value is None else str(value)
            return new_value, new_value != value
        if target_type in ("integer", "INTEGER", "number", "NUMBER"):
            if value is None or value == "":
                return value, False
            if isinstance(value, int):
                return value, False
            new_value = int(value)
            return new_value, new_value != value
        return value, False
