from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from ontologia._compat import override

if TYPE_CHECKING:
    from .connection import Ontology

from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel

try:  # Pydantic v2 internal location
    from pydantic._internal._model_construction import (
        ModelMetaclass as PydanticModelMetaclass,  # type: ignore[no-redef]
    )
except Exception:
    try:  # Older export (some v1/v2 builds)
        from pydantic.main import ModelMetaclass as PydanticModelMetaclass  # type: ignore[no-redef]
    except Exception:  # Fallback
        PydanticModelMetaclass = type(BaseModel)  # type: ignore[assignment, misc]
import threading
from contextlib import contextmanager

from sqlmodel import Session

from .connection import CoreServiceProvider
from .errors import NotFound

_model_registry: dict[type[ObjectModel], dict[str, Any]] = {}


def clear_model_registry() -> None:
    """Clear the global model registry. Useful for testing."""
    global _model_registry
    _model_registry.clear()


# Thread-local session context for transactions
_session_local = threading.local()


def _get_current_session() -> Session | None:
    """Get the current thread-local session if inside a transaction."""
    return getattr(_session_local, "session", None)


@contextmanager
def _set_session(session: Session) -> Generator[None, None, None]:
    """Temporarily set the thread-local session."""
    old = getattr(_session_local, "session", None)
    _session_local.session = session
    try:
        yield
    finally:
        if old is None:
            if hasattr(_session_local, "session"):
                delattr(_session_local, "session")
        else:
            _session_local.session = old


# Modern type system with TypeVar for better inference
T = TypeVar("T", bound="ObjectModel")


# Protocol for database-connected models
@runtime_checkable
class DatabaseConnected(Protocol):
    """Protocol for models that have database connections."""

    _db: Ontology

    def get_session(self) -> Any: ...


# Enhanced dataclass for query results
@dataclass(frozen=True, slots=True)
class QueryResult(Generic[T]):
    """Immutable result container with type safety."""

    items: list[T]
    total_count: int | None = None
    has_more: bool = False

    @override
    def __len__(self) -> int:
        return len(self.items)

    def first(self) -> T | None:
        """Get first item or None."""
        return self.items[0] if self.items else None


class ObjectModelMeta(PydanticModelMetaclass):
    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any
    ) -> type:
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        # Only register if it has the required attributes
        if hasattr(cls, "__primary_key__") and hasattr(cls, "__object_type_api_name__"):
            _model_registry[cls] = {
                "primary_key": cls.__primary_key__,
                "object_type_api_name": cls.__object_type_api_name__,
            }
        return cls


class ObjectModel(BaseModel, metaclass=ObjectModelMeta):  # type: ignore[misc]
    # Allow private/aux attributes on instances (e.g., _is_persisted tracking)
    model_config = {"extra": "allow"}
    __primary_key__: ClassVar[str] = "pk"
    _db: ClassVar[Ontology]  # injected by Ontology.model decorator

    @classmethod
    def _meta(cls) -> dict[str, Any]:
        return _model_registry[cls]

    @classmethod
    def object_type_api_name(cls) -> str:
        meta = cls._meta()
        return meta["object_type_api_name"]  # type: ignore[return-value, no-any-return]

    @classmethod
    def get(cls, pk: str | int) -> ObjectModel:
        """Get an object instance by primary key using modern Ontology injection.

        Args:
            pk: Primary key value

        Returns:
            ObjectModel instance

        Raises:
            RuntimeError: If model is not properly configured with @ontology_db decorator
            ValueError: If primary key is invalid
        """
        if not hasattr(cls, "_db"):
            raise RuntimeError(
                f"Model '{cls.__name__}' must be decorated with @ontology_db to use get() without explicit db. "
                "Ensure the model is properly registered with an Ontology connection."
            )

        if not pk:
            raise ValueError("Primary key cannot be empty")

        db = cls._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            svc = provider.instances_service()
            try:
                from datetime import UTC, datetime

                resp = svc.get_object(
                    service,
                    instance,
                    cls.object_type_api_name(),
                    str(pk),
                    valid_at=datetime.now(UTC),
                )
            except HTTPException as e:
                if getattr(e, "status_code", None) == status.HTTP_404_NOT_FOUND:
                    raise NotFound(f"{cls.object_type_api_name()}:{pk} not found") from e
                raise
        data = dict(resp.properties or {})
        # Drop LinkModel descriptor fields from raw properties to avoid validation issues;
        # linked relationships are handled via dedicated APIs.
        try:
            from .link import LinkModel as _LinkModel  # Local import to avoid cycles

            link_fields = {
                name for name, val in cls.__dict__.items() if isinstance(val, _LinkModel)
            }
            for lf in link_fields:
                data.pop(lf, None)
        except Exception:
            pass
        data[cls._meta()["primary_key"]] = resp.pk_value
        try:
            obj = cls.model_construct(**data)  # type: ignore[attr-defined]
        except Exception:
            # Fallback to validated construction if construct is unavailable
            obj = cls(**data)
        # Mark as loaded from persistence so subsequent save() calls treat as update
        try:
            obj._is_persisted = True
        except Exception:
            pass
        return obj

    @classmethod
    def query(cls: type[T]) -> QueryBuilder[T]:
        return QueryBuilder(cls)

    def save(self, session: Any = None) -> ObjectModel:
        """Upsert this object instance using modern Ontology injection."""
        from ontologia.application.instances_service import ObjectUpsertRequest

        pk = getattr(self, self.__primary_key__)
        # Serialize properties excluding primary key and LinkModel descriptors
        properties = dict(self.model_dump(exclude={self.__primary_key__}))
        try:
            from .link import LinkModel as _LinkModel  # Local import to avoid cycles

            link_fields = {
                name for name, val in self.__class__.__dict__.items() if isinstance(val, _LinkModel)
            }
            for lf in link_fields:
                properties.pop(lf, None)
        except Exception:
            # Best-effort cleanup only
            pass

        if not hasattr(self.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use save() without explicit db"
            )

        db = self.__class__._db
        service, instance = db.get_default_scope()

        # Use provided session or get current session
        current = session or _get_current_session()

        if current:
            provider = CoreServiceProvider(current)
            # If this instance was not loaded from DB and another record exists with the same
            # primary key, treat as a duplicate create attempt within an explicit transaction
            # and raise to allow caller-managed rollback semantics.
            if not getattr(self, "_is_persisted", False):
                try:
                    from datetime import UTC as _UTC
                    from datetime import datetime

                    _ = provider.instances_service().get_object(
                        service,
                        instance,
                        self.object_type_api_name(),
                        str(pk),
                        valid_at=datetime.now(_UTC),
                    )
                    # If found, raise duplicate
                    raise ValueError(
                        f"Duplicate primary key for {self.object_type_api_name()}:{pk}"
                    )
                except HTTPException as e:
                    if getattr(e, "status_code", None) != status.HTTP_404_NOT_FOUND:
                        raise
            req = ObjectUpsertRequest(pk_value=pk, properties=properties)
            response = provider.instances_service().upsert_object(
                service, instance, self.object_type_api_name(), req
            )
            # Don't commit when using provided session - let context manager handle it
            # Update self with response data
            for key, value in response.properties.items():
                setattr(self, key, value)
            return self
        else:
            session_ctx = db.get_session()
            with session_ctx as session:
                provider = CoreServiceProvider(session)
                req = ObjectUpsertRequest(pk_value=pk, properties=properties)
                response = provider.instances_service().upsert_object(
                    service, instance, self.object_type_api_name(), req
                )
                session.commit()
                # Update self with response data
                for key, value in response.properties.items():
                    setattr(self, key, value)
                return self

    def delete(self) -> None:
        """Delete this object instance using modern Ontology injection."""
        if not hasattr(self.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use delete() without explicit db"
            )

        pk = getattr(self, self.__primary_key__)
        db = self.__class__._db
        service, instance = db.get_default_scope()
        current = _get_current_session()

        if current:
            provider = CoreServiceProvider(current)
            try:
                provider.instances_service().delete_object(
                    service, instance, self.object_type_api_name(), pk
                )
            except HTTPException as e:
                if getattr(e, "status_code", None) == status.HTTP_404_NOT_FOUND:
                    raise NotFound(f"{self.object_type_api_name()}:{pk} not found") from e
                raise
        else:
            session_ctx = db.get_session()
            with session_ctx as session:
                provider = CoreServiceProvider(session)
                try:
                    provider.instances_service().delete_object(
                        service, instance, self.object_type_api_name(), pk
                    )
                    session.commit()
                except HTTPException as e:
                    if getattr(e, "status_code", None) == status.HTTP_404_NOT_FOUND:
                        raise NotFound(f"{self.object_type_api_name()}:{pk} not found") from e
                    raise

    @classmethod
    def where(cls: type[T], *args: Any, **kwargs: Any) -> QueryBuilder[T]:
        qb = QueryBuilder(cls)
        return qb.where(*args, **kwargs)

    @classmethod
    def transaction(cls) -> _TransactionContextManager:
        """Return a session/transaction context manager using modern Ontology injection.

        Example:
            with MyModel.transaction():
                obj1 = MyModel(...).save()
                obj2 = MyModel(...).save()
                # Both use the same session; transaction commits on exit.
        """
        if not hasattr(cls, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use transaction() without explicit db"
            )

        # Always create an independent session per transaction context to ensure
        # nested transactions commit/rollback independently of outer scopes.
        # The context manager maintains thread-local session state so that
        # save() calls within the block use the correct session.
        sess = cls._db.get_session()
        return _TransactionContextManager(sess, owns_session=True)


class _TransactionContextManager:
    """Context manager supporting nested transactions using a thread-local session.

    - Outermost context owns the session and is responsible for commit/rollback/close.
    - Nested contexts reuse the same session and only adjust a depth counter.
    """

    def __init__(self, session: Session, owns_session: bool = True):
        self.session = session
        self.owns_session = owns_session
        self._old_session: Session | None = None
        self._old_depth: int = 0

    def __enter__(self) -> Session:
        # Always establish a new session context, preserving any existing one
        self._old_session = getattr(_session_local, "session", None)
        self._old_depth = getattr(_session_local, "depth", 0)
        _session_local.session = self.session
        _session_local.depth = self._old_depth + 1
        # Annotate session with OGM transaction nesting depth for downstream heuristics
        try:
            info = getattr(self.session, "info", None)
            if isinstance(info, dict):
                info["ogm_tx_depth"] = _session_local.depth
        except Exception:
            pass
        return self.session

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        # Commit or rollback this session independently of outer contexts
        try:
            if exc_type:
                try:
                    self.session.rollback()
                except Exception:
                    pass
            else:
                try:
                    self.session.commit()
                except Exception:
                    pass
        finally:
            try:
                self.session.close()
            except Exception:
                pass
            # Restore previous thread-local session and depth
            if self._old_session is not None:
                _session_local.session = self._old_session
                _session_local.depth = self._old_depth
            else:
                if hasattr(_session_local, "session"):
                    try:
                        delattr(_session_local, "session")
                    except Exception:
                        pass
                if hasattr(_session_local, "depth"):
                    try:
                        delattr(_session_local, "depth")
                    except Exception:
                        pass


class QueryBuilder(Generic[T]):
    """
    Fluent builder for querying OntologyModel instances.

    Supports advanced filtering and ordering with full JSON field support.
    All operations are executed via InstancesService.search_objects.

    Features:
    - Filters: eq, ne, lt, le, gt, ge, like, ilike, in
    - Ordering: ascending/descending on any field
    - Pagination: limit and offset
    - JSON field filtering on nested data
    """

    def __init__(self, model_cls: type[T], *, limit: int | None = None, offset: int | None = None):
        self._model_cls = model_cls
        self._limit = limit
        self._offset = offset
        self._filters: list[tuple[str, str, Any]] = []  # (field, operator, value)
        self._order_by: list[tuple[str, str]] = []  # (field, direction)
        self._distinct_fields: list[str] | None = None  # Fields for DISTINCT clause
        self._valid_at: datetime | None = None  # Point-in-time query timestamp
        self._temporal_range: dict[str, datetime | None] | None = (
            None  # Complex temporal range query
        )

    def limit(self, n: int) -> QueryBuilder[T]:
        """Set the maximum number of results to return."""
        self._limit = n
        return self

    def offset(self, n: int) -> QueryBuilder[T]:
        """Set the number of results to skip."""
        self._offset = n
        return self

    def filter(self, field: str, operator: str, value: Any) -> QueryBuilder[T]:
        """Add a filter condition. Supported operators: eq, ne, lt, le, gt, ge, like, ilike, in.

        Args:
            field: Field name to filter on (e.g., "price", "name", "data.category")
            operator: Comparison operator (eq, ne, lt, le, gt, ge, like, ilike, in)
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        self._filters.append((field, operator, value))
        return self

    def where(self, field: str, operator: str, value: Any) -> QueryBuilder[T]:
        """Alias for filter method - add a filter condition.

        Args:
            field: Field name to filter on
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining
        """
        return self.filter(field, operator, value)

    def order_by(self, field: str, direction: str = "asc") -> QueryBuilder[T]:
        """Add ordering. direction: 'asc' or 'desc'.

        Args:
            field: Field name to sort by
            direction: Sort direction ('asc' or 'desc')

        Returns:
            Self for method chaining
        """
        self._order_by.append((field, direction.lower()))
        return self

    def all(self) -> list[T]:
        """Execute the query and return all matching instances using modern Ontology injection.

        Returns:
            List of model instances matching the query criteria

        Raises:
            RuntimeError: If model is not properly configured with @ontology_db decorator
            ValueError: If query parameters are invalid
        """
        if not hasattr(self._model_cls, "_db"):
            raise RuntimeError(
                f"Model '{self._model_cls.__name__}' must be decorated with @ontology_db to use query() without explicit db. "
                "Ensure the model is properly registered with an Ontology connection."
            )

        db = self._model_cls._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            from ontologia.application.instances_service import (
                ObjectSearchRequest,
                SearchFilter,
                SearchOrder,
            )

            req = ObjectSearchRequest(
                filters=[SearchFilter(field=f, operator=o, value=v) for f, o, v in self._filters],
                order_by=[SearchOrder(field=f, direction=d) for f, d in self._order_by],
                limit=self._limit,
                offset=self._offset,
            )
            resp = provider.instances_service().search_objects(
                service, instance, self._model_cls.object_type_api_name(), req
            )
            pk_field = self._model_cls.__primary_key__
            results = []
            for obj_data in resp.objects:
                data = dict(obj_data.properties or {})
                data[pk_field] = obj_data.pk_value
                # Remove link descriptor fields to avoid validation noise
                try:
                    from .link import LinkModel as _LinkModel  # Local import to avoid cycles

                    link_fields = {
                        name
                        for name, val in self._model_cls.__dict__.items()
                        if isinstance(val, _LinkModel)
                    }
                    for lf in link_fields:
                        data.pop(lf, None)
                except Exception:
                    pass
                results.append(self._model_cls(**data))
            return results

    def __iter__(self):
        """Make QueryBuilder iterable."""
        return iter(self.all())

    def first(self) -> T | None:
        """Return the first matching instance or None.

        Returns:
            First matching object or None if no results
        """
        self._limit = 1
        results = self.all()
        return results[0] if results else None

    def exists(self) -> bool:
        """Check if any objects match the query criteria.

        Returns:
            True if any objects exist matching the current filters
        """
        self._limit = 1
        return len(self.all()) > 0

    def count(self) -> int:
        """Get the count of objects matching the query criteria.

        Returns:
            Total count of matching objects
        """
        self._limit = None
        # For count, we can optimize - we just need to know if there are any matches
        # TODO: Implement efficient count() method in InstancesService
        results = self.all()
        return len(results)

    def distinct(self, fields: str | list[str]) -> QueryBuilder[T]:
        """Add DISTINCT clause for the specified fields.

        Args:
            fields: Single field name as string or list of field names

        Returns:
            Self for method chaining
        """
        # Store DISTINCT requirement for later use in execution
        if isinstance(fields, str):
            self._distinct_fields = [fields]
        else:
            self._distinct_fields = fields
        return self

    def valid_at(self, timestamp: datetime | str) -> QueryBuilder[T]:
        """Filter results to be valid at the specified point in time.

        Args:
            timestamp: Point in time to check validity

        Returns:
            Self for method chaining
        """
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        self._valid_at = timestamp
        return self

    def as_of(self, timestamp: datetime | str) -> QueryBuilder[T]:
        """Alias for valid_at() - filter results to be valid at the specified point in time.

        Args:
            timestamp: Point in time to check validity

        Returns:
            Self for method chaining
        """
        return self.valid_at(timestamp)

    def temporal_range(
        self,
        valid_from: datetime | str | None = None,
        valid_to: datetime | str | None = None,
        transaction_from: datetime | str | None = None,
        transaction_to: datetime | str | None = None,
    ) -> QueryBuilder[T]:
        """Filter results by temporal ranges for more complex historical queries.

        Args:
            valid_from: Start of valid time range (inclusive)
            valid_to: End of valid time range (inclusive)
            transaction_from: Start of transaction time range (inclusive)
            transaction_to: End of transaction time range (inclusive)

        Returns:
            Self for method chaining
        """
        # Convert string timestamps to datetime objects
        if isinstance(valid_from, str):
            valid_from = datetime.fromisoformat(valid_from)
        if isinstance(valid_to, str):
            valid_to = datetime.fromisoformat(valid_to)
        if isinstance(transaction_from, str):
            transaction_from = datetime.fromisoformat(transaction_from)
        if isinstance(transaction_to, str):
            transaction_to = datetime.fromisoformat(transaction_to)

        self._temporal_range = {
            "valid_from": valid_from,
            "valid_to": valid_to,
            "transaction_from": transaction_from,
            "transaction_to": transaction_to,
        }
        return self
