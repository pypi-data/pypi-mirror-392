"""
⚙️ Configuration utilities for Ontologia scripts.

Provides standardized configuration loading using Pydantic Settings
with proper environment variable handling and validation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from ontologia.config import load_config as load_ontologia_config
except ImportError:
    # Fallback for when ontologia.config is not available
    def load_ontologia_config(path: Path | None = None) -> dict[str, Any]:
        """Fallback configuration loader."""
        return {}


class ScriptConfig(BaseSettings):
    """Base configuration for all Ontologia scripts."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Project configuration
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Root directory of the Ontologia project",
    )
    config_root: Path = Field(
        default_factory=lambda: Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())),
        description="Configuration root directory",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    # API configuration
    api_url: str | None = Field(default=None, description="Ontologia API base URL")
    api_token: str | None = Field(default=None, description="API authentication token")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    def load_ontologia_config(self) -> Any:
        """Load the main Ontologia configuration."""
        return load_ontologia_config(self.config_root)


def load_script_config(config_root: Path | None = None, **overrides: Any) -> ScriptConfig:
    """
    Load standardized script configuration.

    Args:
        config_root: Optional configuration root directory
        **overrides: Configuration values to override

    Returns:
        ScriptConfig instance with loaded configuration
    """
    if config_root:
        overrides["config_root"] = config_root

    return ScriptConfig(**overrides)
