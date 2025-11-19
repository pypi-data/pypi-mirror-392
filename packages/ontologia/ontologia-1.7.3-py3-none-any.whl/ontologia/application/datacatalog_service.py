"""Core data catalog service used by API routes and change-set workflows."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction, TransactionType
from fastapi import HTTPException, status
from registro.core.resource import Resource
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class DataCatalogService:
    """Manage datasets, branches, and transactions within the data catalog."""

    def __init__(
        self,
        session_or_metamodel: Session | Any,
        instances_service: Any | None = None,
        *,
        service: str = "ontology",
        instance: str = "default",
        principal: Any | None = None,
        session: Session | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        if isinstance(session_or_metamodel, Session):
            self.session = session_or_metamodel
            self.metamodel_service = legacy_kwargs.get("metamodel_service")
            self.instances_service = instances_service
        else:
            self.metamodel_service = session_or_metamodel
            self.instances_service = instances_service
            self.session = session or self._infer_session()
            if self.session is None:
                raise ValueError("DataCatalogService requires an active SQLModel Session")

        self.service = service
        self.instance = instance
        self.principal = principal
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Dataset operations
    # ------------------------------------------------------------------
    def list_datasets(self) -> list[Dataset]:
        stmt = self._dataset_stmt()
        return list(self.session.exec(stmt).all())

    def get_dataset(self, api_name: str) -> Dataset | None:
        return self._dataset_by_api_name(api_name)

    def delete_dataset(self, api_name: str) -> bool:
        dataset = self._dataset_by_api_name(api_name)
        if not dataset:
            return False
        self.session.delete(dataset)
        self.session.commit()
        return True

    def upsert_dataset(
        self,
        api_name: str,
        *,
        source_type: str,
        source_identifier: str,
        display_name: str | None = None,
        schema_definition: dict[str, Any] | None = None,
    ) -> Dataset:
        dataset = self._dataset_by_api_name(api_name)
        if dataset:
            dataset.source_type = source_type
            dataset.source_identifier = source_identifier
            dataset.schema_definition = dict(schema_definition or {})
            if display_name:
                dataset.display_name = display_name
            self.session.add(dataset)
        else:
            dataset = Dataset(
                service=self.service,
                instance=self.instance,
                api_name=api_name,
                display_name=display_name or api_name,
                source_type=source_type,
                source_identifier=source_identifier,
                schema_definition=dict(schema_definition or {}),
            )
            self.session.add(dataset)
        self.session.commit()
        self.session.refresh(dataset)
        return dataset

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def create_transaction(
        self,
        dataset_api_name: str,
        *,
        transaction_type: TransactionType,
        commit_message: str | None = None,
    ) -> DatasetTransaction:
        dataset = self._require_dataset(dataset_api_name)
        tx = DatasetTransaction(
            service=self.service,
            instance=self.instance,
            api_name=f"{dataset_api_name}-tx-{int(datetime.now(UTC).timestamp())}",
            display_name=commit_message or transaction_type.value,
            dataset_rid=dataset.rid,
            transaction_type=transaction_type,
            commit_message=commit_message,
        )
        self.session.add(tx)
        self.session.commit()
        self.session.refresh(tx)
        return tx

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------
    def list_branches(self, dataset_api_name: str) -> list[DatasetBranch]:
        dataset = self._require_dataset(dataset_api_name)
        stmt = select(DatasetBranch).where(DatasetBranch.dataset_rid == dataset.rid)
        return list(self.session.exec(stmt).all())

    def upsert_branch(
        self,
        dataset_api_name: str,
        *,
        branch_name: str,
        head_transaction_rid: str,
    ) -> DatasetBranch:
        dataset = self._require_dataset(dataset_api_name)
        stmt = select(DatasetBranch).where(
            DatasetBranch.dataset_rid == dataset.rid,
            DatasetBranch.branch_name == branch_name,
        )
        branch = self.session.exec(stmt).first()

        if branch:
            branch.head_transaction_rid = head_transaction_rid
            self.session.add(branch)
        else:
            branch = DatasetBranch(
                service=self.service,
                instance=self.instance,
                api_name=f"{dataset_api_name}-branch-{branch_name}",
                display_name=branch_name,
                dataset_rid=dataset.rid,
                branch_name=branch_name,
                head_transaction_rid=head_transaction_rid,
            )
            self.session.add(branch)

        self.session.flush()
        if dataset.default_branch_rid is None:
            dataset.default_branch_rid = branch.rid
            self.session.add(dataset)

        self.session.commit()
        self.session.refresh(branch)
        return branch

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _infer_session(self) -> Session | None:
        candidates = []
        repo = getattr(self.metamodel_service, "repository", None)
        if repo is not None:
            candidates.append(getattr(repo, "session", None))
        inst_repo = getattr(
            getattr(self.instances_service, "instances_repository", None), "session", None
        )
        candidates.append(inst_repo)
        for candidate in candidates:
            if candidate is not None:
                return candidate
        return None

    def _dataset_stmt(self):
        return (
            select(Dataset)
            .join(Resource, Resource.rid == Dataset.rid)
            .where(
                Resource.service == self.service,
                Resource.instance == self.instance,
            )
        )

    def _dataset_by_api_name(self, api_name: str) -> Dataset | None:
        stmt = self._dataset_stmt().where(Dataset.api_name == api_name)
        return self.session.exec(stmt).first()

    def _require_dataset(self, api_name: str) -> Dataset:
        dataset = self._dataset_by_api_name(api_name)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{api_name}' not found",
            )
        return dataset
        # Implementation would perform full-text search
        raise NotImplementedError("Data catalog service implementation pending")

    async def get_lineage(
        self,
        entry_id: str,
        *,
        direction: str = "downstream",
        max_depth: int = 5,
    ) -> dict[str, Any]:
        """
        Get data lineage for a catalog entry.

        Args:
            entry_id: ID of the catalog entry
            direction: Direction of lineage ("upstream", "downstream", "both")
            max_depth: Maximum depth of lineage traversal

        Returns:
            Lineage graph representation
        """
        self.logger.info(f"Getting lineage for catalog entry: {entry_id}")
        # Implementation would traverse lineage relationships
        raise NotImplementedError("Data catalog service implementation pending")

    async def validate_schema(
        self,
        schema_definition: dict[str, Any],
        data_type: str,
    ) -> bool:
        """
        Validate a schema definition.

        Args:
            schema_definition: Schema definition to validate
            data_type: Type of data being validated

        Returns:
            True if valid, False otherwise
        """
        self.logger.info(f"Validating schema for data type: {data_type}")
        # Implementation would validate schema structure
        raise NotImplementedError("Data catalog service implementation pending")
