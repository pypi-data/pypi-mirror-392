"""
🖥️ CLI interface for Ontologia setup.

Provides interactive and command-line setup for different deployment modes.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import questionary
from rich.panel import Panel

from scripts.utils import BaseCLI, ExitCode

from .config import ConfigGenerator
from .modes import SetupMode, get_mode_config, validate_mode
from .services import ServiceManager


class SetupCLI(BaseCLI):
    """CLI for Ontologia setup operations."""

    def __init__(self) -> None:
        super().__init__(
            name="setup",
            description="Guided setup for different Ontologia deployment modes",
            version="1.0.0",
        )
        self.service_manager = ServiceManager(self.console)
        self.config_generator = ConfigGenerator(self.console)

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "mode",
            nargs="?",
            choices=[mode.value for mode in SetupMode],
            help="Setup mode (core, analytics, full)",
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Force interactive mode selection",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show setup plan without executing",
        )
        parser.add_argument(
            "--skip-dependency-check",
            action="store_true",
            help="Skip dependency checking",
        )
        parser.add_argument(
            "--config-only",
            action="store_true",
            help="Only generate configuration files",
        )

    def run(self, args) -> ExitCode:
        # Show welcome message
        self._show_welcome()

        # Determine setup mode
        mode = self._get_setup_mode(args)
        if mode is None:
            return ExitCode.INVALID_ARGUMENTS

        mode_config = get_mode_config(mode)

        if args.dry_run:
            return self._dry_run(mode_config)

        if args.config_only:
            return self._config_only(mode_config)

        return self._full_setup(mode_config, args)

    def _show_welcome(self) -> None:
        """Show welcome message."""
        self.console.print(
            Panel.fit(
                "🚀 Welcome to Ontologia Setup!\\n\\n"
                "This script will help you get Ontologia running in minutes.\\n"
                "Choose your setup mode and we'll handle the configuration.",
                title="Ontologia Setup",
                border_style="blue",
            )
        )

    def _get_setup_mode(self, args) -> SetupMode | None:
        """Get the setup mode from arguments or interactive selection."""
        if args.mode and not args.interactive:
            try:
                return validate_mode(args.mode)
            except ValueError as e:
                self.console.print(f"❌ {e}")
                return None

        # Interactive mode selection
        return self._interactive_mode_selection()

    def _interactive_mode_selection(self) -> SetupMode:
        """Interactive mode selection using questionary."""
        choice = questionary.select(
            "Choose Ontologia setup mode:",
            choices=[
                questionary.Choice(
                    "Core - Minimal setup (PostgreSQL + API)",
                    value=SetupMode.CORE.value,
                    description="Perfect for getting started and simple APIs",
                ),
                questionary.Choice(
                    "Analytics - Add data processing (DuckDB + dbt + Dagster)",
                    value=SetupMode.ANALYTICS.value,
                    description="For data platforms and analytics workflows",
                ),
                questionary.Choice(
                    "Full - Complete enterprise stack",
                    value=SetupMode.FULL.value,
                    description="All features including graph DB, search, workflows",
                ),
            ],
            default=SetupMode.CORE.value,
        ).ask()

        return SetupMode(choice or SetupMode.CORE.value)

    def _dry_run(self, mode_config) -> ExitCode:
        """Show setup plan without executing."""
        self.console.print(f"\\n🔍 Dry run mode - {mode_config.display_name} setup plan:")

        # Show configuration summary
        config_summary = self.config_generator.get_config_summary(mode_config)

        self.console.print("\\n📊 Configuration Summary:")
        for key, value in config_summary.items():
            self.console.print(f"  {key}: {value}")

        # Show setup steps
        self.console.print("\\n📋 Setup Steps:")
        steps = [
            "1. Check dependencies",
            "2. Generate configuration files",
            "3. Start Docker services",
            "4. Wait for services to be ready",
            "5. Run database migrations",
            "6. Generate SDK",
        ]

        for step in steps:
            self.console.print(f"  {step}")

        # Show next steps
        self.console.print("\\n🚀 Next Steps (after setup):")
        for step in mode_config.next_steps:
            self.console.print(f"  {step}")

        return ExitCode.SUCCESS

    def _config_only(self, mode_config) -> ExitCode:
        """Only generate configuration files."""
        project_dir = Path.cwd()

        self.console.print(f"\\n⚙️  Generating configuration for {mode_config.display_name} mode...")

        # Generate .env file
        env_file = self.config_generator.generate_env_file(mode_config, project_dir)

        # Validate configuration
        if self.config_generator.validate_config(env_file):
            self.console.print("✅ Configuration generation completed successfully")
            return ExitCode.SUCCESS
        else:
            return ExitCode.CONFIGURATION_ERROR

    def _full_setup(self, mode_config, args) -> ExitCode:
        """Execute the complete setup process."""
        project_dir = Path.cwd()

        self.console.print(f"\\n🎯 Setting up Ontologia in {mode_config.display_name} mode...")

        try:
            # Generate configuration
            self.console.print("Generating configuration...")
            env_file = self.config_generator.generate_env_file(mode_config, project_dir)

            # Check dependencies (unless skipped)
            if not args.skip_dependency_check:
                from .services import DependencyChecker

                checker = DependencyChecker(self.console)
                dependencies = checker.check_mode_dependencies(mode_config)

                missing = [dep for dep, available in dependencies.items() if not available]
                if missing:
                    checker.report_missing_dependencies(dependencies, mode_config)
                    return ExitCode.MISSING_DEPENDENCIES

            # Setup services
            if not self.service_manager.setup_mode(mode_config, project_dir):
                return ExitCode.GENERAL_ERROR

            # Show success message
            self._show_success_message(mode_config)

            return ExitCode.SUCCESS

        except KeyboardInterrupt:
            self.console.print("\\n❌ Setup cancelled")
            return ExitCode.GENERAL_ERROR
        except Exception as e:
            self.console.print(f"\\n❌ Setup failed: {e}")
            self.logger.exception("Setup failed")
            return ExitCode.GENERAL_ERROR

    def _show_success_message(self, mode_config) -> None:
        """Show success message with next steps."""
        self.console.print(
            Panel.fit(
                "\\n".join(mode_config.next_steps),
                title=f"✅ Ontologia {mode_config.display_name} Mode Setup Complete!",
                border_style="green",
            )
        )


def main(argv: Sequence[str] | None = None) -> ExitCode:
    """Main entry point for the setup script."""
    cli = SetupCLI()
    return cli.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
