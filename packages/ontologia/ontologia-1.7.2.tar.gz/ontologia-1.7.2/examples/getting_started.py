#!/usr/bin/env python3
"""
Getting Started with Ontologia - Basic Usage Example

This script demonstrates the fundamental concepts and operations
of the Ontologia platform. It covers:

1. Setting up the basic services
2. Creating object types and instances
3. Working with relationships
4. Running basic analytics
5. Using the cache for performance

Run with: uv run examples/getting_started.py
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main getting started example."""

    print("🚀 Ontologia Getting Started Guide")
    print("=" * 50)

    # Step 1: Setup basic infrastructure
    print("\n📦 Step 1: Setting up Infrastructure")
    await setup_infrastructure()

    # Step 2: Define object types
    print("\n🏗️  Step 2: Defining Object Types")
    await define_object_types()

    # Step 3: Create instances
    print("\n📝 Step 3: Creating Object Instances")
    await create_instances()

    # Step 4: Work with relationships
    print("\n🔗 Step 4: Creating Relationships")
    await create_relationships()

    # Step 5: Query and analyze
    print("\n📊 Step 5: Querying and Analytics")
    await run_analytics()

    # Step 6: Performance optimization
    print("\n⚡ Step 6: Performance with Caching")
    await demonstrate_caching()

    print("\n✅ Getting Started Complete!")
    print("\nNext steps:")
    print("- Explore advanced analytics in examples/advanced_analytics.py")
    print("- Try the REST API: uv run ontologia-api")
    print("- Check the documentation: mkdocs serve")


async def setup_infrastructure():
    """Setup basic infrastructure components."""

    # Import here to avoid circular imports in examples
    from ontologia.application.analytics_service import AnalyticsService
    from ontologia.application.instances_service import InstancesService
    from ontologia.application.linked_objects_service import LinkedObjectsService
    from ontologia.infrastructure.cache_repository import create_memory_cache_repository
    from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository

    # Create in-memory DuckDB database
    duckdb_repo = DuckDBRepository(duckdb_path=":memory:")
    print("✅ DuckDB repository created (in-memory)")

    # Create memory cache
    cache_repo = create_memory_cache_repository(default_ttl=3600)
    print("✅ Cache repository created (in-memory)")

    # Create services
    instances_service = InstancesService(duckdb_repo=duckdb_repo, cache_repo=cache_repo)
    print("✅ Instances service created")

    linked_objects_service = LinkedObjectsService(duckdb_repo=duckdb_repo, cache_repo=cache_repo)
    print("✅ Linked objects service created")

    analytics_service = AnalyticsService(duckdb_repo=duckdb_repo, cache_repo=cache_repo)
    print("✅ Analytics service created")

    # Store services globally for this example
    global services
    services = {
        "instances": instances_service,
        "linked_objects": linked_objects_service,
        "analytics": analytics_service,
        "duckdb_repo": duckdb_repo,
        "cache_repo": cache_repo,
    }


async def define_object_types():
    """Define basic object types for our example."""

    from ontologia.domain.metamodels.types.object_type import ObjectType

    # Define Person object type
    person_type = ObjectType(
        api_name="person",
        display_name="Person",
        description="A person in the system",
        properties={
            "name": {"type": "string", "required": True, "display_name": "Full Name"},
            "age": {"type": "integer", "required": True, "display_name": "Age"},
            "email": {"type": "string", "required": False, "display_name": "Email Address"},
            "department": {"type": "string", "required": True, "display_name": "Department"},
        },
    )

    # Define Company object type
    company_type = ObjectType(
        api_name="company",
        display_name="Company",
        description="A company organization",
        properties={
            "name": {"type": "string", "required": True, "display_name": "Company Name"},
            "industry": {"type": "string", "required": True, "display_name": "Industry"},
            "founded_year": {"type": "integer", "required": False, "display_name": "Founded Year"},
            "employee_count": {
                "type": "integer",
                "required": False,
                "display_name": "Number of Employees",
            },
        },
    )

    # Define Project object type
    project_type = ObjectType(
        api_name="project",
        display_name="Project",
        description="A work project",
        properties={
            "name": {"type": "string", "required": True, "display_name": "Project Name"},
            "status": {
                "type": "string",
                "required": True,
                "display_name": "Status",
                "enum": ["planning", "active", "completed", "cancelled"],
            },
            "budget": {"type": "decimal", "required": False, "display_name": "Budget"},
            "start_date": {"type": "date", "required": False, "display_name": "Start Date"},
        },
    )

    # Store object types for this example
    global object_types
    object_types = {"person": person_type, "company": company_type, "project": project_type}

    print("✅ Object types defined: person, company, project")


async def create_instances():
    """Create sample instances of our object types."""

    instances_service = services["instances"]

    # Create people
    people_data = [
        {
            "object_type_api_name": "person",
            "primary_key_value": "alice",
            "properties": {
                "name": "Alice Johnson",
                "age": 32,
                "email": "alice@company.com",
                "department": "Engineering",
            },
        },
        {
            "object_type_api_name": "person",
            "primary_key_value": "bob",
            "properties": {
                "name": "Bob Smith",
                "age": 28,
                "email": "bob@company.com",
                "department": "Marketing",
            },
        },
        {
            "object_type_api_name": "person",
            "primary_key_value": "carol",
            "properties": {
                "name": "Carol Davis",
                "age": 35,
                "email": "carol@company.com",
                "department": "Engineering",
            },
        },
    ]

    created_people = []
    for person_data in people_data:
        person = await instances_service.upsert_object(person_data)
        created_people.append(person)
        print(f"✅ Created person: {person.properties['name']}")

    # Create companies
    companies_data = [
        {
            "object_type_api_name": "company",
            "primary_key_value": "techcorp",
            "properties": {
                "name": "TechCorp Inc.",
                "industry": "Technology",
                "founded_year": 2010,
                "employee_count": 500,
            },
        },
        {
            "object_type_api_name": "company",
            "primary_key_value": "marketco",
            "properties": {
                "name": "MarketCo",
                "industry": "Marketing",
                "founded_year": 2015,
                "employee_count": 100,
            },
        },
    ]

    created_companies = []
    for company_data in companies_data:
        company = await instances_service.upsert_object(company_data)
        created_companies.append(company)
        print(f"✅ Created company: {company.properties['name']}")

    # Create projects
    projects_data = [
        {
            "object_type_api_name": "project",
            "primary_key_value": "webapp",
            "properties": {
                "name": "Web Application Redesign",
                "status": "active",
                "budget": 50000.00,
                "start_date": "2024-01-15",
            },
        },
        {
            "object_type_api_name": "project",
            "primary_key_value": "marketing",
            "properties": {
                "name": "Q1 Marketing Campaign",
                "status": "completed",
                "budget": 25000.00,
                "start_date": "2024-01-01",
            },
        },
    ]

    created_projects = []
    for project_data in projects_data:
        project = await instances_service.upsert_object(project_data)
        created_projects.append(project)
        print(f"✅ Created project: {project.properties['name']}")

    # Store instances for this example
    global instances
    instances = {
        "people": created_people,
        "companies": created_companies,
        "projects": created_projects,
    }


async def create_relationships():
    """Create relationships between instances."""

    linked_objects_service = services["linked_objects"]

    # Link people to companies (works_for relationship)
    person_company_links = [
        ("alice", "techcorp", "works_for"),
        ("bob", "marketco", "works_for"),
        ("carol", "techcorp", "works_for"),
    ]

    for person_id, company_id, link_type in person_company_links:
        await linked_objects_service.create_link(
            source_object_type="person",
            source_primary_key=person_id,
            target_object_type="company",
            target_primary_key=company_id,
            link_type_api_name=link_type,
            properties={"start_date": datetime.now().isoformat()},
        )
        print(f"✅ Linked {person_id} -> {company_id} ({link_type})")

    # Link people to projects (assigned_to relationship)
    person_project_links = [
        ("alice", "webapp", "assigned_to"),
        ("bob", "marketing", "assigned_to"),
        ("carol", "webapp", "assigned_to"),
    ]

    for person_id, project_id, link_type in person_project_links:
        await linked_objects_service.create_link(
            source_object_type="person",
            source_primary_key=person_id,
            target_object_type="project",
            target_primary_key=project_id,
            link_type_api_name=link_type,
            properties={"role": "team_member"},
        )
        print(f"✅ Linked {person_id} -> {project_id} ({link_type})")


async def run_analytics():
    """Run basic analytics on our data."""

    analytics_service = services["analytics"]

    # Count people by department
    print("\n📊 People by Department:")
    dept_count = await analytics_service.count_by_property(
        object_type_api_name="person", property_name="department"
    )
    for dept, count in dept_count.items():
        print(f"  {dept}: {count} people")

    # Average age by department
    print("\n📊 Average Age by Department:")
    dept_ages = await analytics_service.average_by_property(
        object_type_api_name="person", property_name="age", group_by="department"
    )
    for dept, avg_age in dept_ages.items():
        print(f"  {dept}: {avg_age:.1f} years")

    # Company statistics
    print("\n📊 Company Statistics:")
    total_companies = await analytics_service.count_objects("company")
    print(f"  Total companies: {total_companies}")

    avg_employees = await analytics_service.average_property("company", "employee_count")
    print(f"  Average employees: {avg_employees:.1f}")

    # Project status distribution
    print("\n📊 Project Status Distribution:")
    status_dist = await analytics_service.distribution_by_property(
        object_type_api_name="project", property_name="status"
    )
    for status, count in status_dist.items():
        print(f"  {status}: {count} projects")


async def demonstrate_caching():
    """Demonstrate caching for performance."""

    cache_repo = services["cache_repo"]

    # Cache a computation result
    def expensive_computation():
        # Simulate expensive operation
        import time

        time.sleep(0.1)  # 100ms delay
        return {"result": "expensive_data", "timestamp": datetime.now().isoformat()}

    print("\n⚡ Demonstrating Cache Performance:")

    # First call - should compute
    import time

    start_time = time.time()
    result1 = cache_repo.get_or_set("computation:key1", expensive_computation, ttl_seconds=60)
    first_call_time = time.time() - start_time
    print(f"  First call (computed): {first_call_time:.3f}s")

    # Second call - should use cache
    start_time = time.time()
    result2 = cache_repo.get_or_set("computation:key1", expensive_computation, ttl_seconds=60)
    second_call_time = time.time() - start_time
    print(f"  Second call (cached): {second_call_time:.3f}s")

    speedup = first_call_time / second_call_time if second_call_time > 0 else float("inf")
    print(f"  Speedup: {speedup:.1f}x faster")

    # Demonstrate cache invalidation
    cache_repo.set("temp:key", {"data": "temporary"}, ttl_seconds=1)
    print("  Cached temporary data")

    # Wait and check expiration
    import asyncio

    await asyncio.sleep(1.1)

    expired_data = cache_repo.get("temp:key")
    print(f"  After TTL expiration: {expired_data}")


if __name__ == "__main__":
    asyncio.run(main())
