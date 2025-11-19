# Ontologia MCP - Model Context Protocol Server

## Overview

The `ontologia_mcp` package provides a Model Context Protocol (MCP) server for the Ontologia framework, enabling AI assistants and language models to interact with ontology data through a standardized, secure interface. This server exposes Ontologia's capabilities as MCP tools, allowing AI agents to query, modify, and reason over structured knowledge graphs.

## Installation

```bash
# Install the MCP server
pip install ontologia-mcp

# Install with Claude Desktop support
pip install ontologia-mcp[claude]

# Install with all AI platform integrations
pip install ontologia-mcp[all]
```

## Quick Start

### Claude Desktop Integration

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "ontologia": {
      "command": "python",
      "args": ["-m", "ontologia_mcp.server"],
      "env": {
        "ONTOLOGIA_BASE_URL": "http://localhost:8000",
        "ONTOLOGIA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Standalone Server

```bash
# Start the MCP server
python -m ontologia_mcp.server --host localhost --port 8080

# Or with configuration file
python -m ontologia_mcp.server --config mcp_config.yaml
```

### Client Usage

```python
from mcp import ClientSession, StdioServerParameters
from ontologia_mcp import create_ontologia_session

# Create MCP session
async with create_ontologia_session(
    base_url="http://localhost:8000",
    api_key="your-api-key"
) as session:

    # List available tools
    tools = await session.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # Query ontology
    result = await session.call_tool("query_instances", {
        "object_type": "Person",
        "filters": {"age": {"gte": 18}}
    })

    print(f"Found {len(result.content)} adult persons")
```

## Core Architecture

The MCP server provides a bridge between AI models and the Ontologia framework:

```
ontologia_mcp/
├── server.py          # Main MCP server implementation
├── tools/             # MCP tool definitions
├── handlers/          # Request handlers and business logic
├── auth/              # Authentication and authorization
├── config.py          # Server configuration
├── middleware/        # Request/response middleware
└── utils/             # Helper functions
```

## Available Tools

### Ontology Query Tools

#### `query_instances`
Query ontology instances with filtering and pagination.

```python
# Tool call example
result = await session.call_tool("query_instances", {
    "object_type": "Person",
    "filters": {
        "age": {"gte": 18, "lte": 65},
        "department": "Engineering"
    },
    "limit": 50,
    "sort": [{"field": "name", "direction": "asc"}]
})
```

#### `get_instance`
Retrieve a specific instance by ID.

```python
result = await session.call_tool("get_instance", {
    "object_type": "Person",
    "instance_id": "person_123"
})
```

#### `search_instances`
Full-text search across instances.

```python
result = await session.call_tool("search_instances", {
    "query": "software engineer with Python experience",
    "object_types": ["Person"],
    "limit": 10
})
```

### Schema Management Tools

#### `list_object_types`
List all available object types.

```python
result = await session.call_tool("list_object_types", {})
```

#### `get_object_type`
Get detailed object type schema.

```python
result = await session.call_tool("get_object_type", {
    "object_type": "Person"
})
```

#### `validate_instance`
Validate instance data against schema.

```python
result = await session.call_tool("validate_instance", {
    "object_type": "Person",
    "data": {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }
})
```

### Relationship Tools

#### `query_relationships`
Query relationships between instances.

```python
result = await session.call_tool("query_relationships", {
    "link_type": "works_for",
    "source_type": "Person",
    "target_type": "Company",
    "filters": {
        "properties.start_date": {"gte": "2023-01-01"}
    }
})
```

#### `get_related_instances`
Find instances related to a specific instance.

```python
result = await session.call_tool("get_related_instances", {
    "instance_id": "person_123",
    "relationship_type": "works_for",
    "direction": "outgoing"
})
```

### Data Catalog Tools

#### `list_datasets`
List available datasets.

```python
result = await session.call_tool("list_datasets", {})
```

#### `get_dataset`
Get dataset schema and metadata.

```python
result = await session.call_tool("get_dataset", {
    "dataset_name": "customer_analytics"
})
```

#### `query_dataset`
Query dataset data.

```python
result = await session.call_tool("query_dataset", {
    "dataset_name": "customer_analytics",
    "branch": "main",
    "filters": {
        "segment": "premium",
        "created_date": {"gte": "2024-01-01"}
    }
})
```

### Action and Workflow Tools

#### `list_actions`
List available actions.

```python
result = await session.call_tool("list_actions", {})
```

#### `execute_action`
Execute a registered action.

```python
result = await session.call_tool("execute_action", {
    "action_name": "validate_customer_data",
    "parameters": {
        "dataset": "customer_analytics",
        "rules": ["email_format", "required_fields"]
    }
})
```

#### `get_workflow_status`
Check workflow execution status.

```python
result = await session.call_tool("get_workflow_status", {
    "workflow_id": "workflow_456"
})
```

## Configuration

### Server Configuration

```yaml
# mcp_config.yaml
server:
  host: localhost
  port: 8080
  log_level: INFO

ontologia:
  base_url: http://localhost:8000
  api_key: ${ONTOLOGIA_API_KEY}
  timeout: 30
  retry_attempts: 3

security:
  enable_auth: true
  allowed_origins: ["http://localhost:3000"]
  rate_limit:
    requests_per_minute: 100

features:
  enable_write_operations: true
  enable_workflow_execution: true
  max_query_results: 1000
  enable_caching: true
```

### Environment Configuration

```bash
# Environment variables
export ONTOLOGIA_BASE_URL=http://localhost:8000
export ONTOLOGIA_API_KEY=your-api-key
export MCP_SERVER_HOST=localhost
export MCP_SERVER_PORT=8080
export MCP_LOG_LEVEL=INFO
```

### Programmatic Configuration

```python
from ontologia_mcp import MCPServerConfig, create_server

config = MCPServerConfig(
    host="localhost",
    port=8080,
    ontologia_base_url="http://localhost:8000",
    ontologia_api_key="your-api-key",
    enable_write_operations=True,
    max_query_results=1000,
    rate_limit_requests_per_minute=100
)

server = create_server(config)
await server.start()
```

## Authentication and Security

### API Key Authentication

```python
from ontologia_mcp.auth import APIKeyAuth

auth = APIKeyAuth(
    api_key="your-api-key",
    header_name="X-API-Key"
)

server = create_server(config, auth=auth)
```

### JWT Authentication

```python
from ontologia_mcp.auth import JWTAuth

auth = JWTAuth(
    secret_key="your-secret-key",
    algorithm="HS256",
    token_expiry=3600
)
```

### Role-based Access Control

```python
from ontologia_mcp.auth import RBACAuth

# Define roles and permissions
rbac_config = {
    "roles": {
        "reader": {
            "permissions": ["read", "query"],
            "tools": ["query_instances", "get_instance", "search_instances"]
        },
        "writer": {
            "permissions": ["read", "write", "query"],
            "tools": ["*"]  # All tools
        },
        "admin": {
            "permissions": ["*"],
            "tools": ["*"]
        }
    },
    "default_role": "reader"
}

auth = RBACAuth(rbac_config)
```

## Middleware

### Request Logging

```python
from ontologia_mcp.middleware import LoggingMiddleware

middleware = LoggingMiddleware(
    log_requests=True,
    log_responses=True,
    include_body=False
)

server.add_middleware(middleware)
```

### Rate Limiting

```python
from ontologia_mcp.middleware import RateLimitMiddleware

middleware = RateLimitMiddleware(
    requests_per_minute=100,
    burst_size=20,
    key_func=lambda request: request.client_ip
)

server.add_middleware(middleware)
```

### Caching

```python
from ontologia_mcp.middleware import CacheMiddleware

middleware = CacheMiddleware(
    ttl_seconds=300,
    max_size=1000,
    cache_key_func=lambda tool, args: f"{tool.name}:{hash(str(args))}"
)

server.add_middleware(middleware)
```

## Custom Tools

### Creating Custom Tools

```python
from ontologia_mcp.tools import BaseTool, tool
from ontologia_sdk import OntologyClient

@tool(
    name="analyze_customer_churn",
    description="Analyze customer churn patterns",
    parameters={
        "time_period": {"type": "string", "description": "Analysis period"},
        "segment": {"type": "string", "description": "Customer segment"}
    }
)
class AnalyzeChurnTool(BaseTool):
    def __init__(self, ontologia_client: OntologyClient):
        self.client = ontologia_client

    async def execute(self, **kwargs):
        time_period = kwargs["time_period"]
        segment = kwargs["segment"]

        # Query customer data
        customers = await self.client.query_instances({
            "object_type": "Customer",
            "filters": {
                "segment": segment,
                "last_activity": {"gte": time_period}
            }
        })

        # Analyze churn patterns
        churn_rate = self.calculate_churn_rate(customers)

        return {
            "segment": segment,
            "time_period": time_period,
            "churn_rate": churn_rate,
            "total_customers": len(customers),
            "recommendations": self.generate_recommendations(churn_rate)
        }

    def calculate_churn_rate(self, customers):
        # Implementation
        pass

    def generate_recommendations(self, churn_rate):
        # Implementation
        pass

# Register custom tool
server.register_tool(AnalyzeChurnTool(ontologia_client))
```

### Tool Composition

```python
from ontologia_mcp.tools import CompositeTool

@tool(name="customer_360_analysis")
class Customer360Tool(CompositeTool):
    """Composite tool for comprehensive customer analysis."""

    def __init__(self, ontologia_client: OntologyClient):
        super().__init__([
            AnalyzeChurnTool(ontologia_client),
            AnalyzeSatisfactionTool(ontologia_client),
            PredictLifetimeValueTool(ontologia_client)
        ])

    async def execute(self, customer_id: str):
        # Execute sub-tools and combine results
        results = {}
        for sub_tool in self.sub_tools:
            result = await sub_tool.execute(customer_id=customer_id)
            results[sub_tool.name] = result

        return self.combine_results(results)
```

## AI Platform Integrations

### Claude Desktop

```json
{
  "mcpServers": {
    "ontologia": {
      "command": "python",
      "args": ["-m", "ontologia_mcp.server"],
      "env": {
        "ONTOLOGIA_BASE_URL": "http://localhost:8000",
        "ONTOLOGIA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### OpenAI Function Calling

```python
from ontologia_mcp.integrations import OpenAIIntegration

# Create OpenAI integration
integration = OpenAIIntegration(
    mcp_server_url="http://localhost:8080",
    api_key="your-openai-key"
)

# Use with OpenAI client
import openai

response = await openai.ChatCompletion.acreate(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Find all software engineers in the Engineering department"}
    ],
    functions=integration.get_functions()
)

# Execute function calls
if response.choices[0].message.function_call:
    result = await integration.execute_function_call(
        response.choices[0].message.function_call
    )
```

### LangChain Integration

```python
from ontologia_mcp.integrations import LangChainOntologiaTool

# Create LangChain tool
tool = LangChainOntologiaTool(
    mcp_server_url="http://localhost:8080",
    tool_name="query_instances"
)

# Use in LangChain agent
from langchain.agents import initialize_agent, ToolType

tools = [tool]
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

result = agent.run("Find all customers who placed orders in the last 30 days")
```

## Testing

### Unit Testing

```python
from ontologia_mcp.testing import MockMCPServer, MockOntologiaClient

def test_query_instances_tool():
    # Setup mock client
    mock_client = MockOntologiaClient()
    mock_client.add_instances("Person", [
        {"id": "1", "name": "Alice", "age": 30},
        {"id": "2", "name": "Bob", "age": 25}
    ])

    # Create server with mock client
    server = MockMCPServer(ontologia_client=mock_client)

    # Test tool execution
    result = await server.call_tool("query_instances", {
        "object_type": "Person",
        "filters": {"age": {"gte": 25}}
    })

    assert len(result.content) == 2
    assert all(person["age"] >= 25 for person in result.content)
```

### Integration Testing

```python
from ontologia_mcp.testing import IntegrationTestServer

async def test_full_workflow():
    # Start test server
    async with IntegrationTestServer() as server:
        # Create test data
        await server.setup_test_data()

        # Execute workflow
        result = await server.call_tool("execute_action", {
            "action_name": "customer_analysis",
            "parameters": {"segment": "premium"}
        })

        # Verify results
        assert result.success
        assert "analysis_results" in result.data
```

## Performance Optimization

### Connection Pooling

```python
from ontologia_mcp.performance import PooledOntologiaClient

client = PooledOntologiaClient(
    base_url="http://localhost:8000",
    pool_size=20,
    max_overflow=10
)

server = create_server(config, ontologia_client=client)
```

### Response Caching

```python
from ontologia_mcp.performance import ResponseCache

cache = ResponseCache(
    ttl_seconds=300,
    max_size=1000,
    cache_strategy="lru"
)

server.add_middleware(cache)
```

### Batch Processing

```python
from ontologia_mcp.tools import BatchQueryTool

# Tool for batch queries
batch_tool = BatchQueryTool(
    ontologia_client=client,
    max_batch_size=100,
    timeout_seconds=60
)

server.register_tool(batch_tool)
```

## Monitoring and Observability

### Metrics Collection

```python
from ontologia_mcp.monitoring import MetricsCollector

metrics = MetricsCollector(
    collect_request_count=True,
    collect_response_time=True,
    collect_error_rate=True
)

server.add_middleware(metrics)
```

### Health Checks

```python
from ontologia_mcp.health import HealthCheckServer

health_server = HealthCheckServer(
    mcp_server=server,
    checks=[
        "ontolia_connection",
        "database_health",
        "memory_usage"
    ]
)

# Health endpoint available at /health
```

### Distributed Tracing

```python
from ontologia_mcp.tracing import TracingMiddleware

tracing = TracingMiddleware(
    service_name="ontologia-mcp",
    jaeger_endpoint="http://localhost:14268/api/traces"
)

server.add_middleware(tracing)
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "ontologia_mcp.server", "--host", "0.0.0.0", "--port", "8080"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ontologia-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ontologia-mcp
  template:
    metadata:
      labels:
        app: ontologia-mcp
    spec:
      containers:
      - name: mcp-server
        image: ontologia-mcp:latest
        ports:
        - containerPort: 8080
        env:
        - name: ONTOLOGIA_BASE_URL
          value: "http://ontologia-service:8000"
        - name: ONTOLOGIA_API_KEY
          valueFrom:
            secretKeyRef:
              name: ontologia-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Dependencies

Core dependencies:
- **mcp**: Model Context Protocol implementation
- **ontologia-sdk**: Ontologia client library
- **fastapi**: Web framework for HTTP transport
- **pydantic**: Data validation

Optional dependencies:
- **claude-desktop**: Claude Desktop integration
- **openai**: OpenAI API integration
- **langchain**: LangChain framework integration
- **prometheus-client**: Metrics collection
- **jaeger-client**: Distributed tracing

## Version Information

Current version: `0.1.0`

Compatible with MCP specification 1.0 and Ontologia >= 0.1.0.

## Contributing

When contributing to the MCP server:
1. Follow MCP specification guidelines
2. Ensure tool descriptions are clear and comprehensive
3. Include proper error handling and validation
4. Add tests for all tools and functionality
5. Document security considerations

## License

This package is part of the Ontologia framework and follows the same license terms.
