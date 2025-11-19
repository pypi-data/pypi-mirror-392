from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from ontologia_edge.enrichment import ContextProvider

logger = logging.getLogger(__name__)


class OGMContextProvider(ContextProvider):
    """Context provider that loads enrichment data via OGM models.

    Configure with a map of objectTypeApiName -> dict of:
        - links: list[str] linkType api names to traverse for enrichment
        - fields: list[str] fields to include from the root object

    If a model for a given object type is not registered, provider returns empty context.
    """

    def __init__(self, config: dict[str, dict[str, Any]] | None = None) -> None:
        self._config = config or {}

    async def fetch(self, snapshot) -> Mapping[str, Mapping[str, object]]:
        from ontologia.ogm import get_model_class

        object_type = snapshot.object_type
        entity_id = snapshot.entity_id
        conf = self._config.get(object_type, {})
        result: dict[str, dict[str, object]] = {}

        model = get_model_class(object_type)
        if model is None:
            return result

        try:
            obj = model.get(entity_id)
        except Exception:
            return result

        # Include fields from root object
        fields = conf.get("fields") or []
        if fields:
            data = obj.model_dump()
            result["object"] = {k: data.get(k) for k in fields if k in data}

        # Traverse links for enrichment
        for link_api_name in conf.get("links", []):
            try:
                # First try attribute by name; otherwise find attribute whose link api_name matches
                proxy = getattr(obj, link_api_name, None)
                if proxy is None:
                    # Scan class dict for LinkModel descriptors with matching api_name
                    from ontologia.ogm.link import LinkModel as _LinkModel

                    for attr_name, descriptor in obj.__class__.__dict__.items():
                        if (
                            isinstance(descriptor, _LinkModel)
                            and descriptor.api_name == link_api_name
                        ):
                            proxy = getattr(obj, attr_name, None)
                            break
                if proxy is None:
                    continue
                # Support 1:1 and 1:N
                if hasattr(proxy, "all"):
                    targets = proxy.all()
                    result[link_api_name] = {
                        "count": len(targets),
                        "items": [t.model_dump() for t in targets],
                    }
                else:
                    target = proxy.get()
                    if target is not None:
                        result[link_api_name] = target.model_dump()
            except Exception:
                logger.debug("OGM enrichment for link failed", exc_info=True)
                continue

        return result


__all__ = ["OGMContextProvider"]
