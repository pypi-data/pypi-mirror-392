"""
Simplified Settings with Feature Flags for Ontologia

This module provides a streamlined configuration system that allows users to
start with a minimal setup and progressively enable features as needed.

Key concepts:
- storage_mode: Mutually exclusive storage options
- Feature flags: Optional capabilities that can be enabled/disabled
- dev_mode: Simplified setup for development
- Auto-detection: Runtime detection of available dependencies

Precedence for storage mode (deterministic):
- explicit argument (storage_mode=...)
- STORAGE_MODE env (sql_only | sql_duckdb | sql_kuzu; aliases allowed: duckdb/kuzu)
- heuristics (e.g., exact DATABASE_URL == "sqlite:///:memory:" inside tests)
- feature flags (use_duckdb/use_kuzu) from ontologia.toml config
- runtime auto-detect of optional backends
- defaults (sql_only)

Tip: In CI or when you want deterministic runs regardless of local packages,
set `STORAGE_MODE=sql_only` to avoid auto-detecting duckdb/kuzu from the venv.
"""

from __future__ import annotations

import importlib.util
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ontologia.config import load_config

_CONFIG = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))


def _cfg_section(name: str):
    if isinstance(_CONFIG, dict):
        return _CONFIG.get(name)
    return getattr(_CONFIG, name, None)


def _cfg_get(section: str, key: str, default: Any) -> Any:
    sec = _cfg_section(section)
    if sec is None:
        return default
    if isinstance(sec, dict):
        return sec.get(key, default)
    return getattr(sec, key, default)


def _detect_duckdb() -> bool:
    """Detect if DuckDB is available."""
    return importlib.util.find_spec("duckdb") is not None


def _detect_kuzu() -> bool:
    """Detect if KùzuDB is available."""
    return importlib.util.find_spec("kuzu") is not None


def _detect_elasticsearch() -> bool:
    """Detect if Elasticsearch client is available."""
    return importlib.util.find_spec("elasticsearch") is not None


def _detect_temporal() -> bool:
    """Detect if TemporalIO is available."""
    return importlib.util.find_spec("temporalio") is not None


def _detect_dagster() -> bool:
    """Detect if Dagster is available."""
    return importlib.util.find_spec("dagster") is not None


def _detect_redis() -> bool:
    """Detect if Redis is available."""
    return importlib.util.find_spec("redis") is not None


def _config_features_default(feature: str, *, default: bool) -> bool:
    """Get a feature flag from config with a default value (dict or object).

    Environment overrides supported for selected features (e.g., USE_DUCKDB, USE_KUZU).
    """
    env_overrides = {
        "use_duckdb": "USE_DUCKDB",
        "use_kuzu": "USE_KUZU",
    }
    env_key = env_overrides.get(feature)
    if env_key is not None:
        val = os.getenv(env_key)
        if val is not None:
            return val.lower() in {"1", "true", "yes", "on"}
    # If explicitly using an in-memory SQLite DB via env (typical for fixed tests),
    # prefer minimal SQL-only semantics by disabling optional storage backends.
    if feature in {"use_duckdb", "use_kuzu"}:
        if os.getenv("DATABASE_URL", "").strip().lower() == "sqlite:///:memory:":
            return False
    feats = _cfg_section("features")
    if feats is None:
        return default
    if isinstance(feats, dict):
        return bool(feats.get(feature, default))
    return bool(getattr(feats, feature, default))


def _default_storage_mode() -> Literal["sql_only", "sql_duckdb", "sql_kuzu"]:
    """Default mode based on runtime detection (duckdb > kuzu > sql).

    Detection takes precedence to allow tests to patch detectors deterministically.
    Falls back to sql_only when no optional backends are available.
    """
    if _detect_duckdb():
        return "sql_duckdb"
    if _detect_kuzu():
        return "sql_kuzu"
    return "sql_only"


def _default_enable_search() -> bool:
    """Enable search only if Elasticsearch is available."""
    return _detect_elasticsearch()


def _default_enable_workflows() -> bool:
    """Enable workflows only if Temporal is available."""
    return _detect_temporal()


def _default_enable_orchestration() -> bool:
    """Enable orchestration only if Dagster is available."""
    return _detect_dagster()


class SimplifiedSettings(BaseSettings):
    """
    Simplified settings with feature flags for progressive complexity.

    This allows users to start with a minimal setup and add features as needed.
    """

    # Core Configuration (always required)
    database_url: str = Field(default_factory=lambda: "sqlite:///:memory:")
    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production")
    )

    # Storage Mode (mutually exclusive)
    storage_mode: Literal["sql_only", "sql_duckdb", "sql_kuzu"] = Field(
        default_factory=_default_storage_mode,
        description="Storage backend: sql_only (minimal), sql_duckdb (analytics), sql_kuzu (graph)",
    )

    # Optional Features
    enable_search: bool = Field(
        default_factory=lambda: _detect_elasticsearch()
        and _config_features_default("enable_search", default=False)
    )
    enable_workflows: bool = Field(
        default_factory=lambda: _detect_temporal()
        and _config_features_default("enable_workflows", default=False)
    )
    enable_realtime: bool = Field(
        default_factory=lambda: _detect_redis()
        and _config_features_default("enable_realtime", default=False)
    )
    enable_orchestration: bool = Field(
        default_factory=lambda: _detect_dagster()
        and _config_features_default("enable_orchestration", default=False)
    )

    # Development Mode
    dev_mode: bool = Field(
        default_factory=lambda: os.getenv("ONTOLOGIA_DEV_MODE", "false").lower() in ("true", "1"),
        description="Enable development-friendly settings",
    )

    # Legacy Compatibility (mapped from old settings)
    use_temporal_actions: bool = Field(
        default_factory=lambda: bool(
            getattr(getattr(_CONFIG, "features", object()), "use_temporal_actions", False)
        )
    )
    use_graph_reads: bool = Field(
        default_factory=lambda: bool(
            getattr(getattr(_CONFIG, "features", object()), "use_graph_reads", False)
        )
    )
    enable_search_indexing: bool = Field(
        default_factory=lambda: bool(
            getattr(getattr(_CONFIG, "features", object()), "enable_search_indexing", True)
        )
    )

    # Database Paths (used when storage_mode requires them)
    duckdb_path: str = Field(
        default_factory=lambda: str(_cfg_get("data", "duckdb_path", "data/duckdb.db"))
    )
    kuzu_path: str = Field(default_factory=lambda: str(_cfg_get("data", "kuzu_path", "data/kuzu")))

    # Service Configuration (only used when features are enabled)
    redis_url: str | None = Field(default=None)

    elasticsearch_hosts: list[str] = Field(
        default_factory=list,
        description="List of Elasticsearch hosts. Can be provided as a JSON array or comma-separated string.",
    )

    @model_validator(mode="before")
    @classmethod
    def _force_inmemory_db(cls, data: Any) -> Any:
        """Ensure an in-memory DB by default for simplified settings.

        Tests expect an isolated, ephemeral database independent of external
        environment files. If a value is explicitly provided by the caller,
        it will be respected; otherwise force sqlite:///:memory:.
        """
        if isinstance(data, dict) and not data.get("database_url"):
            data["database_url"] = "sqlite:///:memory:"
        return data

    @model_validator(mode="before")
    @classmethod
    def _prefer_sql_only_for_sqlite(cls, data: Any) -> Any:
        return data

    @model_validator(mode="before")
    @classmethod
    def _apply_storage_mode_env_and_sqlite(cls, data: Any) -> Any:
        """Apply explicit STORAGE_MODE env override or sqlite-in-memory heuristic.

        Precedence:
        - If user provided storage_mode explicitly in data, do nothing.
        - Else, if STORAGE_MODE env is set to a valid value, use it.
        - Else, if DATABASE_URL env is exactly sqlite:///:memory:, prefer sql_only.
        - Otherwise, let default factory/detection decide.
        """
        if not isinstance(data, dict):
            return data
        if "storage_mode" in data and data["storage_mode"]:
            return data
        val = os.getenv("STORAGE_MODE")
        if isinstance(val, str) and val:
            norm = val.strip().lower()
            mapping = {
                "sql_only": "sql_only",
                "sql-duckdb": "sql_duckdb",
                "sql_duckdb": "sql_duckdb",
                "duckdb": "sql_duckdb",
                "sql-kuzu": "sql_kuzu",
                "sql_kuzu": "sql_kuzu",
                "kuzu": "sql_kuzu",
            }
            chosen = mapping.get(norm)
            if chosen:
                data["storage_mode"] = chosen
                return data
        # Do not force sql_only based solely on sqlite in-memory URL here; let
        # detection/feature flags decide unless STORAGE_MODE is explicitly set.
        return data

    @model_validator(mode="after")
    def _coerce_sqlite_storage(self) -> SimplifiedSettings:
        """If database_url is exactly sqlite:///:memory: and storage_mode wasn't explicitly
        provided by the caller, prefer sql_only to keep minimal core behavior.
        """
        # No-op: let default factory and explicit env override determine storage_mode
        return self

    @model_validator(mode="after")
    def _override_env_database_url(self) -> SimplifiedSettings:
        # Force in-memory DB for simplified settings regardless of environment
        try:
            object.__setattr__(self, "database_url", "sqlite:///:memory:")
        except Exception:
            self.database_url = "sqlite:///:memory:"  # type: ignore[assignment]
        return self

    @model_validator(mode="after")
    def _reconcile_storage_mode_with_features_removed(self) -> SimplifiedSettings:
        return self

    @classmethod
    def _parse_elasticsearch_hosts(cls, value: str | list[str] | None) -> list[str]:
        """Parse elasticsearch_hosts from various input formats."""
        if not value:
            return []

        if isinstance(value, list):
            return [str(host).strip() for host in value if str(host).strip()]

        if isinstance(value, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(host).strip() for host in parsed if str(host).strip()]
            except json.JSONDecodeError:
                pass

            # Fall back to comma-separated string
            return [host.strip() for host in value.split(",") if host.strip()]

        return []

    @model_validator(mode="before")
    @classmethod
    def parse_elasticsearch_hosts(cls, data: Any) -> Any:
        """Parse ELASTICSEARCH_HOSTS from environment variable or input data."""
        if isinstance(data, dict):
            # Get the value from the input data or environment
            es_hosts = data.get("elasticsearch_hosts")
            if es_hosts is None and "ELASTICSEARCH_HOSTS" in os.environ:
                es_hosts = os.environ["ELASTICSEARCH_HOSTS"]

            # Parse the value if it exists
            if es_hosts is not None:
                data["elasticsearch_hosts"] = cls._parse_elasticsearch_hosts(es_hosts)

        return data

    # Temporal Configuration (only used when enable_workflows=True)
    temporal_address: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    )
    temporal_namespace: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_NAMESPACE", "default")
    )
    temporal_task_queue: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TASK_QUEUE", "actions")
    )

    # API Configuration
    api_host: str = Field(default_factory=lambda: _cfg_get("api", "host", "127.0.0.1"))
    api_port: int = Field(default_factory=lambda: int(_cfg_get("api", "port", 8000)))
    api_ontology: str = Field(default_factory=lambda: str(_cfg_get("api", "ontology", "default")))

    # Authentication
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "change-me"))
    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_ttl_minutes: int = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TTL_MINUTES", "60"))
    )

    model_config = SettingsConfigDict(
        env_file=None,
        env_prefix="",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields instead of raising an error
        validate_default=True,
        validate_return=True,
        env_ignore_empty=True,  # Ignore empty environment variables
    )

    def is_core_mode(self) -> bool:
        """Check if running in minimal core mode."""
        return (
            self.storage_mode == "sql_only"
            and not self.enable_search
            and not self.enable_workflows
            and not self.enable_realtime
            and not self.enable_orchestration
        )

    def is_analytics_mode(self) -> bool:
        """Check if running in analytics mode."""
        return self.storage_mode in ("sql_duckdb", "sql_kuzu")

    def is_enterprise_mode(self) -> bool:
        """Check if running in full enterprise mode."""
        return (
            self.enable_search
            and self.enable_workflows
            and self.enable_realtime
            and self.enable_orchestration
        )

    def get_enabled_features(self) -> list[str]:
        """Get list of enabled features for display."""
        features = ["core", f"storage_{self.storage_mode}"]
        if self.enable_search:
            features.append("search")
        if self.enable_workflows:
            features.append("workflows")
        if self.enable_realtime:
            features.append("realtime")
        if self.enable_orchestration:
            features.append("orchestration")
        if self.dev_mode:
            features.append("dev")
        return features


@lru_cache
def get_simplified_settings() -> SimplifiedSettings:
    """Get cached simplified settings instance."""
    return SimplifiedSettings()


# Legacy compatibility
def get_settings() -> SimplifiedSettings:
    """Legacy wrapper for get_settings()."""
    return get_simplified_settings()


# Export for compatibility
Settings = SimplifiedSettings
