"""
Ontologia - An ontology management system built on Registro and SQLModel.

This package provides tools for defining and managing ontologies with:
- Object types with properties and relationships
- Rich data type system
- Validation and persistence
- Data source integration
- High-level OGM (Object-Graph Mapper) for easy ontology interaction
"""

from importlib import import_module
from typing import Any

__version__ = "1.1.0"

# Metamodel exports
ObjectTypeDataSource: Any | None
try:
    from ontologia.domain.metamodels.instances.object_type_data_source import (
        ObjectTypeDataSource as _ObjectTypeDataSource,
    )

    ObjectTypeDataSource = _ObjectTypeDataSource
except ImportError:
    # Fallback when datacatalog is not available
    ObjectTypeDataSource = None

from ontologia.domain.metamodels.types.link_type import Cardinality
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.property_type import PropertyType

# OGM exports - high-level API
ObjectModel: Any | None
Ontology: Any | None
LinkModel: Any | None
connect: Any | None
apply_schema: Any | None
get_engine: Any | None
get_session: Any | None
try:
    from ontologia.ogm import (
        LinkModel as _LinkModel,
    )
    from ontologia.ogm import (
        ObjectModel as _ObjectModel,
    )
    from ontologia.ogm import (
        Ontology as _Ontology,
    )
    from ontologia.ogm import (
        apply_schema as _apply_schema,
    )
    from ontologia.ogm import (
        connect as _connect,
    )
    from ontologia.ogm import (
        get_engine as _get_engine,
    )
    from ontologia.ogm import (
        get_session as _get_session,
    )

    LinkModel = _LinkModel
    ObjectModel = _ObjectModel
    Ontology = _Ontology
    apply_schema = _apply_schema
    connect = _connect
    get_engine = _get_engine
    get_session = _get_session
except ImportError:
    # Fallback when OGM components are not available
    ObjectModel = None
    Ontology = None
    LinkModel = None
    connect = None
    apply_schema = None
    get_engine = None
    get_session = None

__all__: tuple[str, ...] = (
    "Cardinality",
    "LinkedObject",
    "ObjectInstance",
    "ObjectType",
    "ObjectTypeDataSource",
    "PropertyType",
    # OGM exports
    "ObjectModel",
    "Ontology",
    "LinkModel",
    "connect",
    "apply_schema",
    "get_engine",
    "get_session",
)


def __getattr__(name: str) -> Any:
    """Lazy import for instance models to avoid circular dependencies."""
    if name in ("ObjectInstance", "LinkedObject"):
        module = import_module("ontologia.domain.metamodels.instances.models_sql", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Include lazy exports in dir() output."""
    return sorted(list(globals().keys()) + list(__all__))
