"""
🚀 Ontologia Setup System

Modular setup system for different deployment modes.
Provides guided setup with dependency checking, service orchestration,
and configuration generation.
"""

from .cli import SetupCLI, main
from .config import ConfigGenerator
from .modes import SetupMode, get_mode_config
from .services import DependencyChecker, ServiceManager

__all__ = [
    "SetupCLI",
    "main",
    "SetupMode",
    "get_mode_config",
    "ServiceManager",
    "DependencyChecker",
    "ConfigGenerator",
]
