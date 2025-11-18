"""Schema evolution utilities for managing YAML definitions and migration tasks."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from sqlmodel import Session, select

from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)

logger = logging.getLogger(__name__)


class _PropertyAdapter(dict):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        for key, value in data.items():
            setattr(self, key, value)

    def model_dump(self) -> dict[str, Any]:
        return dict(self)


class _ObjectTypeRequestAdapter:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.primaryKey = payload.get("primaryKey", "id")
        self.properties = payload.get("properties", {})
        display_name = payload.get("displayName")
        self.displayName = display_name
        self.display_name = display_name
        self.description = payload.get("description")
        implements = payload.get("implements", [])
        self.implements = implements
        self.model_fields_set = {"implements"} if implements else set()

    def model_dump(self) -> dict[str, Any]:  # pragma: no cover - compatibility helper
        return {
            "displayName": self.displayName,
            "description": self.description,
            "primaryKey": self.primaryKey,
            "properties": {
                key: value.model_dump() if hasattr(value, "model_dump") else dict(value)
                for key, value in (self.properties or {}).items()
            },
            "implements": list(self.implements or []),
        }


class SchemaEvolutionService:
    """Plan and apply schema changes based on repository definitions."""

    def __init__(
        self,
        metamodel_service: Any,
        migration_service: Any | None = None,
        *,
        definitions_dir: str | Path | None = None,
        session: Session | None = None,
    ) -> None:
        self.metamodel_service = metamodel_service
        self.migration_service = migration_service
        self._definitions_dir = Path(definitions_dir) if definitions_dir else Path("definitions")
        self._session = session or self._resolve_session(metamodel_service)
        if self._session is None:
            raise ValueError("SchemaEvolutionService requires a SQLModel session")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def plan_schema_changes(
        self,
        definitions_dir: str | Path | None = None,
        *,
        include_impact: bool = False,
        include_dependencies: bool = False,
    ) -> dict[str, list[dict[str, Any]]]:
        _ = include_impact, include_dependencies  # placeholders for future enrichment
        directory = Path(definitions_dir) if definitions_dir else self._definitions_dir
        definitions = self._load_object_type_definitions(directory)
        plan: list[dict[str, Any]] = []
        for definition in definitions:
            entry = self._build_plan_entry(definition)
            if entry is not None:
                plan.append(entry)
        return {"plan": plan}

    def apply_schema_changes(
        self,
        *,
        allow_destructive: bool = False,
        definitions_dir: str | Path | None = None,
        regenerate_sdk: bool = False,
    ) -> dict[str, Any]:
        _ = regenerate_sdk  # placeholder for future behaviour
        directory = Path(definitions_dir) if definitions_dir else self._definitions_dir
        plan_info = self.plan_schema_changes(definitions_dir=directory)
        definitions = {
            item["apiName"]: item for item in self._load_object_type_definitions(directory)
        }
        applied: list[dict[str, Any]] = []

        for entry in plan_info["plan"]:
            api_name = entry["apiName"]
            if entry.get("dangerous") and not allow_destructive:
                raise ValueError(
                    "Destructive schema changes require allow_destructive=True",
                )

            definition = definitions.get(api_name)
            if not definition:
                continue

            request = self._definition_to_request(definition)
            self.metamodel_service.upsert_object_type(api_name, request)
            applied.append({"apiName": api_name, "action": entry.get("action", "update")})

        return {"applied": applied}

    def list_migration_tasks(self) -> list[dict[str, Any]]:
        tasks = self._session.exec(select(MigrationTask)).all()
        results: list[dict[str, Any]] = []
        for task in tasks or []:
            results.append(
                {
                    "rid": task.rid,
                    "objectTypeApiName": task.object_type_api_name,
                    "fromVersion": task.from_version,
                    "toVersion": task.to_version,
                    "status": (
                        task.status.value
                        if isinstance(task.status, MigrationTaskStatus)
                        else str(task.status)
                    ),
                    "operationsPlanned": len((task.plan or {}).get("operations", [])),
                }
            )
        return results

    def update_migration_task(
        self,
        task_rid: str,
        *,
        status: str | MigrationTaskStatus,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        task = self._session.get(MigrationTask, task_rid)
        if task is None:
            raise ValueError(f"MigrationTask '{task_rid}' not found")

        if isinstance(status, str):
            status_enum = MigrationTaskStatus(status)
        else:
            status_enum = status

        task.status = status_enum
        if error_message is not None:
            task.error_message = error_message

        self._session.add(task)
        self._session.commit()
        self._session.refresh(task)

        return {
            "rid": task.rid,
            "status": task.status.value,
            "errorMessage": task.error_message,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_session(self, metamodel_service: Any) -> Session | None:
        repo = getattr(metamodel_service, "repo", None)
        if repo is not None:
            candidate = getattr(repo, "session", None)
            if candidate is not None:
                return candidate
        return getattr(metamodel_service, "session", None)

    def _load_object_type_definitions(self, directory: Path | None = None) -> list[dict[str, Any]]:
        base_dir = Path(directory) if directory else self._definitions_dir
        if not base_dir.exists():
            return []
        object_types_dir = base_dir / "object_types"
        if not object_types_dir.exists():
            return []

        definitions: list[dict[str, Any]] = []
        for path in sorted(object_types_dir.glob("*.yml")):
            with path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
            if not payload:
                continue
            payload.setdefault("apiName", path.stem)
            payload["__path__"] = path
            definitions.append(payload)
        return definitions

    def _build_plan_entry(self, definition: dict[str, Any]) -> dict[str, Any] | None:
        api_name = definition.get("apiName")
        if not api_name:
            return None

        existing = self._get_existing_object_type(api_name)
        if existing is None:
            return {
                "apiName": api_name,
                "action": "create",
                "dangerous": False,
            }

        existing_props = self._map_existing_properties(existing)
        desired_props = definition.get("properties", {}) or {}

        removed = sorted(set(existing_props) - set(desired_props))
        type_changes: list[dict[str, Any]] = []
        for name, old_prop in existing_props.items():
            desired = desired_props.get(name)
            if desired is None:
                continue
            old_type = getattr(old_prop, "data_type", None)
            new_type = desired.get("dataType", old_type)
            if new_type != old_type:
                type_changes.append({"property": name, "from": old_type, "to": new_type})

        if not removed and not type_changes and set(existing_props) == set(desired_props):
            # No significant change
            return None

        return {
            "apiName": api_name,
            "action": "update",
            "dangerous": bool(removed),
            "removedProperties": removed,
            "typeChanges": type_changes,
        }

    def _get_existing_object_type(self, api_name: str):
        repo = getattr(self.metamodel_service, "repo", None)
        if repo is None:
            return None
        model = repo.get_object_type_by_api_name(
            getattr(self.metamodel_service, "_service_name", "ontology"),
            getattr(self.metamodel_service, "_instance_name", "default"),
            api_name,
        )
        return model

    def _map_existing_properties(self, existing: Any) -> dict[str, Any]:
        properties = list(getattr(existing, "property_types", []) or [])
        if not properties:
            repo = getattr(self.metamodel_service, "repo", None)
            fetcher = getattr(repo, "list_property_types_by_object_type", None)
            if callable(fetcher):
                properties = list(fetcher(existing.rid))
        return {prop.api_name: prop for prop in properties or []}

    def _definition_to_request(self, definition: dict[str, Any]) -> Any:
        api_name = definition.get("apiName")
        properties: dict[str, _PropertyAdapter] = {}
        for name, value in (definition.get("properties") or {}).items():
            value = value or {}
            properties[name] = _PropertyAdapter(
                {
                    "dataType": value.get("dataType", "string"),
                    "displayName": value.get("displayName", name),
                    "description": value.get("description"),
                    "required": value.get("required", False),
                    "qualityChecks": value.get("qualityChecks"),
                    "securityTags": value.get("securityTags"),
                    "derivationScript": value.get("derivationScript"),
                }
            )

        payload = {
            "displayName": definition.get("displayName", api_name or ""),
            "description": definition.get("description"),
            "primaryKey": definition.get("primaryKey", "id"),
            "properties": properties,
            "implements": list(definition.get("implements", []) or []),
        }
        return _ObjectTypeRequestAdapter(payload)
