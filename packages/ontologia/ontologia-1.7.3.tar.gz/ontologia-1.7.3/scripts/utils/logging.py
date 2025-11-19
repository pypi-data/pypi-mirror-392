"""
📝 Logging utilities for Ontologia scripts.

Provides consistent logging setup with proper formatting,
structured output, and integration with the script configuration.
"""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from .config import ScriptConfig


def setup_logging(
    config: ScriptConfig | None = None,
    name: str | None = None,
    console_output: bool = True,
    file_output: bool = False,
    log_file: Path | None = None,
) -> logging.Logger:
    """
    Setup standardized logging for scripts.

    Args:
        config: Script configuration instance
        name: Logger name (defaults to calling module)
        console_output: Enable console output with Rich formatting
        file_output: Enable file output
        log_file: Path to log file (auto-generated if not provided)

    Returns:
        Configured logger instance
    """
    if config is None:
        config = ScriptConfig()

    # Get logger name
    if name is None:
        name = "ontologia.scripts"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with Rich formatting
    if console_output:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
        )
        console_handler.setLevel(getattr(logging, config.log_level))
        logger.addHandler(console_handler)

    # File handler for structured logging
    if file_output:
        if log_file is None:
            log_file = Path("logs") / f"{name.replace('.', '_')}.log"

        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, config.log_level))

        # Use simple format for file logs
        formatter = logging.Formatter(config.log_format)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger with standard configuration.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    if name is None:
        name = "ontologia.scripts"

    return logging.getLogger(name)
