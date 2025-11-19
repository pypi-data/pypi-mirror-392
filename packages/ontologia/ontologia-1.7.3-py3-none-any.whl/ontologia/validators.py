"""Validation utilities for ontologia-core.

Provides common validation functions used across services.
"""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException, status


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Validate that a value is a non-empty string."""
    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be a string"
        )
    if not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} cannot be empty"
        )
    return value.strip()


def validate_rid(rid: str, field_name: str = "RID") -> str:
    """Validate RID format (basic check)."""
    clean_rid = validate_non_empty_string(rid, field_name)
    if len(clean_rid) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} appears to be invalid (too short)",
        )
    return clean_rid


def validate_different_values(value1: str, value2: str, field1_name: str, field2_name: str) -> None:
    """Validate that two values are different."""
    if value1 == value2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field1_name} and {field2_name} must be different",
        )


def validate_api_name(name: str, field_name: str = "API name") -> str:
    """Validate API name format (alphanumeric, underscores, hyphens)."""
    clean_name = validate_non_empty_string(name, field_name)
    if not re.match(r"^[a-zA-Z0-9_-]+$", clean_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} can only contain letters, numbers, underscores, and hyphens",
        )
    return clean_name


def validate_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Validate properties dictionary."""
    if properties is None:
        return {}
    if not isinstance(properties, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Properties must be a dictionary"
        )
    # Ensure all keys are strings
    for key in properties.keys():
        if not isinstance(key, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Property key '{key}' must be a string",
            )
    return properties


def validate_service_instance(service: str, instance: str) -> tuple[str, str]:
    """Validate service and instance parameters."""
    clean_service = validate_non_empty_string(service, "Service")
    clean_instance = validate_non_empty_string(instance, "Instance")
    return clean_service, clean_instance
