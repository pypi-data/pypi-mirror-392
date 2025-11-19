# Ontologia CLI - Command Line Interface Package

## Overview

The `ontologia_cli` package provides a comprehensive command-line interface for the Ontologia framework. This tool enables developers, data engineers, and system administrators to interact with ontology management capabilities directly from the terminal, supporting everything from basic CRUD operations to complex workflow orchestration and SDK generation.

## Installation

```bash
# Install as part of the ontologia framework
pip install ontologia[cli]

# Or install standalone
pip install ontologia-cli
```

## Quick Start

```bash
# Initialize connection to Ontologia server
ontologia config set --server-url http://localhost:8000

# Login for authenticated operations
ontologia auth login --username user@example.com

# List available object types
ontologia object-types list

# Create a new object type
ontologia object-types create --name Person --properties name:string,email:string

# Generate SDK for current ontology
ontologia generate-sdk --output-dir ./generated-sdk
```

## Command Structure

The CLI follows a hierarchical command structure:

```
ontologia <command> <subcommand> [options]
```

### Main Commands

- **`config`** - Manage configuration settings
- **`auth`** - Authentication and authorization
- **`object-types`** - Ontology schema management
- **`instances`** - Instance CRUD operations
- **`links`** - Relationship management
- **`search`** - Query and search operations
- **`actions`** - Workflow and action execution
- **`datasets`** - Data catalog management
- **`generate-sdk`** - Client SDK generation
- **`playground`** - Interactive development environment
- **`migrate`** - Database migration management

## Configuration Management

### Server Configuration

```bash
# Set server URL
ontologia config set --server-url http://localhost:8000

# Set authentication method
ontologia config set --auth-method jwt

# Configure timeouts
ontologia config set --timeout 30

# View current configuration
ontologia config get

# Reset configuration
ontologia config reset
```

### Configuration File

The CLI stores configuration in `~/.ontologia/config.yaml`:

```yaml
server:
  url: http://localhost:8000
  timeout: 30
  verify_ssl: true

auth:
  method: jwt
  token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

preferences:
  output_format: table
  color: true
  verbose: false
```

## Authentication

### JWT Authentication

```bash
# Login with username/password
ontologia auth login --username user@example.com
# Password will be prompted securely

# Login with API key
ontologia auth login --api-key your-api-key-here

# Check current authentication status
ontologia auth status

# Logout and clear credentials
ontologia auth logout

# Refresh token
ontologia auth refresh
```

### Service Account Authentication

```bash
# Use service account credentials
ontologia auth login --service-account --key-file service-account.json

# Impersonate user (admin only)
ontologia auth login --impersonate user@example.com
```

## Ontology Schema Management

### Object Types

```bash
# List all object types
ontologia object-types list

# Get detailed object type information
ontologia object-types get --name Person

# Create new object type
ontologia object-types create \
  --name Person \
  --description "A person in the system" \
  --properties name:string:required,email:string:email,age:integer:min=0

# Update object type
ontologia object-types update \
  --name Person \
  --add-properties address:string,phone:string \
  --remove-properties age

# Delete object type
ontologia object-types delete --name Person --confirm

# Export object type schema
ontologia object-types export --name Person --format yaml > person.yaml

# Import object type from file
ontologia object-types import --file person.yaml
```

### Property Types

```bash
# List available property types
ontologia object-types property-types list

# Create custom property type
ontologia object-types property-types create \
  --name email \
  --type string \
  --format email \
  --description "Email address format"

# Validate property type
ontologia object-types property-types validate \
  --type email \
  --value user@example.com
```

### Link Types

```bash
# List relationship types
ontologia links types list

# Create new link type
ontologia links types create \
  --name works_for \
  --source Person \
  --target Company \
  --cardinality many-to-one \
  --description "Person works for company"

# Update link type
ontologia links types update \
  --name works_for \
  --cardinality many-to-many
```

## Instance Management

### CRUD Operations

```bash
# List instances with filtering
ontologia instances list \
  --object-type Person \
  --limit 10 \
  --offset 0

# Search instances
ontologia instances search \
  --query "name:John AND age:>25" \
  --object-type Person

# Create new instance
ontologia instances create \
  --object-type Person \
  --data '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Create instance from JSON file
ontologia instances create \
  --object-type Person \
  --file person_data.json

# Get specific instance
ontologia instances get --id person_123

# Update instance
ontologia instances update \
  --id person_123 \
  --data '{"age": 31}'

# Patch instance (partial update)
ontologia instances patch \
  --id person_123 \
  --data '{"email": "john.doe@example.com"}'

# Delete instance
ontologia instances delete --id person_123 --confirm
```

### Bulk Operations

```bash
# Bulk create from CSV
ontologia instances bulk-create \
  --object-type Person \
  --file persons.csv \
  --mapping name=name,email=email,age=age

# Bulk update from JSON
ontologia instances bulk-update \
  --file updates.json

# Bulk delete with filter
ontologia instances bulk-delete \
  --object-type Person \
  --filter "age:<18" --confirm
```

## Relationship Management

### Link Operations

```bash
# List relationships
ontologia links list \
  --source-type Person \
  --target-type Company

# Create relationship
ontologia links create \
  --type works_for \
  --source person_123 \
  --target company_456

# Create multiple relationships
ontologia links create \
  --type works_for \
  --source person_123 \
  --targets company_456,company_789

# Get relationship details
ontologia links get --id link_789

# Delete relationship
ontologia links delete --id link_789 --confirm

# Find related instances
ontologia links find-related \
  --instance person_123 \
  --relationship works_for
```

## Search and Query

### Search Operations

```bash
# Full-text search
ontologia search query "John Doe"

# Search within object type
ontologia search query \
  --object-type Person \
  "email:@example.com"

# Advanced search with filters
ontologia search query \
  --object-type Person \
  --filters "age:>25,email:*@company.com" \
  --sort name:asc \
  --limit 5

# Faceted search
ontologia search facets \
  --object-type Person \
  --facets age_range,department
```

### Query Builder

```bash
# Interactive query builder
ontologia search build

# Execute saved query
ontologia search execute --query-file my_query.json

# Export query results
ontologia search query \
  --query "name:John" \
  --format csv \
  --output results.csv
```

## Actions and Workflows

### Action Management

```bash
# List available actions
ontologia actions list

# Get action details
ontologia actions get --name validate_data

# Execute action
ontologia actions execute \
  --name validate_data \
  --parameters '{"dataset": "customers"}'

# Execute action asynchronously
ontologia actions execute \
  --name validate_data \
  --parameters '{"dataset": "customers"}' \
  --async

# Monitor action execution
ontologia actions status --execution-id exec_123

# Cancel running action
ontologia actions cancel --execution-id exec_123
```

### Workflow Management

```bash
# List workflow templates
ontologia workflows templates list

# Start workflow
ontologia workflows start \
  --template data_migration \
  --parameters '{"source": "old_db", "target": "new_db"}'

# List running workflows
ontologia workflows list --status running

# Get workflow details
ontologia workflows get --id workflow_456

# Resume paused workflow
ontologia workflows resume --id workflow_456

# Terminate workflow
ontologia workflows terminate --id workflow_456 --confirm
```

## Data Catalog Management

### Dataset Operations

```bash
# List datasets
ontologia datasets list

# Create dataset
ontologia datasets create \
  --name customer_data \
  --description "Customer master data" \
  --schema-file schema.json

# Get dataset details
ontologia datasets get --name customer_data

# Create dataset branch
ontologia datasets branch create \
  --dataset customer_data \
  --branch feature_enhancement \
  --from-branch main

# List dataset branches
ontologia datasets branch list --dataset customer_data

# Merge branches
ontologia datasets branch merge \
  --dataset customer_data \
  --source feature_enhancement \
  --target main
```

### Transaction Management

```bash
# List transactions
ontologia datasets transactions list \
  --dataset customer_data \
  --branch main

# Create transaction
ontologia datasets transactions create \
  --dataset customer_data \
  --type insert \
  --file data.json

# Get transaction details
ontologia datasets transactions get \
  --dataset customer_data \
  --transaction tx_123

# Commit transaction
ontologia datasets transactions commit \
  --dataset customer_data \
  --transaction tx_123
```

## SDK Generation

### Generate Client SDKs

```bash
# Generate Python SDK
ontologia generate-sdk \
  --language python \
  --output-dir ./ontologia-sdk

# Generate TypeScript SDK
ontologia generate-sdk \
  --language typescript \
  --output-dir ./ontologia-sdk-ts

# Generate with specific object types only
ontologia generate-sdk \
  --language python \
  --include-types Person,Company,Address

# Generate with custom package name
ontologia generate-sdk \
  --language python \
  --package-name my-ontology-sdk

# Generate with validation
ontologia generate-sdk \
  --language python \
  --include-validation
```

### SDK Configuration

```bash
# Configure SDK generation settings
ontologia config set-sdk \
  --language python \
  --package-prefix com.mycompany \
  --include-docs true \
  --include-examples true
```

## Interactive Playground

### Development Environment

```bash
# Start interactive playground
ontologia playground

# Start with specific object types loaded
ontologia playground --load-types Person,Company

# Start with sample data
ontologia playground --sample-data

# Start in debug mode
ontologia playground --debug
```

### Playground Features

- Interactive Python shell with pre-loaded ontology client
- Auto-completion for object types and properties
- Built-in query builder and tester
- Real-time validation and error checking
- Export playground session to script

## Migration Management

### Database Migrations

```bash
# List pending migrations
ontologia migrate list

# Create new migration
ontologia migrate create \
  --name add_person_object_type \
  --description "Add Person object type with basic properties"

# Apply migrations
ontologia migrate up

# Apply specific migration
ontologia migrate up --version 20240101_120000

# Rollback migration
ontologia migrate down

# Rollback to specific version
ontologia migrate down --version 20240101_120000

# Get migration status
ontologia migrate status
```

### Schema Migration

```bash
# Export current schema
ontologia migrate export --format yaml > schema.yaml

# Import schema from file
ontologia migrate import --file schema.yaml

# Validate schema
ontologia migrate validate --file schema.yaml

# Compare schemas
ontologia migrate diff \
  --from schema_old.yaml \
  --to schema_new.yaml
```

## Output Formats

### Table Format (Default)

```bash
ontologia object-types list --format table
```

```
┌─────────┬─────────────┬──────────────┬─────────────┐
│ Name    │ Description │ Properties   │ Created At  │
├─────────┼─────────────┼──────────────┼─────────────┤
│ Person  │ A person    │ name, email  │ 2024-01-01  │
│ Company │ Organization│ name, founded│ 2024-01-02  │
└─────────┴─────────────┴──────────────┴─────────────┘
```

### JSON Format

```bash
ontologia instances list --format json
```

```json
[
  {
    "id": "person_123",
    "object_type": "Person",
    "data": {"name": "John Doe", "email": "john@example.com"},
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### YAML Format

```bash
ontologia object-types get --name Person --format yaml
```

```yaml
name: Person
description: A person in the system
properties:
  - name: name
    type: string
    required: true
  - name: email
    type: string
    format: email
```

### CSV Format

```bash
ontologia instances list --format csv --output data.csv
```

## Advanced Usage

### Scripting and Automation

```bash
# Execute commands from file
ontologia --file commands.txt

# Pipe commands
echo "object-types list" | ontologia

# Use in shell scripts
#!/bin/bash
for type in $(ontologia object-types list --format json | jq -r '.[].name'); do
    echo "Processing $type"
    ontologia instances list --object-type $type --format csv > ${type}.csv
done
```

### Configuration Profiles

```bash
# Create named profile
ontologia config profile create dev --server-url http://dev-server:8000

# Switch to profile
ontologia config profile use dev

# List profiles
ontologia config profile list

# Delete profile
ontologia config profile delete dev
```

### Environment Variables

```bash
# Override configuration with environment variables
export ONTOLOGIA_SERVER_URL=http://localhost:8000
export ONTOLOGIA_API_KEY=your-api-key
export ONTOLOGIA_TIMEOUT=60

# Use environment-specific config
ontologia --config-file ./prod-config.yaml object-types list
```

## Error Handling

### Exit Codes

- `0` - Success
- `1` - General error
- `2` - Authentication error
- `3` - Network error
- `4` - Validation error
- `5` - Permission error

### Error Output

```bash
# Verbose error messages
ontologia --verbose object-types create --name "Invalid Name!"

# JSON error output for scripting
ontologia --format json object-types get --name nonexistent 2>&1 | jq .
```

## Completion

### Bash Completion

```bash
# Enable bash completion
eval "$(ontologia completion bash)"

# Add to .bashrc for permanent completion
echo 'eval "$(ontologia completion bash)"' >> ~/.bashrc
```

### Zsh Completion

```bash
# Enable zsh completion
eval "$(ontologia completion zsh)"

# Add to .zshrc for permanent completion
echo 'eval "$(ontologia completion zsh)"' >> ~/.zshrc
```

## Plugin System

### Installing Plugins

```bash
# Install plugin from PyPI
ontologia plugin install ontologia-cli-plugin-aws

# Install plugin from local file
ontologia plugin install ./my-plugin.tar.gz

# List installed plugins
ontologia plugin list

# Remove plugin
ontologia plugin remove ontologia-cli-plugin-aws
```

### Creating Plugins

```python
# my_plugin.py
from ontologia_cli import Plugin, Command

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"

    def get_commands(self):
        return [MyCommand()]

class MyCommand(Command):
    name = "my-command"
    help = "My custom command"

    def run(self, args):
        print("Hello from my plugin!")
```

## Testing

### CLI Testing

```bash
# Run CLI tests
ontologia test --cli

# Test specific command
ontologia test --command object-types

# Run integration tests
ontologia test --integration
```

### Mock Mode

```bash
# Run in mock mode for testing
ontologia --mock object-types list

# Use mock data file
ontologia --mock --data-file mock_data.json instances list
```

## Performance

### Caching

```bash
# Enable local caching
ontologia config set --cache-enabled true

# Clear cache
ontologia cache clear

# Set cache TTL
ontologia config set --cache-ttl 3600
```

### Batch Operations

```bash
# Use batch mode for better performance
ontologia --batch-size 100 instances bulk-create --file large_dataset.csv

# Parallel processing
ontologia --parallel 4 instances bulk-update --file updates.json
```

## Troubleshooting

### Debug Mode

```bash
# Enable debug logging
ontologia --debug object-types list

# Save debug logs to file
ontologia --debug --log-file debug.log object-types list
```

### Connection Issues

```bash
# Test server connectivity
ontologia test connection

# Check server status
ontologia server status

# Verify authentication
ontologia auth test
```

## Dependencies

Core dependencies:
- **Click**: Command-line interface framework
- **Rich**: Terminal formatting and progress bars
- **Pydantic**: Data validation
- **httpx**: Async HTTP client
- **PyYAML**: YAML configuration support

Optional dependencies:
- **pandas**: CSV and data manipulation
- **jq**: JSON processing (system dependency)
- **postgresql-client**: Direct database access

## Version Information

Current version: `0.1.0`

Follows semantic versioning with CLI compatibility guarantees.

## Contributing

When contributing to the CLI:
1. Follow command-line interface best practices
2. Include comprehensive help text and examples
3. Add tests for all commands
4. Ensure backward compatibility
5. Update documentation

## License

This package is part of the Ontologia framework and follows the same license terms.
