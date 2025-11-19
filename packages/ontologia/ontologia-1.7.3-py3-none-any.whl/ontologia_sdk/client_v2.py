"""
Unified OntologyClient with dual-mode operation (remote/local).

Provides a high-level interface that automatically detects and uses
the appropriate session implementation based on configuration.
"""

from __future__ import annotations

import logging
from typing import Any

from ontologia_sdk.ogm_query import OGMQuery
from ontologia_sdk.session import LocalSession, RemoteSession, create_session

logger = logging.getLogger(__name__)


class OntologyClient:
    """
    Unified client with automatic mode detection and fluent interface.

    Supports both remote (HTTP) and local (direct core) modes of operation.
    The mode is automatically determined based on initialization parameters.
    """

    def __init__(
        self,
        *,
        host: str | None = None,
        token: str | None = None,
        connection_string: str | None = None,
        ontology: str = "default",
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        use_ogm: bool = False,
        ogm_module: str | None = None,
    ):
        """
        Initialize the unified client.

        Args:
            host: Remote API host URL (enables remote mode)
            token: Authentication token for remote access
            connection_string: Database connection string (enables local mode)
            ontology: Ontology name for remote sessions
            timeout: Request timeout for remote sessions
            headers: Additional HTTP headers for remote sessions

        Raises:
            ValueError: If neither host nor connection_string provided
            ValueError: If both host and connection_string provided
        """
        self.ontology = ontology
        self.timeout = timeout
        self._custom_headers = headers or {}

        # Create session using factory
        self._session = create_session(
            host=host,
            token=token,
            connection_string=connection_string,
            timeout=timeout,
            ontology=ontology,
            use_ogm=use_ogm,
            ogm_module=ogm_module,
        )

        # Determine mode
        if isinstance(self._session, RemoteSession):
            self._mode = "remote"
            logger.info(f"OntologyClient initialized in REMOTE mode (host: {host})")
        elif isinstance(self._session, LocalSession):
            self._mode = "local"
            logger.info("OntologyClient initialized in LOCAL mode")
        else:
            # Check using duck typing for mocked instances in tests
            if hasattr(self._session, "_client") and hasattr(self._session, "_headers"):
                self._mode = "remote"
                logger.info(f"OntologyClient initialized in REMOTE mode (host: {host})")
            elif hasattr(self._session, "connection_string") and hasattr(
                self._session, "_services"
            ):
                self._mode = "local"
                logger.info("OntologyClient initialized in LOCAL mode")
            else:
                self._mode = "unknown"
                logger.warning("OntologyClient initialized in UNKNOWN mode")

        # Initialize managers (will be implemented in next phases)
        self._initialize_managers()

    def _initialize_managers(self):
        """Initialize high-level managers for different operations."""
        # These will be implemented in subsequent phases
        # For now, provide direct access to session methods
        pass

    # --- OGM Query Interface ---
    def ogm_query(self, object_type: str) -> OGMQuery:
        """Return an OGMQuery builder bound to this client's session."""
        return OGMQuery(self._session, object_type)

    @property
    def mode(self) -> str:
        """Get the current operation mode."""
        return self._mode

    @property
    def is_remote(self) -> bool:
        """Check if operating in remote mode."""
        return self._mode == "remote"

    @property
    def is_local(self) -> bool:
        """Check if operating in local mode."""
        return self._mode == "local"

    # --- Direct session methods (temporary, will be replaced by managers) ---

    async def get_object(self, object_type: str, pk: str) -> dict[str, Any] | None:
        """Retrieve a single object by type and primary key."""
        return await self._session.get_object(object_type, pk)

    async def list_objects(self, object_type: str, **filters: Any) -> list[dict[str, Any]]:
        """List objects of a type with optional filters."""
        return await self._session.list_objects(object_type, **filters)

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object instance."""
        return await self._session.create_object(object_type, data)

    async def update_object(
        self, object_type: str, pk: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing object."""
        return await self._session.update_object(object_type, pk, data)

    async def delete_object(self, object_type: str, pk: str) -> bool:
        """Delete an object by type and primary key."""
        return await self._session.delete_object(object_type, pk)

    async def list_object_types(self) -> list[dict[str, Any]]:
        """List all available object types."""
        return await self._session.list_object_types()

    async def get_object_type(self, api_name: str) -> dict[str, Any] | None:
        """Get object type definition by API name."""
        return await self._session.get_object_type(api_name)

    async def create_object_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new object type."""
        return await self._session.create_object_type(data)

    async def update_object_type(self, api_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing object type."""
        return await self._session.update_object_type(api_name, data)

    async def list_link_types(self) -> list[dict[str, Any]]:
        """List all available link types."""
        return await self._session.list_link_types()

    async def get_link_type(self, api_name: str) -> dict[str, Any] | None:
        """Get link type definition by API name."""
        return await self._session.get_link_type(api_name)

    async def create_link_type(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new link type."""
        return await self._session.create_link_type(data)

    async def get_linked_objects(
        self, object_type: str, pk: str, link_type: str, direction: str = "outgoing"
    ) -> list[dict[str, Any]]:
        """Get objects linked via a specific link type."""
        return await self._session.get_linked_objects(object_type, pk, link_type, direction)

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
        return await self._session.create_link(
            source_type, source_pk, link_type, target_type, target_pk, properties
        )

    # --- Convenience methods ---

    async def object_exists(self, object_type: str, pk: str) -> bool:
        """Check if an object exists."""
        obj = await self.get_object(object_type, pk)
        return obj is not None

    async def count_objects(self, object_type: str, **filters: Any) -> int:
        """Count objects of a type with optional filters."""
        objects = await self.list_objects(object_type, **filters)
        return len(objects)

    async def get_or_create_object(
        self, object_type: str, pk: str, data: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        """
        Get object if exists, otherwise create it.

        Returns:
            Tuple of (object_data, was_created)
        """
        existing = await self.get_object(object_type, pk)
        if existing is not None:
            return existing, False

        created = await self.create_object(object_type, data)
        return created, True

    # --- Context manager support ---

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close session resources."""
        await self._session.close()

    # --- Synchronous convenience methods (for backward compatibility) ---

    def get_object_sync(self, object_type: str, pk: str) -> dict[str, Any] | None:
        """Synchronous version of get_object."""
        import asyncio

        return asyncio.run(self.get_object(object_type, pk))

    def list_objects_sync(self, object_type: str, **filters: Any) -> list[dict[str, Any]]:
        """Synchronous version of list_objects."""
        import asyncio

        return asyncio.run(self.list_objects(object_type, **filters))

    def create_object_sync(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Synchronous version of create_object."""
        import asyncio

        return asyncio.run(self.create_object(object_type, data))

    def update_object_sync(self, object_type: str, pk: str, data: dict[str, Any]) -> dict[str, Any]:
        """Synchronous version of update_object."""
        import asyncio

        return asyncio.run(self.update_object(object_type, pk, data))

    def delete_object_sync(self, object_type: str, pk: str) -> bool:
        """Synchronous version of delete_object."""
        import asyncio

        return asyncio.run(self.delete_object(object_type, pk))

    # --- String representation ---

    def __repr__(self) -> str:
        """String representation of the client."""
        mode_info = f"mode={self._mode}"
        if self.is_remote:
            mode_info += f", ontology={self.ontology}"
        return f"OntologyClient({mode_info})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.is_remote:
            return f"OntologyClient (Remote: {self.ontology})"
        elif self.is_local:
            return "OntologyClient (Local)"
        else:
            return "OntologyClient (Unknown mode)"


# Factory functions for convenience


def create_remote_client(
    host: str,
    *,
    token: str | None = None,
    ontology: str = "default",
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
) -> OntologyClient:
    """
    Create a client configured for remote operation.

    Args:
        host: Remote API host URL
        token: Authentication token
        ontology: Ontology name
        timeout: Request timeout
        headers: Additional HTTP headers

    Returns:
        OntologyClient configured for remote access
    """
    return OntologyClient(
        host=host, token=token, ontology=ontology, timeout=timeout, headers=headers
    )


def create_local_client(
    connection_string: str,
    *,
    ontology: str = "default",
) -> OntologyClient:
    """
    Create a client configured for local operation.

    Args:
        connection_string: Database connection string
        ontology: Ontology name (for consistency with remote client)

    Returns:
        OntologyClient configured for local access
    """
    return OntologyClient(connection_string=connection_string, ontology=ontology)
