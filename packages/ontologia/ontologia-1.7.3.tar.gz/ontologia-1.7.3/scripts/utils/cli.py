"""
🖥️ CLI utilities for Ontologia scripts.

Provides standardized command-line interface patterns,
argument parsing, and error handling with proper exit codes.
"""

from __future__ import annotations

import argparse
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from enum import IntEnum
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from .config import ScriptConfig
from .logging import setup_logging


class ExitCode(IntEnum):
    """Standard exit codes for Ontologia scripts."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGUMENTS = 2
    MISSING_DEPENDENCIES = 3
    CONFIGURATION_ERROR = 4
    PERMISSION_ERROR = 5
    NETWORK_ERROR = 6
    TIMEOUT_ERROR = 7


class BaseCLI(ABC):
    """
    Base class for standardized CLI interfaces.

    Provides common patterns for argument parsing, configuration loading,
    logging setup, and error handling.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        config: ScriptConfig | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.version = version
        self.config = config or ScriptConfig()
        self.console = Console()

        # Setup logging
        self.logger = setup_logging(self.config, name=f"ontologia.scripts.{name}")

        # Initialize argument parser
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the base argument parser."""
        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Add common arguments
        parser.add_argument(
            "--version",
            action="version",
            version=f"{self.name} {self.version}",
        )

        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default=self.config.log_level,
            help="Set logging level",
        )

        parser.add_argument(
            "--config-root",
            type=Path,
            default=self.config.config_root,
            help="Configuration root directory",
        )

        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress console output",
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

        # Add script-specific arguments
        self.add_arguments(parser)

        return parser

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add script-specific arguments to the parser."""
        pass

    @abstractmethod
    def run(self, args: argparse.Namespace) -> ExitCode:
        """Execute the main script logic."""
        pass

    def handle_error(
        self, error: Exception, exit_code: ExitCode = ExitCode.GENERAL_ERROR
    ) -> ExitCode:
        """Handle errors with consistent formatting."""
        self.console.print(
            Panel.fit(
                f"❌ Error: {error}",
                title=f"{self.name} Error",
                border_style="red",
            )
        )

        if self.config.log_level == "DEBUG":
            self.logger.exception("Detailed error information:")

        return exit_code

    def main(self, argv: Sequence[str] | None = None) -> ExitCode:
        """
        Main entry point for the CLI.

        Args:
            argv: Command line arguments (defaults to sys.argv)

        Returns:
            Exit code
        """
        try:
            # Parse arguments
            args = self.parser.parse_args(argv)

            # Update configuration based on arguments
            if args.log_level:
                self.config.log_level = args.log_level
            if args.config_root:
                self.config.config_root = args.config_root

            # Reconfigure logging with updated settings
            self.logger = setup_logging(
                self.config,
                name=f"ontologia.scripts.{self.name}",
                console_output=not args.quiet,
            )

            # Run the main logic
            return self.run(args)

        except KeyboardInterrupt:
            self.console.print("\n⚠️  Operation cancelled by user")
            return ExitCode.GENERAL_ERROR
        except argparse.ArgumentError as e:
            self.console.print(f"❌ Argument error: {e}")
            return ExitCode.INVALID_ARGUMENTS
        except Exception as e:
            return self.handle_error(e)


def create_simple_cli(
    name: str,
    description: str,
    main_func: Callable[..., Any],
    arguments: list[dict[str, Any]] | None = None,
) -> Callable[..., Any]:
    """
    Create a simple CLI wrapper for a function.

    Args:
        name: Script name
        description: Script description
        main_func: Main function to call
        arguments: List of argument specifications

    Returns:
        CLI main function
    """

    def cli_main(argv: Sequence[str] | None = None) -> ExitCode:
        parser = argparse.ArgumentParser(
            prog=name,
            description=description,
        )

        # Add common arguments
        parser.add_argument("--log-level", default="INFO", help="Log level")
        parser.add_argument("--config-root", type=Path, help="Config root")

        # Add custom arguments
        if arguments:
            for arg_spec in arguments:
                parser.add_argument(**arg_spec)

        args = parser.parse_args(argv)

        try:
            # Setup configuration
            config = ScriptConfig(
                log_level=args.log_level,
                config_root=getattr(args, "config_root", None) or Path.cwd(),
            )

            # Setup logging
            logger = setup_logging(config, name=f"ontologia.scripts.{name}")

            # Call main function
            result = main_func(args, config, logger)
            return ExitCode.SUCCESS if result is None else result

        except Exception as e:
            console = Console()
            console.print(f"❌ Error: {e}")
            return ExitCode.GENERAL_ERROR

    return cli_main
