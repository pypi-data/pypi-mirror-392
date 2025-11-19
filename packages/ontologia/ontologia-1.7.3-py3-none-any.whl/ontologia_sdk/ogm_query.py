from __future__ import annotations

from typing import Any


class OGMQuery:
    """Fluent OGM query builder that works in both remote and local modes.

    - In remote mode: executes via API `POST /objects/{type}/search?use_ogm=true`.
    - In local mode + use_ogm: executes via local InstancesService.search_objects under OGM Ontology.
    - Falls back to session.list_objects when OGM not available.
    """

    def __init__(self, client_session, object_type: str):
        self._session = client_session
        self._type = object_type
        self._filters: list[tuple[str, str, Any]] = []
        self._order_by: list[tuple[str, str]] = []
        self._limit: int = 100
        self._offset: int = 0

    def where(self, field: str, operator: str, value: Any) -> OGMQuery:
        self._filters.append((field, operator, value))
        return self

    def order_by(self, field: str, direction: str = "asc") -> OGMQuery:
        self._order_by.append((field, direction.lower()))
        return self

    def limit(self, n: int) -> OGMQuery:
        self._limit = n
        return self

    def offset(self, n: int) -> OGMQuery:
        self._offset = n
        return self

    async def all(self) -> list[dict[str, Any]]:
        # Remote path if session is RemoteSession-like
        if hasattr(self._session, "_client") and hasattr(self._session, "_headers"):
            # Build ObjectSearchRequest payload
            where = [
                {"property": f, "op": self._normalize_op(op), "value": v}
                for f, op, v in self._filters
            ]
            order_by = [{"property": f, "direction": d} for f, d in self._order_by]
            payload = {
                "where": where,
                "orderBy": order_by,
                "limit": self._limit,
                "offset": self._offset,
            }
            # Use httpx client directly to keep dependency minimal

            params = {"use_ogm": "true"}
            url = self._session._build_url(f"objects/{self._type}/search")
            resp = await self._session._client.post(
                url, headers=self._session._headers, params=params, json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                obj.get("properties", {}) | {"pk": obj.get("pkValue")}
                for obj in data.get("objects", [])
            ]

        # Local OGM path via InstancesService
        if getattr(self._session, "_use_ogm", False):
            try:
                from ontologia.ogm import get_model_class

                model = get_model_class(self._type)
                if model is not None and hasattr(model, "_db"):
                    db = model._db
                    service, instance = db.get_default_scope()
                    from ontologia.application.instances_service import (
                        ObjectSearchRequest,
                        SearchFilter,
                        SearchOrder,
                    )

                    req = ObjectSearchRequest(
                        filters=[
                            SearchFilter(field=f, operator=self._normalize_op(op), value=v)
                            for f, op, v in self._filters
                        ],
                        order_by=[SearchOrder(field=f, direction=d) for f, d in self._order_by],
                        limit=self._limit,
                        offset=self._offset,
                    )
                    with db.get_session() as session:
                        from ontologia.ogm.connection import CoreServiceProvider

                        provider = CoreServiceProvider(session)
                        resp = provider.instances_service().search_objects(
                            service, instance, self._type, req
                        )
                        return [dict(o.properties or {}) | {"pk": o.pk_value} for o in resp.objects]
            except Exception:
                pass

        # Fallback to list_objects
        return await self._session.list_objects(self._type, limit=self._limit, offset=self._offset)

    def _normalize_op(self, op: str) -> str:
        return op.lower().replace("lte", "le").replace("gte", "ge")


__all__ = ["OGMQuery"]
