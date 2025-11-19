"""Migration system for ontologia-core schema evolution.

Provides Alembic-inspired migration management with safety guarantees
and automatic change detection.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlmodel import text

from .connection import Ontology
from .migration_errors import DangerousMigrationError
from .schema import SchemaPlan, _plan_schema


class MigrationRecord:
    """Represents a migration record in the database."""

    def __init__(self, id: str, timestamp: datetime, description: str, applied_at: datetime):
        self.id = id
        self.timestamp = timestamp
        self.description = description
        self.applied_at = applied_at


class DestructiveChange:
    """Represents a destructive schema change."""

    def __init__(self, change_type: str, target: str, description: str):
        self.change_type = change_type  # "property_removed", "type_changed", etc.
        self.target = target  # "User.age", "Post.status", etc.
        self.description = description


class MigrationPlan:
    """Plan for applying migrations with safety information."""

    def __init__(self, migrations: list[Path], destructive_changes: list[DestructiveChange]):
        self.migrations = migrations
        self.destructive_changes = destructive_changes

    def is_destructive(self) -> bool:
        """Check if any migrations contain destructive changes."""
        return len(self.destructive_changes) > 0

    def summary(self) -> str:
        """Get a human-readable summary of the plan."""
        lines = []
        lines.append(f"Found {len(self.migrations)} pending migration(s)")
        if self.is_destructive():
            lines.append(f"⚠️  Contains {len(self.destructive_changes)} destructive change(s)")
        else:
            lines.append("✅ All changes are non-destructive")
        return "\n".join(lines)

    def destructive_summary(self) -> str:
        """Get detailed summary of destructive changes."""
        if not self.is_destructive():
            return "No destructive changes detected."

        lines = ["Destructive changes:"]
        for change in self.destructive_changes:
            lines.append(f"  - {change.change_type}: {change.target}")
            lines.append(f"    {change.description}")
        return "\n".join(lines)


class MigrationsManager:
    """Manages schema migrations for ontologia-core."""

    def __init__(self, ontology: Ontology, migrations_dir: str = "migrations/versions"):
        self.ontology = ontology
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize tracking table if needed
        self._ensure_tracking_table()

    def _ensure_tracking_table(self):
        """Create the migration tracking table if it doesn't exist."""
        with self.ontology.get_session() as session:
            # Check if table exists
            result = session.exec(
                text(
                    """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='ontologia_migration'
            """
                )
            ).all()

            if not result:
                session.exec(
                    text(
                        """
                    CREATE TABLE ontologia_migration (
                        id VARCHAR(255) PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )
                session.commit()

    def get_applied_migrations(self) -> list[MigrationRecord]:
        """Get list of applied migrations from database."""
        with self.ontology.get_session() as session:
            result = session.exec(
                text(
                    """
                SELECT id, timestamp, description, applied_at
                FROM ontologia_migration
                ORDER BY timestamp
            """
                )
            ).all()

            return [
                MigrationRecord(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    description=row[2] or "",
                    applied_at=datetime.fromisoformat(row[3]),
                )
                for row in result
            ]

    def get_pending_migrations(self) -> list[Path]:
        """Get list of pending migration files."""
        applied_ids = {m.id for m in self.get_applied_migrations()}
        pending = []

        # Get all migration files sorted by timestamp
        for migration_file in sorted(self.migrations_dir.glob("*.py")):
            migration_id = migration_file.stem
            if migration_id not in applied_ids:
                pending.append(migration_file)

        return pending

    def _detect_destructive_changes(self, plan: SchemaPlan) -> list[DestructiveChange]:
        """Detect destructive changes in a schema plan."""
        changes = []

        # Check for property removals in updates
        for _, _, existing in plan.object_types_to_update:
            # This is simplified - in real implementation we'd compare
            # old and new property definitions
            changes.append(
                DestructiveChange(
                    change_type="property_removal",
                    target=f"{existing.api_name}.*",
                    description="Properties may be removed or modified",
                )
            )

        # Check for link type changes
        for _, _, existing in plan.link_types_to_update:
            changes.append(
                DestructiveChange(
                    change_type="link_modified",
                    target=existing.api_name,
                    description="Link type definition is being modified",
                )
            )

        return changes

    def make_migration(self, message: str, auto_apply: bool = False) -> Path:
        """Generate a new migration file for detected schema changes."""
        # Generate schema plan
        plan = _plan_schema()

        # Check if there are any changes
        if not plan.summary() or plan.summary() == "No changes":
            raise ValueError("No schema changes detected")

        # Generate migration ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_message = re.sub(r"[^a-zA-Z0-9_]", "_", message.lower())
        migration_id = f"{timestamp}_{safe_message}"

        # Detect destructive changes
        destructive_changes = self._detect_destructive_changes(plan)

        # Generate migration file content
        content = self._generate_migration_file(migration_id, message, plan, destructive_changes)

        # Write migration file
        migration_file = self.migrations_dir / f"{migration_id}.py"
        migration_file.write_text(content)

        if auto_apply:
            self.migrate(allow_destructive=len(destructive_changes) > 0)

        return migration_file

    def _generate_migration_file(
        self,
        migration_id: str,
        message: str,
        plan: SchemaPlan,
        destructive_changes: list[DestructiveChange],
    ) -> str:
        """Generate the content of a migration file."""
        lines = [
            f'"""{message}."""',
            "",
            "from __future__ import annotations",
            "from datetime import datetime",
            "from typing import TYPE_CHECKING",
            "",
            "if TYPE_CHECKING:",
            "    from ontologia.domain.metamodels.aggregates.object_type import ObjectTypeAggregate",
            "    from ontologia.domain.metamodels.types.object_type import ObjectType",
            "",
            "# Migration metadata",
            f'id = "{migration_id}"',
            f"timestamp = datetime({datetime.now().year}, {datetime.now().month}, {datetime.now().day}, {datetime.now().hour}, {datetime.now().minute}, {datetime.now().second})",
            "dependencies = []  # List of migration IDs this depends on",
            f'description = "{message}"',
            "",
            "# DDL changes (auto-generated, read-only)",
            "ddl_changes = {",
        ]

        # Add object types to create
        if plan.object_types_to_create:
            lines.append('    "object_types_to_create": [')
            for model_cls, agg in plan.object_types_to_create:
                lines.append(f"        # {model_cls.__name__}: {agg.object_type.api_name}")
                lines.append("        # TODO: Add ObjectTypeAggregate definition")
            lines.append("    ],")

        # Add object types to update
        if plan.object_types_to_update:
            lines.append('    "object_types_to_update": [')
            for model_cls, agg, existing in plan.object_types_to_update:
                lines.append(f"        # {model_cls.__name__}: {agg.object_type.api_name}")
                lines.append("        # TODO: Add (model_cls, aggregate, existing) tuple")
            lines.append("    ],")

        # Add link types
        if plan.link_types_to_create or plan.link_types_to_update:
            lines.append('    "link_types_to_create": [')
            for link_api_name, lt in plan.link_types_to_create:
                lines.append(f"        # {link_api_name}: {lt.api_name}")
                lines.append("        # TODO: Add LinkType definition")
            lines.append("    ],")
            lines.append('    "link_types_to_update": [')
            for link_api_name, lt, existing in plan.link_types_to_update:
                lines.append(f"        # {link_api_name}: {lt.api_name}")
                lines.append("        # TODO: Add (link_api_name, new_link, existing) tuple")
            lines.append("    ],")

        lines.extend(
            [
                "}",
                "",
                "def forwards(session, context):",
                '    """Apply data migration logic (custom DML).',
                "    ",
                "    Args:",
                "        session: Database session for executing SQL",
                "        context: Migration context with metadata and helpers",
                '    """',
                "    # Add your custom data migration logic here",
                '    # Example: session.execute(text("UPDATE table SET column = value"))',
                "    pass",
                "",
                "def backwards(session, context):",
                '    """Rollback data migration logic (optional).',
                "    ",
                "    Only implemented for reversible migrations.",
                '    """',
                "    # Add rollback logic here if migration is reversible",
                "    pass",
            ]
        )

        return "\n".join(lines)

    def showplan(self) -> MigrationPlan:
        """Show what migrations would be applied without executing them."""
        pending = self.get_pending_migrations()

        # For now, assume all pending migrations might be destructive
        # In real implementation, we'd analyze each migration file
        destructive_changes = []
        for migration_file in pending:
            destructive_changes.append(
                DestructiveChange(
                    change_type="unknown",
                    target=migration_file.stem,
                    description="Migration may contain destructive changes",
                )
            )

        return MigrationPlan(pending, destructive_changes)

    def migrate(
        self, target: str = "head", allow_destructive: bool = False, dry_run: bool = False
    ) -> dict[str, Any]:
        """Apply pending migrations."""
        plan = self.showplan()

        if plan.is_destructive() and not allow_destructive:
            raise DangerousMigrationError(
                f"Destructive changes detected. Use allow_destructive=True to proceed.\n"
                f"{plan.destructive_summary()}"
            )

        if dry_run:
            return {
                "dry_run": True,
                "plan": plan.summary(),
                "migrations": [m.name for m in plan.migrations],
            }

        results = {}
        with self.ontology.get_session() as session:
            for migration_file in plan.migrations:
                try:
                    # Import and execute migration
                    migration_id = migration_file.stem

                    # Load migration module
                    spec = __import__(
                        f"migrations.versions.{migration_id}",
                        fromlist=["forwards", "backwards", "description"],
                    )

                    # Execute forwards migration
                    if hasattr(spec, "forwards"):
                        forwards_func = getattr(spec, "forwards", None)
                        if forwards_func and callable(forwards_func):
                            forwards_func(session, {"migration_id": migration_id})

                    # Record migration
                    session.exec(
                        text(
                            """
                        INSERT INTO ontologia_migration (id, timestamp, description, applied_at)
                        VALUES (:id, :timestamp, :description, :applied_at)
                    """
                        ),
                        {
                            "id": migration_id,
                            "timestamp": datetime.now().isoformat(),
                            "description": getattr(spec, "description", ""),
                            "applied_at": datetime.now().isoformat(),
                        },
                    )

                    results[migration_id] = "applied"

                except Exception as e:
                    results[migration_file.stem] = f"failed: {str(e)}"
                    raise

            session.commit()

        return {"applied": len([r for r in results.values() if r == "applied"]), "results": results}
