# Ontologia Dagster - Data Orchestration Integration

## Overview

The `ontologia_dagster` package provides seamless integration between the Ontologia framework and Dagster, the modern data orchestrator. This package enables you to build, schedule, and monitor data pipelines that leverage Ontologia's ontology management, data catalog, and real-time processing capabilities within Dagster's powerful orchestration platform.

## Installation

```bash
# Install with Dagster support
pip install ontologia[dagster]

# Or install the package directly
pip install ontologia-dagster

# Install with all optional dependencies
pip install ontologia-dagster[pandas,spark,cloud]
```

## Quick Start

```python
from ontologia_dagster import (
    ontologia_asset,
    ontologia_op,
    OntologiaResource,
    defs
)
import pandas as pd

# Define Ontologia resource
@ontologia_config
class OntologiaConfig:
    base_url: str
    api_key: str

# Create Dagster resource
ontologia_resource = OntologiaResource(config=OntologiaConfig())

# Define asset that queries Ontologia
@ontologia_asset(
    key="customer_data",
    group_name="ontology_assets"
)
def extract_customers(ontologia: OntologiaResource) -> pd.DataFrame:
    """Extract customer data from Ontologia."""
    clients = ontology.list_instances("Person", filters={"type": "customer"})
    return pd.DataFrame([client.data for client in clients])

# Define transformation op
@ontologia_op
def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Transform customer data."""
    df['segment'] = df['purchase_count'].apply(
        lambda x: 'premium' if x > 10 else 'standard'
    )
    return df

# Define asset that writes back to Ontologia
@ontologia_asset(
    key="segmented_customers",
    group_name="ontology_assets",
    deps=[extract_customers, transform_customers]
)
def load_segmented_customers(
    transformed: pd.DataFrame,
    ontology: OntologiaResource
) -> None:
    """Load segmented customers back to Ontologia."""
    for _, row in transformed.iterrows():
        ontology.update_instance(
            "Person",
            row['id'],
            {"segment": row['segment']}
        )
```

## Core Architecture

The integration provides several key components:

```
ontologia_dagster/
├── assets/           # Ontologia-aware asset definitions
├── ops/             # Dagster operations for Ontologia
├── resources/       # Dagster resources for Ontologia clients
├── sensors/         # Change detection and monitoring
├── schedules/       # Time-based and event-based scheduling
├── types/           # Custom Dagster type system
└── utils/           # Helper functions and utilities
```

## Resources and Configuration

### Ontologia Resource

```python
from ontologia_dagster import OntologiaResource, ontologia_config

# Configuration class
@ontologia_config
class OntologiaConfig:
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3

# Resource definition
ontologia_resource = OntologiaResource(config=OntologiaConfig())

# Use in definitions
@job(resource_defs={"ontologia": ontology_resource})
def my_ontology_job():
    extract_data()
```

### Multi-Environment Configuration

```python
from dagster import build_resources

# Development configuration
dev_config = OntologiaConfig(
    base_url="http://dev-ontologia:8000",
    api_key=os.getenv("DEV_ONTOLOGIA_API_KEY")
)

# Production configuration
prod_config = OntologiaConfig(
    base_url="https://prod-ontologia.company.com",
    api_key=os.getenv("PROD_ONTOLOGIA_API_KEY"),
    timeout=60
)

# Environment-specific resources
dev_resources = build_resources({"ontologia": OntologiaResource(dev_config)})
prod_resources = build_resources({"ontologia": OntologiaResource(prod_config)})
```

## Assets

### Ontology Query Assets

```python
from ontologia_dagster import ontologia_asset, OntologiaQueryConfig

# Simple query asset
@ontologia_asset(
    key="all_persons",
    group_name="raw_data"
)
def extract_all_persons(ontologia: OntologiaResource) -> pd.DataFrame:
    """Extract all person instances."""
    persons = ontologia.list_instances("Person")
    return pd.DataFrame([p.data for p in persons])

# Configured query asset
@ontologia_asset(
    key="active_customers",
    group_name="filtered_data",
    config_schema={
        "min_orders": Field(int, default_value=5),
        "date_range": Field(str, is_required=False)
    }
)
def extract_active_customers(
    ontology: OntologiaResource,
    config: dict
) -> pd.DataFrame:
    """Extract active customers with filters."""
    filters = {"order_count": {"gte": config["min_orders"]}}
    if config.get("date_range"):
        filters["last_order_date"] = {"gte": config["date_range"]}

    customers = ontology.list_instances("Person", filters=filters)
    return pd.DataFrame([c.data for c in customers])
```

### Data Catalog Assets

```python
from ontologia_dagster import dataset_asset, transaction_asset

# Dataset asset
@dataset_asset(
    key="customer_dataset",
    dataset_name="customer_analytics",
    branch="main"
)
def customer_analytics_dataset(ontology: OntologiaResource) -> None:
    """Ensure customer analytics dataset exists."""
    # Dataset is automatically created/validated
    pass

# Transaction asset
@transaction_asset(
    key="daily_customer_updates",
    dataset_name="customer_analytics",
    transaction_type="upsert"
)
def load_daily_updates(
    transformed_data: pd.DataFrame,
    ontology: OntologiaResource
) -> None:
    """Load daily customer updates."""
    for _, row in transformed_data.iterrows():
        ontology.create_transaction(
            dataset_name="customer_analytics",
            transaction_type="upsert",
            data=row.to_dict()
        )
```

### Materialization Assets

```python
from ontologia_dagster import materialize_to_ontology

# Asset with automatic materialization
@ontologia_asset(
    key="processed_metrics",
    group_name="analytics",
    auto_materialize_policy=AutoMaterializePolicy.eager()
)
def compute_customer_metrics(
    customers: pd.DataFrame,
    orders: pd.DataFrame
) -> MaterializationResult:
    """Compute customer metrics and store in Ontologia."""

    # Compute metrics
    metrics = customers.merge(orders, on='customer_id')\
        .groupby('customer_id')\
        .agg({
            'total_orders': 'count',
            'total_value': 'sum',
            'avg_order_value': 'mean'
        }).reset_index()

    # Materialize to Ontologia
    materialize_to_ontology(
        ontology_client=ontology,
        object_type="CustomerMetrics",
        data=metrics.to_dict('records')
    )

    return MaterializationResult(
        description=f"Materialized {len(metrics)} customer metrics"
    )
```

## Operations

### Ontology Operations

```python
from ontologia_dagster import ontologia_op, OntologiaOpConfig

# Simple operation
@ontologia_op
def validate_instance_data(
    instance_data: dict,
    ontology: OntologiaResource
) -> bool:
    """Validate instance data against ontology schema."""
    return ontology.validate_instance("Person", instance_data)

# Configurable operation
@ontologia_op(
    config_schema={
        "object_type": str,
        "batch_size": int,
        "validate_only": bool
    }
)
def bulk_create_instances(
    data: pd.DataFrame,
    ontology: OntologiaResource,
    config: dict
) -> int:
    """Bulk create instances with configuration."""
    created_count = 0
    batch_size = config["batch_size"]

    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i+batch_size].to_dict('records')
        results = ontology.create_instances(config["object_type"], batch)
        created_count += len(results)

    return created_count
```

### Data Processing Operations

```python
from ontologia_dagster import ontology_aware_op

# Operation that uses ontology metadata
@ontology_aware_op
def enrich_with_metadata(
    raw_data: pd.DataFrame,
    ontology: OntologiaResource
) -> pd.DataFrame:
    """Enrich data with ontology metadata."""
    # Get object type metadata
    person_type = ontology.get_object_type("Person")

    # Add metadata columns
    enriched = raw_data.copy()
    for prop in person_type.properties:
        if prop.name not in enriched.columns:
            enriched[prop.name] = None

    return enriched
```

## Sensors and Triggers

### Change Detection Sensors

```python
from ontologia_dagster import ontology_change_sensor, ChangeConfig

# Monitor ontology changes
@ontology_change_sensor(
    object_types=["Person", "Company"],
    change_types=["created", "updated"],
    interval_minutes=5
)
def ontology_changes_sensor(context):
    """Sensor for detecting ontology changes."""
    changes = context.resources.ontologia.get_recent_changes(
        object_types=["Person", "Company"],
        since=context.last_run_time
    )

    for change in changes:
        context.log.info(f"Detected change: {change}")
        yield RunRequest(
            run_key=f"process_{change.object_type}_{change.instance_id}",
            run_config={
                "ops": {
                    "process_change": {
                        "config": {
                            "change_id": change.id,
                            "object_type": change.object_type
                        }
                    }
                }
            }
        )
```

### Dataset Sensors

```python
from ontologia_dagster import dataset_transaction_sensor

# Monitor dataset transactions
@dataset_transaction_sensor(
    dataset_name="customer_data",
    transaction_types=["insert", "update"]
)
def customer_data_sensor(context):
    """Sensor for customer data changes."""
    new_transactions = context.resources.ontologia.get_new_transactions(
        dataset_name="customer_data",
        since=context.last_run_time
    )

    if new_transactions:
        yield RunRequest(
            run_key="process_customer_updates",
            run_config={"transactions": [t.id for t in new_transactions]}
        )
```

## Schedules

### Time-based Schedules

```python
from ontologia_dagster import ontology_schedule

# Daily ontology sync
@ontology_schedule(
    cron_schedule="0 2 * * *",  # 2 AM daily
    execution_timezone="UTC"
)
def daily_ontology_sync(context):
    """Daily schedule for ontology synchronization."""
    return RunRequest(
        run_key=f"daily_sync_{context.scheduled_execution_time}",
        run_config={
            "ops": {
                "sync_ontology": {
                    "config": {
                        "sync_date": context.scheduled_execution_time.isoformat()
                    }
                }
            }
        }
    )
```

### Event-based Schedules

```python
from ontologia_dagster import event_driven_schedule

# Schedule triggered by ontology events
@event_driven_schedule(
    event_type="object_type_created",
    object_type_pattern=".*_data$"
)
def process_new_data_types(context):
    """Process newly created data object types."""
    return RunRequest(
        run_key="setup_new_type",
        run_config={"new_type": context.event.object_type_name}
    )
```

## Types and Validation

### Custom Dagster Types

```python
from ontologia_dagster.types import OntologyDataFrame, OntologyInstance

# Custom type for ontology data frames
@dagster_type(loader=OntologyDataFrameLoader())
class OntologyDataFrame:
    """DataFrame with ontology metadata."""
    pass

# Custom type for ontology instances
@dagster_type(loader=OntologyInstanceLoader())
class OntologyInstance:
    """Ontology instance with type information."""
    pass

# Use in operations
@ontologia_op
def process_ontology_data(data: OntologyDataFrame) -> OntologyDataFrame:
    """Process data with ontology awareness."""
    # Access ontology metadata
    object_type = data.metadata.object_type
    properties = data.metadata.properties

    # Process with type awareness
    processed = data.copy()
    for prop in properties:
        if prop.type == "date":
            processed[prop.name] = pd.to_datetime(processed[prop.name])

    return processed
```

## Testing

### Unit Testing with Mock Ontology

```python
from ontologia_dagster.testing import MockOntologiaResource
from dagster import build_op_context

# Test with mock resource
def test_extract_customers():
    mock_ontologia = MockOntologiaResource()
    mock_ontologia.add_instances("Person", [
        {"id": "1", "name": "Alice", "type": "customer"},
        {"id": "2", "name": "Bob", "type": "prospect"}
    ])

    context = build_op_context(resources={"ontologia": mock_ontologia})
    result = extract_customers(context)

    assert len(result) == 2
    assert result.iloc[0]["name"] == "Alice"
```

### Integration Testing

```python
from ontologia_dagster.testing import OntoliaTestInstance

# Integration test with test instance
def test_full_pipeline():
    with OntoliaTestInstance() as test_instance:
        # Setup test data
        test_instance.create_object_type("Person", [
            {"name": "name", "type": "string"},
            {"name": "email", "type": "string"}
        ])

        # Run pipeline
        result = test_instance.run_job("customer_pipeline")

        # Verify results
        assert result.success
        customers = test_instance.list_instances("Person")
        assert len(customers) > 0
```

## Monitoring and Observability

### Asset Health Monitoring

```python
from ontologia_dagster.monitoring import asset_health_check

# Asset health sensor
@asset_health_check(asset_keys=["customer_data", "order_data"])
def ontology_asset_health(context):
    """Monitor health of ontology assets."""
    for asset_key in context.selected_asset_keys:
        asset_data = context.instance.get_latest_materialization(asset_key)

        if not asset_data:
            yield AssetCheckResult(
                asset_key=asset_key,
                passed=False,
                description="No materializations found"
            )
        elif asset_data.metadata.get("row_count", 0) == 0:
            yield AssetCheckResult(
                asset_key=asset_key,
                passed=False,
                description="Asset contains no data"
            )
        else:
            yield AssetCheckResult(
                asset_key=asset_key,
                passed=True,
                description=f"Asset healthy with {asset_data.metadata['row_count']} rows"
            )
```

### Performance Metrics

```python
from ontologia_dagster.metrics import track_ontology_performance

# Performance tracking decorator
@track_ontology_performance(
    metrics=["query_time", "result_count", "error_rate"]
)
@ontologia_op
def complex_ontology_query(ontology: OntologiaResource) -> pd.DataFrame:
    """Complex query with performance tracking."""
    # Query implementation
    result = ontology.complex_query(...)
    return result
```

## Best Practices

### Asset Organization

```python
# Group related assets
@ontologia_asset(group_name="customer_360")
def customer_profile(ontology: OntologiaResource) -> pd.DataFrame:
    """Customer profile data."""
    pass

@ontologia_asset(group_name="customer_360")
def customer_transactions(ontology: OntologiaResource) -> pd.DataFrame:
    """Customer transaction data."""
    pass

@ontologia_asset(group_name="customer_360")
def customer_metrics(ontology: OntologiaResource) -> pd.DataFrame:
    """Customer calculated metrics."""
    pass
```

### Error Handling

```python
from ontologia_dagster import handle_ontology_errors

@handle_ontology_errors(
    retry_on=[ConnectionError, TimeoutError],
    max_retries=3
)
@ontologia_op
def resilient_ontology_operation(ontology: OntologiaResource) -> None:
    """Operation with automatic error handling."""
    # Implementation with automatic retries
    pass
```

### Configuration Management

```python
from ontologia_dagster import OntologiaConfigSource

# Environment-specific configuration
config_source = OntologiaConfigSource(
    dev="configs/dev_ontologia.yaml",
    staging="configs/staging_ontologia.yaml",
    prod="configs/prod_ontologia.yaml"
)

@job(config=config_source)
def environment_aware_job():
    process_data()
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11

WORKDIR /opt/dagster/dagster_home

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Dagster code
COPY . .

# Install Dagster and Ontologia
RUN pip install dagster dagster-webserver ontologia-dagster

EXPOSE 3000

CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dagster-ontologia
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dagster-ontologia
  template:
    metadata:
      labels:
        app: dagster-ontologia
    spec:
      containers:
      - name: dagster
        image: ontologia-dagster:latest
        env:
        - name: ONTOLOGIA_BASE_URL
          value: "http://ontologia-service:8000"
        - name: ONTOLOGIA_API_KEY
          valueFrom:
            secretKeyRef:
              name: ontologia-secrets
              key: api-key
```

## Dependencies

Core dependencies:
- **dagster**: Data orchestration platform
- **ontologia-sdk**: Ontologia client library
- **pandas**: Data manipulation

Optional dependencies:
- **dagster-aws**: AWS integrations
- **dagster-gcp**: Google Cloud integrations
- **dagster-spark**: Apache Spark support
- **dbt-dagster**: DBT integration

## Version Information

Current version: `0.1.0`

Compatible with Dagster >= 1.0 and Ontologia >= 0.1.0.

## Contributing

When contributing to the Dagster integration:
1. Follow Dagster's asset and op patterns
2. Include comprehensive error handling
3. Add appropriate type annotations
4. Write tests for all components
5. Document configuration options

## License

This package is part of the Ontologia framework and follows the same license terms.
