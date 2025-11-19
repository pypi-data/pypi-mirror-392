# Migration Guide: YAML → Python (OGM-first)

This guide helps you migrate ontology definitions from YAML files to Python OGM models, while keeping YAML as an export artifact for interoperability.

## Why migrate?

- Reuse: inheritance, mixins, and composition in Python.
- Safety: stronger validation and IDE/type hints.
- Maintainability: less boilerplate, easier refactors.

## Before you start

- Ensure `ontologia` and `ontologia_cli` are installed in your environment.
- Your current YAML lives under `ontologia/object_types/` and `ontologia/link_types/`.

## 1) Create Python models

Create files under `ontology_definitions/models/` using `ObjectModel` and `LinkModel`.

Example (`ontology_definitions/models/core.py`):

```python
from __future__ import annotations
from pydantic import Field
from ontologia.ogm import ObjectModel, LinkModel

class Company(ObjectModel):
    __object_type_api_name__ = "company"
    __primary_key__ = "company_id"
    company_id: str = Field(title="Company ID")
    name: str = Field(title="Name")

class Employee(ObjectModel):
    __object_type_api_name__ = "employee"
    __primary_key__ = "employee_id"
    employee_id: str = Field(title="Employee ID")
    name: str = Field(title="Name")
    company: LinkModel[Company] = LinkModel(
        "works_for", inverse="has_employees", cardinality="many_to_one"
    )
```

## 2) Apply schema from Python

```bash
uv run ontologia-cli apply --source python --module ontology_definitions.models
```

This inspects Python models at runtime and applies the migration plan to the server.

## 3) Export YAML (optional)

```bash
uv run ontologia-cli export:yaml --module ontology_definitions.models --out ontologia
```

This generates YAML under `ontologia/object_types/` and `ontologia/link_types/`, preserving compatibility for non-Python tooling.

## 4) Keep YAML or remove it?

- Keep: if other systems or teams still consume YAML.
- Remove: if your workflow is fully Python-first.

## 5) Tips & gotchas

- Display names: set `__display_name__` on models if you need a friendly name.
- Link properties: define via `LinkModel(..., properties={...})`.
- Custom modules: use `--module` and optionally `--module-path` for alternate project layouts.

## 6) Rollback and safety

- Use `--allow-destructive` sparingly; review plans before apply.
- To compare, run a dry run with `--source yaml` vs `--source python` and confirm parity.
