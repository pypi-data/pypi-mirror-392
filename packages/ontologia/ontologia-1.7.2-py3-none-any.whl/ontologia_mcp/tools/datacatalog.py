from __future__ import annotations

from typing import Any

from fastapi import Depends
from ontologia_api.v2.schemas.datasets import DatasetPutRequest

from ontologia_mcp.server import _datacatalog_read_service, _datacatalog_service, mcp


@mcp.tool()
def upsert_dataset(
    api_name: str,
    schema: DatasetPutRequest,
    service=Depends(_datacatalog_service),
) -> dict[str, Any]:
    """Create or update a dataset in the Data Catalog."""

    dataset = service.upsert_dataset(
        api_name,
        source_type=schema.sourceType,
        source_identifier=schema.sourceIdentifier,
        display_name=schema.displayName,
        schema_definition=schema.schemaDefinition,
    )
    return dataset.model_dump(exclude_none=True)


@mcp.tool()
def list_datasets(
    service=Depends(_datacatalog_read_service),
) -> list[dict[str, Any]]:
    """List datasets registered in the Data Catalog for the current ontology."""

    datasets = service.list_datasets()
    return [ds.model_dump(exclude_none=True) for ds in datasets]
