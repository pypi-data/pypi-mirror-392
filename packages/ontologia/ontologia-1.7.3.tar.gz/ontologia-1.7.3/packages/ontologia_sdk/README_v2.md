# Ontologia SDK v2

Unified SDK for the Ontologia platform with dual-mode operation support.

## Overview

The Ontologia SDK v2 provides a unified interface for working with ontology data in both remote (HTTP API) and local (direct core) modes. It offers:

- **Dual-mode operation**: Automatic detection and seamless switching between remote and local modes
- **Type-safe models**: Dynamic Pydantic model generation from ontology definitions
- **Fluent queries**: Chainable QueryBuilder for complex data operations
- **Async-first design**: Full async/await support with synchronous convenience methods
- **IDE support**: Full autocompletion and type hints for better developer experience

## Installation

```bash
pip install ontologia-sdk
```

## Quick Start

### Remote Mode (HTTP API)

```python
import asyncio
from ontologia_sdk import OntologyClient

async def main():
    # Create client for remote operation
    async with OntologyClient(
        host="http://localhost:8000",
        token="your-api-token",
        ontology="my-ontology"
    ) as client:

        # List objects
        people = await client.list_objects("person")
        print(f"Found {len(people)} people")

        # Create a new person
        person = await client.create_object("person", {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        })
        print(f"Created person: {person['pk']}")

asyncio.run(main())
```

### Local Mode (Direct Core)

```python
import asyncio
from ontologia_sdk import OntologyClient

async def main():
    # Create client for local operation
    async with OntologyClient(
        connection_string="sqlite:///./my-database.db"
    ) as client:

        # Same API works in local mode
        people = await client.list_objects("person")
        print(f"Found {len(people)} people")

asyncio.run(main())
```

## Core Components

### OntologyClient

The main client class that automatically detects operation mode and provides a unified interface.

```python
from ontologia_sdk import OntologyClient

# Remote mode (OGM-enabled)
remote_client = OntologyClient(
    host="http://localhost:8000",
    token="api-token",
    ontology="default",
    use_ogm=True  # route via OGM endpoints when available
)

# Local mode (OGM-enabled)
local_client = OntologyClient(
    connection_string="postgresql://user:pass@localhost/db",
    use_ogm=True,
    ogm_module="ontology_definitions.models"  # auto-register ObjectModel classes
)

# Check mode
print(f"Remote client mode: {remote_client.mode}")  # "remote"
print(f"Local client mode: {local_client.mode}")    # "local"
```

### QueryBuilder

Fluent interface for building complex queries:

```python
from ontologia_sdk import query

# Build a complex query
results = await client.list_objects("person", **(
    query("person")
    .where("age", ">=", 18)
    .and_where("status", "=", "active")
    .or_where("vip_status", "=", True)
    .order_by_asc("name")
    .order_by_desc("created_at")
    .limit(20)
    .build()
))

# Or use QueryExecutor for more control
from ontologia_sdk import QueryExecutor

executor = QueryExecutor(client)
query_builder = query("person").where("department", "=", "engineering")
results = await executor.execute(query_builder)
count = await executor.count(query_builder)
```

### ModelFactory

Dynamic Pydantic model generation:

```python
from ontologia_sdk import ModelFactory

# Create factory
factory = ModelFactory()

# Define object type from ontology
person_type = {
    "api_name": "person",
    "properties": [
        {"name": "name", "type": "string", "required": True},
        {"name": "age", "type": "integer", "required": False, "minimum": 0},
        {"name": "email", "type": "string", "required": True}
    ]
}

# Generate Pydantic model
PersonModel = factory.create_model(person_type)

# Use the model with full validation
person = PersonModel(
    pk="person-1",
    name="John Doe",
    age=30,
    email="john@example.com"
)

# Type-safe access
print(person.name)  # "John Doe"
```

## API Reference

### OntologyClient Methods

#### Object Operations
- `get_object(object_type, pk)` - Retrieve single object
- `list_objects(object_type, **filters)` - List objects with filters
- `create_object(object_type, data)` - Create new object
- `update_object(object_type, pk, data)` - Update existing object
- `delete_object(object_type, pk)` - Delete object

#### Type Operations
- `list_object_types()` - List all object types
- `get_object_type(api_name)` - Get object type definition
- `create_object_type(data)` - Create new object type
- `update_object_type(api_name, data)` - Update object type

#### Link Operations
- `list_link_types()` - List all link types
- `get_link_type(api_name)` - Get link type definition
- `create_link_type(data)` - Create new link type
- `get_linked_objects(object_type, pk, link_type, direction)` - Get linked objects
- `create_link(source_type, source_pk, link_type, target_type, target_pk, properties)` - Create link

#### Convenience Methods
- `object_exists(object_type, pk)` - Check if object exists
- `count_objects(object_type, **filters)` - Count objects
- `get_or_create_object(object_type, pk, data)` - Get or create object

When `use_ogm=True`:
- Remote mode: requests include `use_ogm=true` to opt into OGM routing.
- Local mode: operations use registered `ObjectModel` classes when available, falling back to service-layer implementations.

### OGM Query Builder

Execute OGM queries uniformly in remote and local modes:

```python
from ontologia_sdk import OntologyClient

client = OntologyClient(host="http://localhost:8000", ontology="default", use_ogm=True)
results = await client.ogm_query("employee").where("department", "eq", "engineering").order_by("name").limit(20).all()
```

In local mode, enable OGM and provide your models module for auto-registration:

```python
client = OntologyClient(connection_string="sqlite:///./dev.db", use_ogm=True, ogm_module="ontology_definitions.models")
results = await client.ogm_query("company").where("name", "contains", "Acme").all()
```

### QueryBuilder Methods

#### Filtering
- `where(field, operator, value)` - Add WHERE condition
- `and_where(field, operator, value)` - Add AND condition
- `or_where(field, operator, value)` - Add OR condition
- `not_where(field, operator, value)` - Add NOT condition
- `where_in(field, values)` - WHERE field IN (values)
- `where_not_in(field, values)` - WHERE field NOT IN (values)
- `where_like(field, pattern)` - WHERE field LIKE pattern
- `where_between(field, start, end)` - WHERE field BETWEEN start AND end
- `where_null(field)` - WHERE field IS NULL
- `where_not_null(field)` - WHERE field IS NOT NULL

#### Sorting and Pagination
- `order_by(field, direction)` - Add ORDER BY
- `order_by_asc(field)` - ORDER BY field ASC
- `order_by_desc(field)` - ORDER BY field DESC
- `limit(count)` - Set LIMIT
- `offset(count)` - Set OFFSET
- `paginate(page, per_page)` - Set page-based pagination

#### Field Selection and Relationships
- `select(*fields)` - Select specific fields
- `include_related(link_type, direction, fields)` - Include related objects
- `include_outgoing(link_type, fields)` - Include outgoing relationships
- `include_incoming(link_type, fields)` - Include incoming relationships

## Advanced Usage

### Custom Type Mappings

```python
from ontologia_sdk import ModelFactory
from decimal import Decimal

factory = ModelFactory()

# Register custom type mapping
factory.register_type_mapping("decimal", Decimal)

# Now use in object type definition
product_type = {
    "api_name": "product",
    "properties": [
        {"name": "price", "type": "decimal", "required": True}
    ]
}

ProductModel = factory.create_model(product_type)
```

### Model Registry

```python
from ontologia_sdk import ModelRegistry

registry = ModelRegistry()

# Register object type
await registry.register_object_type(person_type)

# Get model
PersonModel = registry.get_model("person")

# List all registered models
models = registry.list_models()
print(f"Registered models: {models}")
```

### Context Manager Support

```python
# Automatic cleanup
async with OntologyClient(host="http://localhost:8000") as client:
    # Use client
    results = await client.list_objects("person")
# Client automatically closed

# Manual cleanup
client = OntologyClient(host="http://localhost:8000")
try:
    results = await client.list_objects("person")
finally:
    await client.close()
```

### Synchronous Convenience Methods

For legacy code or simple scripts:

```python
client = OntologyClient(host="http://localhost:8000")

# Synchronous versions available
person = client.get_object_sync("person", "person-1")
people = client.list_objects_sync("person", status="active")
```

## Error Handling

The SDK uses standard Python exceptions:

```python
from ontologia_sdk import OntologyClient
import httpx

async def main():
    client = OntologyClient(host="http://localhost:8000")

    try:
        person = await client.get_object("person", "nonexistent")
        if person is None:
            print("Person not found")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

## Testing

The SDK includes comprehensive test coverage:

```bash
# Run all tests
python -m pytest packages/ontologia_sdk/

# Run specific test modules
python -m pytest packages/ontologia_sdk/test_session.py
python -m pytest packages/ontologia_sdk/test_client_v2.py
python -m pytest packages/ontologia_sdk/test_model_factory.py
python -m pytest packages/ontologia_sdk/test_query_builder.py
```

## Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/ontologia/ontologia.git
cd ontologia

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest packages/ontologia_sdk/

# Run type checking
ty packages/ontologia_sdk/

# Run linting
ruff check packages/ontologia_sdk/
ruff format packages/ontologia_sdk/
```

### Project Structure

```
packages/ontologia_sdk/
├── ontologia_sdk/
│   ├── __init__.py
│   ├── session.py          # ClientSession protocol and implementations
│   ├── client_v2.py        # Unified OntologyClient
│   ├── model_factory.py    # Dynamic model generation
│   ├── query_builder.py    # Fluent query interface
│   └── test_*.py          # Comprehensive tests
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v2.0.0 (Current)

- **Added**: ClientSession protocol with RemoteSession and LocalSession implementations
- **Added**: Unified OntologyClient with automatic mode detection
- **Added**: Dynamic ModelFactory for runtime Pydantic model generation
- **Added**: Fluent QueryBuilder for complex query construction
- **Added**: Comprehensive test coverage
- **Added**: Full async/await support with synchronous convenience methods
- **Added**: Type safety and IDE autocompletion support
- **Added**: Context manager support for automatic cleanup

### v1.x.x (Legacy)

- Basic HTTP client functionality
- Limited type support
- No local mode support
