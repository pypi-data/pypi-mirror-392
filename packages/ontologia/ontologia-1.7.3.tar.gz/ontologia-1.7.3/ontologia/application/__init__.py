"""
ontologia.application
---------------------
Application layer: serviços e casos de uso de alto nível.

Este módulo contém a lógica de aplicação que orquestra
os componentes do domínio para realizar tarefas complexas.
"""

# Core services (no heavy optional deps)
from ontologia.application.instances_service import InstancesService
from ontologia.application.linked_objects_service import LinkedObjectsService
from ontologia.application.metamodel_service import MetamodelService

# Optional services (guarded to avoid import-time hard dependencies)
try:  # pragma: no cover - optional
    from ontologia.application.analytics_service import AnalyticsService
except Exception:  # pragma: no cover - optional not installed
    AnalyticsService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional
    from ontologia.application.data_analysis_service import DataAnalysisService
except Exception:  # pragma: no cover - optional not installed
    DataAnalysisService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional external dep
    from ontologia.application.datacatalog_service import DataCatalogService
except Exception:  # pragma: no cover - optional not installed
    DataCatalogService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional
    from ontologia.application.migration_execution_service import MigrationExecutionService
except Exception:  # pragma: no cover - optional not installed
    MigrationExecutionService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional
    from ontologia.application.policy_service import PolicyService
except Exception:  # pragma: no cover - optional not installed
    PolicyService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional
    from ontologia.application.schema_evolution_service import SchemaEvolutionService
except Exception:  # pragma: no cover - optional not installed
    SchemaEvolutionService = None  # type: ignore[assignment]
try:  # pragma: no cover - optional heavy dep
    from ontologia.application.sync_service import OntologySyncService
except Exception:  # pragma: no cover - optional not installed
    OntologySyncService = None  # type: ignore[assignment]

__all__ = [
    name
    for name, val in {
        "InstancesService": InstancesService,
        "LinkedObjectsService": LinkedObjectsService,
        "MetamodelService": MetamodelService,
        "PolicyService": PolicyService,
        "DataCatalogService": DataCatalogService,
        "AnalyticsService": AnalyticsService,
        "OntologySyncService": OntologySyncService,
        "DataAnalysisService": DataAnalysisService,
        "SchemaEvolutionService": SchemaEvolutionService,
        "MigrationExecutionService": MigrationExecutionService,
    }.items()
    if val is not None
]
