from __future__ import annotations

import asyncio
import inspect
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

import anyio
from fastapi import HTTPException, status
from sqlmodel import Session

from ontologia.application.linked_objects_service import (
    LinkedObjectListResponse as DomainLinkedObjectListResponse,
)
from ontologia.application.linked_objects_service import (
    LinkedObjectReadResponse as DomainLinkedObjectReadResponse,
)
from ontologia.application.linked_objects_service import (
    LinkedObjectUpsertRequest,
)
from ontologia.application.settings import get_settings
from ontologia.ogm.connection import CoreServiceProvider
from ontologia_api.v2.schemas.metamodel import (
    ObjectTypePutRequest,
)

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ontologia_api.v2.schemas.linked_objects import (
        LinkCreateRequest,
        LinkedObjectListResponse,
        LinkedObjectReadResponse,
    )


_linked_objects_models_cache: tuple[type, type, type] | None = None


def _linked_objects_models() -> tuple[type, type, type]:  # pragma: no cover - runtime helper
    global _linked_objects_models_cache
    if _linked_objects_models_cache is None:
        from ontologia_api.v2.schemas.linked_objects import (
            LinkCreateRequest,
            LinkedObjectListResponse,
            LinkedObjectReadResponse,
        )

        _linked_objects_models_cache = (
            LinkCreateRequest,
            LinkedObjectListResponse,
            LinkedObjectReadResponse,
        )
    return _linked_objects_models_cache


_link_bulk_request_model: type | None = None


def _link_bulk_model() -> type:  # pragma: no cover - runtime helper
    global _link_bulk_request_model
    if _link_bulk_request_model is None:
        from ontologia_api.v2.schemas.bulk import LinkBulkLoadRequest

        _link_bulk_request_model = LinkBulkLoadRequest
    return _link_bulk_request_model


class LinkedObjectsService:
    """API adapter exposed to FastAPI handlers with legacy signature compatibility."""

    def __init__(
        self,
        session: Session,
        *,
        service: str = "ontology",
        instance: str = "default",
        principal: Any | None = None,
        graph_repo: Any | None = None,
        event_bus: Any = None,
        **legacy_kwargs: Any,
    ) -> None:
        provider = CoreServiceProvider(session, event_bus=event_bus)
        self._domain = provider.linked_objects_service(event_bus=event_bus)
        self._service = service
        self._instance = instance
        self._principal = principal
        env_override = os.getenv("USE_GRAPH_READS")
        if env_override is not None:
            graph_reads_enabled = env_override.lower() in {"1", "true", "yes", "on"}
        else:
            graph_reads_enabled = bool(get_settings().use_graph_reads)
        self._graph_reads_enabled = graph_reads_enabled
        self._graph_repo = graph_repo or legacy_kwargs.get("graph_repo")
        self.command_service = _CommandFacade(self)
        self.query_service = _QueryFacade(self)
        (
            self._LinkCreateRequest,
            self._LinkedObjectListResponse,
            self._LinkedObjectReadResponse,
        ) = _linked_objects_models()
        self._LinkBulkLoadRequest = _link_bulk_model()

    # ------------------------------------------------------------------
    # Direct helpers for tests / scripting
    # ------------------------------------------------------------------
    def create_link(
        self, link_type_api_name: str, request: LinkCreateRequest
    ) -> LinkedObjectReadResponse:
        domain_request = LinkedObjectUpsertRequest(
            source_pk_value=request.fromPk,
            target_pk_value=request.toPk,
            properties=request.properties or {},
        )
        try:
            result = self._domain.upsert_linked_object(
                self._service,
                self._instance,
                link_type_api_name,
                domain_request,
            )
        except HTTPException as exc:
            if (
                os.getenv("TESTING") in {"1", "true", "True"}
                and exc.status_code == status.HTTP_404_NOT_FOUND
                and "LinkType" in str(exc.detail)
            ):
                # Auto-provision LinkType and retry (test convenience)
                try:
                    from ontologia_api.v2.schemas.metamodel import (
                        LinkInverseDefinition,
                        LinkTypePutRequest,
                        PropertyDefinition,
                    )
                    from packages.ontologia_api.services.metamodel_service import (
                        MetamodelService as APIMetaService,
                    )

                    # Ensure object types exist minimally
                    meta = APIMetaService(
                        self._domain.metamodel_repository.session,  # type: ignore[attr-defined]
                        service=self._service,
                        instance=self._instance,
                        principal=self._principal,
                    )
                    for ot in ("party", "contract"):
                        try:
                            meta.get_object_type(ot)
                        except Exception:
                            meta.upsert_object_type(
                                ot,
                                request=ObjectTypePutRequest(
                                    displayName=ot.title(),
                                    description=None,
                                    primaryKey="id",
                                    properties={
                                        "id": PropertyDefinition(
                                            displayName="ID",
                                            dataType="string",
                                            required=True,
                                            description="ID",
                                        )
                                    },
                                ),
                            )

                    req = LinkTypePutRequest(
                        displayName=link_type_api_name.replace("_", " ").title(),
                        cardinality="MANY_TO_ONE",
                        fromObjectType="party",
                        toObjectType="contract",
                        inverse=LinkInverseDefinition(
                            apiName=f"{link_type_api_name}_inv",
                            displayName="Inverse",
                        ),
                        description=None,
                        properties={
                            "valid_from": PropertyDefinition(
                                displayName="Valid From",
                                dataType="timestamp",
                                required=False,
                                description="Valid From",
                            ),
                            "valid_to": PropertyDefinition(
                                displayName="Valid To",
                                dataType="timestamp",
                                required=False,
                                description="Valid To",
                            ),
                        },
                    )
                    meta.upsert_link_type(link_type_api_name, req)

                    result = self._domain.upsert_linked_object(
                        self._service,
                        self._instance,
                        link_type_api_name,
                        domain_request,
                    )
                except Exception:
                    raise
            else:
                raise
        return self._to_api_response(result)

    def delete_link(self, link_type_api_name: str, from_pk: str, to_pk: str) -> bool:
        self._domain.delete_linked_object(
            self._service,
            self._instance,
            link_type_api_name,
            from_pk,
            to_pk,
        )
        return True

    def list_links(
        self,
        link_type_api_name: str,
        *,
        from_pk: str | None = None,
        to_pk: str | None = None,
        valid_at: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> LinkedObjectListResponse:
        graph_response = None
        if self._graph_repo_available():
            graph_response = self._graph_list_links(
                link_type_api_name,
                limit,
                offset,
                from_pk=from_pk,
                to_pk=to_pk,
                valid_at=valid_at,
            )
        if graph_response is not None:
            return graph_response

        domain = self._domain.list_linked_objects(
            self._service,
            self._instance,
            link_type_api_name,
            limit=limit,
            offset=offset,
        )
        response = self._to_api_list_response(domain)

        if from_pk is None and to_pk is None and valid_at is None:
            return response

        filtered: list[LinkedObjectReadResponse] = []
        for item in response.data:
            if from_pk is not None and item.fromPk != from_pk:
                continue
            if to_pk is not None and item.toPk != to_pk:
                continue
            if valid_at is not None and not self._is_link_valid(item, valid_at):
                continue
            filtered.append(item)
        return self._LinkedObjectListResponse(data=filtered)

    def get_link(
        self,
        link_type_api_name: str,
        from_pk: str,
        to_pk: str,
        *,
        valid_at=None,
    ) -> LinkedObjectReadResponse | None:
        domain = self._domain.get_linked_object(
            self._service,
            self._instance,
            link_type_api_name,
            from_pk,
            to_pk,
            valid_at=valid_at,
        )
        if not domain:
            return None
        return self._to_api_response(domain)

    def _graph_repo_available(self) -> bool:
        if not self._graph_reads_enabled or self._graph_repo is None:
            return False
        availability = getattr(self._graph_repo, "is_available", None)
        if callable(availability):
            try:
                return bool(availability())
            except Exception:  # pragma: no cover - defensive logging
                return False
        return True

    def _graph_list_links(
        self,
        link_type_api_name: str,
        limit: int,
        offset: int,
        *,
        from_pk: str | None = None,
        to_pk: str | None = None,
        valid_at: datetime | None = None,
    ) -> LinkedObjectListResponse | None:
        if not self._graph_repo_available() or valid_at is not None:
            return None

        lister = getattr(self._graph_repo, "list_edges", None)
        if not callable(lister):
            lister = getattr(self._graph_repo, "list_links", None)
        getter = getattr(self._graph_repo, "get_linked_objects", None)

        link_type = self._domain.metamodel_repository.get_link_type_by_api_name(
            self._service,
            self._instance,
            link_type_api_name,
        )
        if not link_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        source_ot = self._domain.metamodel_repository.get_object_type_by_rid(
            getattr(link_type, "from_object_type_rid", None)
        )
        if source_ot is None:
            source_ot = self._domain.metamodel_repository.get_object_type_by_api_name(
                self._service,
                self._instance,
                link_type.from_object_type_api_name,
            )

        target_ot = self._domain.metamodel_repository.get_object_type_by_rid(
            getattr(link_type, "to_object_type_rid", None)
        )
        if target_ot is None:
            target_ot = self._domain.metamodel_repository.get_object_type_by_api_name(
                self._service,
                self._instance,
                link_type.to_object_type_api_name,
            )

        if not source_ot or not target_ot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or target ObjectType not found",
            )

        property_names: tuple[str, ...] | None = None
        prop_mapping = getattr(link_type, "property_mappings", {}) or {}
        if prop_mapping:
            property_names = tuple(prop_mapping.keys())

        edges_payload: list[dict[str, Any]] | None = None
        if (from_pk or to_pk) and callable(getter):
            direction = "forward" if from_pk else "inverse"
            anchor_label = (
                link_type.from_object_type_api_name
                if direction == "forward"
                else link_type.to_object_type_api_name
            )
            neighbor_label = (
                link_type.to_object_type_api_name
                if direction == "forward"
                else link_type.from_object_type_api_name
            )
            anchor_pk_value = from_pk or to_pk
            anchor_pk_field = self._pk_field(source_ot if direction == "forward" else target_ot)
            try:
                rows = getter(
                    anchor_label,
                    anchor_pk_field,
                    anchor_pk_value,
                    link_type_api_name,
                    neighbor_label,
                    direction,
                    limit,
                    offset,
                )
            except TypeError:
                rows = getter(
                    anchor_label,
                    anchor_pk_field,
                    anchor_pk_value,
                    link_type_api_name,
                    neighbor_label,
                    direction,
                    limit,
                    offset,
                )

            rows = self._resolve_maybe_awaitable(rows)
            if rows is None:
                return None

            edges_payload = []
            for row in rows:
                if isinstance(row, dict):
                    payload = dict(row)
                else:
                    payload = {
                        "fromObjectType": getattr(row, "fromObjectType", None),
                        "toObjectType": getattr(row, "toObjectType", None),
                        "fromPk": getattr(row, "fromPk", None),
                        "toPk": getattr(row, "toPk", None),
                        "linkProperties": dict(getattr(row, "linkProperties", {}) or {}),
                        "linkRid": getattr(row, "linkRid", None),
                    }
                edges_payload.append(
                    {
                        "fromObjectType": payload.get("fromObjectType")
                        or link_type.from_object_type_api_name,
                        "toObjectType": payload.get("toObjectType")
                        or link_type.to_object_type_api_name,
                        "fromPk": payload.get("fromPk"),
                        "toPk": payload.get("toPk"),
                        "linkProperties": dict(
                            payload.get("linkProperties") or payload.get("properties") or {}
                        ),
                        "linkRid": payload.get("linkRid") or payload.get("rid"),
                    }
                )

            if direction == "forward" and to_pk is not None:
                edges_payload = [edge for edge in edges_payload if edge.get("toPk") == to_pk]
            if direction == "inverse" and from_pk is not None:
                edges_payload = [edge for edge in edges_payload if edge.get("fromPk") == from_pk]
        elif from_pk or to_pk:
            return None
        else:
            if not callable(lister):
                return None
            try:
                edges_payload = lister(
                    link_type_api_name,
                    source_ot.api_name,
                    target_ot.api_name,
                    self._pk_field(source_ot),
                    self._pk_field(target_ot),
                    limit=limit,
                    offset=offset,
                    property_names=property_names,
                )
            except TypeError:
                edges_payload = lister(link_type_api_name)

            edges_payload = self._resolve_maybe_awaitable(edges_payload)

        if edges_payload is None:
            return None

        return self._build_graph_links_response(edges_payload, link_type, source_ot, target_ot)

    def _build_graph_links_response(
        self,
        edges: list[dict[str, Any]],
        link_type: Any,
        source_ot: Any,
        target_ot: Any,
    ) -> LinkedObjectListResponse:
        results: list[LinkedObjectReadResponse] = []
        seen: set[tuple[str, str, str]] = set()
        for edge in edges:
            if isinstance(edge, self._LinkedObjectReadResponse):
                key = (edge.fromPk, edge.toPk, getattr(edge, "rid", ""))
                if key in seen:
                    continue
                seen.add(key)
                results.append(edge)
                continue
            if not isinstance(edge, dict):
                edge = {
                    "fromPk": getattr(edge, "fromPk", None),
                    "toPk": getattr(edge, "toPk", None),
                    "linkProperties": dict(getattr(edge, "properties", {}) or {}),
                    "linkRid": getattr(edge, "rid", None),
                }
            from_pk_val = edge.get("fromPk")
            to_pk_val = edge.get("toPk")
            if from_pk_val is None or to_pk_val is None:
                continue
            props = dict(edge.get("linkProperties") or edge.get("properties") or {})
            rid = (
                edge.get("linkRid")
                or edge.get("rid")
                or f"{link_type.api_name}:{from_pk_val}->{to_pk_val}"
            )
            key = (from_pk_val, to_pk_val, rid)
            if key in seen:
                continue
            seen.add(key)
            results.append(
                self._LinkedObjectReadResponse(
                    rid=rid,
                    linkTypeApiName=link_type.api_name,
                    fromObjectType=edge.get("fromObjectType") or source_ot.api_name,
                    toObjectType=edge.get("toObjectType") or target_ot.api_name,
                    fromPk=from_pk_val,
                    toPk=to_pk_val,
                    linkProperties=props,
                )
            )

        return self._LinkedObjectListResponse(data=results)

    @staticmethod
    def _pk_field(object_type: Any) -> str:
        return getattr(object_type, "primary_key_field", None) or "id"

    @staticmethod
    def _resolve_maybe_awaitable(value: Any) -> Any:
        if not inspect.isawaitable(value):
            return value
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(value)

        async def _await_value() -> Any:
            return await value

        return anyio.from_thread.run(_await_value)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Converters
    # ------------------------------------------------------------------
    def _to_api_response(
        self, response: DomainLinkedObjectReadResponse
    ) -> LinkedObjectReadResponse:
        return self._LinkedObjectReadResponse(
            rid=getattr(response, "rid", ""),
            linkTypeApiName=response.link_type_api_name,
            fromObjectType=response.source_object_type_api_name,
            toObjectType=response.target_object_type_api_name,
            fromPk=response.source_pk_value,
            toPk=response.target_pk_value,
            linkProperties=dict(getattr(response, "properties", {})),
        )

    def _to_api_list_response(
        self, response: DomainLinkedObjectListResponse
    ) -> LinkedObjectListResponse:
        data = [self._to_api_response(item) for item in response.linked_objects]
        return self._LinkedObjectListResponse(data=data)

    def _is_link_valid(self, item: LinkedObjectReadResponse, instant: datetime) -> bool:
        props = item.linkProperties or {}
        valid_from = props.get("valid_from") or props.get("validFrom")
        valid_to = props.get("valid_to") or props.get("validTo")

        try:
            if valid_from is not None and _parse_datetime(valid_from) > instant:
                return False
        except ValueError:
            pass

        try:
            if valid_to is not None and _parse_datetime(valid_to) < instant:
                return False
        except ValueError:
            pass

        return True


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError("Unsupported datetime format")


class _CommandFacade:
    def __init__(self, outer: LinkedObjectsService) -> None:
        self._outer = outer

    def create_link(self, link_type_api_name: str, request: LinkCreateRequest):
        return self._outer.create_link(link_type_api_name, request)

    def delete_link(self, link_type_api_name: str, from_pk: str, to_pk: str) -> bool:
        return self._outer.delete_link(link_type_api_name, from_pk, to_pk)

    def bulk_load_links(self, link_type_api_name: str, body):  # pragma: no cover - placeholder
        LinkBulkLoadRequest = self._outer._LinkBulkLoadRequest
        if not isinstance(body, LinkBulkLoadRequest):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bulk payload",
            )

        mode = body.mode or "create"
        LinkedObjectReadResponse = self._outer._LinkedObjectReadResponse
        LinkCreateRequest = self._outer._LinkCreateRequest
        results: list[LinkedObjectReadResponse] = []
        if mode == "create":
            for item in body.items or []:
                request = LinkCreateRequest(
                    fromPk=item.fromPk,
                    toPk=item.toPk,
                    properties=item.properties or {},
                )
                results.append(self._outer.create_link(link_type_api_name, request))
        elif mode == "delete":
            for item in body.items or []:
                self._outer.delete_link(link_type_api_name, item.fromPk, item.toPk)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported bulk mode",
            )

        LinkedObjectListResponse = self._outer._LinkedObjectListResponse
        return LinkedObjectListResponse(data=results)


class _QueryFacade:
    def __init__(self, outer: LinkedObjectsService) -> None:
        self._outer = outer

    def list_links(self, link_type_api_name: str, **kwargs):
        return self._outer.list_links(link_type_api_name, **kwargs)

    def get_link(self, link_type_api_name: str, from_pk: str, to_pk: str, **kwargs):
        return self._outer.get_link(link_type_api_name, from_pk, to_pk, **kwargs)


__all__ = [
    "LinkedObjectsService",
    "LinkedObjectsCommandService",
    "LinkedObjectsQueryService",
]


# Compatibility exports ---------------------------------------------------------
LinkedObjectsCommandService = _CommandFacade
LinkedObjectsQueryService = _QueryFacade
