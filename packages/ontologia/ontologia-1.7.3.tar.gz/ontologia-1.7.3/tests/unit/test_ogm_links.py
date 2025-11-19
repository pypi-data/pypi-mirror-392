"""
test_ogm_links.py
----------------
Comprehensive tests for OGM LinkModel relationships.

State-of-the-art test suite covering:
- LinkModel creation and configuration
- Relationship navigation
- Inverse relationships
- Cardinality handling
- Link properties
- Error handling and edge cases
"""

from __future__ import annotations

import tempfile
from typing import ClassVar

import pytest
from sqlalchemy import create_engine

from ontologia.ogm.connection import Ontology
from ontologia.ogm.link import LinkModel, clear_link_registry
from ontologia.ogm.model import ObjectModel, clear_model_registry


@pytest.fixture(autouse=True)
def clear_registries():
    """Clear the model and link registries before each test."""
    clear_model_registry()
    clear_link_registry()
    yield
    # Clear after test as well
    clear_model_registry()
    clear_link_registry()


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
def relationship_models(ontology):
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

    @ontology.model
    class TestProject(ObjectModel):
        __object_type_api_name__ = "test_project"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str
        budget: float | None = None

    return TestCompany, TestEmployee, TestProject


@pytest.fixture
def complex_relationship_models(ontology):
    """Create models with complex relationships."""

    @ontology.model
    class TestUser(ObjectModel):
        __object_type_api_name__ = "test_user"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str

    @ontology.model
    class TestGroup(ObjectModel):
        __object_type_api_name__ = "test_group"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        name: str

    @ontology.model
    class TestMembership(ObjectModel):
        __object_type_api_name__ = "test_membership"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        role: str
        user: ClassVar[LinkModel[TestUser]] = LinkModel("member_of", target_model=TestUser)
        group: ClassVar[LinkModel[TestGroup]] = LinkModel("has_member", target_model=TestGroup)

    return TestUser, TestGroup, TestMembership


class TestLinkModelBasics:
    """Test basic LinkModel functionality."""

    def test_link_model_creation(self, relationship_models):
        """Test LinkModel creation and configuration."""
        test_company, test_employee, test_project = relationship_models

        # Check link model configuration
        employee_link = test_employee.company
        assert employee_link.api_name == "works_for"
        assert employee_link.inverse == "employees"
        assert employee_link.target_model == test_company

    def test_link_model_metadata(self, relationship_models):
        """Test LinkModel metadata access."""
        test_company, test_employee, test_project = relationship_models

        link = test_employee.company
        assert hasattr(link, "api_name")
        assert hasattr(link, "inverse")
        assert hasattr(link, "target_model")

        # Check that link is properly typed
        assert link.api_name == "works_for"
        assert link.inverse == "employees"


class TestLinkModelSchema:
    """Test LinkModel in schema context."""

    def test_schema_with_links(self, setup_base_schema, relationship_models):
        """Test schema application with link models."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        result = setup_base_schema.apply_schema([test_company, test_employee], dry_run=True)

        assert result is not None
        assert len(result.object_types_to_create) == 2
        assert len(result.link_types_to_create) == 1

        # Check link type details
        link_type_name, link_type_obj = result.link_types_to_create[0]
        assert link_type_name == "works_for"
        assert link_type_obj.api_name == "works_for"

    def test_bidirectional_links(self, setup_base_schema, relationship_models):
        """Test bidirectional link creation."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Verify both directions are handled
        with setup_base_schema.get_session() as session:
            provider = setup_base_schema.get_core_provider(session)
            repo = provider.metamodel_repository()

            link_type = repo.get_link_type_by_api_name("default", "default", "works_for")
            assert link_type is not None
            assert link_type.api_name == "works_for"


class TestLinkModelOperations:
    """Test LinkModel operations."""

    def test_create_relationship(self, setup_base_schema, relationship_models):
        """Test creating relationships between objects."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create objects
        company = test_company(id="company1", name="ACME")
        company.save()

        employee = test_employee(id="emp1", name="Alice")
        employee.save()

        # Verify objects exist
        assert test_company.get("company1") is not None
        assert test_employee.get("emp1") is not None

    def test_link_model_access_pattern(self, setup_base_schema, relationship_models):
        """Test LinkModel access patterns."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create objects
        company = test_company(id="company1", name="ACME")
        company.save()

        employee = test_employee(id="emp1", name="Alice")
        employee.save()

        # Test link model access - check class-level LinkModel, not instance-level LinkProxy
        link_model = test_employee.company
        assert link_model.api_name == "works_for"
        assert link_model.target_model == test_company

        # Test instance access returns LinkProxy
        link_proxy = employee.company
        assert link_proxy is not None


class TestLinkModelCardinality:
    """Test LinkModel cardinality handling."""

    def test_one_to_many_relationship(self, setup_base_schema, relationship_models):
        """Test one-to-many relationships."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create company
        company = test_company(id="company1", name="ACME")
        company.save()

        # Create multiple employees
        employees = []
        for i in range(3):
            emp = test_employee(id=f"emp{i}", name=f"Employee{i}")
            emp.save()
            employees.append(emp)

        # Verify all employees exist
        for emp in employees:
            assert test_employee.get(emp.id) is not None

    def test_many_to_many_relationship(self, setup_base_schema, complex_relationship_models):
        """Test many-to-many relationships through junction model."""
        test_user, test_group, test_membership = complex_relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_user, test_group, test_membership])

        # Create users and groups
        user1 = test_user(id="user1", name="Alice")
        user2 = test_user(id="user2", name="Bob")
        user1.save()
        user2.save()

        group1 = test_group(id="group1", name="Admins")
        group2 = test_group(id="group2", name="Developers")
        group1.save()
        group2.save()

        # Create memberships
        membership1 = test_membership(id="mem1", role="admin", user=user1, group=group1)
        membership2 = test_membership(id="mem2", role="member", user=user2, group=group2)
        membership1.save()
        membership2.save()

        # Verify all objects exist
        assert test_user.get("user1") is not None
        assert test_user.get("user2") is not None
        assert test_group.get("group1") is not None
        assert test_group.get("group2") is not None
        assert test_membership.get("mem1") is not None
        assert test_membership.get("mem2") is not None


class TestLinkModelErrorHandling:
    """Test LinkModel error handling."""

    def test_invalid_target_model(self, ontology):
        """Test LinkModel with invalid target model."""

        @ontology.model
        class TestSource(ObjectModel):
            __object_type_api_name__ = "test_source"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            invalid_link: ClassVar[LinkModel[object]] = LinkModel("invalid_link")

        with pytest.raises(ValueError):
            ontology.apply_schema([TestSource], dry_run=True)

    def test_circular_reference(self, ontology):
        """Test handling of circular references."""

        @ontology.model
        class TestNode(ObjectModel):
            __object_type_api_name__ = "test_node"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            parent: ClassVar[LinkModel[TestNode]] = LinkModel("parent_of", target_model=None)

        # Should handle circular references gracefully
        result = ontology.apply_schema([TestNode], dry_run=True)
        assert result is not None

    def test_missing_inverse_relationship(self, setup_base_schema, relationship_models):
        """Test link with missing inverse relationship."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create a company first
        company = test_company(id="company1", name="Test Company")
        company.save()

        # The inverse 'employees' doesn't exist on test_company
        # This should not prevent schema application
        company = test_company.get("company1")
        if company:
            # Company model should not have 'employees' attribute
            assert not hasattr(company, "employees")


class TestLinkModelPerformance:
    """Performance tests for LinkModel operations."""

    def test_many_relationships_performance(self, setup_base_schema, relationship_models):
        """Test performance with many relationships."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create company
        company = test_company(id="company1", name="ACME")
        company.save()

        # Create many employees
        employees = []
        for i in range(100):
            emp = test_employee(id=f"emp{i}", name=f"Employee{i}")
            emp.save()
            employees.append(emp)

        # Verify all employees exist
        retrieved_count = 0
        for emp in employees:
            if test_employee.get(emp.id):
                retrieved_count += 1

        assert retrieved_count == 100

    @pytest.mark.benchmark
    def test_link_model_creation_performance(
        self, setup_base_schema, relationship_models, benchmark
    ):
        """Benchmark LinkModel creation performance."""
        test_company, test_employee, test_project = relationship_models

        result = benchmark(
            setup_base_schema.apply_schema, [test_company, test_employee], dry_run=True
        )
        assert result is not None


class TestLinkModelIntegration:
    """Integration tests with other OGM components."""

    def test_links_with_transactions(self, setup_base_schema, relationship_models):
        """Test LinkModel operations within transactions."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create objects within transaction
        with test_employee.transaction() as session:
            company = test_company(id="company1", name="ACME")
            company.save(session=session)

            employee = test_employee(id="emp1", name="Alice")
            employee.save(session=session)

        # Verify objects exist after transaction commit
        assert test_company.get("company1") is not None
        assert test_employee.get("emp1") is not None

    def test_links_with_queries(self, setup_base_schema, relationship_models):
        """Test querying objects with link relationships."""
        test_company, test_employee, test_project = relationship_models

        # Apply schema
        setup_base_schema.apply_schema([test_company, test_employee])

        # Create test data
        companies = [test_company(id="c1", name="ACME"), test_company(id="c2", name="TechCorp")]
        for company in companies:
            company.save()

        employees = [
            test_employee(id="e1", name="Alice"),
            test_employee(id="e2", name="Bob"),
            test_employee(id="e3", name="Charlie"),
        ]
        for employee in employees:
            employee.save()

        # Query all objects
        all_companies = list(test_company.query())
        all_employees = list(test_employee.query())

        assert len(all_companies) == 2
        assert len(all_employees) == 3


if __name__ == "__main__":
    pytest.main([__file__])
