"""
models_sql.py
-------------
SQLModel-backed persistence models for instance layer.
Separated from public module names to allow `object_instance.py` and
`linked_object.py` to become DTOs.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import JSON, TIMESTAMP, Column, Field


class ObjectInstance(ResourceTypeBaseModel, table=True):
    __resource_type__ = "object-instance"
    __tablename__ = "objectinstance"

    __table_args__ = (
        UniqueConstraint(
            "object_type_rid",
            "pk_value",
            "valid_from",
            "transaction_from",
            name="uq_objectinstance_ot_pk_temporal",
        ),
    )

    # Service and instance for multi-tenancy
    # Store in different internal fields to avoid conflict with parent properties
    service_value: str = Field(
        default="default", alias="_service", index=True, description="Service identifier"
    )
    instance_value: str = Field(
        default="default", alias="_instance", index=True, description="Instance identifier"
    )

    # Referência ao tipo semântico
    object_type_api_name: str = Field(
        index=True, description="API name do ObjectType desta instância"
    )
    object_type_rid: str = Field(foreign_key="objecttype.rid", index=True)

    # Valor normalizado da PK (armazenado como string)
    pk_value: str = Field(
        index=True, description="Valor da chave primária desta instância, normalizado como string"
    )

    # Payload com propriedades desta instância
    data: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(MutableDict.as_mutable(JSON))
    )

    # === BITEMPORAL COLUMNS ===
    # Valid Time: quando o dado é válido no mundo real
    valid_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Início do período de validade do dado no mundo real",
        sa_column=Column(TIMESTAMP, index=True),
    )
    valid_to: datetime | None = Field(
        default=None,
        description="Fim do período de validade do dado no mundo real (null = ainda válido)",
        sa_column=Column(TIMESTAMP, index=True),
    )

    # Transaction Time: quando o dado foi registrado/conhecido no sistema
    transaction_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Início do período em que o sistema tem conhecimento deste dado",
        sa_column=Column(TIMESTAMP, index=True),
    )
    transaction_to: datetime | None = Field(
        default=None,
        description="Fim do período em que o sistema tem conhecimento deste dado (null = ainda conhecimento)",
        sa_column=Column(TIMESTAMP, index=True),
    )

    # Timestamps para auditoria e controle
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Override service and instance properties to use internal fields
    @property
    def service(self) -> str:
        """Get the service value."""
        return self.service_value

    @service.setter
    def service(self, value: str):
        """Set the service value."""
        self.service_value = value

    @property
    def instance(self) -> str:
        """Get the instance value."""
        return self.instance_value

    @instance.setter
    def instance(self, value: str):
        """Set the instance value."""
        self.instance_value = value

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to ensure service and instance are set."""
        super().model_post_init(__context)
        # Ensure service and instance are properly set from the fields
        if hasattr(self, "service_value") and self.service_value != "default":
            # The field was set, keep it
            pass
        elif hasattr(self, "_service") and self._service != "default":
            # The alias was used, copy it to the field
            self.service_value = self._service
        elif hasattr(self, "service") and self.service != "default":
            # The property was set, copy it to the field
            self.service_value = self.service

        if hasattr(self, "instance_value") and self.instance_value != "default":
            # The field was set, keep it
            pass
        elif hasattr(self, "_instance") and self._instance != "default":
            # The alias was used, copy it to the field
            self.instance_value = self._instance
        elif hasattr(self, "instance") and self.instance != "default":
            # The property was set, copy it to the field
            self.instance_value = self.instance

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"ObjectInstance(api_name='{self.api_name}', object_type='{self.object_type_api_name}', "
            f"pk_value='{self.pk_value}')"
        )


class LinkedObject(ResourceTypeBaseModel, table=True):
    __resource_type__ = "linked-object"
    __tablename__ = "linkedobject"

    __table_args__ = (
        # Unicidade por tipo de link + pares from/to com suporte temporal
        UniqueConstraint(
            "link_type_rid",
            "from_object_rid",
            "to_object_rid",
            "source_pk_value",
            "target_pk_value",
            "valid_from",
            "transaction_from",
            name="uq_linkedobject_unique_temporal",
        ),
    )

    # Referência ao LinkType semântico
    link_type_api_name: str = Field(index=True, description="API name do LinkType desta relação")
    link_type_rid: str = Field(foreign_key="linktype.rid", index=True)

    # Extremidades da relação (instâncias de objetos) - opcionais para compat:
    from_object_rid: str | None = Field(default=None, foreign_key="objectinstance.rid", index=True)
    to_object_rid: str | None = Field(default=None, foreign_key="objectinstance.rid", index=True)

    # Suporte direto por PK (evita joins no service/repos):
    source_pk_value: str = Field(index=True)
    target_pk_value: str = Field(index=True)

    # Link properties payload (edge attributes)
    data: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(MutableDict.as_mutable(JSON))
    )

    # === BITEMPORAL COLUMNS ===
    # Valid Time: quando a relação é válida no mundo real
    valid_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Início do período de validade da relação no mundo real",
        sa_column=Column(TIMESTAMP, index=True),
    )
    valid_to: datetime | None = Field(
        default=None,
        description="Fim do período de validade da relação no mundo real (null = ainda válida)",
        sa_column=Column(TIMESTAMP, index=True),
    )

    # Transaction Time: quando a relação foi registrada/conhecida no sistema
    transaction_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Início do período em que o sistema tem conhecimento desta relação",
        sa_column=Column(TIMESTAMP, index=True),
    )
    transaction_to: datetime | None = Field(
        default=None,
        description="Fim do período em que o sistema tem conhecimento desta relação (null = ainda conhecimento)",
        sa_column=Column(TIMESTAMP, index=True),
    )

    # Timestamps para auditoria
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"LinkedObject(api_name='{self.api_name}', link_type='{self.link_type_api_name}', "
            f"from='{self.source_pk_value}', to='{self.target_pk_value}')"
        )

    # Proxy para compatibilidade com services que usam .properties
    @property
    def properties(self) -> dict[str, Any]:
        return dict(self.data or {})

    @properties.setter
    def properties(self, value: dict[str, Any]) -> None:
        self.data = dict(value or {})


# Late imports to avoid cycles

# Rebuild models after late imports
ObjectInstance.model_rebuild()
LinkedObject.model_rebuild()
