#!/usr/bin/env python3
"""
⏰ Temporal Worker Script for Ontologia

Starts a Temporal worker for action workflows and migrations.
Hosts workflows and activities for asynchronous task execution.

Usage:
    python scripts/run_temporal_worker.py [options]

Examples:
    python scripts/run_temporal_worker.py
    python scripts/run_temporal_worker.py --task-queue custom-queue

Environment Variables:
    TEMPORAL_ADDRESS - Temporal server address (default: 127.0.0.1:7233)
    TEMPORAL_NAMESPACE - Namespace (default: default)
    TEMPORAL_TASK_QUEUE - Task queue name (default: actions)

Workflows Hosted:
    - ActionWorkflow: Execute registered actions
    - MigrationTaskWorkflow: Handle database migrations

Activities Hosted:
    - run_registered_action: Execute action implementations
    - prepare_migration_plan: Prepare migration steps
    - apply_migration_plan: Apply migration changes
"""

from __future__ import annotations

import asyncio

from scripts.utils import BaseCLI, ExitCode, optional_import

# Lazy import Temporal
temporalio = optional_import("temporalio", install_group="full")

# Core imports (will be imported when Temporal is available)
from ontologia_api.actions.temporal.activities import run_registered_action
from ontologia_api.actions.temporal.workflows import ActionWorkflow
from ontologia_api.core.settings import get_settings
from ontologia_api.core.temporal import connect_temporal
from ontologia_api.migrations.temporal.activities import (
    apply_migration_plan,
    prepare_migration_plan,
)
from ontologia_api.migrations.temporal.workflows import MigrationTaskWorkflow


class TemporalWorkerCLI(BaseCLI):
    """CLI for Temporal worker operations."""

    def __init__(self) -> None:
        super().__init__(
            name="run_temporal_worker",
            description="Start Temporal worker for actions and migrations",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--task-queue",
            help="Task queue name (overrides TEMPORAL_TASK_QUEUE)",
        )
        parser.add_argument(
            "--address",
            help="Temporal server address (overrides TEMPORAL_ADDRESS)",
        )
        parser.add_argument(
            "--namespace",
            help="Temporal namespace (overrides TEMPORAL_NAMESPACE)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show worker configuration without starting",
        )

    def run(self, args) -> ExitCode:
        try:
            temporalio_module = temporalio()
        except Exception as e:
            self.console.print(f"❌ Failed to import TemporalIO: {e}")
            return ExitCode.MISSING_DEPENDENCIES

        if args.dry_run:
            return self._dry_run(args)

        return self._run_worker(temporalio_module, args)

    def _dry_run(self, args) -> ExitCode:
        """Show worker configuration without starting."""
        settings = get_settings()

        task_queue = args.task_queue or settings.temporal_task_queue
        address = args.address or settings.temporal_address
        namespace = args.namespace or settings.temporal_namespace

        self.console.print("🔍 Dry run mode - worker configuration:")
        self.console.print("\n⚙️  Configuration:")
        self.console.print(f"  Address: {address}")
        self.console.print(f"  Namespace: {namespace}")
        self.console.print(f"  Task Queue: {task_queue}")

        self.console.print("\n📋 Hosted Workflows:")
        self.console.print("  - ActionWorkflow")
        self.console.print("  - MigrationTaskWorkflow")

        self.console.print("\n🔧 Hosted Activities:")
        self.console.print("  - run_registered_action")
        self.console.print("  - prepare_migration_plan")
        self.console.print("  - apply_migration_plan")

        return ExitCode.SUCCESS

    def _run_worker(self, temporalio_module, args) -> ExitCode:
        """Start the actual Temporal worker."""
        settings = get_settings()

        # Override settings with command line arguments
        task_queue = args.task_queue or settings.temporal_task_queue
        address = args.address or settings.temporal_address
        namespace = args.namespace or settings.temporal_namespace

        self.logger.info(
            f"Starting Temporal worker at {address} (ns={namespace}) on queue '{task_queue}'"
        )

        self.console.print(
            f"🚀 Starting Temporal worker at {address} (ns={namespace}) on queue '{task_queue}'…"
        )

        try:
            # Import Worker class from temporalio
            from temporalio.worker import Worker

            async def run_worker_async():
                client = await connect_temporal(settings)
                async with Worker(
                    client,
                    task_queue=task_queue,
                    workflows=[ActionWorkflow, MigrationTaskWorkflow],
                    activities=[
                        run_registered_action,
                        prepare_migration_plan,
                        apply_migration_plan,
                    ],
                ):
                    self.console.print("✅ Worker running. Press Ctrl+C to stop.")
                    await asyncio.Event().wait()

            asyncio.run(run_worker_async())

        except KeyboardInterrupt:
            self.console.print("\n⚠️  Worker stopped by user")
            return ExitCode.SUCCESS
        except Exception as e:
            self.console.print(f"❌ Worker failed: {e}")
            self.logger.exception("Worker failed")
            return ExitCode.GENERAL_ERROR

        return ExitCode.SUCCESS


def main() -> ExitCode:
    """Main entry point for the Temporal worker script."""
    cli = TemporalWorkerCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
