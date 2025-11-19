from __future__ import annotations

import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ontologia.domain.metamodels.value_objects import PropertyDefinition
from ontologia.ogm.link import LinkModel, _link_registry
from ontologia.ogm.model import ObjectModel, _model_registry
from ontologia.ogm.schema import _build_link_type_aggregate, _build_object_type_aggregate


@dataclass(slots=True)
class PythonDefinitionSet:
    object_types: dict[str, dict[str, Any]]
    link_types: dict[str, dict[str, Any]]
    models: list[type[ObjectModel]]


def load_python_definitions(
    module: str,
    *,
    module_path: str | Path | None = None,
) -> PythonDefinitionSet:
    _reset_registries()
    _import_module_tree(module, module_path)
    models = list(_model_registry.keys())
    object_types = {_model_registry[m]["object_type_api_name"]: _object_to_dict(m) for m in models}
    link_types = {api_name: _link_to_dict(link) for api_name, link in _link_registry.items()}
    return PythonDefinitionSet(object_types=object_types, link_types=link_types, models=models)


def _reset_registries() -> None:
    _model_registry.clear()
    _link_registry.clear()


def _import_module_tree(module_name: str, module_path: str | Path | None) -> None:
    if module_path is not None:
        resolved = str(Path(module_path).resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)

    prefix = module_name + "."
    for name in list(sys.modules.keys()):
        if name == module_name or name.startswith(prefix):
            sys.modules.pop(name)

    module = importlib.import_module(module_name)

    if hasattr(module, "__path__"):
        for _, name, _ in pkgutil.walk_packages(module.__path__, prefix):
            importlib.import_module(name)


def _object_to_dict(model_cls: type[ObjectModel]) -> dict[str, Any]:
    meta = _model_registry[model_cls]
    aggregate = _build_object_type_aggregate(model_cls, meta["primary_key"])
    object_type = aggregate.object_type

    display = (
        getattr(model_cls, "__display_name__", None)
        or object_type.display_name
        or object_type.api_name
    )
    description = getattr(model_cls, "__description__", None) or object_type.description
    implements = list(getattr(model_cls, "__implements__", []) or [])

    properties = {}
    for prop in aggregate.properties:
        properties[prop.api_name] = _property_to_dict(prop)

    return {
        "apiName": object_type.api_name,
        "displayName": display,
        "description": description,
        "primaryKey": aggregate.primary_key.name,
        "properties": properties,
        "implements": implements,
    }


def _property_to_dict(prop: PropertyDefinition) -> dict[str, Any]:
    data: dict[str, Any] = {
        "dataType": prop.data_type,
        "displayName": prop.display_name or prop.api_name,
        "required": bool(prop.required or prop.is_primary_key),
    }
    if prop.description:
        data["description"] = prop.description
    if prop.quality_checks:
        data["qualityChecks"] = list(prop.quality_checks)
    if prop.security_tags:
        data["securityTags"] = list(prop.security_tags)
    if prop.data_type_config:
        data["dataTypeConfig"] = dict(prop.data_type_config)
    if prop.derivation_script:
        data["derivationScript"] = prop.derivation_script
    if prop.references_object_type_api_name:
        data["referencesObjectType"] = prop.references_object_type_api_name
    return data


def _link_to_dict(link: LinkModel) -> dict[str, Any]:
    aggregate = _build_link_type_aggregate(link.api_name, link)

    display_name = getattr(link, "display_name", None) or aggregate.display_name or link.api_name
    inverse_name = link.inverse or aggregate.inverse_api_name
    inverse_display = getattr(link, "inverse_display_name", None) or aggregate.inverse_display_name

    out: dict[str, Any] = {
        "apiName": link.api_name,
        "displayName": display_name or link.api_name,
        "cardinality": str(aggregate.cardinality.name),
        "fromObjectType": aggregate.from_object_type_api_name,
        "toObjectType": aggregate.to_object_type_api_name,
        "inverse": {
            "apiName": inverse_name or f"inverse_{link.api_name}",
            "displayName": inverse_display or _humanize(inverse_name or link.api_name),
        },
    }

    link_description = getattr(link, "description", None)
    if link_description:
        out["description"] = link_description

    properties = {}
    for name, definition in (link.properties or {}).items():
        if isinstance(definition, PropertyDefinition):
            properties[name] = _property_to_dict(definition)
        elif isinstance(definition, dict):
            properties[name] = dict(definition)
    if properties:
        out["properties"] = properties

    return out


def _humanize(value: str) -> str:
    cleaned = value.replace("_", " ")
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "Inverse"
