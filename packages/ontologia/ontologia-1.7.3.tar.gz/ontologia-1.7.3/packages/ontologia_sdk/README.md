# Ontologia SDK - Python Client Library

## Overview

The `ontologia_sdk` package provides a comprehensive Python client library for interacting with the Ontologia API. This SDK offers a clean, type-safe interface for ontology management, enabling developers to integrate ontology operations into their Python applications with minimal boilerplate and maximum productivity.

## Installation

```bash
# Install the SDK
pip install ontologia-sdk

# Install with optional dependencies
pip install ontologia-sdk[async,pandas,validation]

# Install as part of the full ontologia framework
pip install ontologia[sdk]
```

## Quick Start

```python
from ontologia_sdk import OntologyClient

# Initialize client
client = OntologyClient(base_url="http://localhost:8000")

# Create object type
person_type = await client.create_object_type({
    "name": "Person",
    "description": "A person in the system",
    "properties": [
        {"name": "name", "type": "string", "required": True},
        {"name": "email", "type": "string", "format": "email"},
        {"name": "age", "type": "integer", "minimum": 0}
    ]
})

# Create instance
person = await client.create_instance("Person", {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

print(f"Created person with ID: {person.id}")
```

## Core Architecture

The SDK is built around a client-server architecture with clear separation of concerns:

```
ontologia_sdk/
├── client.py          # Main client implementation
├── ontology/          # Auto-generated ontology classes
├── auth.py           # Authentication handling
├── exceptions.py     # Custom exception types
├── models.py         # Shared data models
├── utils.py          # Utility functions
└── config.py         # Configuration management
```

## Client Configuration

### Basic Configuration

```python
from ontologia_sdk import OntologyClient

# Simple initialization
client = OntologyClient(base_url="http://localhost:8000")

# With authentication
client = OntologyClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"
)

# With JWT token
client = OntologyClient(
    base_url="http://localhost:8000",
    token="your-jwt-token"
)
```

### Advanced Configuration

```python
from ontologia_sdk import OntologyClient, ClientConfig

config = ClientConfig(
    base_url="http://localhost:8000",
    api_key="your-api-key",
    timeout=30,
    retry_attempts=3,
    retry_delay=1,
    validate_responses=True,
    log_requests=False,
    user_agent="MyApp/1.0"
)

client = OntologyClient(config=config)
```

### Environment-based Configuration

```python
import os
from ontologia_sdk import OntologyClient

# Automatically loads from environment variables
client = OntologyClient.from_env()

# Environment variables:
# ONTOLOGIA_BASE_URL=http://localhost:8000
# ONTOLOGIA_API_KEY=your-api-key
# ONTOLOGIA_TIMEOUT=30
```

## Authentication

### API Key Authentication

```python
from ontologia_sdk import OntologyClient

client = OntologyClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Test authentication
is_authenticated = await client.test_auth()
print(f"Authenticated: {is_authenticated}")
```

### JWT Authentication

```python
from ontologia_sdk import OntologyClient

# Login with username/password
client = OntologyClient(base_url="http://localhost:8000")
await client.login("user@example.com", "password")

# Token is automatically stored and refreshed
user_info = await client.get_user_info()
```

### Service Account Authentication

```python
from ontologia_sdk import OntologyClient, ServiceAccountAuth

auth = ServiceAccountAuth.from_file("service-account.json")
client = OntologyClient(
    base_url="http://localhost:8000",
    auth=auth
)
```

## Object Type Management

### Creating Object Types

```python
# Simple object type
person_type = await client.create_object_type({
    "name": "Person",
    "properties": [
        {"name": "name", "type": "string", "required": True},
        {"name": "email", "type": "string", "format": "email"}
    ]
})

# Complex object type with relationships
company_type = await client.create_object_type({
    "name": "Company",
    "description": "Business organization",
    "properties": [
        {"name": "name", "type": "string", "required": True},
        {"name": "founded_date", "type": "date"},
        {"name": "employee_count", "type": "integer", "minimum": 0}
    ],
    "indexes": [
        {"properties": ["name"], "unique": True}
    ]
})
```

### Querying Object Types

```python
# List all object types
object_types = await client.list_object_types()

# Get specific object type
person_type = await client.get_object_type("Person")

# Search object types
results = await client.search_object_types(
    query="person",
    limit=10
)
```

### Updating Object Types

```python
# Add properties
updated_type = await client.update_object_type("Person", {
    "add_properties": [
        {"name": "phone", "type": "string"},
        {"name": "address", "type": "object"}
    ]
})

# Remove properties
updated_type = await client.update_object_type("Person", {
    "remove_properties": ["phone"]
})
```

## Instance Management

### Creating Instances

```python
# Create single instance
person = await client.create_instance("Person", {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

# Create with custom ID
person = await client.create_instance("Person", {
    "id": "john_doe_001",
    "name": "John Doe",
    "email": "john@example.com"
})

# Batch create instances
people = await client.create_instances("Person", [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Jones", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"}
])
```

### Querying Instances

```python
# Get specific instance
person = await client.get_instance("person_123")

# List instances with filtering
people = await client.list_instances(
    object_type_name="Person",
    filters={"age": {"gte": 25}},
    limit=10,
    sort="name:asc"
)

# Full-text search
results = await client.search_instances(
    query="John Doe",
    object_type_names=["Person"]
)

# Complex query
results = await client.query_instances({
    "object_type": "Person",
    "filters": {
        "age": {"gte": 18, "lte": 65},
        "email": {"contains": "@company.com"}
    },
    "sort": [{"field": "name", "direction": "asc"}],
    "limit": 20
})
```

### Updating Instances

```python
# Update instance
updated_person = await client.update_instance("person_123", {
    "age": 31,
    "phone": "+1-555-0123"
})

# Partial update (patch)
patched_person = await client.patch_instance("person_123", {
    "age": 32
})

# Batch update
results = await client.update_instances("Person", {
    "filters": {"age": {"lt": 18}},
    "updates": {"status": "minor"}
})
```

### Deleting Instances

```python
# Delete single instance
await client.delete_instance("person_123")

# Batch delete with filter
result = await client.delete_instances("Person", {
    "filters": {"status": "inactive"}
})

print(f"Deleted {result.deleted_count} instances")
```

## Relationship Management

### Creating Relationships

```python
# Create simple relationship
link = await client.create_link("works_for", {
    "source_id": "person_123",
    "target_id": "company_456"
})

# Create relationship with properties
link = await client.create_link("manages", {
    "source_id": "person_123",
    "target_id": "company_456",
    "properties": {
        "start_date": "2023-01-01",
        "role": "Engineering Manager"
    }
})
```

### Querying Relationships

```python
# Get relationships for instance
relationships = await client.get_instance_links("person_123")

# Find related instances
companies = await client.get_related_instances(
    instance_id="person_123",
    link_type_name="works_for",
    direction="outgoing"
)

# Complex relationship query
results = await client.query_links({
    "link_type": "works_for",
    "source_type": "Person",
    "target_type": "Company",
    "filters": {
        "properties.start_date": {"gte": "2023-01-01"}
    }
})
```

## Schema-Generated Classes

When using the SDK with generated ontology classes, you get strongly-typed interfaces:

```python
# After running: ontologia generate-sdk
from ontologia_sdk.ontology import Person, Company, works_for

# Create with typed classes
person = Person(
    name="John Doe",
    email="john@example.com",
    age=30
)

created_person = await person.save()

# Type-safe property access
print(f"Name: {created_person.name}")
print(f"Email: {created_person.email}")

# Typed relationships
company = Company(name="Acme Corp", founded_date="2020-01-01")
await company.save()

# Create typed relationship
relationship = works_for(
    source=created_person,
    target=company,
    start_date="2023-01-01"
)
await relationship.save()
```

## Data Catalog Integration

### Dataset Management

```python
from ontologia_sdk import DatasetClient

dataset_client = DatasetClient(client)

# Create dataset
dataset = await dataset_client.create_dataset({
    "name": "customer_data",
    "description": "Customer master data",
    "schema": {
        "columns": [
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": False},
            {"name": "email", "type": "string", "nullable": True}
        ]
    }
})

# Add data transaction
transaction = await dataset_client.create_transaction(
    dataset_name="customer_data",
    transaction_type="insert",
    data=[
        {"customer_id": "cust_001", "name": "John Doe", "email": "john@example.com"},
        {"customer_id": "cust_002", "name": "Jane Smith", "email": "jane@example.com"}
    ]
)
```

### Branch Operations

```python
# Create branch
branch = await dataset_client.create_branch(
    dataset_name="customer_data",
    branch_name="feature_enhancement",
    base_branch="main"
)

# Switch to branch
dataset_client.set_branch("feature_enhancement")

# Merge branch
merge_result = await dataset_client.merge_branch(
    dataset_name="customer_data",
    source_branch="feature_enhancement",
    target_branch="main"
)
```

## Actions and Workflows

### Executing Actions

```python
# List available actions
actions = await client.list_actions()

# Execute action synchronously
result = await client.execute_action("validate_data", {
    "dataset": "customer_data",
    "rules": ["email_format", "required_fields"]
})

# Execute action asynchronously
execution = await client.execute_action_async("process_large_dataset", {
    "dataset": "customer_data",
    "batch_size": 1000
})

# Monitor execution
status = await client.get_execution_status(execution.id)
while status.status == "running":
    await asyncio.sleep(1)
    status = await client.get_execution_status(execution.id)

result = await client.get_execution_result(execution.id)
```

### Workflow Management

```python
# Start workflow
workflow = await client.start_workflow("data_migration", {
    "source_dataset": "legacy_customers",
    "target_dataset": "customer_data",
    "mapping": {
        "cust_id": "customer_id",
        "cust_name": "name",
        "cust_email": "email"
    }
})

# Monitor workflow
status = await client.get_workflow_status(workflow.id)
print(f"Status: {status.status}")
print(f"Progress: {status.progress}%")
```

## Real-time Updates

### WebSocket Connections

```python
from ontologia_sdk import RealtimeClient

# Connect to real-time updates
async with RealtimeClient(client) as rt_client:
    # Subscribe to object type changes
    await rt_client.subscribe_to_object_type("Person")

    async for event in rt_client.events():
        print(f"Event: {event.type}")
        print(f"Data: {event.data}")

        if event.type == "instance_created":
            person = event.data
            print(f"New person: {person.name}")
```

### Event Filtering

```python
# Subscribe to specific events
await rt_client.subscribe({
    "object_types": ["Person", "Company"],
    "event_types": ["created", "updated"],
    "filters": {
        "instance.age": {"gte": 18}
    }
})
```

## Error Handling

### Exception Types

```python
from ontologia_sdk.exceptions import (
    OntologiaError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError
)

try:
    person = await client.get_instance("nonexistent")
except NotFoundError as e:
    print(f"Instance not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except OntologiaError as e:
    print(f"API error: {e}")
```

### Retry Logic

```python
from ontologia_sdk import OntologyClient, RetryConfig

retry_config = RetryConfig(
    attempts=3,
    delay=1,
    backoff=2,
    retry_on=[RateLimitError, ConnectionError]
)

client = OntologyClient(
    base_url="http://localhost:8000",
    retry_config=retry_config
)
```

## Advanced Features

### Pagination

```python
# Iterate through large result sets
async for person in client.paginate_instances("Person", limit=100):
    print(f"Processing: {person.name}")

# Manual pagination
page = await client.list_instances("Person", limit=50, offset=0)
while page.has_next:
    next_page = await page.next()
    for instance in next_page.instances:
        print(instance.name)
```

### Caching

```python
from ontologia_sdk import CachedClient

# Enable caching for better performance
cached_client = CachedClient(
    base_url="http://localhost:8000",
    cache_ttl=300,  # 5 minutes
    cache_size=1000
)

# Cached operations
object_type = await cached_client.get_object_type("Person")  # From API
object_type = await cached_client.get_object_type("Person")  # From cache
```

### Bulk Operations

```python
# Bulk create with progress tracking
async with client.bulk_operation() as bulk:
    for person_data in large_person_list:
        await bulk.create_instance("Person", person_data)

        if bulk.processed_count % 100 == 0:
            print(f"Processed {bulk.processed_count} records")

result = await bulk.commit()
print(f"Created {result.created_count} instances")
```

## Validation

### Schema Validation

```python
from ontologia_sdk.validation import validate_instance

# Validate instance before creation
person_data = {"name": "John Doe", "email": "invalid-email"}
errors = validate_instance("Person", person_data)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error.field}: {error.message}")
else:
    person = await client.create_instance("Person", person_data)
```

### Custom Validators

```python
from ontologia_sdk.validation import Validator, ValidationError

class EmailValidator(Validator):
    def validate(self, value, context):
        if "@" not in value:
            raise ValidationError("Invalid email format")
        return value

# Register custom validator
client.register_validator("email", EmailValidator())
```

## Testing

### Mock Client for Testing

```python
from ontologia_sdk.testing import MockOntologyClient

# Use mock client for unit tests
mock_client = MockOntologyClient()

# Setup mock responses
mock_client.add_object_type("Person", {
    "name": "Person",
    "properties": [{"name": "name", "type": "string"}]
})

# Use in tests
person = await mock_client.create_instance("Person", {"name": "Test"})
assert person.name == "Test"
```

### Test Utilities

```python
from ontologia_sdk.testing import TestDataGenerator

# Generate test data
generator = TestDataGenerator()
test_person = generator.generate_instance("Person")
test_company = generator.generate_instance("Company")

# Generate test relationships
test_relationship = generator.generate_relationship(
    "works_for",
    test_person,
    test_company
)
```

## Performance Optimization

### Connection Pooling

```python
from ontologia_sdk import OntologyClient, PoolConfig

pool_config = PoolConfig(
    max_connections=20,
    max_keepalive_connections=5,
    keepalive_expiry=30
)

client = OntologyClient(
    base_url="http://localhost:8000",
    pool_config=pool_config
)
```

### Async Operations

```python
import asyncio
from ontologia_sdk import OntologyClient

async def process_multiple_instances():
    client = OntologyClient()

    # Concurrent operations
    tasks = [
        client.get_instance(f"person_{i}")
        for i in range(10)
    ]

    instances = await asyncio.gather(*tasks)
    return instances
```

## Configuration

### Client Settings

```python
from ontologia_sdk import OntologyClient, ClientSettings

settings = ClientSettings(
    timeout=30,
    max_retries=3,
    retry_delay=1,
    validate_responses=True,
    compress_requests=True,
    log_requests=False,
    user_agent="MyApp/1.0"
)

client = OntologyClient(settings=settings)
```

### Environment Variables

```bash
# .env file
ONTOLOGIA_BASE_URL=http://localhost:8000
ONTOLOGIA_API_KEY=your-api-key
ONTOLOGIA_TIMEOUT=30
ONTOLOGIA_MAX_RETRIES=3
ONTOLOGIA_LOG_REQUESTS=true
```

## Dependencies

Core dependencies:
- **httpx**: Async HTTP client
- **pydantic**: Data validation and serialization
- **PyYAML**: Configuration file support

Optional dependencies:
- **pandas**: Data manipulation and analysis
- **aiofiles**: Async file operations
- **cryptography**: Advanced security features
- **redis**: Caching support

## Version Information

Current version: `0.1.0`

Follows semantic versioning with API compatibility guarantees.

## Contributing

When contributing to the SDK:
1. Maintain backward compatibility
2. Add comprehensive type hints
3. Include thorough documentation
4. Write tests for all functionality
5. Follow Python packaging best practices

## License

This package is part of the Ontologia framework and follows the same license terms.
