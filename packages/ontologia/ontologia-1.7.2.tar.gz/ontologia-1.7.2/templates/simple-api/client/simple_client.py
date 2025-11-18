#!/usr/bin/env python3
"""
Simple Ontologia Client

A minimal, easy-to-use client for interacting with Ontologia API.
Perfect for getting started and simple applications.
"""

import os
import sys
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SimpleOntologiaClient:
    """
    Simple client for Ontologia API.

    This client provides a clean, minimal interface for common operations.
    It handles authentication, error handling, and provides convenient methods.
    """

    def __init__(
        self,
        host: str = None,
        port: str = None,
        username: str = "admin",
        password: str = "admin",
        ontology: str = "default",
    ):
        """
        Initialize the client.

        Args:
            host: API host (default from environment or localhost)
            port: API port (default from environment or 8000)
            username: Username for authentication (default: admin)
            password: Password for authentication (default: admin)
            ontology: Ontology name (default: default)
        """
        self.host = host or os.getenv("API_HOST", "localhost")
        self.port = port or os.getenv("API_PORT", "8000")
        self.base_url = f"http://{self.host}:{self.port}"
        self.ontology = ontology
        self.username = username
        self.password = password
        self._token = None
        self._client = None

        # Auto-authenticate
        self._authenticate()

    def _authenticate(self):
        """Authenticate with the API."""
        try:
            response = httpx.post(
                f"{self.base_url}/v2/auth/token",
                data={"username": self.username, "password": self.password},
            )
            response.raise_for_status()
            token_data = response.json()
            self._token = token_data["access_token"]

            # Create HTTP client with default headers
            self._client = httpx.Client(
                base_url=self.base_url, headers={"Authorization": f"Bearer {self._token}"}
            )

        except Exception as e:
            raise Exception(f"Failed to authenticate: {e}")

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 401:
            raise Exception("Authentication failed - token may be expired")
        elif response.status_code == 403:
            raise Exception("Access forbidden - insufficient permissions")
        elif response.status_code == 404:
            raise Exception("Resource not found")
        elif response.status_code >= 400:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        return response.json()

    def health(self) -> dict[str, Any]:
        """Check API health status."""
        response = self._client.get("/health")
        return self._handle_response(response)

    # Object Type Methods

    def create_object_type(self, api_name: str, object_type: dict[str, Any]) -> dict[str, Any]:
        """Create a new object type."""
        response = self._client.put(
            f"/v2/ontologies/{self.ontology}/objectTypes/{api_name}", json=object_type
        )
        return self._handle_response(response)

    def get_object_type(self, api_name: str) -> dict[str, Any]:
        """Get an object type by API name."""
        response = self._client.get(f"/v2/ontologies/{self.ontology}/objectTypes/{api_name}")
        return self._handle_response(response)

    def list_object_types(self) -> dict[str, Any]:
        """List all object types."""
        response = self._client.get(f"/v2/ontologies/{self.ontology}/objectTypes")
        return self._handle_response(response)

    def update_object_type(self, api_name: str, object_type: dict[str, Any]) -> dict[str, Any]:
        """Update an object type."""
        response = self._client.put(
            f"/v2/ontologies/{self.ontology}/objectTypes/{api_name}", json=object_type
        )
        return self._handle_response(response)

    def delete_object_type(self, api_name: str) -> dict[str, Any]:
        """Delete an object type."""
        response = self._client.delete(f"/v2/ontologies/{self.ontology}/objectTypes/{api_name}")
        return self._handle_response(response)

    # Object Methods

    def create_object(
        self, object_type: str, primary_key: str, obj: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new object."""
        response = self._client.put(
            f"/v2/ontologies/{self.ontology}/objects/{object_type}/{primary_key}", json=obj
        )
        return self._handle_response(response)

    def get_object(self, object_type: str, primary_key: str) -> dict[str, Any]:
        """Get an object by primary key."""
        response = self._client.get(
            f"/v2/ontologies/{self.ontology}/objects/{object_type}/{primary_key}"
        )
        return self._handle_response(response)

    def update_object(
        self, object_type: str, primary_key: str, obj: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an object."""
        response = self._client.put(
            f"/v2/ontologies/{self.ontology}/objects/{object_type}/{primary_key}", json=obj
        )
        return self._handle_response(response)

    def delete_object(self, object_type: str, primary_key: str) -> dict[str, Any]:
        """Delete an object."""
        response = self._client.delete(
            f"/v2/ontologies/{self.ontology}/objects/{object_type}/{primary_key}"
        )
        return self._handle_response(response)

    def search_objects(
        self, object_type: str, where: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Search objects with optional filters."""
        search_data = {"objectTypeApiName": object_type}
        if where:
            search_data["where"] = where

        response = self._client.post(
            f"/v2/ontologies/{self.ontology}/objects/search", json=search_data
        )
        return self._handle_response(response)

    # Link Type Methods

    def create_link_type(self, api_name: str, link_type: dict[str, Any]) -> dict[str, Any]:
        """Create a new link type."""
        response = self._client.put(
            f"/v2/ontologies/{self.ontology}/linkTypes/{api_name}", json=link_type
        )
        return self._handle_response(response)

    def get_link_type(self, api_name: str) -> dict[str, Any]:
        """Get a link type by API name."""
        response = self._client.get(f"/v2/ontologies/{self.ontology}/linkTypes/{api_name}")
        return self._handle_response(response)

    def list_link_types(self) -> dict[str, Any]:
        """List all link types."""
        response = self._client.get(f"/v2/ontologies/{self.ontology}/linkTypes")
        return self._handle_response(response)

    # Linked Objects Methods

    def create_link(
        self, link_type: str, from_object: str, to_object: str, link: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a link between objects."""
        response = self._client.put(
            f"/v2/ontologies/linkedObjects/{link_type}/{from_object}/{to_object}", json=link
        )
        return self._handle_response(response)

    def get_links(self, link_type: str, from_object: str, to_object: str = None) -> dict[str, Any]:
        """Get links between objects."""
        if to_object:
            url = f"/v2/ontologies/linkedObjects/{link_type}/{from_object}/{to_object}"
        else:
            url = f"/v2/ontologies/{self.ontology}/objects/{from_object}/{link_type}"

        response = self._client.get(url)
        return self._handle_response(response)

    def delete_link(self, link_type: str, from_object: str, to_object: str) -> dict[str, Any]:
        """Delete a link between objects."""
        response = self._client.delete(
            f"/v2/ontologies/linkedObjects/{link_type}/{from_object}/{to_object}"
        )
        return self._handle_response(response)

    # Utility Methods

    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Example usage of the SimpleOntologiaClient."""
    print("🚀 Simple Ontologia Client Example")
    print("=" * 50)

    try:
        # Initialize client
        with SimpleOntologiaClient() as client:
            print("✅ Connected to Ontologia API")

            # Check health
            health = client.health()
            print(f"✅ API Status: {health['status']}")

            # Create object type
            print("\n📝 Creating object type...")
            employee_type = {
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name", "required": False},
                    "department": {
                        "dataType": "string",
                        "displayName": "Department",
                        "required": False,
                    },
                },
                "implements": [],
            }

            created = client.create_object_type("employee", employee_type)
            print(f"✅ Created: {created['apiName']}")

            # Create objects
            print("\n👥 Creating objects...")
            employees = [
                {"properties": {"id": "emp1", "name": "Alice", "department": "Engineering"}},
                {"properties": {"id": "emp2", "name": "Bob", "department": "Product"}},
            ]

            for emp in employees:
                obj = client.create_object("employee", emp["properties"]["id"], emp)
                print(f"✅ Created: {obj['properties']['name']}")

            # Search objects
            print("\n🔍 Searching objects...")
            results = client.search_objects("employee")
            print(f"✅ Found {len(results['data'])} employees")

            for emp in results["data"]:
                print(f"   - {emp['properties']['name']} ({emp['properties']['department']})")

            print("\n🎉 Client example completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
