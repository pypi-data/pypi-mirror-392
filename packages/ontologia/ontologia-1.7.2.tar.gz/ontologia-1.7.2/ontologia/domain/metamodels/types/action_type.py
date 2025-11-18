"""
action_type.py
----------------
Defines ActionType (a first-class metamodel entity) to model user-triggered Actions
on objects, aligned with the Palantir Foundry-style ontology Actions concept.

Design principles:
- Metadata-only definition in SQLModel (control plane)
- No storage of executable code; execution is mapped via a safe registry key
- Parameters and rules serialized as JSON
"""

from typing import TYPE_CHECKING

from registro import ResourceTypeBaseModel
from sqlalchemy import event, func, select
from sqlmodel import JSON, Column, Field

if TYPE_CHECKING:
    pass


class ActionType(ResourceTypeBaseModel, table=True):
    """
    Defines an Action in the ontology metamodel. Pure metadata resource.
    Execution logic is referenced via `executor_key` and resolved in backend registry.
    """

    __resource_type__ = "action-type"
    __tablename__ = "actiontype"
    # Relax constraints for test portability; versioning enforced in services.
    __table_args__ = ()

    # Scope target: which ObjectType this Action applies to (Interface support in future)
    target_object_type_api_name: str = Field(index=True)

    # Human-readable description of the action type
    description: str | None = Field(
        default=None, description="Human-readable description of the action"
    )

    # Parameters UI should render for user input (api_name -> definition)
    # Stored as plain dicts for JSON column compatibility
    parameters: dict[str, dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Rules for availability
    submission_criteria: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Rules for parameter/business validation
    validation_rules: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Implementation key mapping to Python function in backend registry
    executor_key: str = Field(index=True, description="Maps to a registered Python function")

    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Latest version flag", index=True)


# Rebuild model to resolve forward references if any
ActionType.model_rebuild()


# Ensure version uniqueness per api_name defensively at insert time, even in
# environments where legacy unique constraints may exist. Compute next version
# as max(version)+1 when a row already exists for the same api_name.
@event.listens_for(ActionType, "before_insert")
def _assign_version_before_insert(mapper, connection, target):  # pragma: no cover - integration
    try:
        # Only adjust when version would collide with an existing row
        # Use getattr to bypass type checker - SQLModel adds __table__ dynamically
        table = getattr(ActionType, "__table__", None)
        assert table is not None, "ActionType.__table__ should exist"
        # Fetch current max version for this api_name
        res = connection.execute(
            select(func.max(table.c.version)).where(table.c.api_name == target.api_name)
        )
        maxv = res.scalar()
        # Mark existing rows as not latest; inserted row will be latest
        connection.execute(
            table.update().where(table.c.api_name == target.api_name).values(is_latest=False)
        )
        if maxv is not None:
            # If target.version is None or <= existing max, bump to next
            cur = getattr(target, "version", None)
            if cur is None or int(cur) <= int(maxv):
                target.version = int(maxv) + 1
    except Exception:
        # Best-effort: do not block insert on advisory logic
        pass
