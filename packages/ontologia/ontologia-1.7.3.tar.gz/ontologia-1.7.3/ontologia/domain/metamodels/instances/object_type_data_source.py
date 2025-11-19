"""
object_type_data_source.py
--------------------------
Association table connecting ObjectType (semantic layer) with Dataset (physical layer).

This model is the "glue" between the ontology's semantic definitions and the
physical data sources managed by the datacatalog. It enables:
- Data lineage tracking
- Multiple ObjectTypes from one Dataset
- Multiple Datasets for one ObjectType (federation)
- Sync metadata (last sync time, status, etc.)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from registro import ResourceTypeBaseModel
from sqlmodel import JSON, Column, Field, Relationship

if TYPE_CHECKING:
    # Note: Dataset removed in core - this model is simplified
    from datacatalog.models import Dataset, DatasetBranch

    from ontologia.domain.metamodels.types.object_type import ObjectType


class ObjectTypeDataSource(ResourceTypeBaseModel, table=True):
    """
    Links an ObjectType (semantic) to a Dataset (physical data source).

    This association table enables:
    - One ObjectType can be backed by multiple Datasets (federated sources)
    - One Dataset can power multiple ObjectTypes (reuse)
    - Track synchronization metadata
    - Data lineage and impact analysis

    Example:
        An "Employee" ObjectType might be sourced from:
        - employees.parquet (main data)
        - employee_updates.parquet (incremental updates)
    """

    __resource_type__ = "object-type-data-source"
    __tablename__ = "objecttypedatasource"

    # --- References ---
    object_type_rid: str = Field(foreign_key="objecttype.rid", index=True)
    object_type: "ObjectType" = Relationship(back_populates="data_sources")

    # Reference to the dataset (for backward compatibility)
    dataset_rid: str | None = Field(
        default=None,
        foreign_key="dataset.rid",
        index=True,
        description="Reference to the dataset (for backward compatibility)",
    )
    dataset: Optional["Dataset"] = Relationship(
        back_populates="object_type_links", sa_relationship_kwargs={"lazy": "joined"}
    )

    # Reference to the specific dataset branch this data source uses
    dataset_branch_rid: str | None = Field(
        default=None,
        foreign_key="datasetbranch.rid",
        index=True,
        description="Reference to the specific dataset branch this data source uses",
    )
    dataset_branch: Optional["DatasetBranch"] = Relationship(
        back_populates="object_type_links", sa_relationship_kwargs={"lazy": "joined"}
    )

    # Note: Dataset references removed in core version
    # Future: could add external data source references here

    # --- Sync Metadata ---
    last_sync_time: datetime | None = Field(
        default=None, description="Last time this ObjectType was synced from this Dataset"
    )
    # Optional incremental column name for APPEND mode
    incremental_field: str | None = Field(
        default=None, description="Nome da coluna incremental para sync incremental (APPEND)"
    )

    sync_status: str | None = Field(
        default="pending",
        description="Current sync status: 'pending', 'in_progress', 'completed', 'failed'",
    )

    # Record last transaction used for sync (lineage)
    last_synced_transaction_rid: str | None = Field(
        default=None,
        description="RID lógico da transação usada no último sync (sem FK no core)",
    )

    # --- Mapping Configuration ---
    # Optional: store mapping rules if column names differ between Dataset and ObjectType
    # For example: Dataset has "emp_id" but ObjectType expects "employee_id"
    property_mappings: dict[str, str] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Map dataset column -> ObjectType property (e.g., 'emp_id' -> 'id')",
    )

    def __repr__(self) -> str:
        return (
            "ObjectTypeDataSource("
            f"object_type_rid='{self.object_type_rid}', "
            f"last_sync_time='{self.last_sync_time}', "
            f"incremental_field='{self.incremental_field}', "
            f"last_synced_transaction_rid='{self.last_synced_transaction_rid}', "
            f"sync_status='{self.sync_status}')"
        )


# Import at the end to avoid circular imports
# Note: These imports are needed for model_rebuild() to work

from ontologia.domain.metamodels.types.object_type import ObjectType

ObjectTypeDataSource.model_rebuild()
