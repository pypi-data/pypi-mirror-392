# Ontologia - Core Ontology Management System

## Overview

Ontologia is the core library of the Ontologia framework, providing a comprehensive ontology management system built on Registro and SQLModel. This package serves as the foundation for defining, managing, and persisting ontologies with rich data types, validation, and data source integration.

## Architecture

The ontologia package follows Domain-Driven Design (DDD) principles with clear separation of concerns:

```
ontologia/
├── actions/          # Command and query handlers
├── application/      # Application services and use cases
├── domain/          # Core domain models and business logic
├── event_handlers/  # Event processing and side effects
├── infrastructure/  # External integrations and persistence
└── config.py        # Configuration management
```

## Core Components

### Domain Models (`domain/`)

The domain layer contains the core business logic and models:

#### Metamodel System
- **Object Types**: Define entity types with properties and relationships
- **Property Types**: Define data type specifications for object attributes
- **Link Types**: Define relationships between objects with cardinality constraints
- **Data Sources**: Integration points for external data systems

#### Key Classes
```python
from ontologia import (
    ObjectType,      # Entity type definitions
    PropertyType,    # Attribute type specifications
    LinkType,        # Relationship definitions
    Cardinality,     # Relationship cardinality constraints
    ObjectTypeDataSource,  # Data source integrations
)
```

### Application Layer (`application/`)

Contains use case implementations and application services:
- **Actions Service**: Orchestrates complex business operations
- **Analytics Service**: Provides analytical capabilities
- **Change Set Service**: Manages batch changes and transactions
- **Instances Service**: Handles instance CRUD operations
- **Metamodel Service**: Manages schema and type definitions
- **Realtime Service**: Handles real-time updates and events
- **Search Service**: Provides search and query capabilities

### Infrastructure Layer (`infrastructure/`)

Handles external concerns and technical implementations:
- **Database**: Persistence layer with multiple database support
- **Event Bus**: Event publishing and subscription
- **External APIs**: Integration with external services
- **File Storage**: File and document management
- **Messaging**: Message queue integrations
- **Monitoring**: Metrics and observability
- **Security**: Authentication and authorization
- **Time Travel**: Historical data access

### Actions (`actions/`)

Implements Command Query Responsibility Segregation (CQRS):
- **Temporal Workflows**: Asynchronous workflow orchestration
- **Action Registry**: Dynamic action registration and execution
- **Exception Handling**: Centralized error management

### Event Handlers (`event_handlers/`)

Processes domain events and manages side effects:
- **Cache Management**: Intelligent cache invalidation and updates
- **Graph Updates**: Real-time graph structure maintenance
- **Search Indexing**: Automatic search index updates

## Key Features

### Rich Type System
- Comprehensive data type support (primitive, complex, custom)
- Type validation and constraints
- Extensible type registry

### Relationship Management
- Flexible relationship definitions
- Cardinality enforcement
- Bidirectional relationship support

### Data Source Integration
- Multiple database backends (PostgreSQL, KùzuDB, DuckDB)
- External data source connectors
- Real-time synchronization

### Validation Framework
- Multi-level validation (type, instance, relationship)
- Custom validation rules
- Constraint enforcement

### Event-Driven Architecture
- Domain event publishing
- Event sourcing capabilities
- Real-time updates

## Usage Examples

### Defining an Ontology

```python
from ontologia import ObjectType, PropertyType, LinkType, Cardinality

# Define object types
person_type = ObjectType(
    name="Person",
    description="A person in the system",
    properties=[
        PropertyType(name="name", data_type="string", required=True),
        PropertyType(name="age", data_type="integer", min_value=0),
        PropertyType(name="email", data_type="string", format="email")
    ]
)

company_type = ObjectType(
    name="Company",
    description="A business organization",
    properties=[
        PropertyType(name="name", data_type="string", required=True),
        PropertyType(name="founded_date", data_type="date")
    ]
)

# Define relationships
works_for_link = LinkType(
    name="works_for",
    description="Person works for company",
    source_type="Person",
    target_type="Company",
    cardinality=Cardinality.MANY_TO_ONE
)
```

### Working with Instances

```python
from ontologia.application import InstancesService

# Create service
instances_service = InstancesService()

# Create instances
person = instances_service.create_instance(
    object_type_name="Person",
    data={"name": "John Doe", "age": 30, "email": "john@example.com"}
)

company = instances_service.create_instance(
    object_type_name="Company",
    data={"name": "Acme Corp", "founded_date": "2020-01-01"}
)

# Create relationship
instances_service.create_link(
    link_type_name="works_for",
    source_id=person.id,
    target_id=company.id
)
```

### Querying the Ontology

```python
from ontologia.application import SearchService

# Create search service
search_service = SearchService()

# Find all people
people = search_service.find_instances(object_type_name="Person")

# Find people working at specific company
employees = search_service.find_related_instances(
    object_type_name="Person",
    link_type_name="works_for",
    target_id=company.id
)

# Complex queries with filters
results = search_service.search({
    "object_type": "Person",
    "filters": {
        "age": {"gte": 25},
        "email": {"contains": "@example.com"}
    },
    "limit": 10
})
```

## Configuration

The ontologia package uses Pydantic Settings for configuration:

```python
from ontologia.config import OntologiaConfig

# Load configuration
config = OntologiaConfig()

# Access configuration
database_url = config.database_url
redis_url = config.redis_url
temporal_address = config.temporal_address
```

## Integration Points

### Database Support
- **PostgreSQL**: Primary relational database
- **KùzuDB**: Graph database for relationship queries
- **DuckDB**: Analytical database for data warehousing
- **SQLite**: Development and testing database

### External Services
- **TemporalIO**: Workflow orchestration
- **Redis**: Caching and session management
- **Elasticsearch**: Full-text search
- **gRPC**: Real-time communication

### Data Sources
- **File Systems**: Local and cloud storage
- **APIs**: REST and GraphQL endpoints
- **Message Queues**: Event streaming
- **Databases**: Direct database connections

## Development Guidelines

### Adding New Object Types
1. Define in domain layer with proper validation
2. Add repository methods for persistence
3. Create application service methods
4. Add API endpoints if needed
5. Write comprehensive tests

### Extending the Type System
1. Create new property type in domain
2. Add validation logic
3. Update serialization/deserialization
4. Document usage examples

### Event Handling
1. Define domain events
2. Create event handlers
3. Register handlers in event bus
4. Add idempotency guarantees

## Testing

The package includes comprehensive test coverage:
- Unit tests for domain logic
- Integration tests for repositories
- End-to-end tests for workflows
- Performance tests for scalability

## Dependencies

Core dependencies:
- **SQLModel**: Database ORM and validation
- **Registro**: Domain-driven design framework
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Database abstraction layer
- **Alembic**: Database migrations

Optional dependencies:
- **KùzuDB**: Graph database support
- **DuckDB**: Analytical database support
- **TemporalIO**: Workflow orchestration
- **Redis**: Caching and sessions

## Version Information

Current version: `0.2.0`

Follows semantic versioning with backward compatibility guarantees within major versions.

## Contributing

When contributing to the ontologia core package:
1. Follow DDD principles
2. Maintain clean architecture boundaries
3. Add comprehensive tests
4. Update documentation
5. Consider backward compatibility

## License

This package is part of the Ontologia framework and follows the same license terms.
