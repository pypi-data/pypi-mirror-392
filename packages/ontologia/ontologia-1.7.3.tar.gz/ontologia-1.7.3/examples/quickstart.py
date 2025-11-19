#!/usr/bin/env python3
"""
Quick Start Tutorial for Ontologia

A minimal example to get you up and running with Ontologia in 5 minutes.
This tutorial covers the absolute basics: creating objects and querying them.

Run with: uv run examples/quickstart.py
"""

import asyncio
from datetime import datetime


async def main():
    """Quick start example - minimal and focused."""

    print("⚡ Ontologia Quick Start")
    print("=" * 30)

    # 1. Setup basic services
    print("\n1️⃣ Setting up services...")
    duckdb_repo, instances_service = await setup_services()
    print("✅ Services ready!")

    # 2. Create a simple object type
    print("\n2️⃣ Creating object type...")
    await create_object_type(duckdb_repo)
    print("✅ 'user' object type created!")

    # 3. Create some users
    print("\n3️⃣ Creating users...")
    user1 = await create_user(instances_service, "alice", "Alice", 25)
    user2 = await create_user(instances_service, "bob", "Bob", 30)
    print(f"✅ Created {user1.properties['name']} and {user2.properties['name']}!")

    # 4. Query users
    print("\n4️⃣ Querying users...")
    all_users = await query_users(instances_service)
    print(f"✅ Found {len(all_users)} users:")
    for user in all_users:
        print(f"   - {user.properties['name']} (age: {user.properties['age']})")

    # 5. Simple analytics
    print("\n5️⃣ Running analytics...")
    await run_analytics(duckdb_repo)

    print("\n🎉 Quick start complete!")
    print("\nNext steps:")
    print("- Try the full getting started guide: examples/getting_started.py")
    print("- Start the API server: uv run ontologia-api")
    print("- Read the docs: mkdocs serve")


async def setup_services():
    """Setup minimal services for the quick start."""

    from ontologia.application.instances_service import InstancesService
    from ontologia.infrastructure.persistence.duckdb.repository import DuckDBRepository

    # Create in-memory database
    duckdb_repo = DuckDBRepository(duckdb_path=":memory:")

    # Create instances service
    instances_service = InstancesService(duckdb_repo=duckdb_repo)

    return duckdb_repo, instances_service


async def create_object_type(duckdb_repo):
    """Create a simple user object type."""

    # Create user table directly in DuckDB for simplicity
    duckdb_repo.execute_query(
        """
        CREATE TABLE ot_user (
            id INTEGER PRIMARY KEY,
            object_type VARCHAR,
            primary_key_value VARCHAR,
            name VARCHAR,
            age INTEGER,
            created_at TIMESTAMP,
            properties VARCHAR
        )
    """,
        read_only=False,
    )


async def create_user(instances_service, user_id, name, age):
    """Create a user instance."""

    user_data = {
        "object_type_api_name": "user",
        "primary_key_value": user_id,
        "properties": {"name": name, "age": age, "created_at": datetime.now().isoformat()},
    }

    return await instances_service.upsert_object(user_data)


async def query_users(instances_service):
    """Query all users."""

    from ontologia.application.instances_service import ListObjectsRequest

    request = ListObjectsRequest(object_type_api_name="user", limit=100)

    result = await instances_service.list_objects(request)
    return result.objects


async def run_analytics(duckdb_repo):
    """Run simple analytics on users."""

    # Count users
    count = duckdb_repo.execute_scalar("SELECT COUNT(*) FROM ot_user")
    print(f"   Total users: {count}")

    # Average age
    avg_age = duckdb_repo.execute_scalar("SELECT AVG(age) FROM ot_user")
    print(f"   Average age: {avg_age:.1f}")

    # Age distribution
    age_dist = duckdb_repo.execute_query(
        """
        SELECT
            CASE
                WHEN age < 25 THEN '18-24'
                WHEN age < 35 THEN '25-34'
                ELSE '35+'
            END as age_group,
            COUNT(*) as count
        FROM ot_user
        GROUP BY age_group
        ORDER BY age_group
    """
    )

    print("   Age distribution:")
    for group, count in age_dist:
        print(f"     {group}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
