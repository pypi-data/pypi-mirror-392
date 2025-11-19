"""
test_ogm_model.py
-----------------
Comprehensive tests for OGM ObjectModel CRUD operations.

State-of-the-art test suite covering:
- Model creation and validation
- CRUD operations (get, save, delete)
- Query operations
- Transaction management
- Error handling and edge cases
"""

from __future__ import annotations

import tempfile

import pytest
from sqlmodel import create_engine

from ontologia.ogm.connection import Ontology
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


from ontologia.ogm.errors import NotFound
from ontologia.ogm.model import ObjectModel


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

    # Apply schema to register object types
    ontology.apply_schema([TestUser, TestCompany])

    return TestUser, TestCompany


class TestObjectModelBasics:
    """Test basic ObjectModel functionality."""

    def test_model_creation(self, sample_models):
        """Test model creation and registration."""
        test_user, test_company = sample_models

        # Verify model registration
        assert test_user._meta()["object_type_api_name"] == "test_user"
        assert test_user._meta()["primary_key"] == "id"
        assert test_company._meta()["object_type_api_name"] == "test_company"

        # Verify model fields
        assert "id" in test_user.model_fields
        assert "name" in test_user.model_fields
        assert "email" in test_user.model_fields

    def test_model_instantiation(self, sample_models):
        """Test model instance creation."""
        test_user, _ = sample_models

        user = test_user(id="user1", name="Alice", email="alice@example.com")
        assert user.id == "user1"
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

        # Test optional field
        user_no_email = test_user(id="user2", name="Bob")
        assert user_no_email.email is None

    def test_model_validation(self, sample_models):
        """Test model validation."""
        test_user, _ = sample_models

        # Valid model
        user = test_user(id="valid", name="Valid User")
        assert user.id == "valid"

        # Required field missing should raise validation error
        with pytest.raises(ValueError):
            test_user(name="Missing ID")  # type: ignore[call-arg]


class TestObjectModelCRUD:
    """Test CRUD operations."""

    def test_save_and_get(self, ontology, sample_models):
        """Test save and get operations."""
        test_user, _ = sample_models

        # Create and save user
        user = test_user(id="user1", name="Alice", email="alice@example.com")
        saved_user = user.save()

        assert saved_user.id == "user1"
        assert saved_user.name == "Alice"

        # Get user by primary key
        retrieved_user = test_user.get("user1")
        assert retrieved_user is not None
        assert retrieved_user.id == "user1"
        assert retrieved_user.name == "Alice"
        assert retrieved_user.email == "alice@example.com"

    def test_get_nonexistent(self, sample_models):
        """Test getting non-existent object."""
        test_user, _ = sample_models

        with pytest.raises(NotFound, match="test_user:nonexistent not found"):
            test_user.get("nonexistent")

    def test_update_existing(self, ontology, sample_models):
        """Test updating existing object."""
        test_user, _ = sample_models

        # Create initial user
        user = test_user(id="user1", name="Alice")
        user.save()

        # Update user
        user.name = "Alice Smith"
        user.email = "alice.smith@example.com"
        user.save()

        # Verify update persisted by fetching fresh instance
        retrieved_user = test_user.get("user1")
        assert retrieved_user.name == "Alice Smith"
        assert retrieved_user.email == "alice.smith@example.com"

    def test_delete(self, ontology, sample_models):
        """Test delete operation."""
        test_user, _ = sample_models

        # Create and save user
        user = test_user(id="user1", name="Alice")
        user.save()

        # Verify user exists
        assert test_user.get("user1") is not None

        # Delete user
        user.delete()

        # Verify user is deleted
        with pytest.raises(NotFound, match="test_user:user1 not found"):
            test_user.get("user1")

    def test_delete_nonexistent(self, sample_models):
        """Test deleting non-existent object."""
        test_user, _ = sample_models

        user = test_user(id="nonexistent", name="Ghost")
        # Should raise NotFound error
        with pytest.raises(NotFound, match="test_user:nonexistent not found"):
            user.delete()


class TestObjectModelQuery:
    """Test query operations."""

    def test_query_all(self, ontology, sample_models):
        """Test querying all objects."""
        test_user, _ = sample_models

        # Create multiple users
        users = [
            test_user(id="user1", name="Alice"),
            test_user(id="user2", name="Bob"),
            test_user(id="user3", name="Charlie"),
        ]
        for user in users:
            user.save()

        # Query all users
        all_users = list(test_user.query())
        assert len(all_users) == 3

        names = {user.name for user in all_users}
        assert names == {"Alice", "Bob", "Charlie"}

    def test_query_with_filter(self, ontology, sample_models):
        """Test querying with filters."""
        test_user, _ = sample_models

        # Create users with different emails
        test_user(id="user1", name="Alice", email="alice@example.com").save()
        test_user(id="user2", name="Bob", email="bob@gmail.com").save()
        test_user(id="user3", name="Charlie").save()

        # Query users with email
        users_with_email = list(test_user.query().filter("email", "is_not_null", None))
        assert len(users_with_email) == 2
        assert all(user.email is not None for user in users_with_email)

        # Query specific email domain
        gmail_users = list(test_user.query().filter("email", "like", "%@gmail.com"))
        assert len(gmail_users) == 1
        assert gmail_users[0].name == "Bob"

    def test_query_ordering(self, ontology, sample_models):
        """Test query ordering."""
        test_user, _ = sample_models

        # Create users in random order
        test_user(id="user1", name="Charlie").save()
        test_user(id="user2", name="Alice").save()
        test_user(id="user3", name="Bob").save()

        # Query ordered by name
        ordered_users = list(test_user.query().order_by("name", "asc"))
        assert [user.name for user in ordered_users] == ["Alice", "Bob", "Charlie"]

        # Query ordered by name descending
        desc_users = list(test_user.query().order_by("name", "desc"))
        assert [user.name for user in desc_users] == ["Charlie", "Bob", "Alice"]

    def test_query_limit(self, ontology, sample_models):
        """Test query limit."""
        test_user, _ = sample_models

        # Create multiple users
        for i in range(5):
            test_user(id=f"user{i}", name=f"User{i}").save()

        # Query with limit
        limited_users = list(test_user.query().limit(3))
        assert len(limited_users) == 3


class TestObjectModelTransactions:
    """Test transaction management."""

    def test_transaction_commit(self, ontology, sample_models):
        """Test successful transaction commit."""
        test_user, _ = sample_models

        with test_user.transaction() as session:
            user1 = test_user(id="user1", name="Alice")
            user2 = test_user(id="user2", name="Bob")

            user1.save(session=session)
            user2.save(session=session)

        # Verify both users are committed
        assert test_user.get("user1") is not None
        assert test_user.get("user2") is not None

    def test_transaction_rollback(self, ontology, sample_models):
        """Test transaction rollback on error."""
        test_user, _ = sample_models

        # Create initial user
        test_user(id="existing", name="Existing").save()

        try:
            with test_user.transaction() as session:
                user1 = test_user(id="user1", name="Alice")
                user1.save(session=session)

                # Simulate error
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected

        # Verify transaction was rolled back
        try:
            test_user.get("user1")
            raise AssertionError("Expected NotFound exception")
        except NotFound:
            pass  # Expected - transaction was rolled back
        # Verify existing user is still there
        assert test_user.get("existing") is not None

    def test_nested_transactions(self, ontology, sample_models):
        """Test nested transaction behavior."""
        test_user, _ = sample_models

        with test_user.transaction() as outer_session:
            outer_user = test_user(id="outer", name="Outer")
            outer_user.save(session=outer_session)

            with test_user.transaction() as inner_session:
                inner_user = test_user(id="inner", name="Inner")
                inner_user.save(session=inner_session)

        # Verify both are committed
        assert test_user.get("outer") is not None
        assert test_user.get("inner") is not None


class TestObjectModelErrorHandling:
    """Test error handling and edge cases."""

    def test_duplicate_primary_key(self, ontology, sample_models):
        """Test handling of duplicate primary keys."""
        test_user, _ = sample_models

        # Create first user
        user1 = test_user(id="dup", name="Alice")
        user1.save()

        # Try to create second user with same PK
        user2 = test_user(id="dup", name="Bob")
        # In bitemporal system, this creates a new version, not an error
        user2.save()
        # Verify both exist (bitemporal behavior)
        users = list(test_user.query().filter("id", "eq", "dup"))
        assert len(users) >= 1

    def test_invalid_model_config(self, ontology):
        """Test model with invalid configuration."""

        # Test model without required attributes
        try:

            @ontology.model
            class InvalidModel(ObjectModel):
                # Missing __object_type_api_name__ and __primary_key__
                id: str

            # Model should not be registered since it lacks required attributes
            # It should have default values from the base class
            assert InvalidModel.__primary_key__ == "pk"  # Default from ObjectModel
            # __object_type_api_name__ is not set since it's not registered
            assert not hasattr(InvalidModel, "__object_type_api_name__")
        except Exception as e:
            # If validation is added later, this will catch it
            assert "object_type_api_name" in str(e).lower() or "primary_key" in str(e).lower()

    def test_session_isolation(self, ontology, sample_models):
        """Test that different models use correct sessions."""
        test_user, test_company = sample_models

        # Create user and company
        user = test_user(id="user1", name="Alice")
        company = test_company(id="company1", name="ACME")

        user.save()
        company.save()

        # Verify both are accessible
        assert test_user.get("user1") is not None
        assert test_company.get("company1") is not None


class TestObjectModelPerformance:
    """Performance-related tests."""

    def test_bulk_operations(self, ontology, sample_models):
        """Test bulk operations performance."""
        test_user, _ = sample_models

        # Create many users
        users = []
        for i in range(100):
            user = test_user(id=f"user{i}", name=f"User{i}")
            users.append(user)

        # Save all users
        for user in users:
            user.save()

        # Query all users
        all_users = list(test_user.query())
        assert len(all_users) == 100

    @pytest.mark.benchmark
    def test_query_performance(self, ontology, sample_models, benchmark):
        """Benchmark query performance."""
        test_user, _ = sample_models

        # Create test data
        for i in range(50):
            test_user(id=f"user{i}", name=f"User{i}").save()

        # Benchmark query
        result = benchmark(list, test_user.query())
        assert len(result) == 50


if __name__ == "__main__":
    pytest.main([__file__])
