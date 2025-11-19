# Enterprise Workflows Template

The complete enterprise stack with all features enabled. This template includes search capabilities, workflow orchestration, real-time updates, and full analytics for production-grade applications.

## 🎯 What You Get

- ✅ **Elasticsearch** for advanced search
- ✅ **Temporal** for durable workflow execution
- ✅ **Redis** for real-time updates and caching
- ✅ **Dagster** for pipeline orchestration
- ✅ **DuckDB** for analytics
- ✅ **KùzuDB** for graph traversals
- ✅ **PostgreSQL** for transactional data
- ✅ **Complete monitoring** and observability

## 🚀 Quick Start

### 1. Create Project
```bash
ontologia init --template enterprise-workflows my-enterprise
cd my-enterprise
```

### 2. Start Services
```bash
# Start complete enterprise stack
docker-compose -f docker-compose.full.yml up -d

# Wait for all services to be ready (this may take a few minutes)
docker-compose logs -f
```

### 3. Access Enterprise Tools
- **API**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200
- **Temporal UI**: http://localhost:7233
- **Dagster UI**: http://localhost:3000
- **Redis Commander**: http://localhost:8081
- **Kibana**: http://localhost:5601

## 📁 Project Structure

```
my-enterprise/
├── README.md              # This file
├── pyproject.toml         # Full enterprise dependencies
├── docker-compose.yml     # Core services
├── docker-compose.full.yml  # Complete stack
├── .env.example          # Full environment configuration
├── workflows/            # Temporal workflow definitions
│   ├── __init__.py
│   ├── activities.py
│   └── workflows.py
├── search/               # Elasticsearch configuration
│   ├── mappings/
│   └── queries/
├── realtime/             # Real-time event handlers
│   ├── __init__.py
│   └── handlers.py
├── monitoring/           # Monitoring and observability
│   ├── prometheus.yml
│   └── grafana/
└── examples/             # Enterprise examples
    ├── workflow_orchestration.py
    ├── advanced_search.py
    ├── realtime_updates.py
    └── enterprise_analytics.py
```

## 🛠️ Development

### Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Install all enterprise dependencies
pip install ontologia[full]

# Enable all features
export STORAGE_MODE=sql_kuzu
export ENABLE_SEARCH=true
export ENABLE_WORKFLOWS=true
export ENABLE_REALTIME=true
export ENABLE_ORCHESTRATION=true

# Configure external services
export ELASTICSEARCH_HOSTS=localhost:9200
export TEMPORAL_ADDRESS=127.0.0.1:7233
export REDIS_URL=redis://localhost:6379

# Start in development mode
uv run uvicorn ontologia_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Service Startup Order
```bash
# 1. Start infrastructure services
docker-compose up -d postgres elasticsearch redis temporal kuzu

# 2. Wait for services to be ready
./scripts/wait-for-services.sh

# 3. Start application services
docker-compose up -d api dagster-webserver

# 4. Start workers and processors
docker-compose up -d temporal-worker dagster-worker
```

## 🔍 Enterprise Search

### Elasticsearch Configuration
```python
# Search schema configuration
from ontologia_api.v2.schemas.search import SearchConfig

search_config = SearchConfig(
    index_name="ontologia_enterprise",
    mappings={
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text", "analyzer": "english"},
            "tags": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "object_type": {"type": "keyword"},
            "properties": {
                "type": "object",
                "dynamic": True
            }
        }
    }
)
```

### Advanced Search Examples
```python
from ontologia_sdk.client import OntologyClient

client = OntologyClient("http://localhost:8000")

# Full-text search with highlighting
search_results = client.search({
    "query": {
        "multi_match": {
            "query": "python developer",
            "fields": ["title", "content", "properties.name^2"],
            "type": "best_fields",
            "fuzziness": "AUTO"
        }
    },
    "highlight": {
        "fields": {
            "content": {},
            "properties.name": {}
        }
    },
    "filter": [
        {"term": {"object_type": "employee"}},
        {"range": {"created_at": {"gte": "now-30d"}}}
    ],
    "sort": [{"updated_at": {"order": "desc"}}],
    "size": 20
})

# Aggregated search for analytics
aggregated_search = client.search({
    "query": {"match_all": {}},
    "aggs": {
        "departments": {
            "terms": {"field": "properties.department.keyword"}
        },
        "skills": {
            "terms": {"field": "properties.skills.keyword"}
        },
        "salary_ranges": {
            "range": {
                "field": "properties.salary",
                "ranges": [
                    {"key": "0-50k", "to": 50000},
                    {"key": "50k-100k", "from": 50000, "to": 100000},
                    {"key": "100k+", "from": 100000}
                ]
            }
        }
    }
})
```

## ⚙️ Workflow Orchestration

### Temporal Workflow Example
```python
from temporalio import workflow, activity
from datetime import timedelta

@activity.defn
async def create_employee_profile(employee_data: dict) -> str:
    """Create employee profile in multiple systems."""
    # Create in main database
    client = OntologyClient("http://localhost:8000")
    result = client.create_object("employee", employee_data["id"], {"properties": employee_data})

    # Index in Elasticsearch
    await index_in_search(employee_data)

    # Update graph database
    await update_graph_database(employee_data)

    # Send real-time notification
    await send_notification("employee_created", employee_data)

    return result["rid"]

@activity.defn
async def onboard_employee(employee_id: str) -> dict:
    """Complete employee onboarding process."""
    # Assign default projects
    await assign_default_projects(employee_id)

    # Set up access permissions
    await setup_permissions(employee_id)

    # Schedule training sessions
    await schedule_training(employee_id)

    # Send welcome emails
    await send_welcome_emails(employee_id)

    return {"status": "completed", "employee_id": employee_id}

@workflow.defn
class EmployeeOnboardingWorkflow:
    """Complete employee onboarding workflow."""

    @workflow.run
    async def run(self, employee_data: dict) -> dict:
        """Execute onboarding workflow."""
        try:
            # Step 1: Create employee profile
            employee_rid = await workflow.execute_activity(
                create_employee_profile,
                employee_data,
                start_to_close_timeout=timedelta(minutes=5)
            )

            # Step 2: Onboarding process (parallel activities)
            onboarding_result = await workflow.execute_activity(
                onboard_employee,
                employee_data["id"],
                start_to_close_timeout=timedelta(minutes=30)
            )

            # Step 3: Schedule follow-up tasks
            await workflow.execute_activity(
                schedule_follow_up,
                employee_data["id"],
                start_to_close_timeout=timedelta(minutes=5)
            )

            return {
                "workflow_id": workflow.info().workflow_id,
                "employee_rid": employee_rid,
                "status": "completed"
            }

        except Exception as e:
            # Handle failures and rollback
            await workflow.execute_activity(
                rollback_onboarding,
                employee_data["id"],
                start_to_close_timeout=timedelta(minutes=10)
            )
            raise e
```

### Workflow Management
```python
# Start workflow
from temporalio.client import Client

temporal_client = Client("localhost:7233")

workflow_id = await temporal_client.start_workflow(
    EmployeeOnboardingWorkflow.run,
    employee_data,
    id=f"onboarding-{employee_data['id']}",
    task_queue="employee-tasks"
)

# Monitor workflow
workflow_handle = temporal_client.get_workflow_handle(workflow_id)
result = await workflow_handle.result()

# Query workflow status
status = await workflow_handle.query("get_status")
```

## 📡 Real-time Updates

### Redis-based Event System
```python
import redis
import json
from typing import Dict, Any

class RealtimeEventHandler:
    """Handle real-time events using Redis pub/sub."""

    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()

    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish real-time event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }

        await self.redis_client.publish(f"ontologia:{event_type}", json.dumps(event))

        # Store in sorted set for recent events
        await self.redis_client.zadd(
            f"ontologia:events:{event_type}",
            {json.dumps(event): datetime.utcnow().timestamp()}
        )

    async def subscribe_to_events(self, event_types: list[str]):
        """Subscribe to specific event types."""
        channels = [f"ontologia:{event_type}" for event_type in event_types]
        await self.pubsub.subscribe(*channels)

    async def listen_for_events(self):
        """Listen for and process events."""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                await self.process_event(event)

    async def process_event(self, event: Dict[str, Any]):
        """Process incoming real-time event."""
        event_type = event['type']
        data = event['data']

        if event_type == "object_created":
            await self.handle_object_created(data)
        elif event_type == "object_updated":
            await self.handle_object_updated(data)
        elif event_type == "link_created":
            await self.handle_link_created(data)

    async def handle_object_created(self, data: Dict[str, Any]):
        """Handle object creation event."""
        # Update search index
        await self.update_search_index(data)

        # Invalidate relevant caches
        await self.invalidate_cache(f"object:{data['object_type']}:{data['pk']}")

        # Trigger workflows
        await self.trigger_workflows("object_created", data)

        # Send notifications
        await self.send_notifications("object_created", data)
```

### WebSocket Integration
```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.user_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)

        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user."""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
```

## 📊 Enterprise Analytics

### Comprehensive Analytics Pipeline
```python
from dagster import job, op, In, Out
import pandas as pd
import duckdb

@op
def extract_all_data() -> Dict[str, pd.DataFrame]:
    """Extract data from all sources."""
    # PostgreSQL data
    pg_data = extract_from_postgres()

    # Elasticsearch analytics
    es_data = extract_from_elasticsearch()

    # Graph analytics
    graph_data = extract_from_kuzu()

    # Real-time events
    realtime_data = extract_from_redis()

    return {
        "postgres": pg_data,
        "elasticsearch": es_data,
        "graph": graph_data,
        "realtime": realtime_data
    }

@op
def comprehensive_analytics(all_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate comprehensive analytics."""
    conn = duckdb.connect('./data/enterprise.duckdb')

    # Combine all data sources
    combined_data = combine_data_sources(all_data)

    # Generate insights
    insights = {
        "user_engagement": analyze_user_engagement(combined_data),
        "workflow_performance": analyze_workflow_performance(combined_data),
        "search_analytics": analyze_search_patterns(all_data["elasticsearch"]),
        "graph_insights": analyze_network_metrics(all_data["graph"]),
        "realtime_metrics": analyze_realtime_events(all_data["realtime"])
    }

    # Store results
    for key, value in insights.items():
        conn.execute(f"CREATE OR REPLACE TABLE {key} AS SELECT * FROM value")

    return insights

@job
def enterprise_analytics_job():
    """Complete enterprise analytics pipeline."""
    all_data = extract_all_data()
    insights = comprehensive_analytics(all_data)
    generate_executive_dashboard(insights)
    send_alerts(insights)
```

## 🔧 Configuration

### Complete Environment Variables
```bash
# Core Database
DATABASE_URL=postgresql://ontologia:ontologia123@localhost:5432/ontologia

# Graph Database
STORAGE_MODE=sql_kuzu
KUZU_PATH=./data/graph.kuzu

# Search Configuration
ENABLE_SEARCH=true
ELASTICSEARCH_HOSTS=localhost:9200
ELASTICSEARCH_INDEX=ontologia_enterprise

# Workflow Configuration
ENABLE_WORKFLOWS=true
TEMPORAL_ADDRESS=127.0.0.1:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=enterprise-tasks

# Real-time Configuration
ENABLE_REALTIME=true
REDIS_URL=redis://localhost:6379
REDIS_CHANNELS=ontologia:*

# Analytics Configuration
ENABLE_ORCHESTRATION=true
DUCKDB_PATH=./data/analytics.duckdb
DAGSTER_HOME=./dagster

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Performance
API_WORKERS=4
CACHE_TTL=3600
BATCH_SIZE=1000
```

## 🚀 Production Deployment

### Enterprise Docker Setup
```bash
# Production with all services
docker-compose -f docker-compose.prod.yml up -d

# Scale services for load
docker-compose -f docker-compose.prod.yml up -d \
  --scale api=4 \
  --scale temporal-worker=3 \
  --scale dagster-worker=2

# Enable monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### High Availability Configuration
```yaml
# docker-compose.ha.yml
version: '3.8'
services:
  postgres:
    deploy:
      replicas: 2
    environment:
      POSTGRES_REPLICATION_MODE: master

  elasticsearch:
    deploy:
      replicas: 3
    environment:
      cluster.name: ontologia-cluster
      discovery.seed_hosts: elasticsearch

  redis:
    deploy:
      replicas: 2
    command: redis-server --appendonly yes --cluster-enabled yes

  temporal:
    deploy:
      replicas: 2
    environment:
      TEMPORAL_HISTORY_MAX_PAGE_SIZE: 1000
```

## 📚 Learn More

- **Elasticsearch Documentation**: https://www.elastic.co/guide/
- **Temporal Documentation**: https://docs.temporal.io/
- **Redis Documentation**: https://redis.io/documentation
- **Dagster Documentation**: https://docs.dagster.io/
- **Enterprise Architecture Guide**: [../../docs/enterprise.md](../../docs/enterprise.md)

## 🎉 Success!

You now have a complete enterprise platform with:
- ✅ Multi-database architecture (PostgreSQL + KùzuDB + DuckDB)
- ✅ Advanced search with Elasticsearch
- ✅ Workflow orchestration with Temporal
- ✅ Real-time updates with Redis
- ✅ Pipeline orchestration with Dagster
- ✅ Comprehensive monitoring and observability
- ✅ High availability and scalability

Ready for enterprise production! 🚀
