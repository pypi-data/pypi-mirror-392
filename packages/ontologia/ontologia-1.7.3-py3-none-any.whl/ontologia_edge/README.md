# Ontologia Edge - Edge Node Management for Distributed Architecture

## Overview

The `ontologia_edge` package provides edge node management capabilities for the Ontologia distributed framework. Built on the EdgeNode philosophy of autonomous semantic agents, this package enables secure, event-driven communication between edge devices and the core ontology system, supporting cryptographic identity, mesh networking, and graduated autonomy levels (L0/L1/L2).

## Installation

```bash
# Install the realtime package
pip install ontologia-realtime

# Install with all dependencies
pip install ontologia-realtime[full]

# Install with specific features
pip install ontologia-realtime[grpc,redis,analytics]
```

## Quick Start

### Server Setup

```python
from ontologia_edge import serve, RealTimeServerConfig
import asyncio

async def main():
    config = RealTimeServerConfig(
        host="localhost",
        port=50051,
        storage_backend="sqlite",
        storage_path="data/realtime.db"
    )

    await serve(config)

if __name__ == "__main__":
    asyncio.run(main())
```

### Client Usage

```python
from ontologia_edge import EntityManager, EntitySnapshot
import asyncio

async def main():
    # Connect to realtime server
    manager = EntityManager("localhost:50051")

    # Create entity
    person = await manager.create_entity(
        object_type="Person",
        data={
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
    )

    # Get entity snapshot
    snapshot = await manager.get_entity(person.id)
    print(f"Entity: {snapshot.data}")

    # Subscribe to changes
    async for change in manager.watch_entity(person.id):
        print(f"Entity changed: {change}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Architecture

The realtime package is built around several key components:

```
ontologia_edge/
├── entity_manager/    # Core entity management
├── journal/          # Event journaling and storage
├── decision/         # Decision engine and rules
├── enrichment/       # Data enrichment services
├── replication/      # Multi-node replication
├── runtime/          # Runtime orchestration
├── schema/           # Schema registry and validation
├── server/           # gRPC server implementation
└── storage/          # Storage backends
```

## Entity Management

### EntityManager

The core component for entity lifecycle management:

```python
from ontologia_edge import EntityManager, EntitySnapshot

# Initialize manager
manager = EntityManager("localhost:50051")

# Create entity
entity = await manager.create_entity(
    object_type="Person",
    data={
        "name": "Alice Smith",
        "email": "alice@example.com",
        "department": "Engineering"
    },
    metadata={
        "source": "hr_system",
        "confidence": 0.95
    }
)

# Update entity
updated = await manager.update_entity(
    entity.id,
    data={"age": 31, "level": "Senior"},
    metadata={"updated_by": "manager"}
)

# Get current state
snapshot = await manager.get_entity(entity.id)
print(f"Current state: {snapshot.data}")

# Delete entity
await manager.delete_entity(entity.id, reason="employee_left")
```

### Entity Queries

```python
# Query entities with filters
results = await manager.query_entities(
    object_type="Person",
    filters={
        "department": "Engineering",
        "age": {"gte": 25}
    },
    limit=10,
    sort="name:asc"
)

# Full-text search
search_results = await manager.search_entities(
    query="software engineer with Python experience",
    object_types=["Person"],
    limit=5
)

# Aggregated queries
stats = await manager.aggregate_entities(
    object_type="Person",
    group_by=["department"],
    metrics=["count", "avg_age"]
)
```

## Event Journaling

### EntityJournal

Comprehensive event tracking and history:

```python
from ontologia_edge import EntityJournal, EntityEvent

# Create journal
journal = EntityJournal(storage_backend="sqlite", db_path="events.db")

# Record events
event = EntityEvent(
    entity_id="person_123",
    event_type="updated",
    data={"age": 31},
    metadata={"source": "hr_update", "timestamp": "2024-01-01T12:00:00Z"}
)

await journal.append(event)

# Query event history
events = await journal.get_events(
    entity_id="person_123",
    from_time="2024-01-01T00:00:00Z",
    to_time="2024-01-02T00:00:00Z"
)

# Get entity state at specific time
snapshot = await journal.get_state_at_time(
    entity_id="person_123",
    timestamp="2024-01-01T15:30:00Z"
)
```

### Journal Storage Backends

```python
# SQLite backend (default)
sqlite_journal = EntityJournal(
    storage_backend="sqlite",
    db_path="data/events.db"
)

# Redis backend for high performance
redis_journal = EntityJournal(
    storage_backend="redis",
    redis_url="redis://localhost:6379",
    ttl_seconds=86400  # 24 hours
)

# PostgreSQL backend for persistence
postgres_journal = EntityJournal(
    storage_backend="postgresql",
    connection_string="postgresql://user:pass@localhost/ontologia"
)
```

## Decision Engine

### Rule-based Decision Making

```python
from ontologia_edge import DecisionEngine, DecisionRule, DecisionConfig

# Create decision engine
engine = DecisionEngine()

# Define rules
rule = DecisionRule(
    name="promote_engineer",
    condition=lambda entity: (
        entity.object_type == "Person" and
        entity.data.get("department") == "Engineering" and
        entity.data.get("experience_years", 0) >= 5
    ),
    action=lambda entity: {
        "type": "update",
        "data": {"level": "Senior"},
        "reason": "Experience-based promotion"
    }
)

engine.add_rule(rule)

# Process entity
decisions = await engine.process_entity(entity_snapshot)
for decision in decisions:
    print(f"Decision: {decision.action}")
    await decision.execute()
```

### Complex Decision Logic

```python
from ontologia_edge import Condition, DecisionAction

# Multi-condition rules
complex_rule = DecisionRule(
    name="customer_segment_assignment",
    condition=Condition.all([
        Condition.field_equals("type", "customer"),
        Condition.field_greater_than("total_orders", 10),
        Condition.field_greater_than("total_value", 1000)
    ]),
    action=DecisionAction.update_fields({
        "segment": "premium",
        "benefits": ["free_shipping", "priority_support"]
    })
)

# Time-based rules
time_rule = DecisionRule(
    name="inactive_customer",
    condition=Condition.field_older_than("last_order_date", days=90),
    action=DecisionAction.trigger_workflow("reactivation_campaign")
)
```

### Decision Simulation

```python
from ontologia_edge import DecisionSimulator

# Simulate decisions without executing
simulator = DecisionSimulator(engine)

results = await simulator.simulate(entity_snapshot)
for result in results:
    print(f"Would execute: {result.decision.action}")
    print(f"Expected impact: {result.impact}")
```

## Data Enrichment

### RealTimeEnricher

Automatic data enrichment and enhancement:

```python
from ontologia_edge import RealTimeEnricher, EnrichmentRule

# Create enricher
enricher = RealTimeEnricher()

# Add enrichment rules
geo_rule = EnrichmentRule(
    name="geocode_location",
    condition=lambda entity: "address" in entity.data,
    enricher=lambda entity: {
        "coordinates": geocode_address(entity.data["address"]),
        "timezone": get_timezone(entity.data["address"])
    }
)

enricher.add_rule(geo_rule)

# Enrich entity
enriched = await enricher.enrich(entity_snapshot)
print(f"Enriched data: {enriched.data}")
```

### External Data Integration

```python
# API-based enrichment
api_rule = EnrichmentRule(
    name="enrich_company_data",
    condition=lambda entity: entity.object_type == "Company",
    enricher=lambda entity: fetch_company_info(entity.data.get("name"))
)

# Database-based enrichment
db_rule = EnrichmentRule(
    name="enrich_customer_history",
    condition=lambda entity: entity.object_type == "Customer",
    enricher=lambda entity: query_purchase_history(entity.id)
)
```

## Replication and Clustering

### Multi-node Replication

```python
from ontologia_edge import EntityReplicator, ReplicationConfig, ReplicationPeer

# Configure replication
config = ReplicationConfig(
    mode="active-active",
    consistency_level="eventual",
    conflict_resolution="last_writer_wins"
)

# Define peers
peers = [
    ReplicationPeer(
        id="node1",
        address="node1.example.com:50051",
        tls_config=TLSConfig(
            cert_file="certs/node1.crt",
            key_file="certs/node1.key"
        )
    ),
    ReplicationPeer(
        id="node2",
        address="node2.example.com:50051",
        tls_config=TLSConfig(
            cert_file="certs/node2.crt",
            key_file="certs/node2.key"
        )
    )
)

# Create replicator
replicator = EntityReplicator(config=config, peers=peers)

# Start replication
await replicator.start()

# Replicate entity
await replicator.replicate_entity(entity_snapshot)
```

### Conflict Resolution

```python
from ontologia_edge import ConflictResolver

# Custom conflict resolution
class BusinessRuleResolver(ConflictResolver):
    async def resolve_conflict(self, entity_id, conflicting_versions):
        # Apply business logic to resolve conflicts
        latest = max(conflicting_versions, key=lambda v: v.timestamp)

        # Merge specific fields
        merged = latest.data.copy()
        for version in conflicting_versions:
            if version.metadata.get("priority") == "high":
                merged.update(version.data)

        return merged

replicator.set_conflict_resolver(BusinessRuleResolver())
```

## Runtime and Orchestration

### RealTimeRuntime

Orchestrate all realtime components:

```python
from ontologia_edge import RealTimeRuntime, RealTimeRuntimeConfig

# Configure runtime
config = RealTimeRuntimeConfig(
    entity_manager_config={
        "storage_backend": "sqlite",
        "db_path": "data/entities.db"
    },
    journal_config={
        "storage_backend": "redis",
        "redis_url": "redis://localhost:6379"
    },
    decision_engine_config={
        "rules_file": "config/decision_rules.yaml"
    },
    replication_config={
        "enabled": True,
        "peers": ["node1:50051", "node2:50051"]
    }
)

# Create and start runtime
runtime = RealTimeRuntime(config)
await runtime.start()

# Get components
entity_manager = runtime.get_entity_manager()
decision_engine = runtime.get_decision_engine()
journal = runtime.get_journal()
```

### Health Monitoring

```python
# Health checks
health_status = await runtime.health_check()
print(f"Runtime healthy: {health_status.healthy}")
print(f"Components: {health_status.components}")

# Metrics
metrics = await runtime.get_metrics()
print(f"Entities processed: {metrics.entities_processed}")
print(f"Decisions made: {metrics.decisions_made}")
print(f"Events journaled: {metrics.events_journaled}")
```

## Schema Management

### SchemaRegistry

Dynamic schema management and validation:

```python
from ontologia_edge import SchemaRegistry, SchemaDefinition

# Create registry
registry = SchemaRegistry()

# Register schema
person_schema = SchemaDefinition(
    object_type="Person",
    properties={
        "name": {"type": "string", "required": True},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0}
    },
    indexes=["name", "email"]
)

await registry.register_schema(person_schema)

# Validate entity
validation_result = await registry.validate_entity(entity_snapshot)
if not validation_result.valid:
    print(f"Validation errors: {validation_result.errors}")
```

### Schema Evolution

```python
# Evolve schema
evolution = await registry.evolve_schema(
    object_type="Person",
    changes={
        "add_properties": [
            {"name": "phone", "type": "string"},
            {"name": "department", "type": "string"}
        ],
        "remove_properties": ["temp_field"]
    }
)

# Apply evolution to existing entities
migration_result = await registry.migrate_entities(
    object_type="Person",
    evolution=evolution
)
```

## gRPC Server

### Server Configuration

```python
from ontologia_edge import serve, RealTimeServerConfig, TLSConfig

# Basic server
config = RealTimeServerConfig(
    host="localhost",
    port=50051,
    max_workers=10,
    storage_backend="sqlite"
)

# Server with TLS
tls_config = TLSConfig(
    cert_file="certs/server.crt",
    key_file="certs/server.key",
    ca_file="certs/ca.crt"
)

config = RealTimeServerConfig(
    host="0.0.0.0",
    port=50051,
    tls_config=tls_config,
    enable_auth=True
)

await serve(config)
```

### Client Connections

```python
from ontologia_edge import EntityManager

# Insecure connection
manager = EntityManager("localhost:50051")

# Secure connection
manager = EntityManager(
    address="secure.example.com:50051",
    tls_config=TLSConfig(
        cert_file="certs/client.crt",
        key_file="certs/client.key",
        ca_file="certs/ca.crt"
    )
)

# Connection with authentication
manager = EntityManager(
    address="secure.example.com:50051",
    auth_token="your-jwt-token"
)
```

## Performance Optimization

### Caching Strategies

```python
from ontologia_edge import CachedEntityManager

# Entity caching
cached_manager = CachedEntityManager(
    base_manager=EntityManager("localhost:50051"),
    cache_size=10000,
    ttl_seconds=300
)

# Query result caching
cached_manager.enable_query_cache(
    max_size=1000,
    ttl_seconds=60
)
```

### Batch Operations

```python
# Batch entity creation
entities = [
    {"name": f"Person_{i}", "age": 20 + i}
    for i in range(100)
]

results = await manager.batch_create_entities(
    object_type="Person",
    entities=entities,
    batch_size=10
)

# Batch updates
updates = [
    {"id": f"person_{i}", "age": 25 + i}
    for i in range(50)
]

await manager.batch_update_entities(updates)
```

### Connection Pooling

```python
from ontologia_edge import PooledEntityManager

pooled_manager = PooledEntityManager(
    address="localhost:50051",
    pool_size=20,
    max_overflow=10
)
```

## Monitoring and Observability

### Metrics Collection

```python
from ontologia_edge.monitoring import MetricsCollector

# Enable metrics
metrics = MetricsCollector(
    collect_entity_metrics=True,
    collect_decision_metrics=True,
    collect_performance_metrics=True
)

runtime.add_metrics_collector(metrics)

# Get metrics
current_metrics = await metrics.get_current_metrics()
print(f"Entity operations: {current_metrics.entity_operations}")
print(f"Decision latency: {current_metrics.decision_latency_ms}ms")
```

### Distributed Tracing

```python
from ontologia_edge.tracing import TracingConfig

# Enable tracing
tracing_config = TracingConfig(
    jaeger_endpoint="http://localhost:14268/api/traces",
    service_name="ontologia-realtime",
    sample_rate=0.1
)

config = RealTimeServerConfig(
    tracing_config=tracing_config
)
```

### Health Checks

```python
# Component health checks
health = await runtime.health_check()
for component, status in health.components.items():
    print(f"{component}: {'healthy' if status.healthy else 'unhealthy'}")
    if not status.healthy:
        print(f"  Issues: {status.issues}")
```

## Testing

### Unit Testing

```python
from ontologia_edge.testing import MockEntityManager, MockJournal

def test_entity_creation():
    # Setup mock manager
    mock_manager = MockEntityManager()

    # Test entity creation
    entity = await mock_manager.create_entity(
        object_type="Person",
        data={"name": "Test Person"}
    )

    assert entity.object_type == "Person"
    assert entity.data["name"] == "Test Person"
```

### Integration Testing

```python
from ontologia_edge.testing import TestRuntime

async def test_full_workflow():
    # Create test runtime
    async with TestRuntime() as runtime:
        manager = runtime.get_entity_manager()

        # Create entity
        entity = await manager.create_entity(
            object_type="Person",
            data={"name": "Test User"}
        )

        # Update entity
        await manager.update_entity(
            entity.id,
            data={"age": 30}
        )

        # Verify journal
        journal = runtime.get_journal()
        events = await journal.get_events(entity.id)
        assert len(events) == 2  # create + update
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 50051

CMD ["python", "-m", "ontologia_edge.server", "--host", "0.0.0.0", "--port", "50051"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ontologia-realtime
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ontologia-realtime
  template:
    metadata:
      labels:
        app: ontologia-realtime
    spec:
      containers:
      - name: realtime-server
        image: ontologia-realtime:latest
        ports:
        - containerPort: 50051
        env:
        - name: STORAGE_BACKEND
          value: "postgresql"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## Dependencies

Core dependencies:
- **grpcio**: gRPC framework
- **grpcio-tools**: gRPC tools and protoc
- **protobuf**: Protocol buffers
- **asyncio**: Async programming support

Optional dependencies:
- **redis**: Redis storage backend
- **psycopg2**: PostgreSQL storage backend
- **prometheus-client**: Metrics collection
- **jaeger-client**: Distributed tracing
- **pydantic**: Data validation

## Version Information

Current version: `0.1.0`

Compatible with gRPC 1.50+ and Python 3.8+.

## Contributing

When contributing to the realtime package:
1. Ensure thread safety and async correctness
2. Include comprehensive error handling
3. Add performance benchmarks for new features
4. Write tests for all components
5. Document configuration options and trade-offs

## License

This package is part of the Ontologia framework and follows the same license terms.
