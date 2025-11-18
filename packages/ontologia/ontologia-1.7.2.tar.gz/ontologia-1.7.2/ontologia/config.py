from __future__ import annotations

import logging
import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProjectConfig(BaseModel):
    name: str = "ontologia-core"
    version: str = "1.0.0"
    # Default directory where ontology YAML definitions live (used by CLI)
    definitions_dir: str = "definitions"


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    ontology: str = "default"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class DataConfig(BaseModel):
    # Core only needs basic data config
    database_url: str = "sqlite:///./ontologia.db"
    duckdb_path: str | None = None
    kuzu_path: str | None = None


class FeaturesConfig(BaseModel):
    # Core features - simplified
    use_sql_persistence: bool = True
    use_graph_writes: bool = False
    use_unified_graph: bool = True
    enable_vector_embeddings: bool = True
    enable_search_indexing: bool = True


class EventBusKafkaConfig(BaseModel):
    bootstrap_servers: list[str] = Field(default_factory=lambda: ["localhost:9092"])
    topic_prefix: str = "ontologia"
    client_id: str | None = None
    security_protocol: str | None = None
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: str | None = None


class EventBusConfig(BaseModel):
    provider: str = "in_process"
    synchronous_publish: bool = False
    kafka: EventBusKafkaConfig = Field(default_factory=EventBusKafkaConfig)


class SdkConfig(BaseModel):
    """Configuration for SDK components."""

    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True
    cache_ttl: int = 3600
    # Default output directory for generated SDK (used by CLI)
    output_dir: str = "sdk"


class ServicesConfig(BaseModel):
    """Configuration for various services."""

    enable_analytics: bool = True
    enable_sync: bool = True
    enable_data_catalog: bool = True
    max_concurrent_operations: int = 10


class VectorStoreConfig(BaseModel):
    """Configuration for vector storage backend."""

    provider: str = "elasticsearch"
    address: str = "http://localhost:9200"
    embedding_dimensions: int = 1536
    similarity_metric: str = "cosine"
    index_name: str = "ontologia_vectors"


class OntologiaConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    event_bus: EventBusConfig = Field(default_factory=EventBusConfig)
    sdk: SdkConfig = Field(default_factory=SdkConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)


def _load_raw_config(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError:
        return {}


@lru_cache
def load_config(base_path: Path | None = None) -> OntologiaConfig:
    root = base_path or Path.cwd()
    path = root / "ontologia.toml"
    raw = _load_raw_config(path)
    try:
        return OntologiaConfig.model_validate(raw)
    except Exception as exc:
        logging.warning("Failed to load config from %s: %s - using defaults", path, exc)
        return OntologiaConfig()


def _config_root() -> Path:
    root_env = os.getenv("ONTOLOGIA_CONFIG_ROOT")
    if root_env:
        try:
            return Path(root_env).resolve()
        except OSError:
            return Path(root_env)
    return Path.cwd()


def use_sql_persistence_enabled() -> bool:
    """Check if SQL persistence is enabled (always true for core)."""
    return True


def use_graph_writes_enabled() -> bool:
    """Check if graph writes are enabled. Defaults to False unless env or config enables."""
    env_override = os.getenv("USE_GRAPH_WRITES")
    if env_override is not None:
        return env_override in ("1", "true", "True")
    config = load_config(_config_root())
    return bool(config.features.use_graph_writes)


def use_unified_graph_enabled() -> bool:
    """Check if unified graph mode is enabled. Always true for core."""
    return True
