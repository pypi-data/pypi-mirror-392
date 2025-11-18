"""Centralized OpenAPI metadata, tags, and reusable schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiError(BaseModel):
    """Canonical error payload returned by the Ontology API.

    The Ontology API uses a consistent error format across all endpoints to enable
    programmatic error handling and user-friendly error messages.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "detail": "ObjectType 'employee' not found",
                    "code": "object_type_not_found",
                    "more_info": "https://ontologia.dev/docs/errors#object-type-not-found",
                }
            ]
        },
    )

    detail: str = Field(
        ...,
        description=(
            "Human-readable message describing why the request failed. "
            "This message is intended for developers and should provide enough context "
            "to understand and debug the issue."
        ),
        examples=[
            "ObjectType 'employee' not found",
            "Validation failed for property 'age': must be >= 0",
            "Insufficient permissions to access resource",
        ],
    )
    code: str | None = Field(
        None,
        description=(
            "Stable, machine-friendly error identifier that can be used for programmatic "
            "error handling. Error codes are stable across API versions unless explicitly "
            "deprecated in release notes."
        ),
        examples=[
            "object_type_not_found",
            "validation_failed",
            "permission_denied",
            "rate_limit_exceeded",
        ],
    )
    more_info: str | None = Field(
        None,
        description=(
            "Optional URL with remediation guidance, additional documentation, or "
            "troubleshooting steps for this specific error."
        ),
        alias="moreInfo",
        serialization_alias="moreInfo",
        examples=[
            "https://ontologia.dev/docs/errors#object-type-not-found",
            "https://ontologia.dev/docs/troubleshooting#validation-errors",
        ],
    )


API_TAGS: list[dict[str, Any]] = [
    {
        "name": "Object Types",
        "description": (
            "## Metamodel Management\n\n"
            "Create, read, update, and delete metamodel ObjectTypes that define the structure "
            "of your ontology. ObjectTypes are the schema definitions that describe what "
            "properties objects can have, their data types, validation rules, and relationships.\n\n"
            "**Key Features:**\n"
            "- Property definitions with type validation\n"
            "- Index configuration for query performance\n"
            "- Interface implementation for polymorphism\n"
            "- Schema evolution with backward compatibility\n"
            "- Import/export for schema versioning\n\n"
            "**Common Operations:**\n"
            "- Define new entity types (Person, Company, etc.)\n"
            "- Add/remove properties with validation\n"
            "- Configure indexes for performance optimization\n"
            "- Manage interface contracts\n\n"
            "**Use Cases:**\n"
            "- Data modeling and schema design\n"
            "- API contract definition\n"
            "- Data governance and validation\n"
            "- Integration with external systems"
        ),
    },
    {
        "name": "Link Types",
        "description": (
            "## Relationship Management\n\n"
            "Manage relationship schemas that connect ObjectTypes together. LinkTypes define "
            "the structure and constraints of relationships between objects, including "
            "cardinality, directionality, and property schemas.\n\n"
            "**Key Features:**\n"
            "- Cardinality constraints (1:1, 1:N, N:N)\n"
            "- Directional and bidirectional relationships\n"
            "- Link properties with validation\n"
            "- Relationship inheritance via interfaces\n"
            "- Cascade operations for data integrity\n\n"
            "**Common Operations:**\n"
            "- Define relationship types (works_for, manages, etc.)\n"
            "- Configure cardinality and constraints\n"
            "- Add link properties (start_date, role, etc.)\n"
            "- Manage relationship lifecycle\n\n"
            "**Use Cases:**\n"
            "- Organizational hierarchies\n"
            "- Network topology modeling\n"
            "- Process flow definitions\n"
            "- Social graph construction"
        ),
    },
    {
        "name": "Actions",
        "description": (
            "## Business Logic Execution\n\n"
            "Discover and invoke actions, whether executed synchronously or orchestrated via Temporal. "
            "Actions encapsulate business logic that can be triggered on objects or datasets, "
            "with support for validation rules, async execution, and workflow integration.\n\n"
            "**Key Features:**\n"
            "- Synchronous and asynchronous execution\n"
            "- Input validation and type safety\n"
            "- Temporal workflow integration\n"
            "- Role-based access control\n"
            "- Execution history and monitoring\n"
            "- Custom action registration\n\n"
            "**Common Operations:**\n"
            "- Execute data validation actions\n"
            "- Trigger data transformation workflows\n"
            "- Run analytics and reporting jobs\n"
            "- Perform bulk data operations\n\n"
            "**Use Cases:**\n"
            "- Data quality validation\n"
            "- ETL pipeline orchestration\n"
            "- Automated decision making\n"
            "- External system integration"
        ),
    },
    {
        "name": "Objects",
        "description": (
            "## Instance Data Management\n\n"
            "Work with instance data, including filtered search, aggregation, traversal, and bulk operations. "
            "Objects are the actual data instances that conform to your ObjectType schemas, "
            "with full CRUD operations and advanced querying capabilities.\n\n"
            "**Key Features:**\n"
            "- Full CRUD operations with validation\n"
            "- Advanced filtering and search\n"
            "- Graph traversal and relationship queries\n"
            "- Aggregation and analytics\n"
            "- Bulk operations for performance\n"
            "- Real-time updates and subscriptions\n"
            "- Data versioning and history\n\n"
            "**Common Operations:**\n"
            "- Create and update object instances\n"
            "- Search with complex filters\n"
            "- Traverse relationship graphs\n"
            "- Run aggregations and analytics\n"
            "- Perform bulk data operations\n\n"
            "**Use Cases:**\n"
            "- Master data management\n"
            "- Knowledge graph population\n"
            "- Real-time data synchronization\n"
            "- Analytics and reporting"
        ),
    },
    {
        "name": "Datasets",
        "description": (
            "## Data Catalog & Versioning\n\n"
            "Inspect dataset definitions, branches, and transactions powering ingestion pipelines. "
            "Datasets provide versioned data management with branching, transactions, and "
            "governance capabilities for enterprise data workflows.\n\n"
            "**Key Features:**\n"
            "- Git-like branching and merging\n"
            "- ACID transactions for data integrity\n"
            "- Schema evolution and validation\n"
            "- Data lineage tracking\n"
            "- Access control and governance\n"
            "- Integration with dbt and data pipelines\n\n"
            "**Common Operations:**\n"
            "- Create and manage dataset branches\n"
            "- Track data changes and lineage\n"
            "- Validate data quality and schema\n"
            "- Govern data access and permissions\n\n"
            "**Use Cases:**\n"
            "- Data warehouse management\n"
            "- ML model versioning\n"
            "- Analytics data curation\n"
            "- Compliance and audit trails"
        ),
    },
    {
        "name": "Interfaces",
        "description": (
            "## Polymorphic Contracts\n\n"
            "Model polymorphic contracts that unify multiple ObjectTypes under a shared interface. "
            "Interfaces enable type abstraction, allowing you to work with different object types "
            "through a common contract while maintaining type safety.\n\n"
            "**Key Features:**\n"
            "- Multiple inheritance support\n"
            "- Abstract property definitions\n"
            "- Runtime type checking\n"
            "- Interface-based queries\n"
            "- Schema composition\n\n"
            "**Common Operations:**\n"
            "- Define interface contracts\n"
            "- Implement interfaces on ObjectTypes\n"
            "- Query across interface implementations\n"
            "- Validate interface compliance\n\n"
            "**Use Cases:**\n"
            "- Plugin architecture design\n"
            "- API contract standardization\n"
            "- Multi-tenant data models\n"
            "- Framework integration patterns"
        ),
    },
    {
        "name": "Analytics",
        "description": (
            "## Data Analytics & Aggregation\n\n"
            "Run aggregate queries across object instances with familiar metrics and groupings. "
            "The analytics engine provides SQL-like aggregation capabilities optimized for "
            "graph-structured data with support for complex metrics and dimensional analysis.\n\n"
            "**Key Features:**\n"
            "- SQL-like aggregation functions\n"
            "- Multi-dimensional grouping\n"
            "- Graph-aware aggregations\n"
            "- Real-time analytics\n"
            "- Custom metric definitions\n"
            "- Performance optimization\n\n"
            "**Common Operations:**\n"
            "- Calculate summary statistics\n"
            "- Group by dimensions\n"
            "- Time-series aggregations\n"
            "- Graph analytics metrics\n\n"
            "**Use Cases:**\n"
            "- Business intelligence\n"
            "- KPI tracking and reporting\n"
            "- Data quality metrics\n"
            "- Network analysis"
        ),
    },
    {
        "name": "Query Types",
        "description": (
            "## Saved Query Management\n\n"
            "Define and execute saved queries that encapsulate complex business logic. "
            "QueryTypes allow you to parameterize and reuse complex queries across your "
            "organization with proper governance and versioning.\n\n"
            "**Key Features:**\n"
            "- Parameterized query templates\n"
            "- Query versioning and governance\n"
            "- Performance optimization\n"
            "- Access control and sharing\n"
            "- Integration with dashboards\n\n"
            "**Common Operations:**\n"
            "- Create reusable query templates\n"
            "- Execute queries with parameters\n"
            "- Manage query versions\n"
            "- Share queries across teams\n\n"
            "**Use Cases:**\n"
            "- Standardized reporting queries\n"
            "- Self-service analytics\n"
            "- API endpoint creation\n"
            "- Data product definition"
        ),
    },
    {
        "name": "Auth",
        "description": (
            "## Authentication & Authorization\n\n"
            "Obtain JWT access tokens for authenticated API usage. The authentication system "
            "supports OAuth2 flows, role-based access control, and tenant-scoped permissions "
            "for enterprise security requirements.\n\n"
            "**Key Features:**\n"
            "- OAuth2 password flow\n"
            "- JWT token-based authentication\n"
            "- Role-based access control (RBAC)\n"
            "- Tenant-scoped permissions\n"
            "- Token refresh and revocation\n"
            "- Multi-factor authentication support\n\n"
            "**Common Operations:**\n"
            "- Obtain access tokens\n"
            "- Refresh expired tokens\n"
            "- Validate token permissions\n"
            "- Manage user roles\n\n"
            "**Use Cases:**\n"
            "- API authentication\n"
            "- User session management\n"
            "- Service account authentication\n"
            "- Third-party integration"
        ),
    },
    {
        "name": "Health & Monitoring",
        "description": (
            "## System Health & Diagnostics\n\n"
            "Monitor system health, performance metrics, and diagnostic information. "
            "These endpoints provide visibility into system status, performance metrics, "
            "and operational health for production monitoring.\n\n"
            "**Key Features:**\n"
            "- Health check endpoints\n"
            "- Performance metrics\n"
            "- System diagnostics\n"
            "- Dependency status\n"
            "- Operational insights\n\n"
            "**Common Operations:**\n"
            "- Check system health\n"
            "- Monitor performance metrics\n"
            "- Diagnose issues\n"
            "- Track service dependencies\n\n"
            "**Use Cases:**\n"
            "- Production monitoring\n"
            "- Load balancer health checks\n"
            "- Performance troubleshooting\n"
            "- SLA monitoring"
        ),
    },
]


SWAGGER_UI_PARAMETERS: dict[str, Any] = {
    "docExpansion": "list",
    "deepLinking": True,
    "displayRequestDuration": True,
    "syntaxHighlight": {"activated": True, "theme": "obsidian"},
    "tryItOutEnabled": True,
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "defaultModelsExpandDepth": 2,
    "defaultModelExpandDepth": 2,
    "displayOperationId": False,
    "operationsSorter": "alpha",
    "tagsSorter": "alpha",
    "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
    "requestInterceptor": """
        function(request) {
            // Add common headers for debugging
            request.headers['X-Request-ID'] = crypto.randomUUID();
            request.headers['X-Client-Version'] = 'ontologia-api/1.0.0';
            return request;
        }
    """,
    "responseInterceptor": """
        function(response) {
            // Log responses for debugging
            console.log('API Response:', response);
            return response;
        }
    """,
}


SERVERS_METADATA = [
    {
        "url": "http://localhost:8001",
        "description": "🚀 Local Development Server",
        "variables": {"port": {"default": "8001", "description": "Local development port"}},
    },
    {
        "url": "https://api.staging.ontologia.dev",
        "description": "🧪 Staging Environment",
        "variables": {"subdomain": {"default": "api", "description": "API subdomain"}},
    },
    {
        "url": "https://api.ontologia.dev",
        "description": "🌐 Production Environment",
        "variables": {"subdomain": {"default": "api", "description": "API subdomain"}},
    },
    {
        "url": "https://api.enterprise.ontologia.dev",
        "description": "🏢 Enterprise Instance",
        "variables": {"subdomain": {"default": "api", "description": "Enterprise API subdomain"}},
    },
]


SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "**JWT Authentication**\n\n"
            "1. **Obtain Token**: Use `/v2/auth/token` with username/password\n"
            "2. **Format**: `Authorization: Bearer <your-jwt-token>`\n"
            "3. **Token Contents**: Includes user ID, roles, and tenant permissions\n"
            "4. **Expiration**: Tokens expire after 24 hours by default\n"
            "5. **Refresh**: Use refresh token or re-authenticate\n\n"
            "**Example Token Payload:**\n"
            "```json\n"
            "{\n"
            '  "sub": "admin",\n'
            '  "exp": 1640995200,\n'
            '  "roles": ["admin", "editor"],\n'
            '  "tenants": {"ontology/default": "admin"}\n'
            "}\n"
            "```\n\n"
            "**Quick Test:**\n"
            "```bash\n"
            "curl -X POST http://localhost:8001/v2/auth/token \\\n"
            '  -H "Content-Type: application/x-www-form-urlencoded" \\\n'
            '  -d "username=admin&password=admin"\n'
            "```"
        ),
    },
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": (
            "**API Key Authentication**\n\n"
            "Alternative authentication method for service accounts and integrations.\n\n"
            "**Usage:**\n"
            "- Header: `X-API-Key: <your-api-key>`\n"
            "- Ideal for: Service-to-service communication\n"
            "- Permissions: Scoped to specific operations\n\n"
            "**Get API Key:**\n"
            "Contact your administrator or use the management console."
        ),
    },
}


DEFAULT_ERROR_COMPONENTS = {
    "responses": {
        "UnauthorizedError": {
            "description": "**🔒 Authentication Required**\n\nAuthentication credentials were missing, invalid, or expired.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "missing_token": {
                            "summary": "Missing Authorization Header",
                            "value": {
                                "detail": "Missing Authorization header",
                                "code": "auth_header_missing",
                                "more_info": "https://ontologia.dev/docs/auth#missing-header",
                            },
                        },
                        "invalid_token": {
                            "summary": "Invalid JWT Token",
                            "value": {
                                "detail": "Invalid or expired JWT token",
                                "code": "invalid_token",
                                "more_info": "https://ontologia.dev/docs/auth#token-validation",
                            },
                        },
                        "expired_token": {
                            "summary": "Token Expired",
                            "value": {
                                "detail": "JWT token has expired",
                                "code": "token_expired",
                                "more_info": "https://ontologia.dev/docs/auth#token-refresh",
                            },
                        },
                    },
                }
            },
        },
        "ForbiddenError": {
            "description": "**🚫 Access Denied**\n\nThe provided credentials are valid but do not grant access to the requested resource.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "insufficient_permissions": {
                            "summary": "Insufficient Permissions",
                            "value": {
                                "detail": "User 'john.doe' lacks 'admin' role for this operation",
                                "code": "insufficient_permissions",
                                "more_info": "https://ontologia.dev/docs/rbac#permissions",
                            },
                        },
                        "tenant_access_denied": {
                            "summary": "Tenant Access Denied",
                            "value": {
                                "detail": "Access denied to tenant 'acme-corp'",
                                "code": "tenant_access_denied",
                                "more_info": "https://ontologia.dev/docs/rbac#tenants",
                            },
                        },
                    },
                }
            },
        },
        "NotFoundError": {
            "description": "**🔍 Resource Not Found**\n\nThe requested resource does not exist or has been deleted.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "object_type_not_found": {
                            "summary": "Object Type Not Found",
                            "value": {
                                "detail": "ObjectType 'employee' not found in ontology 'default'",
                                "code": "object_type_not_found",
                                "more_info": "https://ontologia.dev/docs/object-types#not-found",
                            },
                        },
                        "instance_not_found": {
                            "summary": "Instance Not Found",
                            "value": {
                                "detail": "Object instance 'person_123' not found",
                                "code": "instance_not_found",
                                "more_info": "https://ontologia.dev/docs/objects#not-found",
                            },
                        },
                    },
                }
            },
        },
        "ValidationError": {
            "description": "**⚠️ Validation Failed**\n\nThe request data is invalid or does not conform to the schema requirements.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "schema_validation": {
                            "summary": "Schema Validation Error",
                            "value": {
                                "detail": "Validation failed for property 'age': must be >= 0",
                                "code": "validation_failed",
                                "more_info": "https://ontologia.dev/docs/validation#schema-rules",
                            },
                        },
                        "required_field": {
                            "summary": "Required Field Missing",
                            "value": {
                                "detail": "Required field 'email' is missing",
                                "code": "required_field_missing",
                                "more_info": "https://ontologia.dev/docs/validation#required-fields",
                            },
                        },
                    },
                }
            },
        },
        "ConflictError": {
            "description": "**⚡ Resource Conflict**\n\nThe request conflicts with the current state of the resource.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "duplicate_resource": {
                            "summary": "Duplicate Resource",
                            "value": {
                                "detail": "ObjectType 'employee' already exists",
                                "code": "resource_already_exists",
                                "more_info": "https://ontologia.dev/docs/conflicts#duplicates",
                            },
                        },
                        "version_conflict": {
                            "summary": "Version Conflict",
                            "value": {
                                "detail": "Resource version conflict: expected version 3, got version 2",
                                "code": "version_conflict",
                                "more_info": "https://ontologia.dev/docs/conflicts#versioning",
                            },
                        },
                    },
                }
            },
        },
        "TooManyRequestsError": {
            "description": "**⏱️ Rate Limit Exceeded**\n\nToo many requests have been made. Please retry after the indicated time window.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "rate_limit": {
                            "summary": "Rate Limit Exceeded",
                            "value": {
                                "detail": "Rate limit exceeded: 100 requests per minute",
                                "code": "rate_limit_exceeded",
                                "more_info": "https://ontologia.dev/docs/rate-limiting",
                            },
                        }
                    },
                }
            },
        },
        "ServerError": {
            "description": "**💥 Internal Server Error**\n\nAn unexpected error was encountered while processing the request.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ApiError"},
                    "examples": {
                        "database_error": {
                            "summary": "Database Error",
                            "value": {
                                "detail": "Internal server error: Database connection failed",
                                "code": "database_error",
                                "more_info": "https://ontologia.dev/docs/troubleshooting#database",
                            },
                        },
                        "service_unavailable": {
                            "summary": "Service Unavailable",
                            "value": {
                                "detail": "Internal server error: External service unavailable",
                                "code": "service_unavailable",
                                "more_info": "https://ontologia.dev/docs/troubleshooting#services",
                            },
                        },
                    },
                }
            },
        },
    }
}


def api_error_schema() -> dict[str, Any]:
    """Return the JSON schema for :class:`ApiError` with proper OpenAPI refs."""

    return ApiError.model_json_schema(ref_template="#/components/schemas/{model}")
