from __future__ import annotations

from ontologia_api.services.instances_service import InstancesService
from ontologia_api.services.metamodel_service import MetamodelService
from ontologia_api.services.migration_execution_service import MigrationExecutionService
from ontologia_api.v2.schemas.instances import ObjectUpsertRequest
from ontologia_api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from sqlmodel import Session, select

from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)


def _create_object_type(session: Session, data_type: str) -> MigrationTask | None:
    metamodel = MetamodelService(session, service="ontology", instance="default")
    metamodel.upsert_object_type(
        "customer",
        ObjectTypePutRequest(
            displayName="Customer",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType=data_type, displayName="Age"),  # type: ignore[arg-type]
            },
            implements=[],
        ),
    )
    return session.exec(select(MigrationTask)).first()


def test_migration_execution_service_applies_changes(session: Session) -> None:
    # Clean up any existing customer instances to ensure clean test state
    from sqlmodel import delete

    session.exec(delete(ObjectInstance).where(ObjectInstance.object_type_api_name == "customer"))
    session.commit()

    # Clean up any existing migration tasks for customer
    session.exec(delete(MigrationTask).where(MigrationTask.object_type_api_name == "customer"))
    session.commit()

    _create_object_type(session, "integer")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": 42}),
    )
    session.commit()

    _create_object_type(session, "string")

    # Get the latest migration task for customer (the one that converts integer to string)
    all_tasks = session.exec(
        select(MigrationTask).where(MigrationTask.object_type_api_name == "customer")
    ).all()
    task = all_tasks[-1] if all_tasks else None
    assert task is not None

    executor = MigrationExecutionService(session)
    dry = executor.run_task("ontology", "default", task.rid, dry_run=True)
    assert dry["failedCount"] == 0

    result = executor.run_task("ontology", "default", task.rid)
    assert result["failedCount"] == 0
    assert result["updatedCount"] == 1

    session.refresh(task)
    assert task.status == MigrationTaskStatus.COMPLETED

    stored = session.exec(select(ObjectInstance).where(ObjectInstance.pk_value == "1")).first()
    assert stored is not None
    assert stored.data.get("age") == "42"


def test_migration_execution_service_handles_failure(session: Session) -> None:
    # Clean up any existing customer instances to ensure clean test state
    from sqlmodel import delete

    session.exec(delete(ObjectInstance).where(ObjectInstance.object_type_api_name == "customer"))
    session.commit()

    # Clean up any existing migration tasks for customer
    session.exec(delete(MigrationTask).where(MigrationTask.object_type_api_name == "customer"))
    session.commit()

    _create_object_type(session, "string")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": "not-a-number"}),
    )
    session.commit()

    _create_object_type(session, "integer")

    # Get the latest migration task for customer (the one that converts string to integer)
    all_tasks = session.exec(
        select(MigrationTask).where(MigrationTask.object_type_api_name == "customer")
    ).all()
    task = all_tasks[-1] if all_tasks else None
    assert task is not None

    executor = MigrationExecutionService(session)
    result = executor.run_task("ontology", "default", task.rid)

    session.refresh(task)
    assert task.status == MigrationTaskStatus.FAILED
    assert result["failedCount"] == 1  # type: ignore[index]
    assert result["updatedCount"] == 0  # type: ignore[index]


def test_migration_execution_service_run_pending(session: Session) -> None:
    # Clean up any existing customer instances to ensure clean test state
    from sqlmodel import delete

    session.exec(delete(ObjectInstance).where(ObjectInstance.object_type_api_name == "customer"))
    session.commit()

    # Clean up ALL migration tasks to ensure clean test state
    session.exec(delete(MigrationTask))
    session.commit()

    _create_object_type(session, "integer")

    instances = InstancesService(session, service="ontology", instance="default")
    instances.upsert_object(
        "customer",
        "1",
        ObjectUpsertRequest(properties={"age": 25}),
    )
    session.commit()

    _create_object_type(session, "string")

    executor = MigrationExecutionService(session)
    dry_results = executor.run_pending_tasks("ontology", "default", dry_run=True)
    # Filter results to only include customer tasks
    customer_results = [r for r in dry_results if r.get("objectTypeApiName") == "customer"]
    # We expect at least 1 task (might be 1 or 2 depending on test order)
    assert len(customer_results) >= 1
    # Get the latest task
    latest_task = customer_results[-1]
    assert latest_task["failedCount"] == 0  # type: ignore[index]

    applied_results = executor.run_pending_tasks("ontology", "default")
    # Filter results to only include customer tasks
    customer_applied_results = [
        r for r in applied_results if r.get("objectTypeApiName") == "customer"
    ]
    assert len(customer_applied_results) >= 1
    latest_applied_task = customer_applied_results[-1]
    assert latest_applied_task["failedCount"] == 0  # type: ignore[index]

    # Get the latest customer task
    all_tasks = session.exec(
        select(MigrationTask).where(MigrationTask.object_type_api_name == "customer")
    ).all()
    task = all_tasks[-1] if all_tasks else None
    assert task is not None
    assert task.status == MigrationTaskStatus.COMPLETED
