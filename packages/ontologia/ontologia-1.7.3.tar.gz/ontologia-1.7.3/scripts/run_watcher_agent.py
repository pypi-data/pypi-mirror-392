#!/usr/bin/env python3
"""
👁️ Watcher Agent Script for Ontologia

Real-time event monitoring and autonomous plan generation.
Streams ontology events, analyzes for drift, and creates action plans.

Usage:
    python scripts/run_watcher_agent.py [options]

Examples:
    python scripts/run_watcher_agent.py
    python scripts/run_watcher_agent.py --once
    python scripts/run_watcher_agent.py --interval 60 --duration 30
    python scripts/run_watcher_agent.py --object-type product --entity-id e1

Features:
    - Real-time event streaming
    - Drift detection and analysis
    - Automated plan generation
    - Configurable filtering and intervals
    - Plan persistence and review
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.utils import BaseCLI, ExitCode, optional_import

# Lazy import for agent dependencies
ontologia_agent = optional_import("ontologia_agent", install_group="agents")

from ontologia_cli.main import _load_project_state


def _build_prompt(events: list[dict[str, Any]], window_seconds: float) -> str:
    """Build analysis prompt for the agent."""
    events_json = json.dumps(events, indent=2, default=str)
    return (
        "You are operating in autonomous watch mode. The following real-time events were captured "
        f"during the last {window_seconds:.1f} seconds:\n{events_json}\n\n"
        "Analyze these events. If they reveal an emerging property, new entity relationship, or "
        "other ontology drift, produce an AgentPlan that addresses the issue (YAML updates, dbt "
        "models, migrations, pipeline run). If no action is needed, return an empty plan with the "
        "summary 'Nenhuma ação necessária'."
    )


def _to_record(events: dict[str, Any], plan) -> dict[str, Any]:
    """Convert events and plan to a record."""
    return {
        "generatedAt": datetime.now(UTC).isoformat(),
        "events": events,
        "plan": plan.model_dump(mode="json"),
    }


class WatcherAgentCLI(BaseCLI):
    """CLI for the Watcher agent operations."""

    def __init__(self) -> None:
        super().__init__(
            name="run_watcher_agent",
            description="Real-time event monitoring and autonomous plan generation",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--interval",
            type=float,
            default=300.0,
            help="Sleep interval between scans in seconds (default: 300)",
        )
        parser.add_argument(
            "--duration",
            type=float,
            default=15.0,
            help="Window to capture events in seconds (default: 15)",
        )
        parser.add_argument(
            "--max-events",
            type=int,
            default=50,
            help="Maximum events per window (default: 50)",
        )
        parser.add_argument(
            "--object-type",
            action="append",
            dest="object_type",
            help="Filter events by object type (can be used multiple times)",
        )
        parser.add_argument(
            "--entity-id",
            action="append",
            dest="entity_id",
            help="Filter events by entity id (can be used multiple times)",
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=Path("plans_for_review"),
            help="Directory to store generated plans (default: plans_for_review)",
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Override LLM model name",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run a single iteration and exit",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show configuration and exit without running",
        )
        parser.add_argument(
            "--validate-config",
            action="store_true",
            help="Validate project configuration and exit",
        )

    def run(self, args) -> ExitCode:
        # Validate dependencies first
        try:
            ontologia_agent()
        except Exception as e:
            self.console.print(f"❌ Failed to import agent dependencies: {e}")
            self.console.print("Install with: uv sync --group agents")
            return ExitCode.MISSING_DEPENDENCIES

        if args.validate_config:
            return self._validate_config(args)

        if args.dry_run:
            return self._dry_run(args)

        return self._run_watcher(args)

    def _validate_config(self, args) -> ExitCode:
        """Validate project configuration."""
        self.console.print("🔍 Validating watcher configuration...")

        try:
            state = _load_project_state(model_override=args.model)
            self.console.print(f"✅ Project: {state.name}")
            self.console.print(f"✅ Model: {getattr(state, 'model', 'default')}")

            # Validate output directory
            args.output_dir.mkdir(parents=True, exist_ok=True)
            self.console.print(f"✅ Output directory: {args.output_dir}")

        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            self.console.print("❌ Failed to load project state")
            self.console.print("Ensure 'ontologia genesis' has been executed.")
            return ExitCode.CONFIGURATION_ERROR
        except Exception as e:
            self.console.print(f"❌ Configuration validation failed: {e}")
            return ExitCode.CONFIGURATION_ERROR

        self.console.print("✅ Configuration validation passed")
        return ExitCode.SUCCESS

    def _dry_run(self, args) -> ExitCode:
        """Show configuration without running."""
        self.console.print("🔍 Dry run mode - watcher configuration:")

        self.console.print("\n⚙️  Configuration:")
        self.console.print(f"  Interval: {args.interval}s")
        self.console.print(f"  Duration: {args.duration}s")
        self.console.print(f"  Max events: {args.max_events}")
        self.console.print(f"  Output dir: {args.output_dir}")
        self.console.print(f"  Run once: {args.once}")

        if args.object_type:
            self.console.print(f"  Object types: {', '.join(args.object_type)}")

        if args.entity_id:
            self.console.print(f"  Entity IDs: {', '.join(args.entity_id)}")

        self.console.print("\n🔄 Execution Steps:")
        self.console.print("  1. Load project state and configuration")
        self.console.print("  2. Initialize ArchitectAgent")
        self.console.print("  3. Start event streaming loop")
        self.console.print("  4. Collect events in time windows")
        self.console.print("  5. Analyze events for ontology drift")
        self.console.print("  6. Generate action plans if needed")
        self.console.print("  7. Save plans for review")

        if not args.once:
            self.console.print(f"  8. Sleep {args.interval}s and repeat")

        return ExitCode.SUCCESS

    def _run_watcher(self, args) -> ExitCode:
        """Execute the watcher agent."""
        try:
            # Load project state
            state = _load_project_state(model_override=args.model)

            # Initialize agent
            agent_module = ontologia_agent()
            agent = agent_module.ArchitectAgent(state)

            self.console.print(
                f"👁️ Watcher agent connected to project '{state.name}'. "
                f"Streaming events every {args.interval:.1f}s."
            )

            # Run the watcher loop
            asyncio.run(self._watcher_loop(agent, args))

            return ExitCode.SUCCESS

        except KeyboardInterrupt:
            self.console.print("\n⚠️ Watcher interrupted by user. Exiting.")
            return ExitCode.SUCCESS
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            self.console.print("❌ Failed to load project state")
            self.console.print("Ensure 'ontologia genesis' has been executed.")
            return ExitCode.CONFIGURATION_ERROR
        except Exception as e:
            self.console.print(f"❌ Watcher failed: {e}")
            self.logger.exception("Watcher failed")
            return ExitCode.GENERAL_ERROR

    async def _watcher_loop(self, agent, args) -> None:
        """Main watcher loop."""
        try:
            while True:
                # Collect events
                events_payload = await self._collect_events(agent, args)
                events = events_payload.get("events") or []

                if not events:
                    self.console.print("No events observed during this window.")
                else:
                    # Analyze events and generate plan
                    prompt = _build_prompt(
                        events, events_payload.get("durationSeconds", args.duration)
                    )

                    self.console.print(
                        f"Captured {len(events)} event(s). Generating analysis plan…"
                    )

                    plan = await agent.create_plan(prompt)

                    if plan.is_empty():
                        self.console.print("Agent concluded that no action is required.")
                    else:
                        # Save plan for review
                        record = _to_record(events_payload, plan)
                        target = self._write_plan(args.output_dir, record)
                        self.console.print(
                            f"Proposed plan saved to {target}. Awaiting human review."
                        )

                if args.once:
                    break

                # Sleep before next iteration
                sleep_time = max(args.interval, 1.0)
                self.logger.debug(f"Sleeping {sleep_time}s before next iteration")
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            # Handle gracefully at the top level
            raise
        except Exception as e:
            self.logger.exception(f"Error in watcher loop: {e}")
            raise

    async def _collect_events(self, agent, args) -> dict[str, Any]:
        """Collect events from the agent."""
        payload: dict[str, Any] = {
            "duration_seconds": args.duration,
            "max_events": args.max_events,
        }

        if args.object_type:
            payload["object_types"] = args.object_type

        if args.entity_id:
            payload["entity_ids"] = args.entity_id

        result = await agent.call_tool("stream_ontology_events", payload)

        if isinstance(result, list):
            # Defensive: ensure consistent shape
            return {"events": result, "count": len(result), "durationSeconds": args.duration}

        return dict(result)

    def _write_plan(self, output_dir: Path, plan_payload: dict[str, Any]) -> Path:
        """Write plan to file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        branch = plan_payload["plan"].get("branch_name", "plan")
        safe_branch = branch.replace("/", "-")[:64]

        file_path = output_dir / f"plan_{timestamp}_{safe_branch}.json"
        file_path.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")

        return file_path


def main() -> ExitCode:
    """Main entry point for the watcher agent script."""
    cli = WatcherAgentCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
