#!/usr/bin/env python3
"""
🦆 DuckDB Bootstrap Script for Ontologia

Bootstrap minimal raw DuckDB tables used by the DBT project.
Creates the necessary schema and sample data for analytics workflows.

Usage:
    python scripts/prepare_duckdb_raw.py [options]

Examples:
    python scripts/prepare_duckdb_raw.py
    python scripts/prepare_duckdb_raw.py --db-path ./custom.duckdb

Tables Created:
    - raw_data.employees_tbl(emp_id TEXT, name TEXT)
    - raw_data.works_for_tbl(emp_id TEXT, company_id TEXT)

Environment Variables:
    DUCKDB_PATH - Path to DuckDB database (default: ./data/local.duckdb)
    ONTOLOGIA_CONFIG_ROOT - Configuration root directory
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.utils import BaseCLI, ExitCode, optional_import

# Lazy import DuckDB
duckdb = optional_import("duckdb", install_group="analytics")


class DuckDBBootstrapCLI(BaseCLI):
    """CLI for DuckDB bootstrap operations."""

    def __init__(self) -> None:
        super().__init__(
            name="prepare_duckdb_raw",
            description="Bootstrap DuckDB tables for DBT projects",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--db-path",
            type=Path,
            help="Path to DuckDB database (overrides DUCKDB_PATH)",
        )
        parser.add_argument(
            "--schema",
            default="raw_data",
            help="Schema name for tables (default: raw_data)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show SQL statements without executing them",
        )
        parser.add_argument(
            "--force-recreate",
            action="store_true",
            help="Drop and recreate tables if they exist",
        )

    def run(self, args) -> ExitCode:
        try:
            # Get DuckDB module
            duckdb_module = duckdb()
        except Exception as e:
            self.console.print(f"❌ Failed to import DuckDB: {e}")
            return ExitCode.MISSING_DEPENDENCIES

        # Determine database path
        db_path = self._get_db_path(args)

        if args.dry_run:
            return self._dry_run(args)

        return self._bootstrap_database(duckdb_module, db_path, args)

    def _get_db_path(self, args) -> Path:
        """Get the database path from arguments or environment."""
        if args.db_path:
            return args.db_path

        env_path = os.getenv("DUCKDB_PATH")
        if env_path:
            return Path(env_path)

        # Use configuration
        ontologia_config = self.config.load_ontologia_config()
        return Path(ontologia_config.data.duckdb_path)

    def _dry_run(self, args) -> ExitCode:
        """Show what would be executed without running it."""
        self.console.print("🔍 Dry run mode - showing SQL statements:")

        sql_statements = self._get_sql_statements(args)

        for i, statement in enumerate(sql_statements, 1):
            self.console.print(f"\n{i}. {statement}")

        return ExitCode.SUCCESS

    def _get_sql_statements(self, args) -> list[str]:
        """Get the SQL statements that would be executed."""
        schema = args.schema

        statements = [
            f"CREATE SCHEMA IF NOT EXISTS {schema};",
            f"""
            CREATE TABLE IF NOT EXISTS {schema}.employees_tbl (
              emp_id TEXT,
              name TEXT
            );
            """.strip(),
            f"""
            CREATE TABLE IF NOT EXISTS {schema}.works_for_tbl (
              emp_id TEXT,
              company_id TEXT
            );
            """.strip(),
        ]

        if args.force_recreate:
            statements.insert(1, f"DROP TABLE IF EXISTS {schema}.employees_tbl;")
            statements.insert(2, f"DROP TABLE IF EXISTS {schema}.works_for_tbl;")

        return statements

    def _bootstrap_database(self, duckdb_module, db_path: Path, args) -> ExitCode:
        """Actually bootstrap the database."""
        self.logger.info(f"Bootstrapping DuckDB database at {db_path}")

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            con = duckdb_module.connect(str(db_path))

            try:
                # Execute schema and table creation
                statements = self._get_sql_statements(args)

                for statement in statements:
                    self.logger.debug(f"Executing: {statement}")
                    con.execute(statement)

                # Seed data if tables are empty
                self._seed_data_if_empty(con, args)

                self.console.print(f"✅ DuckDB bootstrap completed at {db_path}")
                self.logger.info("Database bootstrap completed successfully")

                return ExitCode.SUCCESS

            finally:
                con.close()

        except Exception as e:
            self.console.print(f"❌ Failed to bootstrap database: {e}")
            self.logger.exception("Database bootstrap failed")
            return ExitCode.GENERAL_ERROR

    def _seed_data_if_empty(self, con, args) -> None:
        """Seed tables with sample data if they're empty."""
        schema = args.schema

        # Check and seed employees table
        emp_result = con.execute(f"SELECT COUNT(*) FROM {schema}.employees_tbl").fetchone()
        emp_count = emp_result[0] if emp_result else 0

        if emp_count == 0:
            self.logger.info("Seeding employees table")
            con.execute(
                f"INSERT INTO {schema}.employees_tbl (emp_id, name) VALUES (?, ?), (?, ?)",
                ["e1", "Alice", "e2", "Bob"],
            )

        # Check and seed works_for table
        wf_result = con.execute(f"SELECT COUNT(*) FROM {schema}.works_for_tbl").fetchone()
        wf_count = wf_result[0] if wf_result else 0

        if wf_count == 0:
            self.logger.info("Seeding works_for table")
            con.execute(
                f"INSERT INTO {schema}.works_for_tbl (emp_id, company_id) VALUES (?, ?), (?, ?)",
                ["e1", "c1", "e2", "c1"],
            )


def main() -> ExitCode:
    """Main entry point for the DuckDB bootstrap script."""
    cli = DuckDBBootstrapCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
