from fastapi import HTTPException
from ontologia_api.services.actions_service import ActionsService
from ontologia_api.services.linked_objects_service import LinkedObjectsService
from ontologia_api.services.metamodel_service import MetamodelService
from ontologia_api.v2.schemas.actions import ActionParameterDefinition
from ontologia_api.v2.schemas.linked_objects import LinkCreateRequest
from ontologia_api.v2.schemas.metamodel import (
    ActionTypePutRequest,
    LinkTypePutRequest,
    ObjectTypePutRequest,
    PropertyDefinition,
)
from sqlmodel import Session, SQLModel, select

from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
from ontologia.domain.metamodels.types.action_type import ActionType
from ontologia.domain.metamodels.types.object_type import ObjectType


def test_merge_entities_action(session: Session):
    print(f"DEBUG: Test session ID: {id(session)}")
    print(f"DEBUG: Test session class: {session.__class__}")
    print(f"DEBUG: Test session engine: {session.bind}")
    print(f"DEBUG: Test session engine url: {session.bind.url}")

    mm = MetamodelService(session, service="ontology", instance="default")

    # Clean up any existing objects to ensure test isolation
    from sqlalchemy import text

    try:
        session.exec(text("DROP TABLE IF EXISTS objectinstance"))
        session.exec(text("DROP TABLE IF EXISTS linkedobject"))
        session.exec(text("DROP TABLE IF EXISTS objecttype"))
        session.exec(text("DROP TABLE IF EXISTS linktype"))
        session.exec(text("DROP TABLE IF EXISTS resource"))
        session.commit()
    except Exception:
        # Table might not exist, ignore
        pass

    SQLModel.metadata.create_all(session.get_bind())

    req = ObjectTypePutRequest(
        displayName="Employee",
        description=None,
        primaryKey="id",
        properties={
            "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
            "name": PropertyDefinition(dataType="string", displayName="Name"),
            "email": PropertyDefinition(dataType="string", displayName="Email"),
        },
    )
    print(f"DEBUG: Creating ObjectType with session ID: {id(session)}")
    mm.upsert_object_type("employee", req)
    print("DEBUG: ObjectType created")

    # Check if the object type is in the database
    existing_types = session.exec(select(ObjectType).where(ObjectType.api_name == "employee")).all()
    print(f"DEBUG: Found {len(existing_types)} employee types in database")
    for ot in existing_types:
        print(f"  Type: rid={ot.rid}, version={ot.version}, is_latest={ot.is_latest}")

    # Check if Resource table has entries for the object type
    from registro.core.resource import Resource

    resources = session.exec(
        select(Resource).where(Resource.rid.in_([ot.rid for ot in existing_types]))
    ).all()
    print(f"DEBUG: Found {len(resources)} Resource entries for object types")
    for res in resources:
        print(f"  Resource: rid={res.rid}, service={res.service}, instance={res.instance}")

    # Create link type for reports_to
    mm.upsert_link_type(
        "reports_to",
        LinkTypePutRequest(
            displayName="Reports To",
            cardinality="MANY_TO_MANY",
            fromObjectType="employee",
            toObjectType="employee",
            inverse={"apiName": "manages", "displayName": "Manages"},  # type: ignore[arg-type]
        ),
    )

    # Check if the object type is still there after link creation
    existing_types_after = session.exec(
        select(ObjectType).where(ObjectType.api_name == "employee")
    ).all()
    print(
        f"DEBUG: Found {len(existing_types_after)} employee types in database after link creation"
    )
    for ot in existing_types_after:
        print(f"  Type: rid={ot.rid}, version={ot.version}, is_latest={ot.is_latest}")

    # Check if metamodel service is using the same session
    print(f"DEBUG: MetamodelService repository session ID: {id(mm.repository.session)}")
    print(f"DEBUG: Test session ID: {id(session)}")
    print(
        f"DEBUG: MetamodelService repository session is same as test session: {id(mm.repository.session) == id(session)}"
    )

    print(f"DEBUG: About to create ActionsService with session ID: {id(session)}")
    svc = ActionsService(session, service="ontology", instance="default")
    print(f"DEBUG: Created ActionsService with session ID: {id(svc.session)}")
    instances = svc.instances
    print(f"DEBUG: ActionsService service={svc.service}, instance={svc.instance}")
    print(f"DEBUG: ActionsService session ID: {id(svc.session)}")
    print(f"DEBUG: InstancesService service={instances._service}, instance={instances._instance}")
    print(
        f"DEBUG: InstancesService metamodel repo session ID: {id(instances._domain.metamodel_repository.session)}"
    )
    print(
        f"DEBUG: ActionsService session vs InstancesService metamodel repo session: {id(svc.session) == id(instances._domain.metamodel_repository.session)}"
    )

    instances.upsert_object(
        "employee",
        "manager",
        body={"properties": {"name": "Manager"}},
    )
    print(f"DEBUG: Session state after manager: new={len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session ID in test after manager: {id(session)}")
    print(f"DEBUG: Session is active: {session.is_active}")
    print(f"DEBUG: Session identity map after manager: {dict(session.identity_map)}")
    # Check if test session is same as repo session
    print(f"DEBUG: instances type: {type(instances)}")
    print(f"DEBUG: domain instances type: {type(instances._domain)}")
    print(
        f"DEBUG: domain has instances_repository: {hasattr(instances._domain, 'instances_repository')}"
    )
    print(
        f"DEBUG: Test session vs domain repo session: {id(session) == id(instances._domain.instances_repository._sql_repo.session)}"
    )
    print(f"DEBUG: Has instances_repository: {hasattr(svc.instances, 'instances_repository')}")

    print(f"DEBUG: Session state before emp1: new={len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session is active before emp1: {session.is_active}")
    print(f"DEBUG: Session autoflush: {session.autoflush}")
    print(f"DEBUG: Session expire_on_commit: {session.expire_on_commit}")
    print(
        f"DEBUG: Test session vs domain metamodel repo session: {id(session) == id(instances._domain.metamodel_repository.session)}"
    )
    instances.upsert_object(
        "employee",
        "emp1",
        body={"properties": {"name": "Alice", "email": "alice@example.com"}},
    )
    print("DEBUG: Created emp1")
    print(f"DEBUG: Session state after emp1: new={len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session ID in test after emp1: {id(session)}")
    print(f"DEBUG: Session is active: {session.is_active}")

    # Check database contents after emp1
    print(f"DEBUG: Before DB query after emp1 - session new: {len(session.new)}")
    all_objs = session.exec(select(ObjectInstance)).all()
    print(f"DEBUG: After DB query after emp1 - session new: {len(session.new)}")
    print(f"DEBUG: Total objects in DB after emp1: {len(all_objs)}")
    for obj in all_objs:
        print(f"  Object: pk={obj.pk_value}, valid_to={obj.valid_to}")
        if hasattr(obj, "valid_from") and hasattr(obj, "transaction_from"):
            print(f"    valid_from={obj.valid_from}, transaction_from={obj.transaction_from}")
            print(f"    object_type_rid={obj.object_type_rid}")
            print(f"    object_type_api_name={obj.object_type_api_name}")
    # Don't access identity_map as it might contain deleted objects
    # print(f"DEBUG: Session identity map after emp1: {dict(session.identity_map)}")
    print(f"DEBUG: instances type: {type(instances)}")
    print(f"DEBUG: domain instances type: {type(instances._domain)}")
    print(
        f"DEBUG: domain has instances_repository: {hasattr(instances._domain, 'instances_repository')}"
    )
    print(
        f"DEBUG: Test session vs domain repo session: {id(session) == id(instances._domain.instances_repository._sql_repo.session)}"
    )
    print(f"DEBUG: Has instances_repository: {hasattr(svc.instances, 'instances_repository')}")

    # Check if session is still good
    print(f"DEBUG: Session new after emp1 return: {len(session.new)}")
    print(f"DEBUG: Session dirty after emp1 return: {len(session.dirty)}")
    print(f"DEBUG: Session is_active after emp1 return: {session.is_active}")
    print(f"DEBUG: Session in_transaction: {session.in_transaction()}")

    # Check what service/instance emp1 has
    print(f"DEBUG: Before query - session new: {len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session is_active before query: {session.is_active}")
    print(f"DEBUG: Session transaction before query: {session.get_transaction()}")
    emp1_objs = session.exec(select(ObjectInstance).where(ObjectInstance.pk_value == "emp1")).all()
    print(f"DEBUG: After query - session new: {len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session is_active after query: {session.is_active}")
    print(f"DEBUG: Session transaction after query: {session.get_transaction()}")
    # Check if emp1 is still in the identity map

    for obj in session.identity_map.values():
        if hasattr(obj, "pk_value") and obj.pk_value == "emp1":
            print(f"DEBUG: emp1 found in identity map: {obj}")
            break
    else:
        print("DEBUG: emp1 NOT found in identity map")
    print(f"DEBUG: Found {len(emp1_objs)} emp1 objects")
    for obj in emp1_objs:
        print(f"  emp1: service={obj.service}, instance={obj.instance}, valid_to={obj.valid_to}")
    print(f"DEBUG: Session state after emp1: new={len(session.new)}, dirty={len(session.dirty)}")
    print(f"DEBUG: Session ID in test after emp1: {id(session)}")
    print(f"DEBUG: Session is active: {session.is_active}")
    try:
        print(
            f"DEBUG: Session state before emp2: new={len(session.new)}, dirty={len(session.dirty)}"
        )
        print(f"DEBUG: Session is active before emp2: {session.is_active}")
        print("DEBUG: About to create emp2...")

        # Check what's actually in the database before creating emp2
        all_objs_before_emp2 = session.exec(select(ObjectInstance)).all()
        print(f"DEBUG: Total objects in DB before emp2: {len(all_objs_before_emp2)}")
        for obj in all_objs_before_emp2:
            print(f"  Object: pk={obj.pk_value}, valid_to={obj.valid_to}")

        instances.upsert_object(
            "employee",
            "emp2",
            body={"properties": {"name": "Bob", "email": "bob@example.com"}},
        )
        print("DEBUG: Created emp2")
        print(
            f"DEBUG: Session state after emp2: new={len(session.new)}, dirty={len(session.dirty)}"
        )
        print(f"DEBUG: Session is_active after emp2: {session.is_active}")
        print(f"DEBUG: Session transaction after emp2: {session.get_transaction()}")

        # Check if emp2 is actually in the session
        print("DEBUG: Session new contents after emp2:")
        for obj in session.new:
            print(f"  New obj: pk={obj.pk_value}")
        print("DEBUG: Session dirty contents after emp2:")
        for obj in session.dirty:
            print(f"  Dirty obj: pk={obj.pk_value}")

        # Check what's in the database after creating emp2
        print(f"DEBUG: Before DB query after emp2 - session new: {len(session.new)}")
        all_objs_after_emp2 = session.exec(select(ObjectInstance)).all()
        print(f"DEBUG: After DB query after emp2 - session new: {len(session.new)}")
        print(f"DEBUG: Total objects in DB after emp2: {len(all_objs_after_emp2)}")
        for obj in all_objs_after_emp2:
            print(f"  Object: pk={obj.pk_value}, valid_to={obj.valid_to}")
            print(f"    valid_from={obj.valid_from}, transaction_from={obj.transaction_from}")
            print(f"    object_type_rid={obj.object_type_rid}")
            print(f"    object_type_api_name={obj.object_type_api_name}")
    except Exception as e:
        print(f"DEBUG: Error creating emp2: {e}")
        import traceback

        traceback.print_exc()
    try:
        instances.upsert_object(
            "employee",
            "colleague",
            body={"properties": {"name": "Colleague"}},
        )
        print("DEBUG: Created colleague")
    except Exception as e:
        print(f"DEBUG: Error creating colleague: {e}")

    # Check what's in the session before commit
    print(f"DEBUG: Session dirty before commit: {session.dirty}")
    print(f"DEBUG: Session new before commit: {session.new}")
    print(f"DEBUG: Session is_active before commit: {session.is_active}")
    print(f"DEBUG: Session transaction before commit: {session.get_transaction()}")
    # Don't access identity_map as it might contain deleted objects
    # print(f"DEBUG: Session identity map before commit: {dict(session.identity_map)}")

    session.commit()
    print(f"DEBUG: Session is_active after commit: {session.is_active}")
    print(f"DEBUG: Session transaction after commit: {session.get_transaction()}")
    # Don't access identity_map as it might contain deleted objects
    # print(f"DEBUG: Session identity map after commit: {dict(session.identity_map)}")

    # Check what objects were created
    all_objs = session.exec(select(ObjectInstance)).all()
    print(f"DEBUG: Total objects after creation: {len(all_objs)}")
    for obj in all_objs:
        print(
            f"  Object: pk={obj.pk_value}, has_service={hasattr(obj, 'service')}, has_instance={hasattr(obj, 'instance')}, valid_to={obj.valid_to}"
        )
        if hasattr(obj, "service"):
            print(f"    service={obj.service}, instance={obj.instance}")
        if hasattr(obj, "service_value"):
            print(f"    service_value={obj.service_value}, instance_value={obj.instance_value}")

    source_objs = session.exec(
        select(ObjectInstance).where(
            ObjectInstance.pk_value == "emp1",
            ObjectInstance.valid_to.is_(None),
            ObjectInstance.service_value == "ontology",
            ObjectInstance.instance_value == "default",
        )
    ).all()
    target_objs = session.exec(
        select(ObjectInstance).where(
            ObjectInstance.pk_value == "emp2",
            ObjectInstance.valid_to.is_(None),
            ObjectInstance.service_value == "ontology",
            ObjectInstance.instance_value == "default",
        )
    ).all()
    print(f"DEBUG: Found {len(source_objs)} source objects for emp1 with ontology/default")
    print(f"DEBUG: Found {len(target_objs)} target objects for emp2 with ontology/default")
    for obj in target_objs:
        print(
            f"  Target: rid={obj.rid}, data={obj.data}, valid_from={obj.valid_from}, valid_to={obj.valid_to}"
        )
    source = source_objs[0] if source_objs else None
    target = target_objs[0] if target_objs else None

    if source is None or target is None:
        print(f"DEBUG: source={source}, target={target}")
        print(f"DEBUG: source_objs={len(source_objs)}, target_objs={len(target_objs)}")
        raise AssertionError(f"Source or target not found: source={source}, target={target}")

    links = LinkedObjectsService(session, service="ontology", instance="default")
    links.create_link("reports_to", LinkCreateRequest(fromPk="manager", toPk="emp1"))
    links.create_link("reports_to", LinkCreateRequest(fromPk="manager", toPk="emp2"))
    links.create_link("reports_to", LinkCreateRequest(fromPk="emp1", toPk="colleague"))

    SQLModel.metadata.create_all(session.get_bind())
    mm.upsert_action_type(
        "merge_employee",
        ActionTypePutRequest(
            displayName="Merge Employee",
            description="Merge duplicates",
            targetObjectType="employee",
            parameters={
                "source_rid": ActionParameterDefinition(
                    dataType="string",
                    displayName="Source RID",
                    required=True,
                )
            },
            executorKey="system.merge_entities",
        ),
    )

    result = svc.execute_action(
        "employee",
        "emp2",
        "merge_employee",
        {"source_rid": source.rid},
    )

    assert result["status"] == "success"
    assert result["deletedRid"] == source.rid
    assert result["mergedIntoRid"] == target.rid

    remaining = session.get(ObjectInstance, target.rid)
    assert remaining is not None
    assert remaining.data["name"] == "Alice"
    assert remaining.data["email"] == "alice@example.com"

    assert session.get(ObjectInstance, source.rid) is None

    incoming = session.exec(
        select(LinkedObject).where(LinkedObject.to_object_rid == target.rid)
    ).all()
    assert len(incoming) == 1
    assert incoming[0].from_object_rid != source.rid

    outgoing = session.exec(
        select(LinkedObject).where(LinkedObject.from_object_rid == target.rid)
    ).all()
    assert len(outgoing) == 1


def _mk_expense_ot(service: MetamodelService):
    req = ObjectTypePutRequest(
        displayName="Expense",
        description=None,
        primaryKey="id",
        properties={
            "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
            "status": PropertyDefinition(dataType="string", displayName="Status", required=False),
        },
    )
    service.upsert_object_type("expense", req)


def _seed_expense(session: Session, status: str):
    isvc = ActionsService(session, service="ontology", instance="default")
    properties = {"id": "e1", "status": status}
    obj = isvc.instances.upsert_object(
        object_type_api_name="expense",
        pk_value="e1",
        body={"properties": properties},
    )
    session.commit()
    return obj


def _mk_action(session: Session) -> ActionType:
    # ensure table exists for the in-memory session engine
    SQLModel.metadata.create_all(session.get_bind())
    act = ActionType(
        service="ontology",
        instance="default",
        api_name="approve_expense",
        display_name="Approve Expense",
        description="Approve an expense",
        target_object_type_api_name="expense",
        submission_criteria=[{"rule_logic": "target_object['properties']['status'] == 'PENDING'"}],
        executor_key="system.log_message",
    )
    session.add(act)
    session.commit()
    session.refresh(act)
    return act


def test_actions_service_discovery_and_execute(session):
    mm = MetamodelService(session, service="ontology", instance="default")
    _mk_expense_ot(mm)

    # Clean up any existing expense objects to ensure test isolation

    existing = session.exec(select(ObjectInstance).where(ObjectInstance.pk_value == "e1")).all()
    for obj in existing:
        session.delete(obj)
    session.commit()

    # seed draft expense
    _seed_expense(session, status="DRAFT")

    # create action type
    _mk_action(session)

    svc = ActionsService(session, service="ontology", instance="default")

    # not available while DRAFT
    lst = svc.list_available_actions("expense", "e1")
    assert lst == []

    # change to PENDING
    _seed_expense(session, status="PENDING")
    lst2 = svc.list_available_actions("expense", "e1")
    assert [a.api_name for a in lst2] == ["approve_expense"]

    # execute with required params
    res = svc.execute_action("expense", "e1", "approve_expense", {"message": "ok"})
    assert res.get("status") == "success"
    assert res.get("message") == "ok"

    # missing param -> 400
    import pytest

    with pytest.raises(HTTPException) as exc:
        svc.execute_action("expense", "e1", "approve_expense", {})
    assert exc.value.status_code == 400  # type: ignore[attr-defined]
