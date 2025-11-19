# What-If Scenarios Guide

This guide covers the "what-if" analysis capabilities of the Ontologia platform, allowing you to simulate changes to your data without affecting the production environment.

## Overview

The what-if functionality enables you to create temporary, virtual views of your data by applying ChangeSet overlays. This is particularly useful for:

- **Impact Analysis**: See how changes would affect your data before committing
- **Scenario Planning**: Test different business scenarios in isolation
- **Data Validation**: Verify that changes produce expected results
- **Collaborative Decision Making**: Share scenarios with stakeholders for review

## Key Concepts

### ChangeSet

A ChangeSet is a collection of proposed changes to your data that can be applied as an overlay. Changes can include:

- **Upsert**: Create or update objects
- **Delete**: Remove objects
- **Modify**: Update specific properties of existing objects

### Overlay Mechanism

When you make API requests with a ChangeSet RID, the system:

1. **Loads Base Data**: Retrieves the current data from the database
2. **Applies Overlay**: Applies the changes from the specified ChangeSet
3. **Returns Virtual View**: Shows what the data would look like with the changes
4. **No Persistence**: Changes are not saved to the database

## API Usage

### Header-Based Activation

Activate what-if mode by adding the `X-Ontologia-ChangeSet-Rid` header to your API requests:

```http
GET /v2/ontologies/default/objects/customer/123
X-Ontologia-ChangeSet-Rid: cs.12345678-abcd-efgh-ijkl-123456789012
```

### Supported Endpoints

The what-if functionality works with all read endpoints:

- `GET /objects/{objectTypeApiName}/{pk}` - Get single object
- `GET /objects` - List objects
- `POST /objects/search` - Search objects
- `GET /linked-objects/{linkTypeApiName}` - Get linked objects

## Creating Scenarios

### Step 1: Create a ChangeSet

```python
from api.services.change_set_service import ChangeSetService
from api.v2.schemas.change_sets import ChangeSetCreateRequest

# Initialize the service
cs_service = ChangeSetService(session, service="ontology", instance="default")

# Create a new ChangeSet
change_set = cs_service.create_change_set(
    ChangeSetCreateRequest(
        name="Q4 Price Increase Simulation",
        description="Simulate 10% price increase for all products",
        target_object_type="product"
    )
)

print(f"ChangeSet RID: {change_set.rid}")
```

### Step 2: Add Changes to the ChangeSet

```python
# Add price increase changes
changes = [
    {
        "op": "upsert",
        "pk": "prod_001",
        "properties": {
            "price": 110.00,  # 10% increase from 100.00
            "price_category": "premium"
        }
    },
    {
        "op": "upsert",
        "pk": "prod_002",
        "properties": {
            "price": 55.00,   # 10% increase from 50.00
            "price_category": "premium"
        }
    },
    {
        "op": "delete",
        "pk": "prod_999",  # Discontinued product
        "properties": {}
    }
]

# Add changes to the ChangeSet
cs_service.add_changes_to_change_set(change_set.rid, changes)
```

### Step 3: Use the Scenario in API Calls

```python
import requests

# Set up the headers with ChangeSet RID
headers = {
    "Authorization": f"Bearer {your_jwt_token}",
    "X-Ontologia-ChangeSet-Rid": change_set.rid
}

# Get the virtual view with changes applied
response = requests.get(
    "http://localhost:8000/v2/ontologies/default/objects/product/prod_001",
    headers=headers
)

product_data = response.json()
print(f"Virtual price: {product_data['properties']['price']}")  # 110.00
```

## Real-World Examples

### Example 1: Price Impact Analysis

**Scenario**: Your company is considering a 15% price increase across all products and wants to understand the impact on revenue.

```python
# 1. Create ChangeSet
price_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(
        name="Q1 2024 Price Increase Analysis",
        description="15% price increase across all product categories",
        target_object_type="product"
    )
)

# 2. Apply price increases
all_products = get_all_products()  # Your method to get current products
price_changes = []

for product in all_products:
    new_price = product['price'] * 1.15
    price_changes.append({
        "op": "upsert",
        "pk": product['id'],
        "properties": {
            "price": round(new_price, 2),
            "price_effective_date": "2024-01-01"
        }
    })

cs_service.add_changes_to_change_set(price_scenario.rid, price_changes)

# 3. Analyze impact
headers = {"X-Ontologia-ChangeSet-Rid": price_scenario.rid}
response = requests.post(
    "http://localhost:8000/v2/ontologies/default/objects/search",
    json={
        "objectType": "order",
        "where": [
            {"property": "order_date", "op": "gte", "value": "2024-01-01"},
            {"property": "order_date", "op": "lt", "value": "2024-04-01"}
        ]
    },
    headers=headers
)

# Calculate projected revenue with new prices
orders = response.json()['data']
projected_revenue = sum(order['properties']['total_amount'] for order in orders)
print(f"Projected Q1 revenue with price increase: ${projected_revenue:,.2f}")
```

### Example 2: Organizational Restructuring

**Scenario**: Your company is reorganizing departments and needs to see how employee assignments would change.

```python
# 1. Create ChangeSet for reorganization
reorg_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(
        name="Q2 Department Reorganization",
        description="Move employees to new department structure",
        target_object_type="employee"
    )
)

# 2. Define new department assignments
reorg_changes = [
    {
        "op": "upsert",
        "pk": "emp_001",
        "properties": {
            "department": "Data Science",
            "team": "Advanced Analytics",
            "manager_id": "mgr_456"
        }
    },
    {
        "op": "upsert",
        "pk": "emp_002",
        "properties": {
            "department": "Data Science",
            "team": "Machine Learning",
            "manager_id": "mgr_456"
        }
    },
    {
        "op": "upsert",
        "pk": "emp_003",
        "properties": {
            "department": "Engineering",
            "team": "Platform Infrastructure",
            "manager_id": "mgr_789"
        }
    }
]

cs_service.add_changes_to_change_set(reorg_scenario.rid, reorg_changes)

# 3. Analyze new structure
headers = {"X-Ontologia-ChangeSet-Rid": reorg_scenario.rid}

# Get department counts
for dept in ["Data Science", "Engineering", "Product"]:
    response = requests.post(
        f"http://localhost:8000/v2/ontologies/default/objects/search",
        json={
            "objectType": "employee",
            "where": [{"property": "department", "op": "eq", "value": dept}]
        },
        headers=headers
    )
    count = len(response.json()['data'])
    print(f"{dept}: {count} employees")

# Check manager reporting lines
manager_response = requests.post(
    "http://localhost:8000/v2/ontologies/default/objects/search",
    json={
        "objectType": "employee",
        "where": [{"property": "manager_id", "op": "eq", "value": "mgr_456"}]
    },
    headers=headers
)
direct_reports = len(manager_response.json()['data'])
print(f"Manager mgr_456 would have {direct_reports} direct reports")
```

### Example 3: Customer Segmentation Analysis

**Scenario**: Testing different customer segmentation strategies without modifying the actual data.

```python
# 1. Create ChangeSet for segmentation
segmentation_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(
        name="Customer Segmentation Strategy A",
        description="Test value-based customer segmentation",
        target_object_type="customer"
    )
)

# 2. Apply segmentation logic
customers = get_all_customers()
segment_changes = []

for customer in customers:
    total_spend = customer.get('total_purchases', 0)
    order_count = customer.get('order_count', 0)

    # Determine segment based on spending patterns
    if total_spend > 10000 and order_count > 20:
        segment = "VIP"
        tier = "Platinum"
    elif total_spend > 5000 and order_count > 10:
        segment = "Premium"
        tier = "Gold"
    elif total_spend > 1000:
        segment = "Standard"
        tier = "Silver"
    else:
        segment = "Basic"
        tier = "Bronze"

    segment_changes.append({
        "op": "upsert",
        "pk": customer['id'],
        "properties": {
            "customer_segment": segment,
            "loyalty_tier": tier,
            "segmentation_date": datetime.now().isoformat()
        }
    })

cs_service.add_changes_to_change_set(segmentation_scenario.rid, segment_changes)

# 3. Analyze segmentation results
headers = {"X-Ontologia-ChangeSet-Rid": segmentation_scenario.rid}

# Get segment distribution
segments = ["VIP", "Premium", "Standard", "Basic"]
for segment in segments:
    response = requests.post(
        "http://localhost:8000/v2/ontologies/default/objects/search",
        json={
            "objectType": "customer",
            "where": [{"property": "customer_segment", "op": "eq", "value": segment}]
        },
        headers=headers
    )
    count = len(response.json()['data'])
    print(f"{segment} segment: {count} customers")

# Calculate average order value by segment
for segment in segments:
    response = requests.post(
        "http://localhost:8000/v2/ontologies/default/objects/search",
        json={
            "objectType": "customer",
            "where": [{"property": "customer_segment", "op": "eq", "value": segment}]
        },
        headers=headers
    )
    customers_in_segment = response.json()['data']

    if customers_in_segment:
        avg_spend = sum(c['properties']['total_purchases'] for c in customers_in_segment) / len(customers_in_segment)
        print(f"{segment} average spend: ${avg_spend:.2f}")
```

## Advanced Usage

### Combining Multiple Scenarios

You can create multiple ChangeSets to compare different scenarios:

```python
# Scenario A: Conservative price increase (5%)
conservative_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(name="Conservative Price Increase", target_object_type="product")
)

# Scenario B: Aggressive price increase (20%)
aggressive_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(name="Aggressive Price Increase", target_object_type="product")
)

# Apply different price changes to each scenario
for product in get_all_products():
    base_price = product['price']

    # Conservative changes
    cs_service.add_changes_to_change_set(conservative_scenario.rid, [{
        "op": "upsert",
        "pk": product['id'],
        "properties": {"price": base_price * 1.05}
    }])

    # Aggressive changes
    cs_service.add_changes_to_change_set(aggressive_scenario.rid, [{
        "op": "upsert",
        "pk": product['id'],
        "properties": {"price": base_price * 1.20}
    }])

# Compare scenarios
for scenario_name, scenario_rid in [
    ("Conservative", conservative_scenario.rid),
    ("Aggressive", aggressive_scenario.rid)
]:
    headers = {"X-Ontologia-ChangeSet-Rid": scenario_rid}
    # Calculate revenue projection for each scenario
    revenue = calculate_projected_revenue(headers)
    print(f"{scenario_name} scenario projected revenue: ${revenue:,.2f}")
```

### Temporary Data Testing

Use ChangeSets to test data quality with temporary test data:

```python
# Create test data scenario
test_scenario = cs_service.create_change_set(
    ChangeSetCreateRequest(
        name="Data Quality Test Scenario",
        description="Add test data for quality validation",
        target_object_type="order"
    )
)

# Add test orders with various data quality scenarios
test_orders = [
    {
        "op": "upsert",
        "pk": "test_order_001",
        "properties": {
            "customer_id": "test_customer_001",
            "order_date": "2024-01-15",
            "total_amount": 150.00,
            "status": "completed"
        }
    },
    {
        "op": "upsert",
        "pk": "test_order_002",
        "properties": {
            "customer_id": "test_customer_001",
            "order_date": "2024-01-20",
            "total_amount": -25.00,  # Invalid negative amount
            "status": "completed"
        }
    }
]

cs_service.add_changes_to_change_set(test_scenario.rid, test_orders)

# Test data quality rules
headers = {"X-Ontologia-ChangeSet-Rid": test_scenario.rid}
response = requests.post(
    "http://localhost:8000/v2/ontologies/default/objects/search",
    json={
        "objectType": "order",
        "where": [{"property": "total_amount", "op": "lt", "value": 0}]
    },
    headers=headers
)

invalid_orders = response.json()['data']
print(f"Found {len(invalid_orders)} orders with invalid amounts")
```

## Best Practices

### ChangeSet Management

1. **Descriptive Names**: Use clear, descriptive names for your ChangeSets
2. **Regular Cleanup**: Remove old ChangeSets that are no longer needed
3. **Version Control**: Consider tracking important scenarios in version control
4. **Documentation**: Document the purpose and expected outcomes of each scenario

### Performance Considerations

1. **Large ChangeSets**: Be mindful of performance with very large ChangeSets
2. **Caching**: The system caches ChangeSet data for better performance
3. **Concurrent Scenarios**: Multiple users can use different ChangeSets simultaneously

### Collaboration

1. **Shared Scenarios**: Share ChangeSet RIDs with team members for collaborative analysis
2. **Review Process**: Use ChangeSets as part of a formal review process for data changes
3. **Documentation**: Document assumptions and methodologies used in scenarios

## Limitations

### Read-Only Operations

ChangeSets only work with read operations. You cannot use them with:
- `PUT /objects` (Create/update operations)
- `DELETE /objects` (Delete operations)
- `POST /actions` (Action executions)

### Data Consistency

ChangeSets provide a virtual view and don't enforce:
- Foreign key constraints
- Unique constraints
- Data type validations
- Business rules

### Temporary Nature

ChangeSets are stored in memory and:
- Are lost when the application restarts
- Don't persist across sessions
- Should be used for analysis, not long-term storage

## Troubleshooting

### Common Issues

**Problem**: Changes from ChangeSet are not visible
- **Solution**: Ensure the `X-Ontologia-ChangeSet-Rid` header is correctly set and the ChangeSet exists

**Problem**: Getting 404 errors with ChangeSet
- **Solution**: Verify that the ChangeSet RID is valid and the ChangeSet targets the correct object type

**Problem**: Performance issues with large ChangeSets
- **Solution**: Consider breaking large scenarios into smaller, more focused ChangeSets

### Debugging ChangeSets

To debug ChangeSet issues:

1. **Verify ChangeSet exists**: Check that the ChangeSet RID is valid
2. **Check target object type**: Ensure the ChangeSet targets the correct object type
3. **Validate change format**: Make sure changes follow the correct JSON format
4. **Test with simple scenarios**: Start with simple changes before complex ones

## Integration with CI/CD

### Automated Testing

Include ChangeSet-based testing in your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Test Data Scenarios
  run: |
    # Create test scenario
    CS_RID=$(curl -X POST "http://api/changesets" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name": "CI Test Scenario", "targetObjectType": "customer"}' | jq -r '.rid')

    # Add test changes
    curl -X POST "http://api/changesets/$CS_RID/changes" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"changes": [{"op": "upsert", "pk": "test_001", "properties": {"name": "Test Customer"}}]}'

    # Test scenario
    curl -X GET "http://api/v2/ontologies/default/objects/customer/test_001" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-Ontologia-ChangeSet-Rid: $CS_RID"
```

### Scenario Validation

Use ChangeSets to validate data migrations and schema changes before deployment:

```python
def validate_migration_scenario(migration_changes):
    """Validate that migration changes don't break existing functionality"""

    # Create validation scenario
    scenario = cs_service.create_change_set(
        ChangeSetCreateRequest(
            name="Migration Validation",
            description="Validate migration changes",
            target_object_type="customer"
        )
    )

    # Apply migration changes
    cs_service.add_changes_to_change_set(scenario.rid, migration_changes)

    # Test critical workflows
    test_results = []

    # Test 1: Customer search still works
    headers = {"X-Ontologia-ChangeSet-Rid": scenario.rid}
    search_result = search_customers("active", headers)
    test_results.append(("customer_search", len(search_result) > 0))

    # Test 2: Orders can still be placed
    test_order = create_test_order(headers)
    test_results.append(("order_creation", test_order is not None))

    # Test 3: Reports generate correctly
    report_data = generate_customer_report(headers)
    test_results.append(("report_generation", len(report_data) > 0))

    # Return validation results
    return all(result[1] for result in test_results), test_results
```

## Conclusion

The what-if scenarios functionality provides a powerful tool for data analysis and decision making. By using ChangeSets, you can:

- Test changes without risk to production data
- Compare multiple scenarios side-by-side
- Collaborate with stakeholders on data-driven decisions
- Validate assumptions before implementing changes

This functionality makes the Ontologia platform a true data analysis and planning tool, not just a data storage system.
