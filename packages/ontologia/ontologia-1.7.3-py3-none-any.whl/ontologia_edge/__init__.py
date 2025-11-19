"""Edge node management utilities for Ontologia distributed architecture."""

# Expose submodules to support test-time monkeypatching like
# `ontologia_edge.decision.httpx.AsyncClient`.
from . import decision as decision  # noqa: F401
from .decision import (
    ActionSink,
    Condition,
    DecisionAction,
    DecisionAuditLog,
    DecisionConfig,
    DecisionEngine,
    DecisionResult,
    DecisionRule,
    DecisionService,
    DecisionSimulator,
    InMemoryActionSink,
    JsonlActionSink,
    JsonlDecisionAuditLog,
    LoggingActionSink,
    load_rules_from_file,
)
from .enrichment import RealTimeEnricher
from .entity_manager import EntityManager, EntitySnapshot
from .journal import EntityEvent, EntityJournal, InMemoryEntityJournal, JsonlEntityJournal
from .providers.ogm import OGMContextProvider
from .replication import EntityReplicator, ReplicationConfig, ReplicationPeer, TLSConfig
from .runtime import RealTimeRuntime, RealTimeRuntimeConfig
from .schema import SchemaRegistry
from .server import RealTimeServerConfig, serve
from .storage import SQLiteEntityStore

__all__ = [
    "EntityManager",
    "EntitySnapshot",
    "EntityEvent",
    "EntityJournal",
    "InMemoryEntityJournal",
    "JsonlEntityJournal",
    "ActionSink",
    "Condition",
    "DecisionAction",
    "DecisionAuditLog",
    "DecisionConfig",
    "DecisionEngine",
    "DecisionResult",
    "DecisionRule",
    "DecisionService",
    "DecisionSimulator",
    "InMemoryActionSink",
    "JsonlActionSink",
    "JsonlDecisionAuditLog",
    "LoggingActionSink",
    "load_rules_from_file",
    "EntityReplicator",
    "ReplicationConfig",
    "ReplicationPeer",
    "TLSConfig",
    "SchemaRegistry",
    "RealTimeServerConfig",
    "RealTimeRuntime",
    "RealTimeRuntimeConfig",
    "SQLiteEntityStore",
    "RealTimeEnricher",
    "OGMContextProvider",
    "serve",
]
