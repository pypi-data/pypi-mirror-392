#!/usr/bin/env python3
"""
Basic CRUD Operations Example

This example shows how to perform basic Create, Read, Update, Delete operations
with Ontologia using the simple-api template.
"""

import os
import sys

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}"

# Credentials
USERNAME = "admin"
PASSWORD = "admin"


class OntologyClient:
    """Simple HTTP client for Ontologia API."""

    def __init__(self, base_url: str, username: str = USERNAME, password: str = PASSWORD):
        self.base_url = base_url
        self.token = None
        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str):
        """Authenticate and get JWT token."""
        response = httpx.post(
            f"{self.base_url}/v2/auth/token", data={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _headers(self):
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.token}"}

    def create_object_type(self, api_name: str, object_type_data: dict):
        """Create a new object type."""
        response = httpx.put(
            f"{self.base_url}/v2/ontologies/default/objectTypes/{api_name}",
            json=object_type_data,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_object_type(self, api_name: str):
        """Get an object type by API name."""
        response = httpx.get(
            f"{self.base_url}/v2/ontologies/default/objectTypes/{api_name}", headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def list_object_types(self):
        """List all object types."""
        response = httpx.get(
            f"{self.base_url}/v2/ontologies/default/objectTypes", headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def create_object(self, object_type: str, primary_key: str, object_data: dict):
        """Create a new object."""
        response = httpx.put(
            f"{self.base_url}/v2/ontologies/default/objects/{object_type}/{primary_key}",
            json=object_data,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_object(self, object_type: str, primary_key: str):
        """Get an object by primary key."""
        response = httpx.get(
            f"{self.base_url}/v2/ontologies/default/objects/{object_type}/{primary_key}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def update_object(self, object_type: str, primary_key: str, object_data: dict):
        """Update an object."""
        response = httpx.put(
            f"{self.base_url}/v2/ontologies/default/objects/{object_type}/{primary_key}",
            json=object_data,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def delete_object(self, object_type: str, primary_key: str):
        """Delete an object."""
        response = httpx.delete(
            f"{self.base_url}/v2/ontologies/default/objects/{object_type}/{primary_key}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def search_objects(self, object_type: str, where: list = None):
        """Search objects with optional filters."""
        search_data = {"objectTypeApiName": object_type}
        if where:
            search_data["where"] = where

        response = httpx.post(
            f"{self.base_url}/v2/ontologies/default/objects/search",
            json=search_data,
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()


def main():
    """Run basic CRUD example."""
    print("🚀 Ontologia Basic CRUD Example")
    print("=" * 50)

    # Initialize client
    try:
        client = OntologyClient(BASE_URL)
        print("✅ Connected to Ontologia API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("Make sure the API is running: docker-compose up -d")
        return 1

    try:
        # 1. Create an Employee object type
        print("\n📝 Creating Employee object type...")
        employee_type = {
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "Employee ID", "required": True},
                "name": {"dataType": "string", "displayName": "Full Name", "required": False},
                "email": {"dataType": "string", "displayName": "Email Address", "required": False},
                "department": {
                    "dataType": "string",
                    "displayName": "Department",
                    "required": False,
                },
                "salary": {"dataType": "decimal", "displayName": "Salary", "required": False},
            },
            "implements": [],
        }

        created_type = client.create_object_type("employee", employee_type)
        print(f"✅ Created object type: {created_type['apiName']}")

        # 2. Create employee objects
        print("\n👥 Creating employee objects...")

        employees = [
            {
                "id": "emp001",
                "name": "Alice Johnson",
                "email": "alice@company.com",
                "department": "Engineering",
                "salary": "85000.00",
            },
            {
                "id": "emp002",
                "name": "Bob Smith",
                "email": "bob@company.com",
                "department": "Engineering",
                "salary": "92000.00",
            },
            {
                "id": "emp003",
                "name": "Carol Davis",
                "email": "carol@company.com",
                "department": "Product",
                "salary": "88000.00",
            },
        ]

        for emp in employees:
            created = client.create_object("employee", emp["id"], {"properties": emp})
            print(f"✅ Created employee: {created['properties']['name']}")

        # 3. Read operations
        print("\n📖 Reading objects...")

        # Get specific employee
        alice = client.get_object("employee", "emp001")
        print(
            f"✅ Retrieved: {alice['properties']['name']} from {alice['properties']['department']}"
        )

        # List all object types
        types = client.list_object_types()
        print(f"✅ Found {len(types['data'])} object types")

        # 4. Search operations
        print("\n🔍 Searching objects...")

        # Search all employees
        all_employees = client.search_objects("employee")
        print(f"✅ Found {len(all_employees['data'])} employees")

        # Search engineering department
        engineers = client.search_objects(
            "employee", where=[{"property": "department", "op": "eq", "value": "Engineering"}]
        )
        print(f"✅ Found {len(engineers['data'])} engineers")

        # Search high salary employees
        high_earners = client.search_objects(
            "employee", where=[{"property": "salary", "op": "gt", "value": "90000.00"}]
        )
        print(f"✅ Found {len(high_earners['data'])} high earners")

        # 5. Update operations
        print("\n✏️ Updating objects...")

        # Update Carol's salary
        updated_carol = client.update_object(
            "employee",
            "emp003",
            {
                "properties": {
                    "id": "emp003",
                    "name": "Carol Davis",
                    "email": "carol@company.com",
                    "department": "Product",
                    "salary": "95000.00",  # Promotion!
                }
            },
        )
        print(
            f"✅ Updated {updated_carol['properties']['name']}'s salary to ${updated_carol['properties']['salary']}"
        )

        # 6. Delete operations
        print("\n🗑️ Deleting objects...")

        # Delete Bob (he left the company)
        client.delete_object("employee", "emp002")
        print("✅ Deleted employee emp002")

        # Verify deletion
        remaining = client.search_objects("employee")
        print(f"✅ {len(remaining['data'])} employees remaining")

        print("\n🎉 CRUD example completed successfully!")
        print("\n💡 Try these next:")
        print("   - Create relationships between objects")
        print("   - Add more complex search queries")
        print("   - Explore the API at http://localhost:8000/docs")

        return 0

    except Exception as e:
        print(f"\n❌ Error during CRUD operations: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
