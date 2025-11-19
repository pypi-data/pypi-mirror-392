from __future__ import annotations

import logging
import warnings

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine, select

# Import services directly to avoid side-effects from ontologia.application.__init__
from ontologia.application.instances_service import InstancesService
from ontologia.application.linked_objects_service import LinkedObjectsService
from ontologia.application.metamodel_service import MetamodelService
from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.linked_object_adapter import (
    LinkedObjectRepositoryAdapter,
)
from ontologia.infrastructure.persistence.sql.linked_objects_repository import (
    SQLLinkedObjectRepository,
)
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)
from ontologia.infrastructure.persistence.sql.object_instance_adapter import (
    ObjectInstanceRepositoryAdapter,
)

from .errors import ConnectionNotInitialized

_engine: Engine | None = None
_default_service: str = "default"
_default_instance: str = "default"

logger = logging.getLogger(__name__)


def connect(
    db_connection_string: str,
    *,
    echo: bool = False,
    service: str = "default",
    instance: str = "default",
) -> None:
    global _engine, _default_service, _default_instance
    _engine = create_engine(db_connection_string, echo=echo)
    _default_service = service
    _default_instance = instance


def get_ontology() -> Ontology:
    """Get the global Ontology instance."""
    if _engine is None:
        raise ConnectionNotInitialized(
            "ObjectModel not connected. Call connect(db_connection_string) first."
        )
    return Ontology(_engine, _default_service, _default_instance)


def get_engine() -> Engine:  # noqa: F811
    if _engine is None:
        raise ConnectionNotInitialized(
            "ObjectModel not connected. Call connect(db_connection_string) first."
        )
    return _engine


def get_session() -> Session:
    return Session(get_engine())


def get_default_scope() -> tuple[str, str]:
    return _default_service, _default_instance


class CoreServiceProvider:
    def __init__(self, session: Session, event_bus: DomainEventBus | None = None):
        logger.debug("CoreServiceProvider.__init__ session id=%s obj=%s", id(session), session)
        self.session = session
        logger.debug(
            "CoreServiceProvider stored session id=%s obj=%s", id(self.session), self.session
        )
        self._event_bus = event_bus or NullEventBus()
        # Cached components per-session
        self._metamodel_repo: MetamodelRepositoryFacade | None = None
        self._instances_repo: ObjectInstanceRepositoryAdapter | None = None
        self._linked_repo: LinkedObjectRepositoryAdapter | None = None
        self._instances_svc: InstancesService | None = None
        self._linked_svc: LinkedObjectsService | None = None
        self._metamodel_svc: MetamodelService | None = None
        self._instances_bus: DomainEventBus | None = None
        self._linked_bus: DomainEventBus | None = None

    def metamodel_repository(self) -> MetamodelRepositoryFacade:
        if self._metamodel_repo is None:
            self._metamodel_repo = MetamodelRepositoryFacade(self.session)
        return self._metamodel_repo

    def instances_repository(self) -> ObjectInstanceRepositoryAdapter:
        if self._instances_repo is None:
            logger.debug("instances_repository session id=%s", id(self.session))
            self._instances_repo = ObjectInstanceRepositoryAdapter(
                SQLObjectInstanceRepository(self.session), self.metamodel_repository()
            )
        return self._instances_repo

    def linked_objects_repository(self) -> LinkedObjectRepositoryAdapter:
        if self._linked_repo is None:
            self._linked_repo = LinkedObjectRepositoryAdapter(
                SQLLinkedObjectRepository(self.session), self.metamodel_repository()
            )
        return self._linked_repo

    def instances_service(self, event_bus: DomainEventBus | None = None) -> InstancesService:
        """Get instances service with proper dependency injection.

        Args:
            event_bus: Optional event bus for domain events

        Returns:
            InstancesService instance with repository and event bus injection

        Raises:
            RuntimeError: If service initialization fails
        """
        bus = event_bus or self._event_bus or NullEventBus()
        if self._instances_svc is None or self._instances_bus is not bus:
            try:
                self._instances_svc = InstancesService(
                    self.instances_repository(),
                    self.metamodel_repository(),
                    bus,
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize InstancesService: {str(e)}") from e
            self._instances_bus = bus
        return self._instances_svc

    def linked_objects_service(
        self, event_bus: DomainEventBus | None = None
    ) -> LinkedObjectsService:
        """Get linked objects service with proper dependency injection.

        Args:
            event_bus: Optional event bus for domain events

        Returns:
            LinkedObjectsService instance with repository and event bus injection

        Raises:
            RuntimeError: If service initialization fails
        """
        bus = event_bus or self._event_bus or NullEventBus()
        if self._linked_svc is None or self._linked_bus is not bus:
            try:
                self._linked_svc = LinkedObjectsService(
                    self.linked_objects_repository(),
                    self.metamodel_repository(),
                    bus,
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize LinkedObjectsService: {str(e)}") from e
            self._linked_bus = bus
        return self._linked_svc

    def metamodel_service(self) -> MetamodelService:
        """Get metamodel service with proper dependency injection.

        Returns:
            MetamodelService instance with repository injection

        Raises:
            RuntimeError: If repository initialization fails
        """
        if self._metamodel_svc is None:
            try:
                self._metamodel_svc = MetamodelService(self.metamodel_repository())
            except Exception as e:
                raise RuntimeError(f"Failed to initialize MetamodelService: {str(e)}") from e
        return self._metamodel_svc


class MetamodelRepositoryFacade:
    """
    Facade over SQLMetamodelRepository providing additional lookups expected by services/adapters.
    """

    def __init__(self, session: Session):
        self._session = session
        self._repo = SQLMetamodelRepository(session)

    # Direct RID lookups used by services
    def get_object_type_by_rid(self, rid: str) -> ObjectType | None:
        stmt = select(ObjectType).where(ObjectType.rid == rid)
        return self._session.exec(stmt).first()

    def get_link_type_by_rid(self, rid: str) -> LinkType | None:
        stmt = select(LinkType).where(LinkType.rid == rid)
        return self._session.exec(stmt).first()

    # Prefer underlying repository for tenant-aware queries, but provide a resilient fallback
    def get_object_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> ObjectType | None:
        obj = self._repo.get_object_type_by_api_name(
            service, instance, api_name, version=version, include_inactive=include_inactive
        )
        if obj is not None:
            return obj
        # Fallback: ignore Resource join if needed (useful in minimal setups/tests)
        stmt = select(ObjectType).where(ObjectType.api_name == api_name)
        if version is not None:
            stmt = stmt.where(ObjectType.version == version)
        elif not include_inactive:
            from sqlalchemy import true as sa_true

            stmt = stmt.where(ObjectType.is_latest == sa_true())
        return self._session.exec(stmt).first()

    def get_link_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> LinkType | None:
        lt = self._repo.get_link_type_by_api_name(
            service, instance, api_name, version=version, include_inactive=include_inactive
        )
        if lt is not None:
            return lt
        # Fallback without Resource join
        stmt = select(LinkType).where(LinkType.api_name == api_name)
        if version is not None:
            stmt = stmt.where(LinkType.version == version)
        elif not include_inactive:
            from sqlalchemy import true as sa_true

            stmt = stmt.where(LinkType.is_latest == sa_true())
        return self._session.exec(stmt).first()

    def get_interface_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ):
        getter = getattr(self._repo, "get_interface_type_by_api_name", None)
        if callable(getter):
            iface = getter(
                service, instance, api_name, version=version, include_inactive=include_inactive
            )
            if iface is not None:
                return iface
        return None

    # Delegate all other attribute access to underlying repo
    def __getattr__(self, name: str):
        return getattr(self._repo, name)


class Ontology:
    """
    Main entry point for ontology operations with explicit connection management.

    Replaces global state pattern with dependency injection for better testability
    and multi-connection scenarios.
    """

    def __init__(self, engine: Engine, service: str = "default", instance: str = "default"):
        self.engine = engine
        self.service = service
        self.instance = instance
        self._migrations_manager = None
        # Configure SQLite connections for better concurrency in tests
        try:
            if getattr(self.engine, "dialect", None) and self.engine.dialect.name == "sqlite":
                from sqlalchemy import event

                @event.listens_for(self.engine, "connect")
                def _set_sqlite_pragma(dbapi_connection, connection_record):  # pragma: no cover - connection hook
                    try:
                        cursor = dbapi_connection.cursor()
                        # WAL allows readers during a writer transaction and helps reduce lock contention
                        cursor.execute("PRAGMA journal_mode=WAL")
                        # Increase wait time for locks so nested writers can make progress
                        cursor.execute("PRAGMA busy_timeout=30000")
                        # Keep default foreign key behavior (do not force ON) to avoid
                        # constraint failures for synthetic RIDs in minimal test setups.
                        cursor.close()
                    except Exception:
                        pass
        except Exception:
            # Non-fatal if pragmas cannot be applied
            pass

    def initialize_database(self):
        """Initialize base metamodel tables in a clean database."""
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Create a new database session."""
        return Session(self.engine)

    def get_default_scope(self) -> tuple[str, str]:
        """Get the default service/instance scope."""
        return self.service, self.instance

    def get_core_provider(self, session: Session) -> CoreServiceProvider:
        """Get a core service provider for the given session."""
        return CoreServiceProvider(session)

    @property
    def migrations_manager(self):
        """Lazy-loaded migrations manager."""
        if self._migrations_manager is None:
            from .migrations import MigrationsManager

            self._migrations_manager = MigrationsManager(self)
        return self._migrations_manager

    def migrate(
        self, *, allow_destructive: bool = False, dry_run: bool = False, generate: bool = False
    ):
        """
        Apply schema changes with optional migration generation.

        Args:
            allow_destructive: Allow destructive changes (requires migration file)
            dry_run: Show plan without executing
            generate: Generate migration file for detected changes

        Returns:
            Migration plan or execution results.
        """
        if generate:
            return self.migrations_manager.make_migration(
                message="Auto-generated migration", auto_apply=allow_destructive
            )
        return self.migrations_manager.migrate(allow_destructive=allow_destructive, dry_run=dry_run)

    def model(self, model_class):
        """
        Decorator to register a model with this ontology instance.

        Usage:
            @ontology.model
            class MyModel(ObjectModel):
                ...
        """
        from .model import _model_registry

        # Set the database connection on the model class
        model_class._db = self

        # Update registry with ontology info if not already present
        # Only register if it has the required attributes
        if (
            model_class not in _model_registry
            and hasattr(model_class, "__primary_key__")
            and hasattr(model_class, "__object_type_api_name__")
        ):
            _model_registry[model_class] = {
                "primary_key": model_class.__primary_key__,
                "object_type_api_name": model_class.__object_type_api_name__,
                "ontology": self,
                "service": self.service,
                "instance": self.instance,
            }
        elif model_class in _model_registry:
            # Update with ontology-specific info if already registered
            _model_registry[model_class].update(
                {"ontology": self, "service": self.service, "instance": self.instance}
            )

        return model_class

    def apply_schema(self, models, *args, **kwargs):
        """
        Apply schema for the given models.

        Args:
            models: List of model classes to apply schema for
            *args: Additional arguments (for compatibility)
            **kwargs: Additional keyword arguments (for compatibility)

        Returns:
            Dictionary with results for each model
        """
        from .schema import _plan_schema_with_session

        # Get dry_run flag from kwargs
        dry_run = kwargs.get("dry_run", False)

        if dry_run:
            # For dry run, we need to pass session and scope
            with self.get_session() as session:
                return _plan_schema_with_session(models, session, self.service, self.instance)
        else:
            # Execute the schema plan
            with self.get_session() as session:
                plan = _plan_schema_with_session(models, session, self.service, self.instance)
                results = {}

                provider = self.get_core_provider(session)
                repo = provider.metamodel_repository()

                # Create object types first and collect them for link processing
                created_object_types = {}
                for _model_cls, agg in plan.object_types_to_create:
                    try:
                        # Set service and instance on the object type
                        agg.object_type._service = self.service
                        agg.object_type._instance = self.instance
                        saved_object_type = repo.save_object_type(agg.object_type)
                        created_object_types[agg.object_type.api_name] = saved_object_type

                        # Create properties with the correct RID using the conversion function
                        from .schema import _property_type_from_definition

                        for prop in agg.properties:
                            property_type = _property_type_from_definition(
                                prop, saved_object_type.rid, saved_object_type.api_name
                            )
                            property_type._service = self.service
                            property_type._instance = self.instance
                            repo.save_property_type(property_type)

                        results[agg.object_type.api_name] = (True, None)
                    except Exception as e:
                        results[agg.object_type.api_name] = (False, str(e))

                # Create link types after object types are created
                for link_api_name, link_type in plan.link_types_to_create:
                    try:
                        # Set service and instance on the link type
                        link_type._service = self.service
                        link_type._instance = self.instance

                        # Fill in the RIDs from created object types
                        if link_type.from_object_type_api_name in created_object_types:
                            link_type.from_object_type_rid = created_object_types[
                                link_type.from_object_type_api_name
                            ].rid
                        if link_type.to_object_type_api_name in created_object_types:
                            link_type.to_object_type_rid = created_object_types[
                                link_type.to_object_type_api_name
                            ].rid

                        repo.save_link_type(link_type)
                        results[link_api_name] = (True, None)
                    except Exception as e:
                        results[link_api_name] = (False, str(e))

            return results


# Legacy global functions with deprecation warnings
def connect_legacy(  # noqa: F811
    db_connection_string: str,
    *,
    echo: bool = False,
    service: str = "default",
    instance: str = "default",
) -> Ontology:
    """
    Connect to the database and return an Ontology instance.

    DEPRECATED: Use Ontology(engine=create_engine(...)) instead.
    """
    warnings.warn(
        "connect() is deprecated. Use Ontology(engine=create_engine(...)) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    global _engine, _default_service, _default_instance
    _engine = create_engine(db_connection_string, echo=echo)
    _default_service = service
    _default_instance = instance
    return Ontology(_engine, service, instance)


def get_engine() -> Engine:  # noqa: F811
    """
    Get the global engine.

    DEPRECATED: Use Ontology.engine instead.
    """
    warnings.warn(
        "get_engine() is deprecated. Use Ontology.engine instead.", DeprecationWarning, stacklevel=2
    )
    if _engine is None:
        raise ConnectionNotInitialized(
            "ObjectModel not connected. Call connect(db_connection_string) first."
        )
    return _engine


def get_session() -> Session:
    """
    Get a session using the global engine.

    DEPRECATED: Use Ontology.get_session() instead.
    """
    warnings.warn(
        "get_session() is deprecated. Use Ontology.get_session() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Session(get_engine())


def get_default_scope() -> tuple[str, str]:
    """
    Get the default scope from global state.

    DEPRECATED: Use Ontology.get_default_scope() instead.
    """
    warnings.warn(
        "get_default_scope() is deprecated. Use Ontology.get_default_scope() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _default_service, _default_instance
