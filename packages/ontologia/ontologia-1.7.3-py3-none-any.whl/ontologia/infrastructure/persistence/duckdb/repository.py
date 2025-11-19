"""
duckdb/repository.py
--------------------
DuckDB connection manager and repository base class.

Provides centralized connection management for DuckDB analytics operations.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

try:
    import duckdb

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    duckdb: Any = None

from ontologia.application.simplified_settings import get_settings

logger = logging.getLogger(__name__)


@contextmanager
def get_duckdb_connection(
    *,
    read_only: bool = True,
) -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """
    Get a DuckDB connection for analytics operations.

    Args:
        read_only: Whether to open connection in read-only mode

    Yields:
        DuckDB connection instance

    Raises:
        ImportError: If DuckDB is not installed
        ValueError: If DuckDB path is not configured
    """
    if not DUCKDB_AVAILABLE:
        raise ImportError("DuckDB package not installed; install with: pip install duckdb")

    settings = get_settings()
    duckdb_path = settings.duckdb_path

    if not duckdb_path:
        raise ValueError("DuckDB path must be configured")

    conn = None
    try:
        # Open connection
        conn = duckdb.connect(duckdb_path, read_only=read_only)

        # Load essential extensions
        conn.execute("LOAD json")
        conn.execute("LOAD httpfs")

        logger.debug(f"DuckDB connection opened: {duckdb_path} (read_only={read_only})")
        yield conn

    except Exception as e:
        logger.error(f"Failed to open DuckDB connection: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            logger.debug("DuckDB connection closed")


class DuckDBRepository:
    """
    Base repository class for DuckDB analytics operations.

    Provides common functionality for executing queries and managing connections.
    """

    def __init__(self, duckdb_path: str | None = None):
        """
        Initialize DuckDB repository.

        Args:
            duckdb_path: Path to DuckDB database file
        """
        self.logger = logging.getLogger(__name__)

        if duckdb_path:
            self.duckdb_path = duckdb_path
        else:
            settings = get_settings()
            self.duckdb_path = settings.duckdb_path

    def is_available(self) -> bool:
        """
        Check if DuckDB is available and configured.

        Returns:
            True if DuckDB is available
        """
        return DUCKDB_AVAILABLE and bool(self.duckdb_path)

    @contextmanager
    def get_connection(
        self, *, read_only: bool = True
    ) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """
        Get a DuckDB connection for this repository.

        Args:
            read_only: Whether to open connection in read-only mode

        Yields:
            DuckDB connection instance
        """
        if not self.is_available():
            raise RuntimeError("DuckDB is not available or not configured")

        conn = None
        try:
            conn = duckdb.connect(self.duckdb_path, read_only=read_only)
            yield conn
        finally:
            if conn is not None:
                conn.close()

    def execute_query(
        self, query: str, params: dict[str, Any] | list[Any] | tuple[Any, ...] | None = None, *, read_only: bool = True
    ) -> list[dict[str, Any]]:
        """
        Execute a query and return results as list of dictionaries.

        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            read_only: Whether to use read-only connection

        Returns:
            Query results as list of dictionaries
        """
        if not self.is_available():
            raise RuntimeError("DuckDB is not available or not configured")

        with self.get_connection(read_only=read_only) as conn:
            if params:
                # Normalize params for DuckDB: prefer flat list/tuple.
                if isinstance(params, dict):
                    # Special-case: a single key 'values' containing a flat sequence to
                    # match repeated '?' placeholders (used by bulk inserts in tests).
                    if set(params.keys()) == {"values"} and isinstance(
                        params["values"], (list, tuple)
                    ):
                        result = conn.execute(query, list(params["values"]))
                    else:
                        # Fallback: flatten values in insertion order
                        flat: list[Any] = []
                        for v in params.values():
                            if isinstance(v, (list, tuple)):
                                flat.extend(v)
                            else:
                                flat.append(v)
                        result = conn.execute(query, flat)
                else:
                    result = conn.execute(query, params)
            else:
                result = conn.execute(query)

            # For DDL/DML statements, return empty list
            if not result.description:
                return []

            # Convert result to list of lists
            rows = result.fetchall()
            return [list(row) for row in rows]

    def execute_scalar(
        self, query: str, params: dict[str, Any] | None = None, *, read_only: bool = True
    ) -> Any:
        """
        Execute a query that returns a single scalar value.

        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            read_only: Whether to use read-only connection

        Returns:
            Scalar result value
        """
        rows = self.execute_query(query, params, read_only=read_only)

        if not rows:
            return None

        first_row = rows[0]
        if isinstance(first_row, list | tuple):
            return first_row[0] if first_row else None
        return first_row


def create_duckdb_repository(duckdb_path: str | None = None) -> DuckDBRepository:
    """
    Factory function to create DuckDB repository.

    Args:
        duckdb_path: Path to DuckDB database file

    Returns:
        DuckDB repository instance
    """
    return DuckDBRepository(duckdb_path=duckdb_path)


__all__ = ["get_duckdb_connection", "DuckDBRepository", "create_duckdb_repository"]
