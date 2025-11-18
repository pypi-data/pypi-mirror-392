from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ontologia.config import load_config

_CONFIG = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))


def _default_enable_search_indexing() -> bool:
    return _config_features_default("enable_search_indexing", default=True)


def _config_features_default(attr: str, *, default: bool = False) -> bool:
    features = getattr(_CONFIG, "features", None)
    if features is None:
        return default
    return bool(getattr(features, attr, default))


def _config_security_default(path: str, default):
    security = getattr(_CONFIG, "security", None)
    if security is None:
        return default
    value = security
    for segment in path.split("."):
        value = getattr(value, segment, default)
        if value is default:
            break
    return value


def _config_section_attr(section: str, attr: str, default: Any = None) -> Any:
    section_obj = getattr(_CONFIG, section, None)
    if section_obj is None:
        return default
    return getattr(section_obj, attr, default)


def _config_event_bus_attr(path: str, default: Any = None) -> Any:
    event_bus = getattr(_CONFIG, "event_bus", None)
    if event_bus is None:
        return default
    value: Any = event_bus
    for segment in path.split("."):
        value = getattr(value, segment, default)
        if value is default:
            break
    return value


def _default_event_bus_provider() -> str:
    env_provider = os.getenv("EVENT_BUS_BACKEND")
    if env_provider:
        return env_provider
    return str(_config_event_bus_attr("provider", "in_process"))


def _default_event_bus_sync_publish() -> bool:
    env_value = os.getenv("EVENT_BUS_SYNC_PUBLISH")
    if env_value is not None:
        return env_value in {"1", "true", "True", "yes"}
    return bool(_config_event_bus_attr("synchronous_publish", default=False))


def _default_kafka_bootstrap_servers() -> list[str]:
    env_value = os.getenv("EVENT_BUS_KAFKA_BOOTSTRAP_SERVERS")
    if env_value:
        return [server.strip() for server in env_value.split(",") if server.strip()]
    cfg_value = _config_event_bus_attr("kafka.bootstrap_servers", ["localhost:9092"])
    if isinstance(cfg_value, str):
        return [server.strip() for server in cfg_value.split(",") if server.strip()]
    return list(cfg_value or ["localhost:9092"])


def _default_kafka_topic_prefix() -> str:
    return str(_config_event_bus_attr("kafka.topic_prefix", "ontologia"))


def _default_kafka_client_id() -> str | None:
    env_value = os.getenv("EVENT_BUS_KAFKA_CLIENT_ID")
    if env_value:
        return env_value
    client_id = _config_event_bus_attr("kafka.client_id", None)
    return str(client_id) if client_id is not None else None


def _default_kafka_security_attr(name: str) -> str | None:
    env_map = {
        "security_protocol": "EVENT_BUS_KAFKA_SECURITY_PROTOCOL",
        "sasl_mechanism": "EVENT_BUS_KAFKA_SASL_MECHANISM",
        "sasl_username": "EVENT_BUS_KAFKA_SASL_USERNAME",
        "sasl_password": "EVENT_BUS_KAFKA_SASL_PASSWORD",
    }
    env_key = env_map.get(name)
    if env_key:
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
    cfg_value = _config_event_bus_attr(f"kafka.{name}", None)
    return str(cfg_value) if cfg_value is not None else None


class Settings(BaseSettings):
    # Environment
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    # Feature flags
    use_temporal_actions: bool = Field(
        default_factory=lambda: _config_features_default("use_temporal_actions", default=False)
    )
    enable_search_indexing: bool = Field(default_factory=_default_enable_search_indexing)
    use_graph_reads: bool = Field(
        default_factory=lambda: _config_features_default("use_graph_reads", default=True)
    )
    use_graph_writes: bool = Field(
        default_factory=lambda: _config_features_default("use_graph_writes", default=False)
    )
    use_unified_graph: bool = Field(
        default_factory=lambda: _config_features_default("use_unified_graph", default=True)
    )
    event_bus_provider: str = Field(default_factory=_default_event_bus_provider)
    event_bus_synchronous_publish: bool = Field(default_factory=_default_event_bus_sync_publish)
    event_bus_kafka_bootstrap_servers: list[str] = Field(
        default_factory=_default_kafka_bootstrap_servers
    )
    event_bus_kafka_topic_prefix: str = Field(default_factory=_default_kafka_topic_prefix)
    event_bus_kafka_client_id: str | None = Field(default_factory=_default_kafka_client_id)
    event_bus_kafka_security_protocol: str | None = Field(
        default_factory=lambda: _default_kafka_security_attr("security_protocol")
    )
    event_bus_kafka_sasl_mechanism: str | None = Field(
        default_factory=lambda: _default_kafka_security_attr("sasl_mechanism")
    )
    event_bus_kafka_sasl_username: str | None = Field(
        default_factory=lambda: _default_kafka_security_attr("sasl_username")
    )
    event_bus_kafka_sasl_password: str | None = Field(
        default_factory=lambda: _default_kafka_security_attr("sasl_password")
    )
    # NATS EventBus configuration
    event_bus_nats_servers: list[str] = Field(
        default_factory=lambda: _config_event_bus_attr("nats.servers", ["nats://localhost:4222"])
    )
    event_bus_nats_subject_prefix: str = Field(
        default_factory=lambda: _config_event_bus_attr("nats.subject_prefix", "ontologia")
    )
    event_bus_nats_client_name: str | None = Field(
        default_factory=lambda: _config_event_bus_attr("nats.client_name")
    )
    event_bus_nats_max_reconnect_attempts: int = Field(
        default_factory=lambda: _config_event_bus_attr("nats.max_reconnect_attempts", 60)
    )
    event_bus_nats_reconnect_wait: float = Field(
        default_factory=lambda: _config_event_bus_attr("nats.reconnect_wait", 2.0)
    )
    event_bus_nats_ping_interval: int = Field(
        default_factory=lambda: _config_event_bus_attr("nats.ping_interval", 20)
    )
    event_bus_nats_max_outstanding_pings: int = Field(
        default_factory=lambda: _config_event_bus_attr("nats.max_outstanding_pings", 3)
    )
    event_bus_nats_dont_randomize_servers: bool = Field(
        default_factory=lambda: _config_event_bus_attr("nats.dont_randomize_servers", False)
    )
    event_bus_nats_flush_timeout: float = Field(
        default_factory=lambda: _config_event_bus_attr("nats.flush_timeout", 30.0)
    )
    event_bus_nats_user: str | None = Field(
        default_factory=lambda: _config_event_bus_attr("nats.user")
    )
    event_bus_nats_password: str | None = Field(
        default_factory=lambda: _config_event_bus_attr("nats.password")
    )
    event_bus_nats_token: str | None = Field(
        default_factory=lambda: _config_event_bus_attr("nats.token")
    )
    abac_enabled: bool = Field(
        default_factory=lambda: _config_security_default("abac.enabled", default=True)
    )
    abac_role_allowed_tags: dict[str, list[str]] = Field(
        default_factory=lambda: _config_security_default("abac.role_allowed_tags", {"admin": ["*"]})
    )

    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/metamodel.db")
    )
    duckdb_path: str | None = Field(
        default_factory=lambda: _config_section_attr("data", "duckdb_path", None)
    )
    kuzu_path: str | None = Field(
        default_factory=lambda: _config_section_attr("data", "kuzu_path", None)
    )

    # Cache / Search
    redis_url: str | None = Field(default_factory=lambda: os.getenv("REDIS_URL"))
    elasticsearch_hosts: list[str] = Field(
        default_factory=lambda: [
            host.strip()
            for host in (os.getenv("ELASTICSEARCH_HOSTS", "").strip() or "").split(",")
            if host.strip()
        ]
        or ["localhost:9200"]  # Default to localhost if empty or not set
    )

    # Authentication / Authorization
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "change-me"))
    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_ttl_minutes: int = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TTL_MINUTES", "60"))
    )

    # Temporal
    temporal_address: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    )
    temporal_namespace: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_NAMESPACE", "default")
    )
    temporal_task_queue: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TASK_QUEUE", "actions")
    )
    temporal_tls_enabled: bool = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_ENABLED", "0") in {"1", "true", "True"}
    )
    temporal_tls_server_name: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_SERVER_NAME")
    )
    temporal_tls_client_cert_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_CLIENT_CERT")
    )
    temporal_tls_client_key_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_CLIENT_KEY")
    )
    temporal_tls_server_ca_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_SERVER_CA")
    )
    temporal_api_key: str | None = Field(default_factory=lambda: os.getenv("TEMPORAL_API_KEY"))
    temporal_api_key_header: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_API_KEY_HEADER", "authorization")
    )
    temporal_retry_initial_interval_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TEMPORAL_RETRY_INITIAL", "1.0"))
    )

    # API Configuration (from ontologia.toml)
    api_host: str = Field(default_factory=lambda: _CONFIG.api.host)
    api_port: int = Field(default_factory=lambda: _CONFIG.api.port)
    api_ontology: str = Field(default_factory=lambda: _CONFIG.api.ontology)

    # SDK Configuration
    sdk_output_dir: str | None = Field(
        default_factory=lambda: _config_section_attr("sdk", "output_dir", None)
    )
    sdk_auto_generate_on_apply: bool = Field(
        default_factory=lambda: _config_section_attr("sdk", "auto_generate_on_apply", default=False)
    )

    # Service Ports (from ontologia.toml)
    postgres_port: int | None = Field(
        default_factory=lambda: _config_section_attr("services", "postgres_port", None)
    )
    temporal_port: int | None = Field(
        default_factory=lambda: _config_section_attr("services", "temporal_port", None)
    )
    temporal_web_port: int | None = Field(
        default_factory=lambda: _config_section_attr("services", "temporal_web_port", None)
    )
    temporal_retry_max_interval_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TEMPORAL_RETRY_MAX", "60.0"))
    )
    temporal_retry_max_attempts: int = Field(
        default_factory=lambda: int(os.getenv("TEMPORAL_RETRY_ATTEMPTS", "0"))
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )


def _create_settings() -> Settings:
    """Create a new Settings instance."""
    return Settings()


# The actual get_settings function (cached) that tests can clear


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the current settings instance (cached)."""
    return _create_settings()


def clear_settings_cache() -> None:
    """Clear the settings cache (used in tests)."""
    try:
        get_settings.cache_clear()
    except Exception:
        # Ignore if cache is not present
        pass
