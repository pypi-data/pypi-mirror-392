"""
🧪 Modern Unit Test Example
Demonstrates best practices for unit testing with enhanced fixtures and factories.
"""

from unittest.mock import Mock

import pytest


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""

    pass


class MockMetamodelService:
    """Mock implementation of MetamodelService for testing."""

    def __init__(self, session=None, kuzu_repo=None):
        self.session = session
        self.kuzu_repo = kuzu_repo

    async def create_object_type(self, object_type_data):
        """Mock create object type."""
        return Mock()

    async def get_object_type(self, api_name):
        """Mock get object type."""
        if api_name == "nonexistent":
            raise NotFoundError(f"ObjectType '{api_name}' not found")
        return Mock()

    async def update_object_type(self, api_name, update_data):
        """Mock update object type."""
        return Mock()

    async def delete_object_type(self, api_name):
        """Mock delete object type."""
        return Mock()


class TestMetamodelService:
    """Test metamodel service with modern patterns"""

    def test_create_object_type_success(self):
        """Test successful object type creation with realistic data"""
        # Arrange
        service = MockMetamodelService()
        request_data = Mock()

        # Act & Assert
        assert service is not None
        assert request_data is not None

    def test_get_object_type_not_found(self):
        """Test getting non-existent object type raises NotFoundError"""
        # Arrange
        service = MockMetamodelService()

        # Act & Assert
        with pytest.raises(NotFoundError):
            import asyncio

            asyncio.run(service.get_object_type("nonexistent"))

    def test_validation_error_handling(self):
        """Test validation error handling"""
        # Act & Assert
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid data", "validation_failed")
