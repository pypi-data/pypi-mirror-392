"""
📋 Setup modes configuration for Ontologia.

Defines different deployment modes with their specific requirements,
features, and configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SetupMode(Enum):
    """Available setup modes for Ontologia."""

    CORE = "core"
    ANALYTICS = "analytics"
    FULL = "full"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        return {
            SetupMode.CORE: "Core",
            SetupMode.ANALYTICS: "Analytics",
            SetupMode.FULL: "Full",
        }[self]

    @property
    def description(self) -> str:
        """Mode description."""
        return {
            SetupMode.CORE: "Minimal setup (PostgreSQL + API)",
            SetupMode.ANALYTICS: "Add data processing (DuckDB + dbt + Dagster)",
            SetupMode.FULL: "Complete enterprise stack",
        }[self]


@dataclass
class ModeConfig:
    """Configuration for a specific setup mode."""

    mode: SetupMode
    display_name: str
    description: str
    long_description: str
    required_dependencies: list[str]
    optional_dependencies: list[str]
    docker_compose_files: list[str]
    feature_flags: dict[str, str]
    next_steps: list[str]

    def get_dependency_groups(self) -> list[str]:
        """Get the dependency groups required for this mode."""
        groups = []

        if "duckdb" in self.required_dependencies or "polars" in self.required_dependencies:
            groups.append("analytics")

        if any(
            dep in self.required_dependencies for dep in ["kuzu", "elasticsearch", "temporalio"]
        ):
            groups.append("full")

        return groups


# Mode configurations
MODE_CONFIGS: dict[SetupMode, ModeConfig] = {
    SetupMode.CORE: ModeConfig(
        mode=SetupMode.CORE,
        display_name="Core",
        description="Minimal setup (PostgreSQL + API)",
        long_description="Perfect for getting started and simple APIs",
        required_dependencies=["python", "docker"],
        optional_dependencies=[],
        docker_compose_files=["docker-compose.core.yml"],
        feature_flags={
            "STORAGE_MODE": "sql_only",
            "ENABLE_SEARCH": "false",
            "ENABLE_WORKFLOWS": "false",
            "ENABLE_REALTIME": "false",
            "ENABLE_ORCHESTRATION": "false",
        },
        next_steps=[
            "📖 API Documentation: http://localhost:8000/docs",
            "🚀 Try the API: curl -X POST http://localhost:8000/v2/auth/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin'",
            "📦 Install SDK: pip install ontologia[core]",
            "💻 See examples: templates/project/examples/quickstarts/",
        ],
    ),
    SetupMode.ANALYTICS: ModeConfig(
        mode=SetupMode.ANALYTICS,
        display_name="Analytics",
        description="Add data processing (DuckDB + dbt + Dagster)",
        long_description="For data platforms and analytics workflows",
        required_dependencies=["python", "docker", "duckdb", "polars"],
        optional_dependencies=[],
        docker_compose_files=[
            "docker-compose.core.yml",
            "docker-compose.analytics.yml",
        ],
        feature_flags={
            "STORAGE_MODE": "sql_duckdb",
            "ENABLE_SEARCH": "false",
            "ENABLE_WORKFLOWS": "false",
            "ENABLE_REALTIME": "false",
            "ENABLE_ORCHESTRATION": "true",
        },
        next_steps=[
            "📖 API Documentation: http://localhost:8000/docs",
            "📊 Dagster UI: http://localhost:3000",
            "📚 dbt Docs: http://localhost:8080",
            "🔬 Jupyter Lab: http://localhost:8888",
            "🔄 Run pipeline: uv run just pipeline",
            "📦 Install SDK: pip install ontologia[analytics]",
        ],
    ),
    SetupMode.FULL: ModeConfig(
        mode=SetupMode.FULL,
        display_name="Full",
        description="Complete enterprise stack",
        long_description="All features including graph DB, search, workflows",
        required_dependencies=[
            "python",
            "docker",
            "duckdb",
            "polars",
            "kuzu",
            "elasticsearch",
            "temporalio",
        ],
        optional_dependencies=[],
        docker_compose_files=[
            "docker-compose.core.yml",
            "docker-compose.analytics.yml",
            "docker-compose.full.yml",
        ],
        feature_flags={
            "STORAGE_MODE": "sql_duckdb",
            "ENABLE_SEARCH": "true",
            "ENABLE_WORKFLOWS": "true",
            "ENABLE_REALTIME": "false",
            "ENABLE_ORCHESTRATION": "true",
        },
        next_steps=[
            "📖 API Documentation: http://localhost:8000/docs",
            "📊 Dagster UI: http://localhost:3000",
            "🔍 Elasticsearch: http://localhost:9200",
            "⏰ Temporal UI: http://localhost:7233",
            "🔬 Jupyter Lab: http://localhost:8888",
            "🔄 Run pipeline: uv run just pipeline",
            "📦 Install SDK: pip install ontologia[full]",
        ],
    ),
}


def get_mode_config(mode: SetupMode) -> ModeConfig:
    """Get configuration for a specific setup mode."""
    if mode not in MODE_CONFIGS:
        raise ValueError(f"Unknown setup mode: {mode}")
    return MODE_CONFIGS[mode]


def get_all_modes() -> list[SetupMode]:
    """Get all available setup modes."""
    return list(SetupMode)


def validate_mode(mode_str: str) -> SetupMode:
    """Validate and convert mode string to SetupMode enum."""
    try:
        return SetupMode(mode_str.lower())
    except ValueError:
        valid_modes = [mode.value for mode in SetupMode]
        raise ValueError(f"Invalid mode: {mode_str}. Valid modes: {', '.join(valid_modes)}")
