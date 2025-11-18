"""
object_type.py
-------------
This module defines the ObjectType model which represents object types
in the ontology. It manages property definitions and relationships
with other object types through link types.

Key Features:
- Object type metadata
- Property type management
- Link type relationships
- Validation and persistence
"""

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource
    from ontologia.domain.metamodels.types.interface_type import InterfaceType
    from ontologia.domain.metamodels.types.link_type import LinkType
    from ontologia.domain.metamodels.types.property_type import PropertyType

from pydantic import ConfigDict, field_validator
from registro import ResourceTypeBaseModel
from sqlalchemy import true
from sqlmodel import Field, Relationship, Session, delete, select

from ontologia.domain.metamodels.types.object_type_interface_link import ObjectTypeInterfaceLink
from ontologia.domain.metamodels.value_objects import PropertyDefinition as DomainPropertyDefinition


class ObjectType(ResourceTypeBaseModel, table=True):
    """
    Represents an object type in the ontology.
    Object types define the structure and relationships of objects.
    """

    __resource_type__ = "object-type"
    # Note: service and instance are handled by ResourceTypeBaseModel
    # Uniqueness will be enforced at the application level

    # Pydantic v2 config
    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"exclude": {"property_types", "outgoing_link_types"}}
    )

    # Identity and metadata
    api_name: str = Field(index=True)
    display_name: str
    description: str | None = None
    primary_key_field: str = Field(...)
    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Flag indicating latest schema", index=True)

    # Relationships
    property_types: list["PropertyType"] = Relationship(
        back_populates="object_type",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    # Bidirectional link relationships
    # Note: foreign_keys must be specified because LinkType has two FKs to ObjectType
    outgoing_links: list["LinkType"] = Relationship(
        back_populates="from_object_type",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "LinkType.from_object_type_rid",
        },
    )

    incoming_links: list["LinkType"] = Relationship(
        back_populates="to_object_type",
        sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "LinkType.to_object_type_rid"},
    )

    # Data source relationships (connects semantic layer to physical data)
    data_sources: list["ObjectTypeDataSource"] = Relationship(
        back_populates="object_type", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Semantic interfaces implemented by this ObjectType (many-to-many)
    interfaces: list["InterfaceType"] = Relationship(
        back_populates="object_types",
        link_model=ObjectTypeInterfaceLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    @field_validator("property_types", check_fields=False)
    def validate_property_types(cls, v: list["PropertyType"], info: Any) -> list["PropertyType"]:
        """Validate property types and set their object_type_api_name."""
        if v is None:
            return []

        api_name = info.data.get("api_name")
        if not api_name:
            raise ValueError("ObjectType must have an api_name")

        # Set object_type_api_name for each property
        for prop in v:
            prop.object_type_api_name = api_name
            if prop.api_name == info.data.get("primary_key_field"):
                prop.is_primary_key = True
                prop.required = True

        return v

    def get_property(self, api_name: str) -> Optional["PropertyType"]:
        """Get a property type by its API name."""
        return next((p for p in self.property_types if p.api_name == api_name), None)

    # set_properties removed: reconciliation now centralized in MetamodelService.upsert_object_type()

    @property
    def properties(self) -> list[dict[str, Any]]:
        """
        Get properties as a list of dictionaries for backward compatibility.
        """
        return [prop.to_dict() for prop in self.property_types]

    def set_properties(self, desired: Iterable[DomainPropertyDefinition], session: Session) -> None:
        """
        Reconcile this ObjectType's PropertyTypes to match the desired set.

        - Adds new PropertyTypes.
        - Updates existing PropertyTypes (display_name, description, data_type, config, quality_checks, security_tags, required, is_primary_key, derivation_script, references_object_type_api_name).
        - Removes PropertyTypes not present in the desired set.

        Args:
            desired: Iterable of DomainPropertyDefinition describing the desired state.
            session: SQLAlchemy session used to load existing properties and persist changes.
        """
        # Load current properties from DB (ensure up-to-date state)
        from ontologia.domain.metamodels.types.property_type import PropertyType

        desired_by_name = {p.api_name: p for p in desired}

        if self.primary_key_field not in desired_by_name:
            raise ValueError("Desired properties must include primary key")

        # Replace existing properties wholesale to ensure reconciliation matches desired state
        session.exec(delete(PropertyType).where(PropertyType.object_type_rid == self.rid))

        for api_name, prop_def in desired_by_name.items():
            is_pk = (api_name == self.primary_key_field) or bool(
                getattr(prop_def, "is_primary_key", False)
            )
            required = bool(prop_def.required or is_pk)

            new_prop = PropertyType(
                api_name=api_name,
                display_name=prop_def.display_name or api_name,
                description=prop_def.description,
                data_type=prop_def.data_type,
                data_type_config=prop_def.data_type_config or {},
                required=required,
                is_primary_key=is_pk,
                quality_checks=list(prop_def.quality_checks or ()),
                security_tags=list(prop_def.security_tags or ()),
                object_type_rid=self.rid,
                object_type_api_name=self.api_name,
                service=self.service,
                instance=self.instance,
                derivation_script=getattr(prop_def, "derivation_script", None),
                references_object_type_api_name=getattr(
                    prop_def, "references_object_type_api_name", None
                ),
            )
            session.add(new_prop)
        # Note: caller should commit the session after calling this method

    @classmethod
    def validate_unique_service_instance_api_name(
        cls,
        service: str,
        instance: str,
        api_name: str,
        session,
        *,
        exclude_rid: str | None = None,
    ) -> None:
        """Validate that ObjectType.api_name is unique per (service, instance)."""
        from registro.core.resource import Resource

        stmt = (
            select(cls)
            .join(Resource, Resource.rid == cls.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                cls.api_name == api_name,
                cls.is_latest == true(),
            )
        )
        existing = session.exec(stmt).first()
        if existing and existing.rid != exclude_rid:
            raise ValueError(
                f"ObjectType with api_name '{api_name}' already exists in service '{service}' instance '{instance}'"
            )

    def validate_unique_before_save(self, session) -> None:
        """Validate uniqueness constraints before saving."""
        if self.is_latest:
            self.validate_unique_service_instance_api_name(
                self.service,
                self.instance,
                self.api_name,
                session,
                exclude_rid=self.rid,
            )

    @property
    def primary_key(self) -> str:
        """Get the primary key field name for backward compatibility."""
        return self.primary_key_field


# Late imports to avoid cycles
from ontologia.domain.metamodels.types.interface_type import InterfaceType

# Rebuild models after late imports
ObjectType.model_rebuild()
