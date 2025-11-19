"""
Dynamic Pydantic model factory for runtime type generation.

Creates typed models based on object type definitions from the ontologia
metamodel, enabling full IDE support and validation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError, create_model
from pydantic.fields import FieldInfo

logger = logging.getLogger(__name__)


class ModelFactory:
    """
    Factory for creating dynamic Pydantic models from ontology object types.

    Enables runtime generation of typed models with full validation and
    IDE autocompletion support.
    """

    def __init__(self):
        """Initialize the model factory."""
        self._model_cache: dict[str, type[BaseModel]] = {}
        self._type_mappings = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "date": datetime,
            "datetime": datetime,
            "text": str,
            "json": dict[str, Any],
            "array": list[Any],
            "uuid": str,
        }

    def register_type_mapping(self, ontology_type: str, python_type: type) -> None:
        """
        Register a custom type mapping.

        Args:
            ontology_type: Type name from ontology (e.g., "custom_string")
            python_type: Python type to map to
        """
        self._type_mappings[ontology_type] = python_type
        logger.debug(f"Registered type mapping: {ontology_type} -> {python_type}")

    def _map_property_type(self, prop_def: dict[str, Any]) -> type:
        """
        Map ontology property type to Python type.

        Args:
            prop_def: Property definition from ontology

        Returns:
            Python type for the property
        """
        prop_type = prop_def.get("type", "string")

        # Handle array types
        if prop_type.startswith("array["):
            inner_type = prop_type[6:-1]  # Remove "array[" and "]"
            inner_python_type = self._type_mappings.get(inner_type, str)
            return list[inner_python_type]

        # Handle reference types
        if prop_type.startswith("reference["):
            # Reference to another object type
            return str  # For now, store as string (object primary key)

        # Direct type mapping
        python_type = self._type_mappings.get(prop_type, str)

        # Handle optional types
        if not prop_def.get("required", False):
            return Optional[python_type]

        return python_type

    def _create_field_info(self, prop_def: dict[str, Any]) -> FieldInfo:
        """
        Create Pydantic FieldInfo from property definition.

        Args:
            prop_def: Property definition from ontology

        Returns:
            FieldInfo instance for the property
        """
        field_kwargs = {}

        # Description
        if description := prop_def.get("description"):
            field_kwargs["description"] = description

        # Default value
        if "default" in prop_def:
            field_kwargs["default"] = prop_def["default"]
        elif not prop_def.get("required", False):
            field_kwargs["default"] = None

        # Handle constraints
        if min_length := prop_def.get("min_length"):
            field_kwargs["min_length"] = min_length

        if max_length := prop_def.get("max_length"):
            field_kwargs["max_length"] = max_length

        if minimum := prop_def.get("minimum"):
            field_kwargs["ge"] = minimum

        if maximum := prop_def.get("maximum"):
            field_kwargs["le"] = maximum

        # For string types, also constrain length
        if prop_def.get("type") == "string":
            if min_length := prop_def.get("min_length"):
                field_kwargs["min_length"] = min_length
            if max_length := prop_def.get("max_length"):
                field_kwargs["max_length"] = max_length

        # Examples
        if examples := prop_def.get("examples"):
            field_kwargs["examples"] = examples

        return Field(**field_kwargs)

    def create_model(
        self, object_type_def: dict[str, Any], model_name: str | None = None
    ) -> type[BaseModel]:
        """
        Create a Pydantic model from object type definition.

        Args:
            object_type_def: Object type definition from ontology
            model_name: Optional custom model name (defaults to api_name)

        Returns:
            Pydantic model class
        """
        api_name = object_type_def.get("api_name", "UnknownObject")
        # Sanitize model name for Python class
        sanitized_name = api_name.replace("-", "_").replace(".", "_")
        model_name = model_name or f"{sanitized_name.title()}Model"

        # Check cache first
        cache_key = f"{api_name}_{hash(json.dumps(object_type_def, sort_keys=True))}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        # Build model fields
        fields = {}

        # Add primary key field
        fields["pk"] = (str, Field(description="Primary key"))

        # Add properties
        properties = object_type_def.get("properties", [])
        for prop_def in properties:
            prop_name = prop_def["name"]
            prop_type = self._map_property_type(prop_def)
            field_info = self._create_field_info(prop_def)

            fields[prop_name] = (prop_type, field_info)

        # Create model with proper field configuration
        model_fields = {}
        for name, (field_type, field_info) in fields.items():
            model_fields[name] = (field_type, field_info)

        model = create_model(model_name, __base__=BaseModel, **model_fields)

        # Add metadata
        model._ontology_api_name = api_name
        model._ontology_definition = object_type_def

        # Cache the model
        self._model_cache[cache_key] = model

        logger.debug(f"Created model: {model_name} for {api_name}")
        return model

    def create_models_from_types(
        self, object_types: list[dict[str, Any]]
    ) -> dict[str, type[BaseModel]]:
        """
        Create multiple models from object type definitions.

        Args:
            object_types: List of object type definitions

        Returns:
            Dictionary mapping api_name to Pydantic model
        """
        models = {}

        for obj_type_def in object_types:
            api_name = obj_type_def.get("api_name")
            if not api_name:
                continue

            try:
                model = self.create_model(obj_type_def)
                models[api_name] = model
            except Exception as e:
                logger.error(f"Failed to create model for {api_name}: {e}")
                continue

        return models

    def get_model(self, api_name: str) -> type[BaseModel] | None:
        """
        Get cached model by API name.

        Args:
            api_name: API name of the object type

        Returns:
            Cached Pydantic model or None if not found
        """
        # Find model in cache by checking ontology_api_name
        for model in self._model_cache.values():
            if hasattr(model, "_ontology_api_name") and model._ontology_api_name == api_name:
                return model

        return None

    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._model_cache.clear()
        logger.debug("Model cache cleared")

    def get_cached_models(self) -> dict[str, type[BaseModel]]:
        """
        Get all cached models.

        Returns:
            Dictionary of cached models
        """
        return self._model_cache.copy()

    def validate_data(
        self, api_name: str, data: dict[str, Any]
    ) -> tuple[BaseModel | None, str | None]:
        """
        Validate data against a cached model.

        Args:
            api_name: API name of the object type
            data: Data to validate

        Returns:
            Tuple of (validated_model, error_message)
        """
        model = self.get_model(api_name)
        if not model:
            return None, f"No model found for {api_name}"

        try:
            validated = model(**data)
            return validated, None
        except ValidationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Validation error: {e}"


class ModelRegistry:
    """
    Registry for managing dynamic models with lifecycle support.

    Provides centralized access to models and handles updates/deletions.
    """

    def __init__(self, factory: ModelFactory | None = None):
        """Initialize the registry."""
        self.factory = factory or ModelFactory()
        self._registered_models: dict[str, type[BaseModel]] = {}

    async def register_object_type(self, object_type_def: dict[str, Any]) -> type[BaseModel]:
        """
        Register an object type and create its model.

        Args:
            object_type_def: Object type definition

        Returns:
            Created Pydantic model
        """
        api_name = object_type_def.get("api_name")
        if not api_name:
            raise ValueError("Object type definition must have api_name")

        model = self.factory.create_model(object_type_def)
        self._registered_models[api_name] = model

        logger.info(f"Registered model for {api_name}")
        return model

    async def unregister_object_type(self, api_name: str) -> None:
        """
        Unregister an object type.

        Args:
            api_name: API name of the object type to unregister
        """
        if api_name in self._registered_models:
            del self._registered_models[api_name]
            logger.info(f"Unregistered model for {api_name}")

    async def update_object_type(self, object_type_def: dict[str, Any]) -> type[BaseModel]:
        """
        Update an object type and recreate its model.

        Args:
            object_type_def: Updated object type definition

        Returns:
            New Pydantic model
        """
        api_name = object_type_def.get("api_name")
        if not api_name:
            raise ValueError("Object type definition must have api_name")

        # Remove old model from cache
        self.factory.clear_cache()

        # Create new model
        model = self.factory.create_model(object_type_def)
        self._registered_models[api_name] = model

        logger.info(f"Updated model for {api_name}")
        return model

    def get_model(self, api_name: str) -> type[BaseModel] | None:
        """
        Get model by API name.

        Args:
            api_name: API name of the object type

        Returns:
            Pydantic model or None
        """
        return self._registered_models.get(api_name) or self.factory.get_model(api_name)

    def list_models(self) -> list[str]:
        """
        List all registered model API names.

        Returns:
            List of API names
        """
        return list(self._registered_models.keys())

    def clear_all(self) -> None:
        """Clear all registered models and cache."""
        self._registered_models.clear()
        self.factory.clear_cache()
        logger.info("Cleared all registered models")


# Global instance for convenience
default_registry = ModelRegistry()


# Convenience functions


async def register_object_type(object_type_def: dict[str, Any]) -> type[BaseModel]:
    """Register object type using default registry."""
    return await default_registry.register_object_type(object_type_def)


async def unregister_object_type(api_name: str) -> None:
    """Unregister object type using default registry."""
    await default_registry.unregister_object_type(api_name)


def get_model(api_name: str) -> type[BaseModel] | None:
    """Get model using default registry."""
    return default_registry.get_model(api_name)


def validate_data(api_name: str, data: dict[str, Any]) -> tuple[BaseModel | None, str | None]:
    """Validate data using default registry."""
    return default_registry.factory.validate_data(api_name, data)
