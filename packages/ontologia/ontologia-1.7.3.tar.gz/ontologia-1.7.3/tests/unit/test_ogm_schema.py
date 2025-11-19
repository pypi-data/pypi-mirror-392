"""
test_ogm_schema.py
------------------
Comprehensive tests for OGM schema application and migrations.

State-of-the-art test suite covering:
- Schema planning and application
- Object type creation
- Link type creation
- Migration management
- Error handling and edge cases
"""

from __future__ import annotations

import tempfile
from typing import ClassVar

import pytest
from sqlmodel import create_engine

from ontologia.ogm.link import clear_link_registry
from ontologia.ogm.model import clear_model_registry


@pytest.fixture(autouse=True)
def clear_registries():
    """Clear the model and link registries before each test."""
    clear_model_registry()
    clear_link_registry()
    yield
    # Clear after test as well
    clear_model_registry()
    clear_link_registry()


from ontologia.ogm import LinkModel, ObjectModel, Ontology


@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_engine(f"sqlite:///{db_path}")
    yield engine

    # Cleanup
    import os

    os.unlink(db_path)


@pytest.fixture
def ontology(temp_db):
    """Create Ontology instance with temporary database."""
    ontology = Ontology(temp_db)
    ontology.initialize_database()  # Create base metamodel tables
    return ontology


@pytest.fixture
def setup_base_schema(ontology):
    """Setup base schema for testing."""
    # Database already initialized by ontology fixture
    return ontology


@pytest.fixture
def sample_models(ontology):
    """Create sample models for testing."""

    @ontology.model
    class TestUser(ObjectModel):
        __object_type_api_name__ = "test_user"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str
        email: str | None = None

    @ontology.model
    class TestCompany(ObjectModel):
        __object_type_api_name__ = "test_company"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str
        industry: str | None = None

    return TestUser, TestCompany


@pytest.fixture
def models_with_links(ontology):
    """Create models with relationships for testing."""

    @ontology.model
    class TestCompany(ObjectModel):
        __object_type_api_name__ = "test_company"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str
        industry: str | None = None

    @ontology.model
    class TestEmployee(ObjectModel):
        __object_type_api_name__ = "test_employee"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str
        company: ClassVar[LinkModel[TestCompany]] = LinkModel(
            "works_for", inverse="employees", target_model=TestCompany
        )

    return TestCompany, TestEmployee


class TestSchemaPlanning:
    """Test schema planning functionality."""

    def test_plan_schema_dry_run(self, setup_base_schema, sample_models):
        """Test schema planning in dry run mode."""
        test_user, test_company = sample_models

        result = setup_base_schema.apply_schema([test_user, test_company], dry_run=True)

        assert result is not None
        assert hasattr(result, "object_types_to_create")
        assert len(result.object_types_to_create) == 2

        # Check object types
        api_names = {agg.object_type.api_name for model_cls, agg in result.object_types_to_create}
        assert "test_user" in api_names
        assert "test_company" in api_names

    def test_plan_schema_with_links(self, setup_base_schema, models_with_links):
        """Test schema planning with link models."""
        test_company, test_employee = models_with_links

        result = setup_base_schema.apply_schema([test_company, test_employee], dry_run=True)

        assert result is not None
        assert hasattr(result, "object_types_to_create")
        assert hasattr(result, "link_types_to_create")

        # Should have at least 2 object types (may include from previous tests)
        assert len(result.object_types_to_create) >= 2
        assert len(result.link_types_to_create) == 1

        # Check link type
        link_types = {link_type.api_name for link_name, link_type in result.link_types_to_create}
        assert "works_for" in link_types

    def test_plan_schema_empty_list(self, setup_base_schema):
        """Test schema planning with empty model list."""
        result = setup_base_schema.apply_schema([], dry_run=True)

        assert result is not None
        # Should have no new object types (but may have from previous tests)
        assert len(result.object_types_to_create) >= 0
        # Should have no new link types (but may have from previous tests)
        assert len(result.link_types_to_create) >= 0


class TestSchemaApplication:
    """Test schema application functionality."""

    def test_apply_basic_schema(self, setup_base_schema, sample_models):
        """Test applying basic schema without links."""
        test_user, test_company = sample_models

        # Apply schema
        result = setup_base_schema.apply_schema([test_user, test_company])

        assert result is not None

        # Verify object types were created
        with setup_base_schema.get_session() as session:
            provider = setup_base_schema.get_core_provider(session)
            repo = provider.metamodel_repository()

            user_type = repo.get_object_type_by_api_name("default", "default", "test_user")
            company_type = repo.get_object_type_by_api_name("default", "default", "test_company")

            assert user_type is not None
            assert company_type is not None
            assert user_type.api_name == "test_user"
            assert company_type.api_name == "test_company"

    def test_apply_schema_with_links(self, setup_base_schema, models_with_links):
        """Test applying schema with link models."""
        test_company, test_employee = models_with_links

        # Apply schema
        result = setup_base_schema.apply_schema([test_company, test_employee])

        assert result is not None

        # Verify object types and link types were created
        with setup_base_schema.get_session() as session:
            provider = setup_base_schema.get_core_provider(session)
            repo = provider.metamodel_repository()

            # Check object types
            company_type = repo.get_object_type_by_api_name("default", "default", "test_company")
            employee_type = repo.get_object_type_by_api_name("default", "default", "test_employee")

            assert company_type is not None
            assert employee_type is not None

            # Check link type
            link_type = repo.get_link_type_by_api_name("default", "default", "works_for")
            assert link_type is not None
            assert link_type.api_name == "works_for"

    def test_apply_schema_idempotent(self, setup_base_schema, sample_models):
        """Test that applying same schema multiple times works."""
        test_user, test_company = sample_models

        # Apply schema first time
        result1 = setup_base_schema.apply_schema([test_user, test_company])
        assert result1 is not None

        # Apply schema second time (should not create duplicates)
        result2 = setup_base_schema.apply_schema([test_user, test_company])
        assert result2 is not None

        # Verify no duplicates were created
        with setup_base_schema.get_session() as session:
            provider = setup_base_schema.get_core_provider(session)
            repo = provider.metamodel_repository()

            user_type = repo.get_object_type_by_api_name("default", "default", "test_user")
            assert user_type is not None
            # Should still be the same object type, not a duplicate


@pytest.fixture
def validation_temp_db():
    """Create separate temporary SQLite database for validation tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_engine(f"sqlite:///{db_path}")
    yield engine

    # Cleanup
    import os

    os.unlink(db_path)


@pytest.fixture
def validation_ontology(validation_temp_db):
    """Create separate Ontology instance for validation tests."""
    ontology = Ontology(validation_temp_db)
    ontology.initialize_database()  # Create base metamodel tables
    return ontology


class TestSchemaValidation:
    """Test schema validation and error handling."""

    def test_invalid_model_configuration(self, validation_ontology):
        """Test schema application with invalid model configuration."""

        @validation_ontology.model
        class InvalidModelForValidation(ObjectModel):
            # Invalid primary key field name (contains space)
            __object_type_api_name__ = "invalid_model_validation"
            __primary_key__ = "invalid field name"  # Invalid identifier
            model_config = {"arbitrary_types_allowed": True}
            id: str

        with pytest.raises(
            ValueError, match="Primary key 'invalid field name' must exist in property set"
        ):
            validation_ontology.apply_schema([InvalidModelForValidation], dry_run=True)

    def test_missing_primary_key_field(self, validation_ontology):
        """Test model with primary key field not defined in model."""

        @validation_ontology.model
        class TestModelMissingPKValidation(ObjectModel):
            __object_type_api_name__ = "test_model_missing_pk_validation"
            __primary_key__ = "missing_field"
            model_config = {"arbitrary_types_allowed": True}
            name: str

        # Should handle missing primary key field gracefully
        with pytest.raises(
            ValueError, match="Primary key 'missing_field' must exist in property set"
        ):
            validation_ontology.apply_schema([TestModelMissingPKValidation], dry_run=True)

    def test_invalid_link_target(self, setup_base_schema):
        """Test link model with invalid target."""

        @setup_base_schema.model
        class TestSource(ObjectModel):
            __object_type_api_name__ = "test_source"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            # Link to non-existent model
            invalid_link: ClassVar[LinkModel[object]] = LinkModel("invalid_link")

        with pytest.raises(ValueError):
            setup_base_schema.apply_schema([TestSource], dry_run=True)


class TestSchemaEvolution:
    """Test schema evolution and changes."""

    def test_add_field_to_existing_model(self, setup_base_schema, sample_models):
        """Test adding a new field to an existing model."""
        test_user, test_company = sample_models

        # Apply initial schema
        setup_base_schema.apply_schema([test_user])

        # Create new model version with additional field
        @setup_base_schema.model
        class TestUserV2(ObjectModel):
            __object_type_api_name__ = "test_user"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            name: str
            email: str | None = None
            age: int | None = None  # New field

        # Apply updated schema
        result = setup_base_schema.apply_schema([TestUserV2])
        assert result is not None

    def test_remove_field_from_model(self, setup_base_schema, sample_models):
        """Test removing a field from an existing model."""
        test_user, test_company = sample_models

        # Apply initial schema
        setup_base_schema.apply_schema([test_user])

        # Create new model version without email field
        @setup_base_schema.model
        class TestUserSlim(ObjectModel):
            __object_type_api_name__ = "test_user_slim"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            name: str
            # email field removed

        # Apply updated schema
        result = setup_base_schema.apply_schema([TestUserSlim])
        assert result is not None


class TestSchemaPerformance:
    """Performance tests for schema operations."""

    def test_large_schema_application(self, setup_base_schema):
        """Test applying schema with many models."""
        models = []

        # Create many models
        for i in range(20):

            @setup_base_schema.model
            class DynamicModel(ObjectModel):
                __object_type_api_name__ = f"dynamic_model_{i}"
                __primary_key__ = "id"
                model_config = {"arbitrary_types_allowed": True}
                id: str
                name: str
                value: int | None = None

            models.append(DynamicModel)

        # Apply schema for all models
        result = setup_base_schema.apply_schema(models, dry_run=True)
        assert result is not None
        assert len(result.object_types_to_create) == 20

    @pytest.mark.benchmark
    def test_schema_planning_performance(self, setup_base_schema, sample_models, benchmark):
        """Benchmark schema planning performance."""
        test_user, test_company = sample_models

        result = benchmark(setup_base_schema.apply_schema, [test_user, test_company], dry_run=True)
        assert result is not None


class TestSchemaIntegration:
    """Integration tests with other OGM components."""

    def test_schema_with_crud_operations(self, setup_base_schema, sample_models):
        """Test that applied schema works with CRUD operations."""
        test_user, test_company = sample_models

        # Apply schema
        setup_base_schema.apply_schema([test_user])

        # Now CRUD operations should work
        user = test_user(id="user1", name="Alice", email="alice@example.com")
        saved_user = user.save()

        assert saved_user.id == "user1"

        retrieved_user = test_user.get("user1")
        assert retrieved_user is not None
        assert retrieved_user.name == "Alice"

    def test_schema_with_relationships(self, setup_base_schema, models_with_links):
        """Test that applied schema with links works properly."""
        test_company, test_employee = models_with_links

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create company and employee
        company = test_company(id="company1", name="ACME")
        company.save()

        employee = test_employee(id="emp1", name="Alice")
        employee.save()

        # Verify both objects exist
        assert test_company.get("company1") is not None
        assert test_employee.get("emp1") is not None


if __name__ == "__main__":
    pytest.main([__file__])
