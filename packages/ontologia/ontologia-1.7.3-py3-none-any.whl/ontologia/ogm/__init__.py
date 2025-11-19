# Modern OGM - production-ready, performant, secure
from .connection import CoreServiceProvider, Ontology, get_engine, get_session
from .errors import ConnectionNotInitialized, NotFound, ObjectModelError
from .link import LinkModel
from .model import ObjectModel
from .python_features import (
    conditional_jit,
    experimental,
    get_feature_summary,
    require_feature,
    supports_feature,
)

# Legacy compatibility imports
_ontology_instance = None


def connect(
    db_connection_string: str,
    *,
    echo: bool = False,
    service: str = "default",
    instance: str = "default",
):
    """Legacy compatibility wrapper - creates and returns global Ontology instance."""
    global _ontology_instance
    from sqlmodel import create_engine

    engine = create_engine(db_connection_string, echo=echo)
    _ontology_instance = Ontology(engine, service=service, instance=instance)
    return _ontology_instance


# For backward compatibility
OntologyLegacy = Ontology


# For backward compatibility with test imports
def apply_schema(models_or_ontology, *args, **kwargs):
    """Legacy compatibility wrapper - handles both old function style and method calls."""
    # If first argument is a list of models, use the global Ontology singleton
    if isinstance(models_or_ontology, list) or isinstance(models_or_ontology, tuple):
        # Use the global ontology connection
        global _ontology_instance
        if _ontology_instance is None:
            raise ConnectionNotInitialized("Call connect() before apply_schema(list[models])")
        return _ontology_instance.apply_schema(models_or_ontology, *args, **kwargs)
    else:
        # If first argument is an Ontology instance, call its method
        return models_or_ontology.apply_schema(*args, **kwargs)


__version__ = "0.7.0"

__all__ = [
    "CoreServiceProvider",
    "LinkModel",
    "ObjectModel",
    "Ontology",
    "get_model_class",
    "get_engine",
    "get_session",
    "connect",
    "apply_schema",
    "ObjectModelError",
    "NotFound",
    "ConnectionNotInitialized",
    "_ontology_instance",
    # Python features API
    "supports_feature",
    "get_feature_summary",
    "require_feature",
    "conditional_jit",
    "experimental",
]


# ---- Utilities for API integration ----


def get_model_class(object_type_api_name: str):
    """Return the registered ObjectModel class for a given ObjectType apiName.

    This looks up the internal model registry populated by ObjectModelMeta and
    by Ontology.model decorator, matching on ``__object_type_api_name__``.

    Returns None when not found.
    """
    try:
        from .model import _model_registry
    except Exception:  # pragma: no cover - defensive
        return None

    api_name = str(object_type_api_name or "").strip()
    if not api_name:
        return None

    for cls, meta in list(_model_registry.items()):
        try:
            if meta.get("object_type_api_name") == api_name:
                return cls
        except Exception:  # pragma: no cover - resilience guard
            continue
    return None
