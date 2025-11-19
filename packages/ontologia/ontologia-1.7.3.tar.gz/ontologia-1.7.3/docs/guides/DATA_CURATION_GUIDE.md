# Data Curation Guide

This guide covers data curation workflows in the Ontologia platform, including duplicate detection, entity resolution, and data quality management.

## Overview

Data curation is the process of maintaining data quality, resolving inconsistencies, and ensuring that data remains accurate and trustworthy. The Ontologia platform provides tools for automated duplicate detection and manual entity resolution.

## Key Concepts

### Entity Resolution

Entity resolution is the process of identifying and merging records that refer to the same real-world entity. This is crucial for maintaining data quality in systems where the same entity may be represented multiple times.

### Duplicates vs. Master Records

- **Duplicates**: Multiple records representing the same entity that need to be resolved
- **Master Records**: The authoritative record after resolving duplicates
- **Golden Records**: The most complete and accurate version of an entity's data

## Duplicate Detection

### Automatic Duplicate Detection

The platform can automatically detect potential duplicates using the DecisionEngine with configurable rules.

#### Setting Up Duplicate Detection Rules

Create rules in your DecisionEngine configuration to identify potential duplicates:

```yaml
# config/realtime/rules/duplicate_detection.yaml
- name: detect-duplicate-customers-by-email
  object_types: ["customer"]
  logic: all
  when:
    - component: properties
      field: email
      operator: "isnotnull"
  actions:
    - type: find_and_link_duplicates
      payload:
        match_on_field: "email"
        link_type: "possible_match"
        confidence_threshold: 0.8

- name: detect-duplicate-employees-by-name-and-dob
  object_types: ["employee"]
  logic: all
  when:
    - component: properties
      field: first_name
      operator: "isnotnull"
    - component: properties
      field: last_name
      operator: "isnotnull"
    - component: properties
      field: date_of_birth
      operator: "isnotnull"
  actions:
    - type: find_and_link_duplicates
      payload:
        match_on_fields: ["first_name", "last_name", "date_of_birth"]
        link_type: "possible_match"
        confidence_threshold: 0.9
```

### LinkType for Possible Matches

Define a LinkType to represent potential duplicates:

```yaml
# link_types/possible_match.yaml
apiName: possible_match
displayName: Possible Match
cardinality: MANY_TO_MANY
fromObjectType: customer
toObjectType: customer
inverse:
  apiName: possible_match_of
  displayName: Possible Match Of
properties:
  confidence_score:
    dataType: double
    displayName: Confidence Score
  match_fields:
    dataType: string
    displayName: Matched Fields
  detection_method:
    dataType: string
    displayName: Detection Method
```

## Entity Resolution Workflow

### Step 1: Detect Potential Duplicates

The system automatically creates `possible_match` links when data is ingested or updated:

```python
# When new customer data is ingested
new_customer = {
    "email": "john.doe@company.com",
    "name": "John Doe",
    "phone": "555-0123"
}

# System checks for existing customers with same email
# If found, creates possible_match link with confidence score
```

### Step 2: Review Potential Duplicates

Query for potential duplicates that need review:

```python
# Get all customers with potential duplicates
import requests

headers = {"Authorization": f"Bearer {jwt_token}"}

# Search for customers that have possible_match links
response = requests.post(
    "http://localhost:8000/v2/ontologies/default/objects/customer/search",
    json={
        "where": [
            {
                "property": "has_possible_matches",
                "op": "eq",
                "value": True
            }
        ]
    },
    headers=headers
)

customers_with_duplicates = response.json()['data']
```

### Step 3: Analyze Duplicate Candidates

For each customer with potential duplicates, analyze the details:

```python
def analyze_duplicate_candidates(customer_id):
    """Analyze potential duplicates for a customer"""

    # Get the customer and their possible matches
    customer_response = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/customer/{customer_id}",
        headers=headers
    )
    customer = customer_response.json()

    # Get linked possible matches
    matches_response = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/customer/{customer_id}/possible_match",
        headers=headers
    )
    matches = matches_response.json()['data']

    analysis_results = []

    for match in matches:
        # Get full details of potential duplicate
        match_details = requests.get(
            f"http://localhost:8000/v2/ontologies/default/objects/customer/{match['pkValue']}",
            headers=headers
        ).json()

        # Compare key fields
        comparison = {
            "match_id": match['pkValue'],
            "confidence_score": match.get('properties', {}).get('confidence_score', 0),
            "match_fields": match.get('properties', {}).get('match_fields', ''),
            "email_match": customer['properties']['email'] == match_details['properties']['email'],
            "name_similarity": calculate_name_similarity(
                customer['properties']['name'],
                match_details['properties']['name']
            ),
            "phone_match": customer['properties'].get('phone') == match_details['properties'].get('phone'),
            "address_match": compare_addresses(
                customer['properties'].get('address', {}),
                match_details['properties'].get('address', {})
            )
        }

        analysis_results.append(comparison)

    return analysis_results

def calculate_name_similarity(name1, name2):
    """Calculate similarity between two names"""
    # Simple implementation - can be enhanced with more sophisticated algorithms
    name1_words = set(name1.lower().split())
    name2_words = set(name2.lower().split())

    if not name1_words or not name2_words:
        return 0.0

    intersection = len(name1_words & name2_words)
    union = len(name1_words | name2_words)

    return intersection / union if union > 0 else 0.0

def compare_addresses(addr1, addr2):
    """Compare two addresses for similarity"""
    if not addr1 or not addr2:
        return True  # Both empty or missing

    # Compare key address components
    components = ['street', 'city', 'state', 'zip_code']
    matches = 0

    for component in components:
        if addr1.get(component) == addr2.get(component):
            matches += 1

    return matches == len(components)
```

### Step 4: Resolve Duplicates

Once you've identified which records represent the same entity, use the `system.merge_entities` action to resolve them:

```python
def resolve_duplicates(customer_id, duplicate_id, keep_record='newer'):
    """Resolve duplicates by merging records"""

    # Get both records to determine which to keep
    record1 = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/customer/{customer_id}",
        headers=headers
    ).json()

    record2 = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/customer/{duplicate_id}",
        headers=headers
    ).json()

    # Determine source and target based on keep_record preference
    if keep_record == 'newer':
        # Prefer the record with more recent data
        if record1.get('last_updated', '') > record2.get('last_updated', ''):
            source_rid = record2['rid']
            target_rid = record1['rid']
        else:
            source_rid = record1['rid']
            target_rid = record2['rid']
    else:
        # Prefer the more complete record
        record1_completeness = len([k for k, v in record1['properties'].items() if v])
        record2_completeness = len([k for k, v in record2['properties'].items() if v])

        if record1_completeness >= record2_completeness:
            target_rid = record1['rid']
            source_rid = record2['rid']
        else:
            target_rid = record2['rid']
            source_rid = record1['rid']

    # Execute the merge
    merge_response = requests.post(
        f"http://localhost:8000/v2/ontologies/default/objects/customer/{target_rid.split(':')[-1]}/actions/system.merge_entities",
        headers=headers,
        json={
            "parameters": {
                "source_rid": source_rid,
                "target_rid": target_rid
            }
        }
    )

    return merge_response.json()
```

## Automated Bulk Resolution

For large-scale duplicate resolution, you can implement automated bulk resolution:

```python
def bulk_resolve_duplicates(object_type, resolution_strategy='most_complete'):
    """Automatically resolve duplicates for an object type"""

    # Get all objects with potential duplicates
    response = requests.post(
        f"http://localhost:8000/v2/ontologies/default/objects/{object_type}/search",
        json={
            "where": [
                {
                    "property": "has_possible_matches",
                    "op": "eq",
                    "value": True
                }
            ]
        },
        headers=headers
    )

    objects_with_duplicates = response.json()['data']

    resolution_results = []

    for obj in objects_with_duplicates:
        obj_id = obj['pkValue']

        # Get all potential duplicates for this object
        matches_response = requests.get(
            f"http://localhost:8000/v2/ontologies/default/objects/{object_type}/{obj_id}/possible_match",
            headers=headers
        )

        matches = matches_response.json()['data']

        for match in matches:
            match_id = match['pkValue']
            confidence = match.get('properties', {}).get('confidence_score', 0)

            # Only auto-resolve high-confidence matches
            if confidence >= 0.95:
                try:
                    result = resolve_duplicates(obj_id, match_id, resolution_strategy)
                    resolution_results.append({
                        "status": "resolved",
                        "source": match_id,
                        "target": obj_id,
                        "confidence": confidence,
                        "result": result
                    })
                except Exception as e:
                    resolution_results.append({
                        "status": "failed",
                        "source": match_id,
                        "target": obj_id,
                        "confidence": confidence,
                        "error": str(e)
                    })

    return resolution_results
```

## Data Quality Monitoring

### Monitoring Duplicate Detection

Track the effectiveness of your duplicate detection system:

```python
def monitor_duplicate_detection(date_range):
    """Monitor duplicate detection metrics"""

    # Get all possible_match links created in the date range
    links_response = requests.post(
        "http://localhost:8000/v2/ontologies/default/objects/possible_match/search",
        json={
            "where": [
                {
                    "property": "created_date",
                    "op": "gte",
                    "value": date_range['start']
                },
                {
                    "property": "created_date",
                    "op": "lte",
                    "value": date_range['end']
                }
            ]
        },
        headers=headers
    )

    links = links_response.json()['data']

    # Analyze confidence scores
    confidence_scores = [link['properties']['confidence_score'] for link in links]

    metrics = {
        "total_duplicates_detected": len(links),
        "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
        "high_confidence_duplicates": len([s for s in confidence_scores if s >= 0.9]),
        "medium_confidence_duplicates": len([s for s in confidence_scores if 0.7 <= s < 0.9]),
        "low_confidence_duplicates": len([s for s in confidence_scores if s < 0.7])
    }

    return metrics
```

### Tracking Resolution Outcomes

Monitor what happens to detected duplicates:

```python
def track_resolution_outcomes():
    """Track how duplicates are being resolved"""

    # This would typically involve querying your audit logs or tracking database
    # Here's a conceptual implementation

    resolution_metrics = {
        "auto_resolved": 0,
        "manually_resolved": 0,
        "false_positives": 0,
        "pending_review": 0
    }

    # Query your tracking system for resolution outcomes
    # This would be implemented based on your specific tracking requirements

    return resolution_metrics
```

## Best Practices

### Duplicate Detection Rules

1. **Use Multiple Fields**: Combine multiple fields for more accurate matching
2. **Set Appropriate Thresholds**: Balance false positives vs. false negatives
3. **Consider Data Quality**: Account for data entry errors and variations
4. **Regular Review**: Periodically review and adjust detection rules

### Entity Resolution

1. **Preserve Data History**: Keep records of what was merged and when
2. **Manual Review**: Require manual review for low-confidence matches
3. **Undo Capability**: Maintain ability to undo merges if needed
4. **Stakeholder Communication**: Notify stakeholders when their data is affected

### Data Quality

1. **Continuous Monitoring**: Regularly monitor data quality metrics
2. **Feedback Loops**: Use resolution outcomes to improve detection rules
3. **Documentation**: Document data quality standards and procedures
4. **Training**: Train data stewards on resolution processes

## Troubleshooting

### Common Issues

**Problem**: Too many false positives in duplicate detection
- **Solution**: Adjust confidence thresholds and add more specific matching criteria

**Problem**: Missing duplicates that should be detected
- **Solution**: Add additional matching fields or use fuzzy matching algorithms

**Problem**: Merge operations failing
- **Solution**: Check for constraint violations or data inconsistencies before merging

**Problem**: Performance issues with large datasets
- **Solution**: Implement batch processing and optimize duplicate detection queries

### Debugging Tools

```python
def debug_duplicate_detection(object_type, entity_id):
    """Debug why an entity was or wasn't flagged as duplicate"""

    # Get the entity details
    entity = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/{object_type}/{entity_id}",
        headers=headers
    ).json()

    # Check for possible matches
    matches_response = requests.get(
        f"http://localhost:8000/v2/ontologies/default/objects/{object_type}/{entity_id}/possible_match",
        headers=headers
    )

    matches = matches_response.json()['data']

    debug_info = {
        "entity": entity,
        "potential_matches": matches,
        "detection_rules_applied": get_applied_detection_rules(object_type),
        "field_analysis": analyze_matching_fields(entity, matches)
    }

    return debug_info

def get_applied_detection_rules(object_type):
    """Get the detection rules that were applied to an object type"""
    # This would query your DecisionEngine configuration
    # Implementation depends on how you store and access rule configurations
    return []

def analyze_matching_fields(entity, matches):
    """Analyze which fields triggered duplicate detection"""

    entity_props = entity['properties']
    field_analysis = {}

    for match in matches:
        match_props = requests.get(
            f"http://localhost:8000/v2/ontologies/default/objects/{entity['objectTypeApiName']}/{match['pkValue']}",
            headers=headers
        ).json()['properties']

        matching_fields = []
        for field, value in entity_props.items():
            if match_props.get(field) == value:
                matching_fields.append(field)

        field_analysis[match['pkValue']] = {
            "matching_fields": matching_fields,
            "confidence_score": match.get('properties', {}).get('confidence_score', 0)
        }

    return field_analysis
```

## Integration with Other Systems

### CRM Integration

Integrate entity resolution with CRM systems:

```python
def sync_resolved_entities_to_crm(resolved_entities):
    """Sync resolved entities to external CRM system"""

    for entity in resolved_entities:
        crm_data = {
            "entity_id": entity['target_id'],
            "merged_from": entity['source_id'],
            "merge_timestamp": entity['merge_timestamp'],
            "merged_properties": entity['merged_properties']
        }

        # Call CRM API to update the merged record
        crm_response = requests.post(
            f"https://your-crm.com/api/entities/{entity['target_id']}/merge",
            headers={"Authorization": f"Bearer {CRM_API_TOKEN}"},
            json=crm_data
        )

        if crm_response.status_code != 200:
            log_error(f"Failed to sync entity {entity['target_id']} to CRM")
```

### Data Warehouse Integration

Update data warehouse with resolved master records:

```python
def update_data_warehouse(resolved_entity):
    """Update data warehouse with resolved master record"""

    warehouse_payload = {
        "operation": "merge",
        "target_table": "customers_master",
        "target_key": resolved_entity['target_id'],
        "source_records": [resolved_entity['source_id']],
        "merged_record": resolved_entity['merged_properties'],
        "merge_metadata": {
            "merge_timestamp": resolved_entity['merge_timestamp'],
            "merge_method": "automatic",
            "confidence_score": resolved_entity['confidence_score']
        }
    }

    # Send to data warehouse update system
    warehouse_response = requests.post(
        "https://your-warehouse.com/api/update",
        headers={"Authorization": f"Bearer {WAREHOUSE_TOKEN}"},
        json=warehouse_payload
    )

    return warehouse_response.json()
```

## Conclusion

Effective data curation is essential for maintaining data quality and ensuring trustworthy analytics. The Ontologia platform provides a comprehensive set of tools for:

- **Automated duplicate detection** using configurable rules
- **Manual review processes** for ambiguous cases
- **Entity resolution** with the `system.merge_entities` action
- **Quality monitoring** to track system effectiveness

By implementing these workflows, you can maintain high-quality data that supports accurate business decisions and reliable analytics.

Regular monitoring and continuous improvement of your duplicate detection rules will ensure the system remains effective as your data evolves.
