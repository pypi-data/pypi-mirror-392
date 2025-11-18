"""
🔧 Shared utilities for Ontologia scripts.

This module provides standardized patterns for configuration, logging,
CLI argument parsing, and error handling across all scripts.
"""

from .cli import BaseCLI, ExitCode
from .config import ScriptConfig, load_script_config
from .deps import optional_import
from .logging import setup_logging

__all__ = [
    "load_script_config",
    "ScriptConfig",
    "setup_logging",
    "BaseCLI",
    "ExitCode",
    "optional_import",
]
