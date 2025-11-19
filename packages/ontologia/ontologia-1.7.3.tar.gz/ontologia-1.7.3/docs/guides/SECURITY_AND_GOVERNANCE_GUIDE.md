# Security and Governance Guide

This guide covers the security and governance features of the Ontologia platform, including Role-Based Access Control (RBAC), Attribute-Based Access Control (ABAC), and data governance capabilities.

## Overview

Ontologia provides a comprehensive security model that operates at multiple levels:

- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based permissions (RBAC)
- **Data Access Control**: Property-level access control using security tags (ABAC)
- **Data Governance**: Dataset ownership and metadata management

## Authentication and Roles

### JWT Authentication

The platform uses JSON Web Tokens (JWT) for authentication. Users authenticate by providing credentials and receive a JWT that contains their roles and permissions.

### Built-in Roles

The system comes with predefined roles with different permission levels:

| Role | Description | Capabilities |
|------|-------------|--------------|
| `viewer` | Read-only access | Can view objects, subject to ABAC policies |
| `editor` | Read and write access | Can modify objects, subject to ABAC policies |
| `admin` | Full administrative access | Can perform all operations, bypass ABAC restrictions |

### Role Priority

Roles have a hierarchical priority:
- `viewer`: priority 0
- `editor`: priority 1
- `admin`: priority 2

Higher priority roles inherit all capabilities of lower priority roles.

## Attribute-Based Access Control (ABAC)

### Overview

ABAC allows you to control access to individual properties within objects based on security tags and user roles. This provides fine-grained control over sensitive data.

### How It Works

1. **Property Definition**: Define security tags on object properties in your ontology definition
2. **Policy Configuration**: Configure role-to-tag mappings in your settings
3. **Automatic Filtering**: The system automatically filters properties based on user permissions

### Configuration

#### 1. Add Security Tags to Properties

In your ontology YAML definition, add `securityTags` to properties:

```yaml
objectTypes:
  user:
    displayName: "User"
    primaryKey: "id"
    properties:
      id:
        dataType: "string"
        displayName: "ID"
        required: true
      name:
        dataType: "string"
        displayName: "Full Name"
      email:
        dataType: "string"
        displayName: "Email Address"
        securityTags: ["PII"]  # Only accessible to authorized roles
      ssn:
        dataType: "string"
        displayName: "Social Security Number"
        securityTags: ["PII", "HIGHLY_SENSITIVE"]  # Requires special permissions
      salary:
        dataType: "double"
        displayName: "Annual Salary"
        securityTags: ["FINANCIAL", "CONFIDENTIAL"]
```

#### 2. Configure Role-to-Tag Mappings

In your `ontologia.toml` configuration file:

```toml
[security.abac]
enabled = true
role_allowed_tags = {
  admin = ["*"],                    # Admin can access all tags
  editor = ["PII"],                  # Editor can access PII data
  viewer = []                        # Viewer has no special access
}
```

#### 3. Environment Variables

You can also configure using environment variables:

```bash
ABAC_ENABLED=true
ABAC_ROLE_ALLOWED_TAGS='{"admin": ["*"], "editor": ["PII"], "viewer": []}'
```

### Policy Evaluation Rules

The system follows these rules when evaluating access:

1. **Disabled ABAC**: If `abac_enabled` is false, all properties are visible
2. **No Security Tags**: Properties without `securityTags` are visible to all users
3. **Anonymous Users**: Users without authentication are denied access to tagged properties
4. **Wildcard Access**: Users with roles mapped to `["*"]` can access all tagged properties
5. **Tag Matching**: Users can access properties if their allowed tags include any of the property's security tags

### Examples

#### Example 1: Basic PII Protection

```yaml
# ontologia.toml
[security.abac]
enabled = true
role_allowed_tags = { admin = ["*"], viewer = [] }

# ontology definition
properties:
  name:
    dataType: "string"
    displayName: "Name"
    # No securityTags - visible to everyone
  ssn:
    dataType: "string"
    displayName: "SSN"
    securityTags: ["PII"]  # Only visible to admin
```

Result:
- **Admin users**: Can see both `name` and `ssn` properties
- **Viewer users**: Can only see `name` property

#### Example 2: Financial Data Protection

```yaml
# ontologia.toml
[security.abac]
enabled = true
role_allowed_tags = {
  admin = ["*"],
  hr_manager = ["FINANCIAL", "PII"],
  employee = ["PII"]
}

# ontology definition
properties:
  name:
    dataType: "string"
    displayName: "Name"
    securityTags: ["PII"]
  salary:
    dataType: "double"
    displayName: "Salary"
    securityTags: ["FINANCIAL", "CONFIDENTIAL"]
  department:
    dataType: "string"
    displayName: "Department"
    # No security tags - visible to everyone
```

Result:
- **Admin users**: Can see all properties
- **HR Managers**: Can see all properties (has both FINANCIAL and PII tags)
- **Employees**: Can see `name` and `department`, but not `salary`

## API Impact

### Property Filtering in API Responses

When ABAC is enabled, API responses automatically filter properties based on user permissions. Properties that the user is not authorized to access are simply omitted from the response.

#### Example Response

**Admin user request:**
```json
{
  "rid": "user:123",
  "objectTypeApiName": "user",
  "pkValue": "123",
  "properties": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "ssn": "123-45-6789"
  }
}
```

**Viewer user request:**
```json
{
  "rid": "user:123",
  "objectTypeApiName": "user",
  "pkValue": "123",
  "properties": {
    "id": "123",
    "name": "John Doe"
    // email and ssn are omitted due to ABAC policies
  }
}
```

## Data Governance

### Dataset Ownership

Datasets can be assigned ownership and contact information for governance purposes:

```python
# When creating datasets programmatically
dataset = Dataset(
    api_name="customer_data",
    display_name="Customer Master Data",
    owner_team="data_platform",
    contact_email="data-platform@company.com",
    update_frequency="daily"
)
```

### Data Quality and Contracts

Use the `ontologia test-contract` command to validate that your physical data matches your ontology definitions:

```bash
# Validate data contracts
ontologia test-contract --dir ./ontologia

# Output example
✅ Dataset 'customers_gold' matches schema for ObjectType 'customer'
❌ Dataset 'orders_gold' type mismatch for property 'order_date': expected timestamp, found string
✅ All other datasets are valid
```

## Best Practices

### Security Tag Naming

Use consistent and descriptive security tag names:

- `PII` - Personally Identifiable Information
- `FINANCIAL` - Financial data (salary, revenue, costs)
- `CONFIDENTIAL` - Company confidential information
- `INTERNAL_ONLY` - Data for internal use only
- `PUBLIC` - Data that can be shared publicly

### Principle of Least Privilege

- Start with minimal permissions and grant additional access as needed
- Regularly review and audit security tag assignments
- Use specific tags rather than broad categories when possible

### Testing and Validation

1. **Test with different user roles** to ensure proper filtering
2. **Use the test-contract command** in CI/CD pipelines
3. **Monitor access logs** for unauthorized access attempts
4. **Regular security audits** of property access patterns

## Troubleshooting

### Common Issues

**Problem**: Users can't see properties they should have access to
- **Solution**: Check that the user's role is properly mapped to the required security tags in the configuration

**Problem**: Properties are being filtered unexpectedly
- **Solution**: Verify that `abac_enabled` is set to `true` and that the security tags are correctly defined

**Problem**: Anonymous users are being denied access
- **Solution**: This is expected behavior for tagged properties. Consider whether the property should have security tags

### Debugging ABAC

To debug ABAC issues, you can:

1. Check the user's JWT token to verify their roles
2. Review the security tag configuration in `ontologia.toml`
3. Verify the property definitions in your ontology YAML
4. Test with different user roles to isolate permission issues

## Integration with External Systems

### SSO Integration

The JWT-based authentication can integrate with external identity providers:

1. Configure your SSO provider to issue JWT tokens with the expected format
2. Map external roles to Ontologia roles in your authentication middleware
3. Ensure the security tag mappings align with your organizational structure

### Audit Logging

All property access decisions are logged and can be audited for compliance purposes. Monitor logs for:

- Failed access attempts to sensitive properties
- Unusual access patterns
- Changes to security tag configurations

## Migration Guide

### Enabling ABAC on Existing Systems

1. **Phase 1**: Enable ABAC in configuration but don't add security tags yet
2. **Phase 2**: Gradually add security tags to sensitive properties
3. **Phase 3**: Configure role-to-tag mappings based on organizational needs
4. **Phase 4**: Test with different user roles and validate filtering behavior

### Rollback Plan

If issues arise, you can disable ABAC by setting:

```bash
ABAC_ENABLED=false
```

This will restore visibility of all properties to all users while you troubleshoot the configuration.
