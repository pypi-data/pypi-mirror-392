"""REST endpoints for object instances."""

from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session

from ontologia_api.core.auth import UserPrincipal, require_role
from ontologia_api.core.database import get_session
from ontologia_api.handlers.instances import (
    ObjectInstanceCommandService,
    ObjectInstanceQueryService,
    get_instance_admin_command_service,
    get_instance_command_service,
    get_instance_query_service,
)
from ontologia_api.services.analytics_service import AnalyticsService
from ontologia_api.v2.schemas.bulk import ObjectBulkLoadRequest
from ontologia_api.v2.schemas.instances import (
    ObjectListResponse,
    ObjectReadResponse,
    ObjectUpsertRequest,
)
from ontologia_api.v2.schemas.search import (
    AggregateForTypeRequest,
    AggregateRequest,
    AggregateResponse,
    ObjectSearchRequest,
    WhereCondition,
)

"""Dual-mode endpoints (service + OGM).

This module lazily initializes an OGM Ontology bound to the same database
engine used by the API and auto-registers Python ObjectModel definitions.
"""

# OGM imports for dual-mode support
try:  # Prefer optional OGM integration
    from ontologia.ogm import Ontology, get_model_class

    OGM_AVAILABLE = True
except Exception:  # pragma: no cover - OGM optional
    OGM_AVAILABLE = False
    Ontology = None  # type: ignore[assignment]
    get_model_class = None  # type: ignore[assignment]

# Bind to API engine for OGM when available
from ontologia_api.core.database import engine as _api_engine

# Cache Ontology instances per (service, instance)
_ogm_ontologies: dict[tuple[str, str], object] = {}


def _ensure_models_registered(ontology: "Ontology") -> None:
    """Import Python OGM model definitions and register them with this ontology.

    Idempotent: safe to call multiple times; registration updates the bound ontology.
    """
    try:
        # Import package that contains ObjectModel subclasses and walk submodules
        import importlib
        import inspect
        import pkgutil
        from types import ModuleType

        from ontologia.ogm import ObjectModel as _OM

        root_pkg_name = "ontology_definitions.models"
        try:
            root_pkg: ModuleType = importlib.import_module(root_pkg_name)
        except ModuleNotFoundError:
            return

        def _register_from_module(mod: ModuleType) -> None:
            for _, obj in inspect.getmembers(mod, inspect.isclass):
                if obj is _OM:
                    continue
                try:
                    if issubclass(obj, _OM) and hasattr(obj, "__object_type_api_name__"):
                        ontology.model(obj)
                except Exception:
                    continue

        _register_from_module(root_pkg)
        if hasattr(root_pkg, "__path__"):
            for sub in pkgutil.walk_packages(root_pkg.__path__, prefix=root_pkg.__name__ + "."):
                try:
                    m = importlib.import_module(sub.name)
                except Exception:
                    continue
                _register_from_module(m)
    except Exception:
        # Be resilient; failing to auto-register must not break API boot
        pass


def get_ogm_ontology(service: str, instance: str):
    """Get or create an OGM Ontology bound to the API's engine for a scope."""
    if not OGM_AVAILABLE:
        return None
    key = (service, instance)
    onto = _ogm_ontologies.get(key)
    if onto is None:
        onto = Ontology(_api_engine, service=service, instance=instance)  # type: ignore[misc]
        _ensure_models_registered(onto)
        _ogm_ontologies[key] = onto
    return onto


# OGM helper functions
def _ogm_upsert_object(*args, **kwargs) -> ObjectReadResponse:
    """Upsert an object using OGM.

    Backward-compatible signature:
      - _ogm_upsert_object(object_type_api_name, pk, properties)
      - _ogm_upsert_object(service, instance, object_type_api_name, pk, properties)
    """
    if len(args) == 3:
        service, instance = "default", "runtime"
        object_type_api_name, pk, properties = args
    elif len(args) == 5:
        service, instance, object_type_api_name, pk, properties = args
    else:
        service = kwargs.get("service", "default")
        instance = kwargs.get("instance", "runtime")
        object_type_api_name = kwargs["object_type_api_name"]
        pk = kwargs["pk"]
        properties = kwargs["properties"]

    ontology = get_ogm_ontology(service, instance)
    if not ontology:
        raise HTTPException(status_code=500, detail="OGM not available")

    model_class = get_model_class(object_type_api_name)
    if not model_class:
        raise HTTPException(
            status_code=400, detail=f"OGM model not found for {object_type_api_name}"
        )

    # Create or update instance; handle NotFound gracefully
    try:
        obj = model_class.get(pk)
        for key, value in properties.items():
            setattr(obj, key, value)
    except Exception:
        obj = model_class(**{model_class.__primary_key__: pk, **properties})
    obj.save()

    return ObjectReadResponse(
        rid=f"obj-{object_type_api_name}-{pk}",
        objectTypeApiName=object_type_api_name,
        pkValue=pk,
        properties=properties,
    )


def _ogm_get_object(*args, **kwargs) -> ObjectReadResponse:
    """Get an object using OGM (supports legacy 3-arg call)."""
    if len(args) == 2 or len(args) == 3:
        service, instance = "default", "runtime"
        object_type_api_name, pk = args[0], args[1]
        args[2] if len(args) == 3 else None
    else:
        service = kwargs.get("service", "default")
        instance = kwargs.get("instance", "runtime")
        object_type_api_name = kwargs["object_type_api_name"]
        pk = kwargs["pk"]
        kwargs.get("valid_at")

    ontology = get_ogm_ontology(service, instance)
    if not ontology:
        raise HTTPException(status_code=500, detail="OGM not available")

    model_class = get_model_class(object_type_api_name)
    if not model_class:
        raise HTTPException(
            status_code=400, detail=f"OGM model not found for {object_type_api_name}"
        )

    try:
        obj = model_class.get(pk)
    except Exception:
        raise HTTPException(status_code=404, detail="Object not found")

    # Use model_dump for clean properties
    properties = obj.model_dump(exclude={model_class.__primary_key__})

    return ObjectReadResponse(
        rid=f"obj-{object_type_api_name}-{pk}",
        objectTypeApiName=object_type_api_name,
        pkValue=pk,
        properties=properties,
    )


def _ogm_delete_object(*args, **kwargs) -> bool:
    """Delete an object using OGM (supports legacy 2-arg call)."""
    if len(args) == 2:
        service, instance = "default", "runtime"
        object_type_api_name, pk = args
    elif len(args) == 4:
        service, instance, object_type_api_name, pk = args
    else:
        service = kwargs.get("service", "default")
        instance = kwargs.get("instance", "runtime")
        object_type_api_name = kwargs["object_type_api_name"]
        pk = kwargs["pk"]

    ontology = get_ogm_ontology(service, instance)
    if not ontology:
        raise HTTPException(status_code=500, detail="OGM not available")

    model_class = get_model_class(object_type_api_name)
    if not model_class:
        raise HTTPException(
            status_code=400, detail=f"OGM model not found for {object_type_api_name}"
        )

    try:
        obj = model_class.get(pk)
    except Exception:
        return False
    obj.delete()
    return True


def _ogm_list_objects(
    service: str,
    instance: str,
    object_type_api_name: str,
    limit: int,
    offset: int,
    valid_at: datetime | None = None,
) -> ObjectListResponse:
    ontology = get_ogm_ontology(service, instance)
    if not ontology:
        raise HTTPException(status_code=500, detail="OGM not available")

    with ontology.get_session() as session:  # type: ignore[union-attr]
        provider = ontology.get_core_provider(session)  # type: ignore[union-attr]
        resp = provider.instances_service().list_objects(
            service, instance, object_type_api_name, limit=limit, offset=offset, valid_at=valid_at
        )
        # Map back to API DTO
        return ObjectListResponse(
            data=[
                ObjectReadResponse(
                    rid=getattr(o, "rid", f"obj-{object_type_api_name}-{r.pk_value}"),
                    objectTypeApiName=object_type_api_name,
                    pkValue=r.pk_value,
                    properties=dict(r.properties or {}),
                )
                for r in resp.objects
                for o in [r]
            ]
        )


def _map_where_to_filters(where: list[WhereCondition]):
    from ontologia.application.instances_service import SearchFilter

    def op_map(op: str, value):
        op = op.lower()
        if op in ("eq", "ne", "lt", "lte", "gt", "gte", "in"):
            return (
                op.replace("lte", "le").replace("gte", "ge"),
                list(value) if op == "in" else value,
            )
        if op in ("contains", "startswith", "endswith"):
            pattern = (
                f"%{value}%"
                if op == "contains"
                else f"{value}%" if op == "startswith" else f"%{value}"
            )
            return ("ilike", pattern)
        if op == "isnull":
            return ("eq", None)
        if op == "isnotnull":
            # Not equal to None
            return ("ne", None)
        # Fallback
        return ("eq", value)

    filters = []
    for cond in where:
        op, val = op_map(cond.op, cond.value)
        filters.append(SearchFilter(field=cond.property, operator=op, value=val))
    return filters


def _ogm_search_objects(
    service: str,
    instance: str,
    object_type_api_name: str,
    body: ObjectSearchRequest,
) -> ObjectListResponse:
    ontology = get_ogm_ontology(service, instance)
    if not ontology:
        raise HTTPException(status_code=500, detail="OGM not available")

    from ontologia.application.instances_service import (
        ObjectSearchRequest as DomainSearchRequest,
    )
    from ontologia.application.instances_service import (
        SearchOrder,
    )

    domain_req = DomainSearchRequest(
        filters=_map_where_to_filters(body.where),
        order_by=[SearchOrder(field=o.property, direction=o.direction) for o in body.orderBy],
        limit=body.limit,
        offset=body.offset,
    )

    with ontology.get_session() as session:  # type: ignore[union-attr]
        provider = ontology.get_core_provider(session)  # type: ignore[union-attr]
        resp = provider.instances_service().search_objects(
            service, instance, object_type_api_name, domain_req
        )
        return ObjectListResponse(
            data=[
                ObjectReadResponse(
                    rid=getattr(o, "rid", f"obj-{object_type_api_name}-{r.pk_value}"),
                    objectTypeApiName=object_type_api_name,
                    pkValue=r.pk_value,
                    properties=dict(r.properties or {}),
                )
                for r in resp.objects
                for o in [r]
            ]
        )


router = APIRouter()


@router.put(
    "/objects/{objectTypeApiName}/{pk}",
    response_model=ObjectReadResponse,
    summary="Create or update object instance",
    description="Creates a new object instance or updates an existing one by ObjectType and primary key.",
)
def upsert_object_instance(
    body: ObjectUpsertRequest,
    request: Request,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_command_service),
    principal: UserPrincipal = Depends(require_role("editor")),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
) -> ObjectReadResponse:
    # Extract scope from path params
    ontology_api_name = request.path_params.get("ontologyApiName") or "default"
    instance_name = "runtime"

    # Dual-mode: OGM or Service-based
    if use_ogm and OGM_AVAILABLE:
        try:
            return _ogm_upsert_object(
                ontology_api_name, instance_name, objectTypeApiName, pk, body.properties
            )
        except Exception:
            # Fall back to service-based if OGM fails
            pass

    # Service-based approach (original logic)
    r = command_service.upsert_object(objectTypeApiName, pk, body)
    # Accept both API DTO (camelCase) and domain/mock (snake_case) attributes
    pk_camel = getattr(r, "pkValue", None)
    pk_snake = getattr(r, "pk_value", None)
    pk_val = pk if not isinstance(pk_snake, str) and not isinstance(pk_camel, str) else (
        pk_snake if isinstance(pk_snake, str) and pk_snake else pk_camel
    )
    # Ensure pk_val is a string for the response
    pk_val = str(pk_val) if pk_val is not None else ""
    rid_val = getattr(r, "rid", f"obj-{objectTypeApiName}-{pk_val}")
    return ObjectReadResponse(
        rid=rid_val,
        objectTypeApiName=objectTypeApiName,
        pkValue=pk_val,
        properties=dict(getattr(r, "properties", {}) or {}),
    )


@router.get(
    "/objects/{objectTypeApiName}/{pk}",
    response_model=ObjectReadResponse,
    summary="Get object instance",
    description="Returns a single object instance by ObjectType and primary key.",
)
def get_object_instance(
    request: Request,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
    principal: UserPrincipal = Depends(require_role("viewer")),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
) -> ObjectReadResponse:
    # Extract scope from path params
    ontology_api_name = request.path_params.get("ontologyApiName") or "default"
    instance_name = "runtime"

    # Dual-mode: OGM or Service-based
    if use_ogm and OGM_AVAILABLE:
        try:
            return _ogm_get_object(ontology_api_name, instance_name, objectTypeApiName, pk, validAt)
        except Exception:
            # Fall back to service-based if OGM fails
            pass

    # Service-based approach (original logic)
    r = query_service.get_object(
        object_type_api_name=objectTypeApiName,
        pk_value=pk,
        as_of=validAt,
        change_set_rid=changeSetRid,
    )
    # Some implementations may return None when not found
    if r is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    pk_camel = getattr(r, "pkValue", None)
    pk_snake = getattr(r, "pk_value", None)
    pk_val = pk if not isinstance(pk_snake, str) and not isinstance(pk_camel, str) else (
        pk_snake if isinstance(pk_snake, str) and pk_snake else pk_camel
    )
    # Ensure pk_val is a string for the response
    pk_val = str(pk_val) if pk_val is not None else ""
    rid_val = getattr(r, "rid", f"obj-{objectTypeApiName}-{pk_val}")
    return ObjectReadResponse(
        rid=rid_val,
        objectTypeApiName=objectTypeApiName,
        pkValue=pk_val,
        properties=dict(getattr(r, "properties", {}) or {}),
    )


@router.delete(
    "/objects/{objectTypeApiName}/{pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete object instance",
    description="Deletes an object instance by ObjectType and primary key.",
)
def delete_object_instance(
    request: Request,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    pk: str = Path(..., description="Primary key value of the instance"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_admin_command_service),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
):
    # Extract scope from path params
    ontology_api_name = request.path_params.get("ontologyApiName") or "default"
    instance_name = "runtime"

    # Dual-mode: OGM or Service-based
    if use_ogm and OGM_AVAILABLE:
        try:
            ok = _ogm_delete_object(ontology_api_name, instance_name, objectTypeApiName, pk)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Object not found"
                )
            return None
        except Exception:
            # Fall back to service-based if OGM fails
            pass

    # Service-based approach (original logic)
    ok = command_service.delete_object(objectTypeApiName, pk)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")
    return None


@router.get(
    "/objects",
    response_model=ObjectListResponse,
    summary="List object instances",
    description="Lists object instances; optionally filter by objectType via query param.",
)
def list_objects(
    request: Request,
    objectType: str | None = Query(default=None, description="Filter by ObjectType apiName"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
) -> ObjectListResponse:
    # Extract ontologyApiName from request path params
    request.path_params.get("ontologyApiName")

    # Service-based approach (original logic)
    return query_service.list_objects(
        object_type_api_name=objectType,
        limit=limit,
        offset=offset,
        valid_at=validAt,
        change_set_rid=changeSetRid,
    )


@router.get(
    "/objects/{objectTypeApiName}",
    response_model=ObjectListResponse,
    summary="List object instances for a specific ObjectType",
    description="Lists object instances for a specific ObjectType.",
)
def list_objects_by_type(
    request: Request,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
) -> ObjectListResponse:
    # Extract ontologyApiName from request path params
    ontology_api_name = request.path_params.get("ontologyApiName")

    if use_ogm and OGM_AVAILABLE:
        try:
            return _ogm_list_objects(
                ontology_api_name or "default", "runtime", objectTypeApiName, limit, offset, validAt
            )
        except Exception:
            pass
    return query_service.list_objects(
        object_type_api_name=objectTypeApiName,
        limit=limit,
        offset=offset,
        valid_at=validAt,
        change_set_rid=changeSetRid,
    )


@router.post(
    "/objects/{objectTypeApiName}/search",
    response_model=ObjectListResponse,
    summary="Search object instances",
    description="Search for object instances by properties with filtering, ordering, and pagination.",
)
def search_objects(
    request: Request,
    body: ObjectSearchRequest,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
) -> ObjectListResponse:
    # Extract ontologyApiName from request path params
    ontology_api_name = request.path_params.get("ontologyApiName")

    if use_ogm and OGM_AVAILABLE:
        try:
            return _ogm_search_objects(
                ontology_api_name or "default", "runtime", objectTypeApiName, body
            )
        except Exception:
            pass
    return query_service.search_objects(
        objectTypeApiName,
        body,
        change_set_rid=changeSetRid,
    )


@router.post(
    "/objects/{objectTypeApiName}/aggregate",
    response_model=AggregateResponse,
    summary="Aggregate object instances",
    description="Aggregate object instances by specified criteria.",
)
def aggregate_objects(
    request: Request,
    body: AggregateForTypeRequest,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> AggregateResponse:
    # Extract ontologyApiName from request path params
    ontology_api_name = request.path_params.get("ontologyApiName")

    # Use AnalyticsService like the original implementation
    svc = AnalyticsService(
        session, service="ontology", instance=ontology_api_name or "default", principal=principal
    )
    req = AggregateRequest(
        objectTypeApiName=objectTypeApiName,
        where=body.where,
        groupBy=body.groupBy,
        metrics=body.metrics,
    )
    return svc.aggregate(req)


@router.post(
    "/objects/{objectTypeApiName}/load",
    response_model=ObjectListResponse,
    summary="Create or update multiple objects",
    description="Create or update multiple objects in a single call.",
)
def bulk_load_objects(
    request: Request,
    body: ObjectBulkLoadRequest,
    objectTypeApiName: str = Path(..., description="API name of the ObjectType"),
    command_service: ObjectInstanceCommandService = Depends(get_instance_command_service),
) -> ObjectListResponse:
    # Extract ontologyApiName from request path params
    request.path_params.get("ontologyApiName")

    # Service-based approach (original logic)
    return command_service.bulk_load_objects(objectTypeApiName, body)


@router.get(
    "/objects/{objectTypeApiName}/{pk}/{linkTypeApiName}",
    response_model=ObjectListResponse,
    summary="Get linked objects",
    description="Traverse from a starting object along a LinkType to retrieve connected objects.",
)
def get_linked_objects(
    request: Request,
    objectTypeApiName: str = Path(..., description="API name of the starting ObjectType"),
    pk: str = Path(..., description="Primary key of the starting object instance"),
    linkTypeApiName: str = Path(..., description="API name of the LinkType used for traversal"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    direction: str = Query(
        default="outgoing", description="Traversal direction: outgoing or incoming"
    ),
    validAt: datetime | None = Query(
        default=None,
        description="Timestamp used for bitemporal validity filtering",
    ),
    changeSetRid: str | None = Header(
        default=None,
        alias="X-Ontologia-ChangeSet-Rid",
        description="RID of ChangeSet overlay for what-if scenarios",
    ),
    query_service: ObjectInstanceQueryService = Depends(get_instance_query_service),
    use_ogm: bool = Query(default=False, description="Use OGM for this operation"),
) -> ObjectListResponse:
    # Extract ontologyApiName from request path params
    ontology_api_name = request.path_params.get("ontologyApiName")

    if use_ogm and OGM_AVAILABLE:
        try:
            ontology = get_ogm_ontology(ontology_api_name or "default", "runtime")
            if not ontology:
                raise RuntimeError("OGM not available")
            with ontology.get_session() as session:  # type: ignore[union-attr]
                provider = ontology.get_core_provider(session)  # type: ignore[union-attr]
                los = provider.linked_objects_service()
                resp = los.traverse_linked_objects(
                    ontology_api_name or "default",
                    "runtime",
                    object_type_api_name=objectTypeApiName,
                    pk_value=pk,
                    link_type_api_name=linkTypeApiName,
                    direction=direction,
                    limit=limit,
                    offset=offset,
                    valid_at=validAt,
                )
                # Convert linked edges to object reads
                ios = provider.instances_service()
                objs = []
                for edge in resp.linked_objects:
                    target_pk = edge.target_pk_value
                    dto = ios.get_object(
                        ontology_api_name or "default",
                        "runtime",
                        edge.target_object_type_api_name,
                        target_pk,
                    )
                    objs.append(
                        ObjectReadResponse(
                            rid=getattr(
                                dto, "rid", f"obj-{edge.target_object_type_api_name}-{target_pk}"
                            ),
                            objectTypeApiName=edge.target_object_type_api_name,
                            pkValue=target_pk,
                            properties=dict(dto.properties or {}),
                        )
                    )
                return ObjectListResponse(data=objs)
        except Exception:
            pass
    return query_service.get_linked_objects(
        objectTypeApiName,
        pk,
        linkTypeApiName,
        limit=limit,
        offset=offset,
        valid_at=validAt,
        change_set_rid=changeSetRid,
    )
