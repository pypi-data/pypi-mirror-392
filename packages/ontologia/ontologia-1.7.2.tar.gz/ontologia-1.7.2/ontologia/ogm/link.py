from __future__ import annotations

import sys
from typing import Any, Generic, TypeVar, get_args, get_origin

from .connection import CoreServiceProvider
from .model import ObjectModel

T = TypeVar("T", bound=ObjectModel)

# Global registry for link definitions
_link_registry: dict[str, LinkModel] = {}


def clear_link_registry() -> None:
    """Clear the global link registry. Useful for testing."""
    global _link_registry
    _link_registry.clear()


class LinkModel(Generic[T]):
    """
    Descriptor defining an ontological relationship. When accessed on an instance,
    returns a LinkProxy bound to that source instance.

    Target model can be specified in two ways:

    1. Explicit (recommended for clarity and circular imports):
       empregador: Link["Empresa"] = Link("emprega", inverse="funcionarios", target_model=Empresa)

    2. Inferred via type hint:
       funcionarios: Link[Funcionario] = Link("emprega", inverse="empregador")
    """

    def __init__(
        self,
        api_name: str,
        *,
        inverse: str | None = None,
        direction: str = "outgoing",
        target_model: type[T] | None = None,
        cardinality: str = "one_to_many",
        properties: dict[str, Any] | None = None,
    ) -> None:
        self.api_name = api_name
        self.inverse = inverse
        self.direction = direction
        self.cardinality = (
            cardinality  # e.g., "one_to_many", "many_to_one", "one_to_one", "many_to_many"
        )
        self.properties = properties or {}
        self._owner: type[ObjectModel] | None = None
        self._name: str | None = None
        self._target_model: type[T] | None = target_model

    @property
    def target_model(self) -> type[T] | None:
        """Get the target model class."""
        return self._target_model

    def __set_name__(self, owner: type[ObjectModel], name: str) -> None:
        self._owner = owner
        self._name = name

        # Register the link globally
        _link_registry[self.api_name] = self

        # Try to resolve target model from type hints: e.g., Link[Funcionario]
        try:
            module = sys.modules.get(owner.__module__)
            globalns = module.__dict__ if module else None
            # get_type_hints on the owner class may resolve ForwardRefs
            from typing import get_type_hints

            hints = get_type_hints(owner, globalns=globalns, localns=owner.__dict__)
            hint = hints.get(name)

            def _resolve_from_hint(h: Any) -> type[ObjectModel] | None:
                o = get_origin(h)
                if o is LinkModel:
                    args = get_args(h)
                    if args:
                        t = args[0]
                        if isinstance(t, type) and issubclass(t, ObjectModel):
                            return t
                # Handle ClassVar[Link[T]]
                try:
                    from typing import ClassVar as _ClassVar  # type: ignore
                except Exception:
                    _ClassVar = None  # type: ignore
                if _ClassVar is not None and o is _ClassVar:
                    inner = get_args(h)
                    if inner:
                        return _resolve_from_hint(inner[0])
                return None

            target = _resolve_from_hint(hint)
            if target is not None:
                self._target_model = target  # type: ignore[assignment]
        except Exception:
            # Best-effort; keep optional target_model from constructor if provided
            pass

    def __get__(
        self, instance: ObjectModel | None, owner: type[ObjectModel]
    ) -> LinkProxy[T] | LinkModel[T]:
        if instance is None:
            return self
        if self._target_model is None:
            # Attempt late resolution (forward refs) now that class may be fully defined
            if self._name is not None:
                self.__set_name__(owner, self._name)
        if self._target_model is None:
            raise ValueError(
                f"Não foi possível resolver o modelo de destino para o link '{owner.__name__}.{self._name}'. "
                f"Especifique explicitamente com target_model=MeuModelo no Link(...), ou garanta que a anotação "
                f"Link[MeuModelo] esteja resolvível no escopo."
            )
        return LinkProxy(
            source_instance=instance,
            link_type_api_name=self.api_name,
            direction=self.direction,
            target_model=self._target_model,
        )


class LinkProxy(Generic[T]):
    """A proxy bound to a source ObjectModel instance for a specific LinkType."""

    def __init__(
        self,
        *,
        source_instance: ObjectModel,
        link_type_api_name: str,
        direction: str,
        target_model: type[T],
    ) -> None:
        self._source = source_instance
        self._link_type_api_name = link_type_api_name
        self._direction = direction
        self._target_model = target_model

    def _source_pk(self) -> str:
        meta = self._source.__class__._meta()
        pk_field = meta["primary_key"]
        return str(getattr(self._source, pk_field))

    def _target_pk_field(self) -> str:
        meta = self._target_model._meta()
        return meta["primary_key"]  # type: ignore[return-value, no-any-return]

    def all(self) -> list[T]:
        """Fetch all linked target objects as T instances using modern Ontology injection."""
        if not hasattr(self._source.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use Link operations without explicit db"
            )

        db = self._source.__class__._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        source_ot = self._source.__class__.object_type_api_name()
        source_pk = self._source_pk()

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            los = provider.linked_objects_service()
            ios = provider.instances_service()
            response = los.traverse_linked_objects(
                service,
                instance,
                object_type_api_name=source_ot,
                pk_value=source_pk,
                link_type_api_name=self._link_type_api_name,
                direction=self._direction,
                limit=1000,
            )

            # Choose pk side based on direction
            def _to_pk(edge: Any) -> str:  # type: ignore[no-any-return]
                return (
                    edge.target_pk_value if self._direction == "outgoing" else edge.source_pk_value
                )  # type: ignore[return-value, no-any-return]

            objs: list[T] = []
            for edge in response.linked_objects:
                pk = _to_pk(edge)
                dto = ios.get_object(
                    service, instance, self._target_model.object_type_api_name(), pk
                )
                data = dict(dto.properties or {})
                data[self._target_pk_field()] = dto.pk_value
                objs.append(self._target_model(**data))
            return objs

    def add(self, target: T, *, properties: dict[str, Any] | None = None) -> None:
        """Create or update a link between source and target using modern Ontology injection."""
        from ontologia.application.linked_objects_service import LinkedObjectUpsertRequest

        if not isinstance(target, self._target_model):
            raise TypeError(
                f"Expected instance of {self._target_model.__name__}, got {type(target).__name__}"
            )

        if not hasattr(self._source.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use Link operations without explicit db"
            )

        db = self._source.__class__._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        source_pk = self._source_pk()
        target_pk = str(getattr(target, self._target_pk_field()))

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            req = LinkedObjectUpsertRequest(
                source_pk_value=source_pk,
                target_pk_value=target_pk,
                properties=dict(properties or {}),
            )
            provider.linked_objects_service().upsert_linked_object(
                service,
                instance,
                link_type_api_name=self._link_type_api_name,
                request=req,
            )

    def remove(self, target: T) -> None:
        """Delete a link between source and target using modern Ontology injection."""
        if not isinstance(target, self._target_model):
            raise TypeError(
                f"Expected instance of {self._target_model.__name__}, got {type(target).__name__}"
            )

        if not hasattr(self._source.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use Link operations without explicit db"
            )

        db = self._source.__class__._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        source_pk = self._source_pk()
        target_pk = str(getattr(target, self._target_pk_field()))

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            provider.linked_objects_service().delete_linked_object(
                service,
                instance,
                link_type_api_name=self._link_type_api_name,
                source_pk_value=source_pk,
                target_pk_value=target_pk,
            )

    def count(self) -> int:
        """Return the number of linked target objects."""
        return len(self.all())

    def exists(self, target: T) -> bool:
        """Check if a specific target object is linked using modern Ontology injection."""
        if not isinstance(target, self._target_model):
            raise TypeError(
                f"Expected instance of {self._target_model.__name__}, got {type(target).__name__}"
            )

        if not hasattr(self._source.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use Link operations without explicit db"
            )

        db = self._source.__class__._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        source_pk = self._source_pk()
        target_pk = str(getattr(target, self._target_pk_field()))

        with session_ctx as session:
            provider = CoreServiceProvider(session)
            los = provider.linked_objects_service()
            response = los.traverse_linked_objects(
                service,
                instance,
                object_type_api_name=self._source.__class__.object_type_api_name(),
                pk_value=source_pk,
                link_type_api_name=self._link_type_api_name,
                direction=self._direction,
                limit=1000,
            )

            # Choose pk side based on direction
            def _to_pk(edge: Any) -> str:  # type: ignore[no-any-return]
                return (
                    edge.target_pk_value if self._direction == "outgoing" else edge.source_pk_value
                )  # type: ignore[return-value, no-any-return]

            return any(_to_pk(edge) == target_pk for edge in response.linked_objects)

    def remove_all(self) -> None:
        """Remove all linked target objects using modern Ontology injection."""
        if not hasattr(self._source.__class__, "_db"):
            raise RuntimeError(
                "Model must be decorated with @ontology_db to use Link operations without explicit db"
            )

        db = self._source.__class__._db
        service, instance = db.get_default_scope()
        session_ctx = db.get_session()

        source_pk = self._source_pk()
        with session_ctx as session:
            provider = CoreServiceProvider(session)
            los = provider.linked_objects_service()
            response = los.traverse_linked_objects(
                service,
                instance,
                object_type_api_name=self._source.__class__.object_type_api_name(),
                pk_value=source_pk,
                link_type_api_name=self._link_type_api_name,
                direction=self._direction,
                limit=1000,
            )
            for edge in response.linked_objects:
                # Compute source/target for delete based on direction
                src_pk = source_pk if self._direction == "outgoing" else edge.source_pk_value
                tgt_pk = edge.target_pk_value if self._direction == "outgoing" else source_pk
                provider.linked_objects_service().delete_linked_object(
                    service, instance, self._link_type_api_name, src_pk, tgt_pk
                )
