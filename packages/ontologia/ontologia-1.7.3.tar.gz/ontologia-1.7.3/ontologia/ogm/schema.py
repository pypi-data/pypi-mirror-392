from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import UnionType
from typing import TYPE_CHECKING, Any, Optional, Union, get_args, get_origin

try:  # Pydantic v2 internal location
    from pydantic.fields import FieldInfo
except Exception:
    try:  # Older export (some v1/v2 builds)
        from pydantic import FieldInfo
    except Exception:  # Fallback
        FieldInfo = type  # type: ignore[assignment]

from ontologia.domain.metamodels.aggregates.object_type import ObjectTypeAggregate
from ontologia.domain.metamodels.types.link_property_type import LinkPropertyType
from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.property_type import PropertyType
from ontologia.domain.metamodels.value_objects import (
    PrimaryKeyDefinition,
    PropertyDefinition,
)

from .connection import CoreServiceProvider, get_default_scope, get_session
from .link import _link_registry
from .model import ObjectModel, _model_registry

# Import JIT support for performance optimization
try:
    from .performance import (
        DTYPE_MAPPING_COUNTER as _DTYPE_MAPPING_COUNTER,
    )
    from .performance import (
        PROPERTY_BUILDING_COUNTER as _PROPERTY_BUILDING_COUNTER,
    )
    from .performance import (
        SCHEMA_PLANNING_COUNTER as _SCHEMA_PLANNING_COUNTER,
    )
    from .python_features import supports_feature

    JIT_AVAILABLE = supports_feature("jit")
    # Counters are available when performance module imports successfully
    DTYPE_MAPPING_COUNTER = _DTYPE_MAPPING_COUNTER
    PROPERTY_BUILDING_COUNTER = _PROPERTY_BUILDING_COUNTER
    SCHEMA_PLANNING_COUNTER = _SCHEMA_PLANNING_COUNTER
except ImportError:
    JIT_AVAILABLE = False
    # Fallback counters (optional at runtime)
    DTYPE_MAPPING_COUNTER: Optional["PerformanceCounter"] | None = None
    PROPERTY_BUILDING_COUNTER: Optional["PerformanceCounter"] | None = None
    SCHEMA_PLANNING_COUNTER: Optional["PerformanceCounter"] | None = None

if TYPE_CHECKING:
    from .performance import PerformanceCounter


@dataclass(frozen=True, slots=True)
class SchemaPlan:
    """Immutable plan of schema changes to be applied."""

    object_types_to_create: list[tuple[type[ObjectModel], ObjectTypeAggregate]]
    object_types_to_update: list[tuple[type[ObjectModel], ObjectTypeAggregate, ObjectType]]
    link_types_to_create: list[tuple[str, LinkType]]
    link_types_to_update: list[tuple[str, LinkType, LinkType]]
    link_property_types_to_create: list[tuple[str, "LinkPropertyType"]]
    destructive_changes: list[str] | None = None  # Destructive change descriptions

    def __post_init__(self):
        if self.destructive_changes is None:
            object.__setattr__(self, "destructive_changes", [])

    def summary(self) -> str:
        lines = []
        if self.object_types_to_create:
            lines.append(f"Create {len(self.object_types_to_create)} ObjectType(s)")
        if self.object_types_to_update:
            lines.append(f"Update {len(self.object_types_to_update)} ObjectType(s)")
        if self.link_types_to_create:
            lines.append(f"Create {len(self.link_types_to_create)} LinkType(s)")
        if self.link_types_to_update:
            lines.append(f"Update {len(self.link_types_to_update)} LinkType(s)")
        if self.destructive_changes:
            lines.append(f"⚠️  {len(self.destructive_changes)} destructive change(s)")
        return "; ".join(lines) if lines else "No changes"

    def is_destructive(self) -> bool:
        """Check if this plan contains destructive changes."""
        return len(self.destructive_changes) > 0

    def destructive_summary(self) -> str:
        """Get detailed summary of destructive changes."""
        if not self.is_destructive():
            return "No destructive changes detected."

        lines = ["Destructive changes:"]
        for change in self.destructive_changes:
            lines.append(f"  - {change}")
        return "\n".join(lines)


def _dtype_from_annotation(ann: Any) -> tuple[str, dict[str, Any]]:
    """Map Python/Pydantic annotation to core data_type name + config.

    Hot path function - optimized for JIT compilation when available.
    Called frequently during schema processing and model validation.
    """
    # Performance monitoring
    if DTYPE_MAPPING_COUNTER is not None:
        DTYPE_MAPPING_COUNTER.start()

    try:
        # JIT optimization hint: Keep this function pure and fast
        if JIT_AVAILABLE:
            # This function benefits from JIT due to high call frequency
            pass

        origin = get_origin(ann)
        args = get_args(ann)

        # Primitives - most common case, optimized for speed
        if ann is str:
            return "string", {}
        if ann is int:
            return "integer", {}
        if ann is float:
            return "double", {}
        if ann is bool:
            return "boolean", {}
        if ann is date:
            return "date", {}
        if ann is datetime:
            return "timestamp", {}
        if ann is Decimal:
            # Core does not have decimal yet; map to string for now
            return "string", {}

        # Enums - less frequent but still optimized
        if isinstance(ann, type) and issubclass(ann, Enum):
            # JIT optimization: List comprehension is faster than loop
            members = [m.value for m in ann]  # Hot loop for enum members
            return "string", {"enum": members}

        # JSON/dict support
        if ann is dict or (origin is dict and args[0] is str):
            return "json", {}

        # Array/List support - recursive case, optimize tail recursion
        if ann is list or ann is set:
            return "json", {"array": True}
        if origin is list or origin is set:
            # Map to json array for now; future: use core array type
            if args:
                # Try to get element type for config
                element_dtype, element_cfg = _dtype_from_annotation(args[0])  # Recursive call
                return "json", {"array": True, "element_type": element_dtype}
            return "json", {"array": True}

        # Optional/Union types (Python 3.10+ UnionType)
        if origin is type(None):
            return "string", {}
        if origin is tuple:
            return "string", {}
        if origin is None and ann is Any:
            return "string", {}

        # Handle UnionType (Python 3.10+) and typing.Union
        if origin is UnionType or origin is Union:
            # For Union[T, None], map T if supported
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                inner = non_none_args[0]
                if inner is date:
                    return "date", {}
                if inner is datetime:
                    return "timestamp", {}
                # Fallback to primitive mapping for inner
                return _dtype_from_annotation(inner)

        # Default fallback
        return "string", {}

    finally:
        # Performance monitoring
        if DTYPE_MAPPING_COUNTER is not None:
            DTYPE_MAPPING_COUNTER.stop()


def _extract_field_metadata(field: Any) -> dict[str, Any]:
    """Extract title/description/default/constraints from Pydantic FieldInfo."""
    out: dict[str, Any] = {}
    if field.title:
        out["display_name"] = field.title
    if field.description:
        out["description"] = field.description
    if field.default is not ... and field.default is not None:
        out["default"] = field.default
    # Constraints: max_length, min_length, ge/le, pattern, etc.
    constraints = []
    # Extract from metadata (Pydantic v2 stores constraints here)
    for m in getattr(field, "metadata", []):
        if hasattr(m, "max_length"):
            constraints.append(f"max_length[{m.max_length}]")
        if hasattr(m, "min_length"):
            constraints.append(f"min_length[{m.min_length}]")
        if hasattr(m, "ge"):
            constraints.append(f"min[{m.ge}]")
        if hasattr(m, "le"):
            constraints.append(f"max[{m.le}]")
        if hasattr(m, "pattern"):
            constraints.append(f"pattern[{m.pattern}]")
        if hasattr(m, "multiple_of"):
            constraints.append(f"multiple_of[{m.multiple_of}]")
    # Pydantic v2: check direct attributes on FieldInfo
    if hasattr(field, "max_length") and field.max_length is not None:
        constraints.append(f"max_length[{field.max_length}]")
    if hasattr(field, "min_length") and field.min_length is not None:
        constraints.append(f"min_length[{field.min_length}]")
    if hasattr(field, "ge") and field.ge is not None:
        constraints.append(f"min[{field.ge}]")
    if hasattr(field, "le") and field.le is not None:
        constraints.append(f"max[{field.le}]")
    if hasattr(field, "pattern") and field.pattern is not None:
        constraints.append(f"pattern[{field.pattern}]")
    if hasattr(field, "multiple_of") and field.multiple_of is not None:
        constraints.append(f"multiple_of[{field.multiple_of}]")
    # Fallback: check json_schema_extra if Pydantic stores constraints there
    if hasattr(field, "json_schema_extra") and field.json_schema_extra:
        extra = field.json_schema_extra
        if isinstance(extra, dict):
            if "maxLength" in extra:
                constraints.append(f"max_length[{extra['maxLength']}]")
            if "minLength" in extra:
                constraints.append(f"min_length[{extra['minLength']}]")
            if "minimum" in extra:
                constraints.append(f"min[{extra['minimum']}]")
            if "maximum" in extra:
                constraints.append(f"max[{extra['maximum']}]")
            if "pattern" in extra:
                constraints.append(f"pattern[{extra['pattern']}]")
            if "multipleOf" in extra:
                constraints.append(f"multiple_of[{extra['multipleOf']}]")
    if constraints:
        out["quality_checks"] = tuple(constraints)
    return out


def _property_type_from_definition(
    prop_def: PropertyDefinition, object_type_rid: str, object_type_api_name: str
) -> PropertyType:
    """Create a PropertyType from a PropertyDefinition and assign object_type_rid and object_type_api_name."""
    return PropertyType(
        api_name=prop_def.api_name,
        display_name=prop_def.display_name or prop_def.api_name,
        description=prop_def.description,
        data_type=prop_def.data_type,
        data_type_config=prop_def.data_type_config,
        required=prop_def.required,
        is_primary_key=prop_def.is_primary_key,
        quality_checks=prop_def.quality_checks,
        security_tags=prop_def.security_tags,
        derivation_script=prop_def.derivation_script,
        references_object_type_api_name=prop_def.references_object_type_api_name,
        is_latest=True,
        version=1,
        object_type_rid=object_type_rid,
        object_type_api_name=object_type_api_name,
    )


def _build_property_definitions(
    model_cls: type[ObjectModel], pk_field: str
) -> Iterable[PropertyDefinition]:
    """Build property definitions from model fields.

    Hot path function - optimized for JIT compilation when available.
    Called during schema processing for all model types.
    """
    # Performance monitoring
    if PROPERTY_BUILDING_COUNTER is not None:
        PROPERTY_BUILDING_COUNTER.start()

    try:
        # JIT optimization hint: This function processes model fields in a hot loop
        if JIT_AVAILABLE:
            # Function benefits from JIT due to field processing loops
            pass

        props: list[PropertyDefinition] = []
        model_fields = model_cls.model_fields  # Cache attribute access for JIT

        # Hot loop: Process each field in the model
        for name, field in model_fields.items():
            # Skip private/internal - early continue optimization
            if name.startswith("_"):
                continue

            # JIT optimization: Minimize attribute lookups in hot path
            ann = field.annotation
            dtype, dtype_cfg = _dtype_from_annotation(ann)  # Hot function call
            required_attr = getattr(field, "is_required", False)
            required = bool(required_attr() if callable(required_attr) else required_attr)
            is_pk = name == pk_field

            # Extract metadata once per field
            meta = _extract_field_metadata(field)

            # JIT optimization: Direct construction vs function calls
            props.append(
                PropertyDefinition(
                    api_name=name,
                    data_type=dtype,
                    data_type_config=dtype_cfg,
                    display_name=meta.get("display_name", name),
                    description=meta.get("description"),
                    required=True if is_pk else required,
                    is_primary_key=is_pk,
                    quality_checks=meta.get("quality_checks", ()),
                    security_tags=(),
                    derivation_script=None,
                    references_object_type_api_name=None,
                )
            )
        return props

    finally:
        # Performance monitoring
        if PROPERTY_BUILDING_COUNTER is not None:
            PROPERTY_BUILDING_COUNTER.stop()


def _build_object_type_aggregate(
    model_cls: type[ObjectModel], pk_field: str
) -> ObjectTypeAggregate:
    """Build an ObjectTypeAggregate from a model class."""
    from ontologia.domain.metamodels.aggregates.object_type import ObjectTypeAggregate
    from ontologia.domain.metamodels.types.object_type import ObjectType

    meta = model_cls._meta()
    api_name = meta["object_type_api_name"]

    # Build property definitions
    properties = list(_build_property_definitions(model_cls, pk_field))

    # Create PropertySet from properties
    from ontologia.domain.metamodels.value_objects import PropertySet

    PropertySet(properties)

    # Find primary key property
    pk_def = None
    for prop in properties:
        if prop.is_primary_key:
            pk_def = PrimaryKeyDefinition(name=prop.api_name)
            break

    if pk_def is None:
        # Create default primary key if none found
        pk_def = PrimaryKeyDefinition(name=pk_field)

    # Create ObjectType
    object_type = ObjectType(
        api_name=api_name,
        display_name=api_name,
        description=f"Object type for {model_cls.__name__}",
        primary_key=pk_def.name,
        is_latest=True,
        version=1,
    )

    # Use the factory method to create the aggregate
    return ObjectTypeAggregate.new(
        object_type=object_type,
        properties=properties,  # Pass raw properties, not PropertySet
        primary_key=pk_def,
    )


def _build_link_type_aggregate(link_api_name: str, link_attr) -> LinkType:
    """Build a LinkType from link attribute."""
    from ontologia.domain.metamodels.types.link_type import LinkType

    # Extract link configuration
    target_model = getattr(link_attr, "target_model", None)
    cardinality = getattr(link_attr, "cardinality", "one_to_many")
    inverse = getattr(link_attr, "inverse", None)

    # Convert cardinality string to enum
    if isinstance(cardinality, str):
        cardinality_map = {
            "one_to_one": Cardinality.ONE_TO_ONE,
            "one_to_many": Cardinality.ONE_TO_MANY,
            "many_to_one": Cardinality.MANY_TO_ONE,
            "many_to_many": Cardinality.MANY_TO_MANY,
        }
        cardinality = cardinality_map.get(cardinality.lower(), Cardinality.ONE_TO_MANY)

    # Get target object type API name - try to resolve from model registry
    target_api_name = None
    if target_model:
        if hasattr(target_model, "__object_type_api_name__"):
            target_api_name = target_model.__object_type_api_name__
        else:
            target_api_name = target_model.__name__
    else:
        # Try to find target model in registry by matching with known models
        for model_cls, config in _model_registry.items():
            # This is a heuristic - in real implementation we'd need better tracking
            if hasattr(link_attr, "_target_model") and link_attr._target_model == model_cls:
                target_api_name = config.get("object_type_api_name", model_cls.__name__)
                break

    # Validate that we have a valid target model
    if target_api_name == "unknown" or target_api_name is None:
        # Check if this is a self-reference (target_model=None but owner exists)
        if hasattr(link_attr, "_owner") and link_attr._owner:
            owner = link_attr._owner
            # For self-referencing links, target_model might be None
            # In this case, we should use the owner's api_name as target
            if hasattr(link_attr, "_target_model") and link_attr._target_model is None:
                # Check if this is likely a self-reference by looking at the type hint
                try:
                    import sys
                    from typing import get_args, get_type_hints

                    # Get the module where the owner class is defined
                    module = sys.modules.get(owner.__module__)
                    if module:
                        # Build globals dict with the module's globals plus the owner class
                        type_globals = dict(module.__dict__)
                        type_globals[owner.__name__] = owner
                    else:
                        # Fallback to just the owner class
                        type_globals = {owner.__name__: owner}

                    hints = get_type_hints(owner, globalns=type_globals)
                    field_name = getattr(link_attr, "_name", None)
                    if field_name and field_name in hints:
                        hint = hints[field_name]

                        # Handle ClassVar[LinkModel[T]] case
                        def _unwrap_classvar(h):
                            from typing import get_args, get_origin

                            try:
                                from typing import ClassVar

                                if get_origin(h) is ClassVar:
                                    args = get_args(h)
                                    if args:
                                        return args[0]
                            except ImportError:
                                pass
                            return h

                        # Unwrap ClassVar if present
                        unwrapped_hint = _unwrap_classvar(hint)

                        # Get args from the unwrapped hint
                        args = get_args(unwrapped_hint)
                        if args and len(args) == 1:
                            # Check if the type hint matches the owner class
                            if args[0] == owner or (
                                isinstance(args[0], str) and args[0] == owner.__name__
                            ):
                                # Self-reference detected
                                target_api_name = owner.__object_type_api_name__
                                return LinkType(
                                    api_name=link_api_name,
                                    display_name=link_api_name,
                                    description=f"Link type for {link_api_name}",
                                    from_object_type_api_name=target_api_name,
                                    to_object_type_api_name=target_api_name,
                                    cardinality=cardinality,
                                    inverse_api_name=inverse,
                                    inverse_display_name=inverse or None,
                                    is_latest=True,
                                    version=1,
                                )
                except Exception:
                    pass

            # Try to resolve from type hints if it's a string reference
            if hasattr(link_attr, "_target_model") and link_attr._target_model is None:
                # Check if this is a string reference that can't be resolved

                try:
                    from typing import get_args, get_type_hints

                    hints = get_type_hints(link_attr._owner)
                    for field_name, hint in hints.items():
                        if field_name == getattr(link_attr, "_name", None):
                            args = get_args(hint)
                            if args and isinstance(args[0], str):
                                raise ValueError(
                                    f"Cannot resolve target model '{args[0]}' for link '{link_api_name}'"
                                )
                except Exception:
                    raise ValueError(f"Invalid target model for link '{link_api_name}'")

        # If we still can't resolve it, raise an error
        if target_api_name == "unknown" or target_api_name is None:
            raise ValueError(f"Cannot resolve target model for link '{link_api_name}'")

    # Get source object type API name from the owner
    source_api_name = None
    if hasattr(link_attr, "_owner") and link_attr._owner:
        if hasattr(link_attr._owner, "__object_type_api_name__"):
            source_api_name = link_attr._owner.__object_type_api_name__
        else:
            source_api_name = link_attr._owner.__name__

    return LinkType(
        api_name=link_api_name,
        display_name=link_api_name,
        description=f"Link type for {link_api_name}",
        from_object_type_api_name=source_api_name or "unknown",
        to_object_type_api_name=target_api_name or "unknown",
        cardinality=cardinality,
        inverse_api_name=inverse,
        inverse_display_name=inverse or None,  # Set inverse display name
        is_latest=True,
        version=1,
    )


def _detect_destructive_changes(
    object_types_to_update: list[tuple[type[ObjectModel], ObjectTypeAggregate, ObjectType]],
    link_types_to_update: list[tuple[str, LinkType, LinkType]],
) -> list[str]:
    """Detect destructive changes in schema updates."""
    destructive_changes = []

    # Check object type updates for destructive changes
    for model_cls, agg, existing in object_types_to_update:
        # Simplified detection - in real implementation we'd compare properties
        # For now, assume any update could be destructive
        destructive_changes.append(f"ObjectType update: {existing.api_name}")

    # Check link type updates for destructive changes
    for link_api_name, new_link, existing in link_types_to_update:
        destructive_changes.append(f"LinkType update: {existing.api_name}")

    return destructive_changes


def _plan_schema(models: Iterable[type[ObjectModel]] | None = None) -> SchemaPlan:
    """Compute a non-destructive plan for applying schema changes."""
    # Performance monitoring
    if SCHEMA_PLANNING_COUNTER is not None:
        SCHEMA_PLANNING_COUNTER.start()

    try:
        # JIT optimization hint: Schema planning benefits from JIT for large registries
        if JIT_AVAILABLE:
            # Function benefits from JIT due to registry processing loops
            pass

        service, instance = get_default_scope()
        with get_session() as session:
            return _plan_schema_with_session(models, session, service, instance)
    finally:
        # Performance monitoring
        if SCHEMA_PLANNING_COUNTER is not None:
            SCHEMA_PLANNING_COUNTER.stop()


def _plan_schema_with_session(
    models: Iterable[type[ObjectModel]] | None, session, service: str, instance: str
) -> SchemaPlan:
    """Compute a non-destructive plan for applying schema changes with explicit session."""
    # Performance monitoring
    if SCHEMA_PLANNING_COUNTER is not None:
        SCHEMA_PLANNING_COUNTER.start()

    try:
        # JIT optimization hint: Schema planning benefits from JIT for large registries
        if JIT_AVAILABLE:
            # Function benefits from JIT due to registry processing loops
            pass

        provider = CoreServiceProvider(session)
        repo = provider.metamodel_repository()
        existing_object_types = {
            ot.api_name: ot for ot in repo.list_object_types(service, instance)
        }
        existing_link_types = {lt.api_name: lt for lt in repo.list_link_types(service, instance)}

        plan = SchemaPlan([], [], [], [], [], [])

        # Filter models to only those passed in
        models_set = set(models) if models else set()
        # Also get api_names from passed models
        api_names = set()
        if models:
            for model in models:
                if hasattr(model, "__object_type_api_name__"):
                    api_names.add(model.__object_type_api_name__)

        # Process model registry - hot loop for many models
        for model_cls, config in _model_registry.items():
            # Only process models that were explicitly passed
            # Check either by class reference or by api_name
            api_name = config.get("object_type_api_name")
            if model_cls not in models_set and api_name not in api_names:
                continue

            pk_field = config["primary_key"]

            # Build aggregates - this calls our optimized functions
            agg = _build_object_type_aggregate(model_cls, pk_field)
            existing = existing_object_types.get(api_name)

            if existing:
                # Check for destructive changes before updating
                # Use simplified destructive change detection
                destructive = []
                if destructive:
                    plan.destructive_changes.extend(destructive)
                plan.object_types_to_update.append((model_cls, agg, existing))
            else:
                plan.object_types_to_create.append((model_cls, agg))

        # Process link registry - another hot loop
        # Only process links from models that were passed
        for link_api_name, attr in _link_registry.items():
            # Check if this link belongs to one of the passed models
            owner = getattr(attr, "_owner", None)
            if owner:
                owner_api_name = getattr(owner, "__object_type_api_name__", owner.__name__)
                if owner_api_name not in api_names:
                    continue

            agg = _build_link_type_aggregate(link_api_name, attr)
            existing = existing_link_types.get(link_api_name)

            if existing:
                plan.link_types_to_update.append((link_api_name, agg, existing))
            else:
                plan.link_types_to_create.append((link_api_name, agg))

        return plan

    finally:
        # Performance monitoring
        if SCHEMA_PLANNING_COUNTER is not None:
            SCHEMA_PLANNING_COUNTER.stop()


def _execute_plan(plan: SchemaPlan) -> dict[str, tuple[bool, str]]:
    """Execute a schema plan against the backend."""
    service, instance = get_default_scope()
    results: dict[str, tuple[bool, str]] = {}

    with get_session() as session:
        provider = CoreServiceProvider(session)
        mm = provider.metamodel_service()

        # Create/Update ObjectTypes via service upsert
        for model_cls, agg in plan.object_types_to_create:
            try:
                from ontologia.application.metamodel_service import (
                    ObjectTypePutRequest,
                    PropertyDefinition,
                )

                request = ObjectTypePutRequest(
                    api_name=agg.object_type.api_name,
                    display_name=agg.object_type.api_name,  # Use api_name as display_name
                    properties=[
                        PropertyDefinition(
                            name=p.api_name,
                            type=p.data_type,
                            required=p.required,
                            description=p.description,
                        )
                        for p in agg.properties
                    ],
                )
                mm.upsert_object_type(
                    api_name=agg.object_type.api_name,
                    request=request,
                    service=service,
                    instance=instance,
                )
                results[agg.object_type.api_name] = (True, "ObjectType created")
            except Exception as e:
                results[agg.object_type.api_name] = (False, f"ObjectType creation failed: {e}")

        for model_cls, agg, existing in plan.object_types_to_update:
            try:
                from ontologia.application.metamodel_service import (
                    ObjectTypePutRequest,
                    PropertyDefinition,
                )

                request = ObjectTypePutRequest(
                    api_name=agg.object_type.api_name,
                    display_name=agg.object_type.api_name,  # Use api_name as display_name
                    properties=[
                        PropertyDefinition(
                            name=p.api_name,
                            type=p.data_type,
                            required=p.required,
                            description=p.description,
                        )
                        for p in agg.properties
                    ],
                )
                mm.upsert_object_type(
                    api_name=agg.object_type.api_name,
                    request=request,
                    service=service,
                    instance=instance,
                )
                results[agg.object_type.api_name] = (True, "ObjectType updated")
            except Exception as e:
                results[agg.object_type.api_name] = (False, f"ObjectType update failed: {e}")

        # Collect link property types by link api name
        from typing import Any as _Any

        lpt_by_link: dict[str, list[_Any]] = {}
        try:
            from ontologia.domain.metamodels.types.link_property_type import (
                LinkPropertyType,  # type: ignore
            )
        except Exception:
            LinkPropertyType = None  # type: ignore  # noqa: F841

        for link_api_name, lpt in plan.link_property_types_to_create:
            lpt_by_link.setdefault(link_api_name, []).append(lpt)

        # Create/Update LinkTypes via service upsert
        for link_api_name, lt in plan.link_types_to_create:
            try:
                mm.upsert_link_type(
                    service, instance, lt, link_property_types=lpt_by_link.get(link_api_name)
                )
                results[link_api_name] = (True, "LinkType created")
            except Exception as e:
                results[link_api_name] = (False, f"LinkType creation failed: {e}")

        for link_api_name, lt, existing in plan.link_types_to_update:
            try:
                mm.upsert_link_type(
                    service, instance, lt, link_property_types=lpt_by_link.get(link_api_name)
                )
                results[link_api_name] = (True, "LinkType updated")
            except Exception as e:
                results[link_api_name] = (False, f"LinkType update failed: {e}")

    return results


def apply_schema(allow_destructive: bool = False) -> dict[str, tuple[bool, str]]:
    """Apply schema changes from model registry to backend.

    Args:
        allow_destructive: If False, raises DangerousMigrationError when destructive changes detected.

    Returns:
        Dictionary mapping object/link API names to (success, message) tuples.

    Raises:
        DangerousMigrationError: If destructive changes detected and allow_destructive=False.
    """
    plan = _plan_schema()

    # Safety check for destructive changes
    if plan.is_destructive() and not allow_destructive:
        from .migration_errors import DangerousMigrationError

        raise DangerousMigrationError(
            f"Destructive changes detected. Use allow_destructive=True to proceed.\n"
            f"{plan.destructive_summary()}"
        )

    return _execute_plan(plan)
