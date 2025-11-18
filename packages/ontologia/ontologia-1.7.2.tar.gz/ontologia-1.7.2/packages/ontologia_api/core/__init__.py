"""Core utilities for the API."""

from ontologia_api.core.database import engine, get_session

__all__ = ["engine", "get_session"]
