#!/usr/bin/env python3
"""
🔄 Ontology Synchronization Script for Ontologia

Executes ontology synchronization between different data stores.
Handles metamodel data synchronization across PostgreSQL, KùzuDB, and DuckDB.

Usage:
    python scripts/main_sync.py [options]

Examples:
    python scripts/main_sync.py
    python scripts/main_sync.py --duckdb-path ./analytics.duckdb
    python scripts/main_sync.py --dry-run

Environment Variables:
    KUZU_DB_PATH - Path to KùzuDB database
    DUCKDB_PATH - Path to DuckDB database
    ONTOLOGIA_CONFIG_ROOT - Configuration root directory

Features:
    - Multi-database synchronization
    - Graceful dependency handling
    - Transaction safety
    - Progress logging
    - Dry run mode
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.utils import BaseCLI, ExitCode, ScriptConfig, optional_import

# Lazy imports for optional dependencies
kuzu = optional_import("kuzu", install_group="full")
duckdb = optional_import("duckdb", install_group="analytics")

# Core imports
from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction  # noqa: F401
from ontologia_api.core.database import engine
from sqlmodel import Session, SQLModel

from ontologia.application.sync_service import OntologySyncService
from ontologia.domain.metamodels.instances.object_type_data_source import (  # noqa: F401
    ObjectTypeDataSource,
)
from ontologia.domain.metamodels.types.link_type import LinkType  # noqa: F401
from ontologia.domain.metamodels.types.object_type import ObjectType  # noqa: F401


class SyncCLI(BaseCLI):
    """CLI for ontology synchronization operations."""

    def __init__(self) -> None:
        super().__init__(
            name="main_sync",
            description="Execute ontology synchronization between data stores",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--duckdb-path",
            type=Path,
            help="Path to DuckDB database (overrides DUCKDB_PATH)",
        )
        parser.add_argument(
            "--kuzu-path",
            type=Path,
            help="Path to KùzuDB database (overrides KUZU_DB_PATH)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synchronized without executing",
        )
        parser.add_argument(
            "--skip-kuzu",
            action="store_true",
            help="Skip KùzuDB synchronization",
        )
        parser.add_argument(
            "--skip-duckdb",
            action="store_true",
            help="Skip DuckDB synchronization",
        )

    def run(self, args) -> ExitCode:
        if args.dry_run:
            return self._dry_run(args)

        return self._run_sync(args)

    def _dry_run(self, args) -> ExitCode:
        """Show what would be synchronized without executing."""
        self.console.print("🔍 Dry run mode - synchronization plan:")

        duckdb_path = self._get_duckdb_path(args)
        kuzu_path = self._get_kuzu_path(args)

        self.console.print("\n📊 Configuration:")
        self.console.print(f"  DuckDB path: {duckdb_path}")
        self.console.print(f"  KùzuDB path: {kuzu_path}")

        self.console.print("\n🔄 Synchronization steps:")
        self.console.print("  1. Initialize metamodel tables")

        if not args.skip_kuzu:
            if self._check_kuzu_available():
                self.console.print("  2. Connect to KùzuDB")
                self.console.print("  3. Sync graph data")
            else:
                self.console.print("  2. ⚠️  KùzuDB not available - skipping")

        if not args.skip_duckdb:
            if self._check_duckdb_available():
                self.console.print("  4. Connect to DuckDB")
                self.console.print("  5. Sync analytics data")
            else:
                self.console.print("  4. ⚠️  DuckDB not available - skipping")

        self.console.print("  6. Complete synchronization")

        return ExitCode.SUCCESS

    def _run_sync(self, args) -> ExitCode:
        """Execute the actual synchronization."""
        self.logger.info("Starting ontology synchronization")

        try:
            # Get paths
            duckdb_path = self._get_duckdb_path(args)
            kuzu_path = self._get_kuzu_path(args)

            # Run synchronization
            run_sync(
                duckdb_path=str(duckdb_path) if duckdb_path else None,
                kuzu_path=str(kuzu_path) if kuzu_path else None,
                skip_kuzu=args.skip_kuzu,
                skip_duckdb=args.skip_duckdb,
                logger=self.logger,
            )

            self.console.print("✅ Ontology synchronization completed successfully")
            self.logger.info("Synchronization completed successfully")

            return ExitCode.SUCCESS

        except Exception as e:
            self.console.print(f"❌ Synchronization failed: {e}")
            self.logger.exception("Synchronization failed")
            return ExitCode.GENERAL_ERROR

    def _get_duckdb_path(self, args) -> Path | None:
        """Get DuckDB path from arguments, environment, or config."""
        if args.duckdb_path:
            return args.duckdb_path

        env_path = os.getenv("DUCKDB_PATH")
        if env_path:
            return Path(env_path)

        ontologia_config = self.config.load_ontologia_config()
        return Path(ontologia_config.data.duckdb_path)

    def _get_kuzu_path(self, args) -> Path | None:
        """Get KùzuDB path from arguments, environment, or config."""
        if args.kuzu_path:
            return args.kuzu_path

        env_path = os.getenv("KUZU_DB_PATH")
        if env_path:
            return Path(env_path)

        ontologia_config = self.config.load_ontologia_config()
        return Path(ontologia_config.data.kuzu_path)

    def _check_kuzu_available(self) -> bool:
        """Check if KùzuDB is available."""
        try:
            kuzu()
            return True
        except Exception:
            return False

    def _check_duckdb_available(self) -> bool:
        """Check if DuckDB is available."""
        try:
            duckdb()
            return True
        except Exception:
            return False


def run_sync(
    *,
    duckdb_path: str | None = None,
    kuzu_path: str | None = None,
    meta_session: Session | None = None,
    kuzu_conn=None,
    duckdb_conn=None,
    skip_kuzu: bool = False,
    skip_duckdb: bool = False,
    logger=None,
) -> None:
    """
    Execute the synchronization process with dependency injection for testing.

    Args:
        duckdb_path: Path to DuckDB database
        kuzu_path: Path to KùzuDB database
        meta_session: SQLModel session (created if not provided)
        kuzu_conn: KùzuDB connection (created if not provided)
        duckdb_conn: DuckDB connection (created if not provided)
        skip_kuzu: Skip KùzuDB synchronization
        skip_duckdb: Skip DuckDB synchronization
        logger: Logger instance (created if not provided)
    """
    if logger is None:
        from scripts.utils.logging import get_logger

        logger = get_logger("main_sync")

    # Initialize the metamodel tables when running standalone
    try:
        logger.info("Initializing metamodel tables (standalone runner)...")
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.warning(f"Failed to initialize metamodel tables: {e}")

    # Manage session lifecycle
    close_session = False
    if meta_session is None:
        meta_session = Session(engine)
        close_session = True

    try:
        # Create KùzuDB connection if not provided and not skipped
        if kuzu_conn is None and not skip_kuzu:
            try:
                kuzu_module = kuzu()

                if kuzu_path is None:
                    ontologia_config = ScriptConfig().load_ontologia_config()
                    kuzu_path = str(ontologia_config.data.kuzu_path)

                db = kuzu_module.Database(database_path=kuzu_path)
                kuzu_conn = kuzu_module.Connection(db)
                logger.info("KùzuDB connected: %s", kuzu_path)
            except Exception as e:
                logger.warning(
                    "KùzuDB not available; executing only graph-independent steps. Error: %s", e
                )
                kuzu_conn = None

        # Create DuckDB connection if not provided and not skipped
        if duckdb_conn is None and not skip_duckdb and duckdb_path:
            try:
                duckdb_module = duckdb()
                duckdb_conn = duckdb_module.connect(database=duckdb_path)
                logger.info("DuckDB connected: %s", duckdb_path)
            except Exception as e:
                logger.warning(
                    "DuckDB not available; dependent steps will be skipped. Error: %s", e
                )
                duckdb_conn = None

        # Execute synchronization
        svc = OntologySyncService(meta_session, kuzu_conn=kuzu_conn, duckdb_conn=duckdb_conn)
        svc.sync_ontology(duckdb_path=duckdb_path)

    finally:
        if close_session:
            meta_session.close()


def main() -> ExitCode:
    """Main entry point for the synchronization script."""
    cli = SyncCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
