"""
Client session abstraction for unified SDK operations.

Provides protocol and implementations for both remote (HTTP) and local
(direct core) modes of operation.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

import httpx

logger = logging.getLogger(__name__)


@runtime_checkable
class ClientSession(Protocol):
    """
    Protocol defining the contract for data operations agnostic to mode.

    All operations are async to support both HTTP and local operations
    with consistent interface.
    """

    async def get_object(self, object_type: str, pk: str) -> dict[str, Any] | None:
        """Retrieve a single object by type and primary key."""
        ...

    async def list_objects(self, object_type: str, **filters: Any) -> list[dict[str, Any]]:
        """List objects of a type with optional filters."""
        ...

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object instance."""
        ...

    async def update_object(
        self, object_type: str, pk: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing object."""
        ...

    async def delete_object(self, object_type: str, pk: str) -> bool:
        """Delete an object by type and primary key."""
        ...

    async def list_object_types(self) -> list[dict[str, Any]]:
        """List all available object types."""
        ...

    async def get_object_type(self, api_name: str) -> dict[str, Any] | None:
        """Get object type definition by API name."""
        ...

    async def create_object_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object type."""
        ...

    async def update_object_type(self, api_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing object type."""
        ...

    async def list_link_types(self) -> list[dict[str, Any]]:
        """List all available link types."""
        ...

    async def get_link_type(self, api_name: str) -> dict[str, Any] | None:
        """Get link type definition by API name."""
        ...

    async def create_link_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new link type."""
        ...

    async def get_linked_objects(
        self, object_type: str, pk: str, link_type: str, direction: str = "outgoing"
    ) -> list[dict[str, Any]]:
        """Get objects linked via a specific link type."""
        ...

    async def create_link(
        self,
        source_type: str,
        source_pk: str,
        link_type: str,
        target_type: str,
        target_pk: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a link between two objects."""
        ...

    async def close(self) -> None:
        """Close session resources."""
        ...


class RemoteSession(ClientSession):
    """
    HTTP-based session implementation for remote API access.

    Communicates with ontologia-api via REST endpoints.
    """

    def __init__(
        self,
        host: str,
        token: str | None = None,
        timeout: float = 30.0,
        ontology: str = "default",
        *,
        use_ogm: bool = False,
    ):
        self.host = host.rstrip("/")
        self.ontology = ontology
        self.timeout = timeout
        self.use_ogm = bool(use_ogm)

        import httpx

        self._client = httpx.AsyncClient(base_url=self.host, timeout=timeout)

        self._headers: dict[str, str] = {"Accept": "application/json"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    def _build_url(self, path: str) -> str:
        """Build full URL for API endpoint."""
        return f"/v2/ontologies/{self.ontology}/{path}"

    async def get_object(self, object_type: str, pk: str) -> dict[str, Any] | None:
        """Retrieve object via HTTP GET."""
        try:
            params = {"use_ogm": "true"} if self.use_ogm else None
            response = await self._client.get(
                self._build_url(f"objects/{object_type}/{pk}"), headers=self._headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting object {object_type}:{pk}: {e}")
            raise

    async def list_objects(self, object_type: str, **filters: Any) -> list[dict[str, Any]]:
        """List objects via HTTP GET with query parameters."""
        try:
            params = {}
            if filters:
                params.update(filters)

            if self.use_ogm:
                params["use_ogm"] = "true"
            response = await self._client.get(
                self._build_url(f"objects/{object_type}"), headers=self._headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing objects {object_type}: {e}")
            raise

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create object via HTTP POST."""
        try:
            params = {"use_ogm": "true"} if self.use_ogm else None
            response = await self._client.post(
                self._build_url(f"objects/{object_type}"),
                headers=self._headers,
                params=params,
                json=data,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating object {object_type}: {e}")
            raise

    async def update_object(
        self, object_type: str, pk: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update object via HTTP PUT."""
        try:
            params = {"use_ogm": "true"} if self.use_ogm else None
            response = await self._client.put(
                self._build_url(f"objects/{object_type}/{pk}"),
                headers=self._headers,
                params=params,
                json=data,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating object {object_type}:{pk}: {e}")
            raise

    async def delete_object(self, object_type: str, pk: str) -> bool:
        """Delete object via HTTP DELETE."""
        try:
            params = {"use_ogm": "true"} if self.use_ogm else None
            response = await self._client.delete(
                self._build_url(f"objects/{object_type}/{pk}"), headers=self._headers, params=params
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise
        except Exception as e:
            logger.error(f"Error deleting object {object_type}:{pk}: {e}")
            raise

    async def list_object_types(self) -> list[dict[str, Any]]:
        """List object types via HTTP GET."""
        try:
            response = await self._client.get(
                self._build_url("object-types"), headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing object types: {e}")
            raise

    async def get_object_type(self, api_name: str) -> dict[str, Any] | None:
        """Get object type via HTTP GET."""
        try:
            response = await self._client.get(
                self._build_url(f"object-types/{api_name}"), headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting object type {api_name}: {e}")
            raise

    async def create_object_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create object type via HTTP POST."""
        try:
            response = await self._client.post(
                self._build_url("object-types"), headers=self._headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating object type: {e}")
            raise

    async def update_object_type(self, api_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update object type via HTTP PUT."""
        try:
            response = await self._client.put(
                self._build_url(f"object-types/{api_name}"), headers=self._headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating object type {api_name}: {e}")
            raise

    async def list_link_types(self) -> list[dict[str, Any]]:
        """List link types via HTTP GET."""
        try:
            response = await self._client.get(self._build_url("link-types"), headers=self._headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing link types: {e}")
            raise

    async def get_link_type(self, api_name: str) -> dict[str, Any] | None:
        """Get link type via HTTP GET."""
        try:
            response = await self._client.get(
                self._build_url(f"link-types/{api_name}"), headers=self._headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting link type {api_name}: {e}")
            raise

    async def create_link_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create link type via HTTP POST."""
        try:
            response = await self._client.post(
                self._build_url("link-types"), headers=self._headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating link type: {e}")
            raise

    async def get_linked_objects(
        self, object_type: str, pk: str, link_type: str, direction: str = "outgoing"
    ) -> list[dict[str, Any]]:
        """Get linked objects via HTTP GET."""
        try:
            response = await self._client.get(
                self._build_url(f"objects/{object_type}/{pk}/links/{link_type}"),
                headers=self._headers,
                params={"direction": direction},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting linked objects {object_type}:{pk} via {link_type}: {e}")
            raise

    async def create_link(
        self,
        source_type: str,
        source_pk: str,
        link_type: str,
        target_type: str,
        target_pk: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create link via HTTP POST."""
        try:
            data = {
                "source_object_type": source_type,
                "source_pk": source_pk,
                "target_object_type": target_type,
                "target_pk": target_pk,
                "properties": properties or {},
            }

            response = await self._client.post(
                self._build_url(f"links/{link_type}"), headers=self._headers, json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(
                f"Error creating link {source_type}:{source_pk} -> {target_type}:{target_pk} via {link_type}: {e}"
            )
            raise

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()


class LocalSession(ClientSession):
    """
    Direct core session implementation for local database access.

    Uses ontologia-core services directly without HTTP overhead.
    """

    def __init__(
        self, connection_string: str, *, use_ogm: bool = False, ogm_module: str | None = None
    ):
        self.connection_string = connection_string
        self._use_ogm = bool(use_ogm)
        self._ogm_module = ogm_module

        # Import SQLModel for database connection
        from sqlmodel import Session, create_engine

        self.engine = create_engine(connection_string)
        self.session_factory = lambda: Session(self.engine)

        # Cache for services to avoid repeated instantiation
        self._services: dict[str, Any] | None = None
        self._initialized = False
        self._ogm_ontology = None

        if self._use_ogm:
            try:
                from ontologia.ogm import Ontology as _Ontology

                self._ogm_ontology = _Ontology(self.engine, service="default", instance="default")
                if self._ogm_module:
                    self._register_ogm_models(self._ogm_module)
            except Exception as e:
                logger.error(f"Failed to initialize OGM for LocalSession: {e}")
                self._use_ogm = False

    def _register_ogm_models(self, module_name: str) -> None:
        try:
            import importlib
            import inspect
            import pkgutil
            from types import ModuleType

            from ontologia.ogm import ObjectModel as _OM

            root = importlib.import_module(module_name)

            def _register(mod: ModuleType) -> None:
                for _, obj in inspect.getmembers(mod, inspect.isclass):
                    try:
                        if issubclass(obj, _OM) and hasattr(obj, "__object_type_api_name__"):
                            self._ogm_ontology.model(obj)  # type: ignore[union-attr]
                    except Exception:
                        continue

            _register(root)
            if hasattr(root, "__path__"):
                for sub in pkgutil.walk_packages(root.__path__, prefix=root.__name__ + "."):
                    try:
                        m = importlib.import_module(sub.name)
                    except Exception:
                        continue
                    _register(m)
        except ModuleNotFoundError:
            logger.warning(f"OGM module '{module_name}' not found; skipping registration")

    def _get_services(self) -> dict[str, Any]:
        """Get or create core services."""
        if self._services is None:
            try:
                # Import core components from ontologia-core v0.5.0
                from ontologia.dependencies.factories import (
                    create_instances_service,
                    create_linked_object_repository,
                    create_linked_objects_service,
                    create_metamodel_repository,
                    create_metamodel_service,
                    create_object_instance_repository,
                )

                with self.session_factory() as session:
                    # Create repositories using factory functions
                    meta_repo = create_metamodel_repository(session)
                    instances_repo = create_object_instance_repository(session, meta_repo)
                    linked_repo = create_linked_object_repository(session, meta_repo)

                    # Create services using factory functions
                    self._services = {
                        "metamodel": create_metamodel_service(meta_repo),
                        "instances": create_instances_service(instances_repo, meta_repo),
                        "linked": create_linked_objects_service(linked_repo, meta_repo),
                    }
            except ImportError as e:
                logger.error(f"Failed to import core components: {e}")
                raise ImportError(
                    "ontologia-core components not available. "
                    "Install with: pip install ontologia-core"
                )

        return self._services

    async def get_object(self, object_type: str, pk: str) -> dict[str, Any] | None:
        """Get object using core service."""
        try:
            if self._use_ogm:
                from ontologia.ogm import get_model_class

                model = get_model_class(object_type)
                if model is not None:
                    try:
                        obj = model.get(pk)
                        return obj.model_dump()
                    except Exception:
                        # Fallback to service-based lookup on OGM error
                        pass
            services = self._get_services()
            with self.session_factory() as session:
                dto = services["instances"].get_object("default", "default", object_type, pk)
                return dto.model_dump() if dto else None
        except Exception as e:
            logger.error(f"Error getting object {object_type}:{pk}: {e}")
            raise

    async def list_objects(self, object_type: str, **filters: Any) -> list[dict[str, Any]]:
        """List objects using core service."""
        try:
            # OGM-aware listing when enabled and model is available
            if getattr(self, "_use_ogm", False):
                from ontologia.ogm import get_model_class

                model = get_model_class(object_type)
                if model is not None and hasattr(model, "_db"):
                    # Execute search via InstancesService to avoid model instantiation issues
                    limit = int(filters.pop("limit", 100)) if "limit" in filters else 100
                    offset = int(filters.pop("offset", 0)) if "offset" in filters else 0
                    db = model._db
                    service, instance = db.get_default_scope()
                    from ontologia.application.instances_service import (
                        ObjectSearchRequest,
                        SearchFilter,
                    )

                    req = ObjectSearchRequest(
                        filters=[
                            SearchFilter(
                                field=k,
                                operator=("in" if isinstance(v, (list, tuple, set)) else "eq"),
                                value=(list(v) if isinstance(v, (list, tuple, set)) else v),
                            )
                            for k, v in list(filters.items())
                        ],
                        order_by=[],
                        limit=limit,
                        offset=offset,
                    )
                    with db.get_session() as session:
                        from ontologia.ogm.connection import CoreServiceProvider

                        provider = CoreServiceProvider(session)
                        resp = provider.instances_service().search_objects(
                            service, instance, object_type, req
                        )
                        pk_field = getattr(model, "__primary_key__", "pk")
                        out = []
                        for obj in resp.objects:
                            row = dict(obj.properties or {})
                            row[pk_field] = obj.pk_value
                            out.append(row)
                        return out

            services = self._get_services()
            with self.session_factory() as session:
                limit = int(filters.pop("limit", 100)) if "limit" in filters else 100
                offset = int(filters.pop("offset", 0)) if "offset" in filters else 0
                resp = services["instances"].list_objects(
                    "default", "default", object_type, limit=limit, offset=offset
                )
                return [obj.model_dump() for obj in resp.objects]
        except Exception as e:
            logger.error(f"Error listing objects {object_type}: {e}")
            raise

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create object using core service."""
        try:
            if self._use_ogm:
                from ontologia.ogm import get_model_class

                model = get_model_class(object_type)
                if model is not None:
                    pk_field = getattr(model, "__primary_key__", "pk")
                    if pk_field not in data:
                        raise ValueError(f"Missing primary key field '{pk_field}' in data")
                    obj = model(**data)
                    obj.save()
                    return obj.model_dump()
            services = self._get_services()
            with self.session_factory() as session:
                # Convert dict to appropriate request object
                from ontologia.application.instances_service import ObjectUpsertRequest

                # Generate a pk if not provided in data
                pk_value = data.get("pk", "auto-generated")
                request = ObjectUpsertRequest(pk_value=pk_value, properties=data)
                instance = services["instances"].upsert_object(
                    "default", "default", object_type, request.pk_value, request.properties
                )
                return instance.model_dump()
        except Exception as e:
            logger.error(f"Error creating object {object_type}: {e}")
            raise

    async def update_object(
        self, object_type: str, pk: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update object using core service."""
        try:
            if self._use_ogm:
                from ontologia.ogm import get_model_class

                model = get_model_class(object_type)
                if model is not None:
                    try:
                        obj = model.get(pk)
                        for k, v in data.items():
                            setattr(obj, k, v)
                    except Exception:
                        obj = model(**{getattr(model, "__primary_key__", "pk"): pk, **data})
                    obj.save()
                    return obj.model_dump()
            services = self._get_services()
            with self.session_factory() as session:
                from ontologia.application.instances_service import ObjectUpsertRequest

                request = ObjectUpsertRequest(pk_value=pk, properties=data)
                instance = services["instances"].upsert_object(
                    "default", "default", object_type, request.pk_value, request.properties
                )
                return instance.model_dump()
        except Exception as e:
            logger.error(f"Error updating object {object_type}:{pk}: {e}")
            raise

    async def delete_object(self, object_type: str, pk: str) -> bool:
        """Delete object using core service."""
        try:
            if self._use_ogm:
                from ontologia.ogm import get_model_class

                model = get_model_class(object_type)
                if model is not None:
                    try:
                        obj = model.get(pk)
                    except Exception:
                        return False
                    obj.delete()
                    return True
            services = self._get_services()
            with self.session_factory() as session:
                return services["instances"].delete_object("default", "default", object_type, pk)
        except Exception as e:
            logger.error(f"Error deleting object {object_type}:{pk}: {e}")
            raise

    async def list_object_types(self) -> list[dict[str, Any]]:
        """List object types using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                object_types = services["metamodel"].list_object_types()
                return [obj_type.model_dump() for obj_type in object_types]
        except Exception as e:
            logger.error(f"Error listing object types: {e}")
            raise

    async def get_object_type(self, api_name: str) -> dict[str, Any] | None:
        """Get object type using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                obj_type = services["metamodel"].get_object_type_by_api_name(
                    "default", "default", api_name
                )
                return obj_type.model_dump() if obj_type else None
        except Exception as e:
            logger.error(f"Error getting object type {api_name}: {e}")
            raise

    async def create_object_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create object type using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                from ontologia.application.metamodel_service import ObjectTypePutRequest

                request = ObjectTypePutRequest(**data)
                obj_type = services["metamodel"].create_object_type("default", "default", request)
                return obj_type.model_dump()
        except Exception as e:
            logger.error(f"Error creating object type: {e}")
            raise

    async def update_object_type(self, api_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update object type using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                from ontologia.application.metamodel_service import ObjectTypePutRequest

                request = ObjectTypePutRequest(**data)
                obj_type = services["metamodel"].update_object_type(
                    "default", "default", api_name, request
                )
                return obj_type.model_dump()
        except Exception as e:
            logger.error(f"Error updating object type {api_name}: {e}")
            raise

    async def list_link_types(self) -> list[dict[str, Any]]:
        """List link types using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                link_types = services["metamodel"].list_link_types()
                return [link_type.model_dump() for link_type in link_types]
        except Exception as e:
            logger.error(f"Error listing link types: {e}")
            raise

    async def get_link_type(self, api_name: str) -> dict[str, Any] | None:
        """Get link type using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                link_type = services["metamodel"].get_link_type_by_api_name(
                    "default", "default", api_name
                )
                return link_type.model_dump() if link_type else None
        except Exception as e:
            logger.error(f"Error getting link type {api_name}: {e}")
            raise

    async def create_link_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create link type using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                from ontologia.application.metamodel_service import LinkTypePutRequest

                request = LinkTypePutRequest(**data)
                link_type = services["metamodel"].create_link_type("default", "default", request)
                return link_type.model_dump()
        except Exception as e:
            logger.error(f"Error creating link type: {e}")
            raise

    async def get_linked_objects(
        self, object_type: str, pk: str, link_type: str, direction: str = "outgoing"
    ) -> list[dict[str, Any]]:
        """Get linked objects using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                linked_objects = services["linked"].get_linked_objects(
                    object_type, pk, link_type, direction
                )
                return [obj.model_dump() for obj in linked_objects]
        except Exception as e:
            logger.error(f"Error getting linked objects {object_type}:{pk} via {link_type}: {e}")
            raise

    async def create_link(
        self,
        source_type: str,
        source_pk: str,
        link_type: str,
        target_type: str,
        target_pk: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create link using core service."""
        try:
            services = self._get_services()
            with self.session_factory() as session:
                from ontologia.application.linked_objects_service import LinkPutRequest

                request = LinkPutRequest(
                    source_object_type=source_type,
                    source_pk=source_pk,
                    target_object_type=target_type,
                    target_pk=target_pk,
                    properties=properties or {},
                )
                link = services["linked"].create_link(link_type, request)
                return link.model_dump()
        except Exception as e:
            logger.error(
                f"Error creating link {source_type}:{source_pk} -> {target_type}:{target_pk} via {link_type}: {e}"
            )
            raise

    async def close(self) -> None:
        """Close database engine."""
        if hasattr(self.engine, "dispose"):
            self.engine.dispose()


# Factory function for session creation
def create_session(
    *,
    host: str | None = None,
    token: str | None = None,
    connection_string: str | None = None,
    timeout: float = 30.0,
    ontology: str = "default",
    use_ogm: bool = False,
    ogm_module: str | None = None,
) -> ClientSession:
    """
    Factory function to create appropriate session based on parameters.

    Args:
        host: Remote API host URL
        token: Authentication token for remote access
        connection_string: Database connection string for local access
        timeout: Request timeout for remote sessions
        ontology: Ontology name for remote sessions

    Returns:
        ClientSession instance (RemoteSession or LocalSession)

    Raises:
        ValueError: If neither host nor connection_string provided
        ValueError: If both host and connection_string provided
    """
    if host and connection_string:
        raise ValueError("Cannot specify both 'host' and 'connection_string'")

    if not host and not connection_string:
        raise ValueError("Must specify either 'host' or 'connection_string'")

    if host:
        return RemoteSession(
            host=host, token=token, timeout=timeout, ontology=ontology, use_ogm=use_ogm
        )
    else:
        return LocalSession(
            connection_string=connection_string or "", use_ogm=use_ogm, ogm_module=ogm_module
        )


def create_remote_client(
    host: str,
    token: str | None = None,
    timeout: float = 30.0,
    ontology: str = "default",
    *,
    use_ogm: bool = False,
) -> RemoteSession:
    """
    Create a remote client session.

    Args:
        host: Remote API host URL
        token: Authentication token for remote access
        timeout: Request timeout for remote sessions
        ontology: Ontology name for remote sessions

    Returns:
        RemoteSession instance
    """
    return RemoteSession(
        host=host, token=token, timeout=timeout, ontology=ontology, use_ogm=use_ogm
    )


def create_local_client(
    connection_string: str,
    ontology: str = "default",
    *,
    use_ogm: bool = False,
    ogm_module: str | None = None,
) -> LocalSession:
    """
    Create a local client session.

    Args:
        connection_string: Database connection string for local access
        ontology: Ontology name

    Returns:
        LocalSession instance
    """
    return LocalSession(connection_string=connection_string, use_ogm=use_ogm, ogm_module=ogm_module)
