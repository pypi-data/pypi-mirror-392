# Data Catalog - Versioned Data Management Library

## Overview

The `datacatalog` package provides a comprehensive data catalog system inspired by Palantir Foundry, enabling versioned, branch-based data management within the Ontologia framework. This library offers robust models for datasets, transactions, and branching, allowing teams to manage data evolution with full traceability and governance.

## Core Concepts

### Dataset Management
- **Datasets**: Named collections of data with schema and metadata
- **Transactions**: Immutable changesets that capture data modifications
- **Branches**: Parallel lines of development for data evolution
- **Versioning**: Full history tracking with the ability to time-travel

### Branch-Based Workflow
Similar to Git, the data catalog supports branching workflows:
- **Main Branch**: Production data lineage
- **Feature Branches**: Experimental data transformations
- **Merge Operations**: Controlled integration of changes
- **Conflict Resolution**: Handling of competing modifications

## Key Components

### Core Models

#### Dataset
```python
from datacatalog import Dataset

dataset = Dataset(
    name="customer_data",
    description="Customer information and analytics",
    schema={
        "columns": [
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "email", "type": "string", "nullable": False},
            {"name": "created_at", "type": "timestamp", "nullable": False}
        ]
    },
    metadata={
        "owner": "data-team",
        "classification": "pii",
        "retention_policy": "7_years"
    }
)
```

#### DatasetTransaction
```python
from datacatalog import DatasetTransaction, TransactionType

transaction = DatasetTransaction(
    dataset_id="customer_data",
    transaction_type=TransactionType.INSERT,
    data=[
        {"customer_id": "cust_001", "email": "user@example.com", "created_at": "2024-01-01"},
        {"customer_id": "cust_002", "email": "user2@example.com", "created_at": "2024-01-02"}
    ],
    metadata={"source": "crm_system", "batch_id": "batch_123"}
)
```

#### DatasetBranch
```python
from datacatalog import DatasetBranch

branch = DatasetBranch(
    dataset_name="customer_data",
    branch_name="feature_enhancement",
    base_branch="main",
    description="Adding customer segmentation data"
)
```

### Transaction Types

The library supports various transaction types:

- **INSERT**: Add new records
- **UPDATE**: Modify existing records
- **DELETE**: Remove records
- **SCHEMA_CHANGE**: Modify dataset structure
- **METADATA_UPDATE**: Update dataset metadata

## Usage Examples

### Creating a Dataset

```python
from datacatalog import Dataset, ColumnSchema

# Define schema
schema = [
    ColumnSchema(name="id", type="string", nullable=False, description="Unique identifier"),
    ColumnSchema(name="name", type="string", nullable=False, description="Customer name"),
    ColumnSchema(name="email", type="string", nullable=True, description="Contact email"),
    ColumnSchema(name="created_at", type="timestamp", nullable=False, description="Creation timestamp")
]

# Create dataset
dataset = Dataset(
    name="customers",
    description="Master customer dataset",
    schema=schema,
    metadata={
        "owner": "analytics-team",
        "classification": "sensitive",
        "refresh_frequency": "daily"
    }
)
```

### Working with Branches

```python
from datacatalog import DatasetBranch, DatasetTransaction, TransactionType

# Create a new branch
branch = DatasetBranch.create(
    dataset_name="customers",
    branch_name="feature_segmentation",
    base_branch="main"
)

# Add data to branch
transaction = DatasetTransaction(
    dataset_id="customers",
    branch_name="feature_segmentation",
    transaction_type=TransactionType.INSERT,
    data=[
        {
            "id": "cust_001",
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "segment": "premium"
        }
    ]
)

# Commit transaction
transaction.commit()
```

### Querying Dataset History

```python
from datacatalog import Dataset

# Get dataset
dataset = Dataset.get("customers")

# Get current state (main branch)
current_data = dataset.get_data()

# Get specific branch data
branch_data = dataset.get_data(branch="feature_segmentation")

# Get historical data at specific transaction
historical_data = dataset.get_data(at_transaction="txn_12345")

# Get transaction history
history = dataset.get_transaction_history(limit=100)
```

### Merging Branches

```python
from datacatalog import DatasetBranch

# Get branch
branch = DatasetBranch.get("customers", "feature_segmentation")

# Review changes before merge
changes = branch.get_pending_changes()
conflicts = branch.detect_conflicts(target_branch="main")

# Merge if no conflicts
if not conflicts:
    merge_result = branch.merge_to(target_branch="main")
    print(f"Merged {merge_result.transactions_merged} transactions")
else:
    print(f"Found {len(conflicts)} conflicts to resolve")
```

## Advanced Features

### Schema Evolution

```python
from datacatalog import DatasetTransaction, TransactionType, ColumnSchema

# Add new column through schema change transaction
schema_change = DatasetTransaction(
    dataset_id="customers",
    transaction_type=TransactionType.SCHEMA_CHANGE,
    schema_changes={
        "added_columns": [
            ColumnSchema(name="segment", type="string", nullable=True, description="Customer segment")
        ]
    }
)

schema_change.commit()
```

### Data Lineage Tracking

```python
from datacatalog import Dataset

# Trace data origins
dataset = Dataset.get("customers")

# Get upstream sources
upstream = dataset.get_upstream_sources()

# Get downstream dependencies
downstream = dataset.get_downstream_dependencies()

# Get full lineage graph
lineage = dataset.get_lineage_graph()
```

### Governance and Compliance

```python
from datacatalog import Dataset

# Access control
dataset = Dataset.get("customers")
dataset.set_access_policy({
    "roles": {
        "analyst": ["read"],
        "data_engineer": ["read", "write"],
        "admin": ["read", "write", "delete"]
    }
})

# Data classification
dataset.update_metadata({
    "classification": "pii",
    "retention_days": 2555,  # 7 years
    "privacy_requirements": ["gdpr", "ccpa"]
})

# Audit trail
audit_log = dataset.get_audit_log(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Integration with Ontologia

The data catalog integrates seamlessly with the core ontologia package:

### Ontology Integration

```python
from ontologia import ObjectType, PropertyType
from datacatalog import Dataset

# Define ontology type for datasets
dataset_type = ObjectType(
    name="Dataset",
    properties=[
        PropertyType(name="name", data_type="string", required=True),
        PropertyType(name="schema", data_type="json", required=True),
        PropertyType(name="classification", data_type="string")
    ]
)

# Link datasets to ontology concepts
dataset.link_to_concept("customer_data", "Customer")
```

### Real-time Synchronization

```python
from datacatalog import Dataset
from ontologia.event_handlers import DataCatalogHandler

# Set up real-time sync
handler = DataCatalogHandler()
handler.sync_dataset_changes_to_ontology("customers")
```

## Configuration

```python
from datacatalog.config import DataCatalogConfig

config = DataCatalogConfig(
    storage_backend="postgresql",
    enable_versioning=True,
    max_branch_depth=10,
    default_retention_days=2555,
    enable_lineage_tracking=True
)
```

## Best Practices

### Dataset Design
1. **Clear Naming**: Use descriptive, consistent naming conventions
2. **Schema Documentation**: Document all columns and their purposes
3. **Data Classification**: Apply appropriate sensitivity labels
4. **Access Control**: Implement principle of least privilege

### Branch Management
1. **Short-lived Branches**: Keep feature branches focused and temporary
2. **Regular Merges**: Merge frequently to reduce conflicts
3. **Code Review**: Review dataset changes before merging
4. **Testing**: Validate data quality in branches before promotion

### Transaction Management
1. **Batch Operations**: Group related changes in single transactions
2. **Atomic Changes**: Ensure transactions are logically complete
3. **Metadata**: Include rich metadata for traceability
4. **Validation**: Validate data before committing transactions

## Performance Considerations

### Query Optimization
- Use appropriate indexes for frequent queries
- Leverage partitioning for large datasets
- Implement caching for metadata operations
- Use time-travel queries judiciously

### Storage Efficiency
- Compress historical data
- Archive old transactions
- Use columnar storage for analytical queries
- Implement data lifecycle policies

## Error Handling

```python
from datacatalog.exceptions import (
    DatasetNotFoundError,
    BranchNotFoundError,
    TransactionConflictError,
    SchemaValidationError
)

try:
    dataset = Dataset.get("nonexistent")
except DatasetNotFoundError:
    print("Dataset not found")

try:
    transaction.commit()
except TransactionConflictError as e:
    print(f"Conflict detected: {e.conflicts}")
```

## Testing

The package includes comprehensive test coverage:
- Unit tests for all model operations
- Integration tests for branch management
- Performance tests for large datasets
- Concurrency tests for transaction handling

## Dependencies

Core dependencies:
- **SQLModel**: Data modeling and validation
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **Alembic**: Database migrations

Optional dependencies:
- **PostgreSQL**: Production storage backend
- **Redis**: Caching and session management
- **Pandas**: Data manipulation and analysis

## Version Information

Current version: `0.1.0`

Follows semantic versioning with backward compatibility guarantees.

## Contributing

When contributing to the data catalog:
1. Maintain data integrity and consistency
2. Add comprehensive tests for new features
3. Document schema changes and migrations
4. Consider performance implications
5. Follow data governance best practices

## License

This package is part of the Ontologia framework and follows the same license terms.
