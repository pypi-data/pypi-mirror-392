"""Services for business logic."""

__all__ = ["MetamodelService", "MigrationExecutionService"]


def __getattr__(name):  # pragma: no cover - lazy import helpers
    if name == "MetamodelService":
        from .metamodel_service import MetamodelService

        return MetamodelService
    if name == "MigrationExecutionService":
        from .migration_execution_service import MigrationExecutionService

        return MigrationExecutionService
    raise AttributeError(name)
