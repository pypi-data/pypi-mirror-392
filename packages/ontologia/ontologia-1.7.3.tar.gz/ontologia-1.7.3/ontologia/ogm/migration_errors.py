"""Exception classes for migration system."""

from __future__ import annotations


class DangerousMigrationError(Exception):
    """Raised when attempting destructive changes without explicit approval."""

    pass


class MigrationDependencyError(Exception):
    """Raised when migration dependencies cannot be resolved."""

    pass


class MigrationExecutionError(Exception):
    """Raised when migration execution fails."""

    pass
