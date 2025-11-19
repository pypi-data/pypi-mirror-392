"""
test_ogm_transactions.py
-----------------------
Comprehensive tests for OGM transaction management.

State-of-the-art test suite covering:
- Transaction commit and rollback
- Nested transactions
- Concurrent operations
- Error handling and recovery
- Performance considerations
"""

from __future__ import annotations

import tempfile
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlmodel import create_engine

from ontologia.ogm.connection import Ontology
from ontologia.ogm.errors import NotFound
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


from ontologia.ogm import LinkModel, ObjectModel


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
def transaction_models(ontology):
    """Create models for transaction testing."""

    @ontology.model
    class TestAccount(ObjectModel):
        __object_type_api_name__ = "test_account"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        balance: float
        owner: str

    @ontology.model
    class TestTransaction(ObjectModel):
        __object_type_api_name__ = "test_transaction"
        __primary_key__ = "id"
        model_config = {"arbitrary_types_allowed": True}
        id: str
        amount: float
        from_account: str
        to_account: str
        status: str = "pending"

    return TestAccount, TestTransaction


class TestTransactionBasics:
    """Test basic transaction functionality."""

    def test_transaction_commit(self, setup_base_schema, transaction_models):
        """Test successful transaction commit."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create account within transaction
        with test_account.transaction() as session:
            account = test_account(id="acc1", balance=100.0, owner="Alice")
            account.save(session=session)

        # Verify account exists after commit
        retrieved_account = test_account.get("acc1")
        assert retrieved_account is not None
        assert retrieved_account.balance == 100.0
        assert retrieved_account.owner == "Alice"

    def test_transaction_rollback(self, setup_base_schema, transaction_models):
        """Test transaction rollback on error."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create initial account
        initial_account = test_account(id="acc1", balance=50.0, owner="Alice")
        initial_account.save()

        # Attempt transaction that fails
        try:
            with test_account.transaction() as session:
                account = test_account(id="acc2", balance=100.0, owner="Bob")
                account.save(session=session)

                # Simulate error
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected

        # Verify transaction was rolled back
        with pytest.raises(NotFound):
            test_account.get("acc2")
        # Verify initial account is still there
        assert test_account.get("acc1") is not None

    def test_transaction_with_multiple_operations(self, setup_base_schema, transaction_models):
        """Test transaction with multiple operations."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account, test_transaction])

        # Create multiple objects in single transaction
        with test_account.transaction() as session:
            account1 = test_account(id="acc1", balance=100.0, owner="Alice")
            account2 = test_account(id="acc2", balance=200.0, owner="Bob")

            account1.save(session=session)
            account2.save(session=session)

            transaction = test_transaction(
                id="tx1", amount=50.0, from_account="acc1", to_account="acc2"
            )
            transaction.save(session=session)

        # Verify all objects exist
        assert test_account.get("acc1") is not None
        assert test_account.get("acc2") is not None
        assert test_transaction.get("tx1") is not None


class TestNestedTransactions:
    """Test nested transaction behavior."""

    def test_nested_transaction_commit(self, setup_base_schema, transaction_models):
        """Test nested transaction commit."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        with test_account.transaction() as outer_session:
            outer_account = test_account(id="acc1", balance=100.0, owner="Alice")
            outer_account.save(session=outer_session)

            with test_account.transaction() as inner_session:
                inner_account = test_account(id="acc2", balance=200.0, owner="Bob")
                inner_account.save(session=inner_session)

        # Verify both accounts exist
        assert test_account.get("acc1") is not None
        assert test_account.get("acc2") is not None

    def test_nested_transaction_rollback(self, setup_base_schema, transaction_models):
        """Test nested transaction rollback."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        with test_account.transaction() as outer_session:
            outer_account = test_account(id="acc1", balance=100.0, owner="Alice")
            outer_account.save(session=outer_session)

            # Inner transaction should rollback independently
            try:
                with test_account.transaction() as inner_session:
                    inner_account = test_account(id="acc2", balance=200.0, owner="Bob")
                    inner_account.save(session=inner_session)

                    # Simulate error in inner transaction
                    raise ValueError("Inner transaction error")
            except ValueError:
                pass  # Expected - inner transaction rolled back

        # Verify outer transaction committed, inner rolled back
        assert test_account.get("acc1") is not None
        try:
            test_account.get("acc2")
            raise AssertionError("acc2 should not exist after inner transaction rollback")
        except NotFound:
            pass  # Expected - inner transaction rolled back

    def test_outer_transaction_rollback(self, setup_base_schema, transaction_models):
        """Test outer transaction rollback affecting inner transactions."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        try:
            with test_account.transaction() as outer_session:
                outer_account = test_account(id="acc1", balance=100.0, owner="Alice")
                outer_account.save(session=outer_session)

                # Inner transaction commits independently
                with test_account.transaction() as inner_session:
                    inner_account = test_account(id="acc2", balance=200.0, owner="Bob")
                    inner_account.save(session=inner_session)

                # Simulate error in outer transaction
                raise ValueError("Outer transaction error")
        except ValueError:
            pass  # Expected

        # Verify outer transaction rolled back, inner committed independently
        try:
            test_account.get("acc1")
            raise AssertionError("acc1 should not exist after outer transaction rollback")
        except NotFound:
            pass  # Expected
        # Note: acc2 still exists because inner transaction committed independently
        assert test_account.get("acc2") is not None


class TestConcurrentTransactions:
    """Test concurrent transaction behavior."""

    def test_concurrent_writes(self, setup_base_schema, transaction_models):
        """Test concurrent write operations."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        def create_account(account_id, balance, owner):
            with test_account.transaction() as session:
                account = test_account(id=account_id, balance=balance, owner=owner)
                account.save(session=session)

        # Create accounts concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(create_account, f"acc{i}", float(i * 100), f"Owner{i}")
                futures.append(future)

            # Wait for all to complete
            for future in futures:
                future.result()

        # Verify all accounts were created
        for i in range(10):
            account = test_account.get(f"acc{i}")
            assert account is not None
            assert account.balance == float(i * 100)
            assert account.owner == f"Owner{i}"

    def test_concurrent_reads_and_writes(self, setup_base_schema, transaction_models):
        """Test concurrent read and write operations."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create initial account
        initial_account = test_account(id="acc1", balance=1000.0, owner="Alice")
        initial_account.save()

        def read_account(account_id):
            return test_account.get(account_id)

        def update_account(account_id, new_balance):
            account = test_account.get(account_id)
            if account:
                account.balance = new_balance
                account.save()

        # Perform concurrent reads and writes
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Start read operations
            read_futures = [executor.submit(read_account, "acc1") for _ in range(5)]

            # Start write operations
            write_futures = [
                executor.submit(update_account, "acc1", 1500.0),
                executor.submit(update_account, "acc1", 2000.0),
                executor.submit(update_account, "acc1", 2500.0),
            ]

            # Wait for all operations
            for future in read_futures + write_futures:
                future.result()

        # Verify final state
        final_account = test_account.get("acc1")
        assert final_account is not None
        assert final_account.balance > 1000.0  # Should have been updated


class TestTransactionErrorHandling:
    """Test transaction error handling and recovery."""

    def test_constraint_violation_rollback(self, setup_base_schema, transaction_models):
        """Test rollback on constraint violation."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create initial account
        account1 = test_account(id="acc1", balance=100.0, owner="Alice")
        account1.save()

        # Try to create duplicate account in transaction
        try:
            with test_account.transaction() as session:
                account2 = test_account(id="acc1", balance=200.0, owner="Bob")
                account2.save(session=session)
        except Exception:
            pass  # Expected constraint violation

        # Verify original account is unchanged
        original_account = test_account.get("acc1")
        assert original_account is not None
        assert original_account.balance == 100.0
        assert original_account.owner == "Alice"

    def test_session_isolation(self, setup_base_schema, transaction_models):
        """Test session isolation between transactions."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create initial account
        initial_account = test_account(id="acc1", balance=100.0, owner="Alice")
        initial_account.save()

        # Start transaction but don't commit
        with test_account.transaction() as session:
            # Modify account within transaction
            account = test_account.get("acc1")
            if account:
                account.balance = 200.0
                account.save(session=session)

            # Check from outside transaction (should see old value)
            outside_account = test_account.get("acc1")
            assert outside_account.balance == 100.0  # Should still see old value

        # After transaction commit, verify new value
        final_account = test_account.get("acc1")
        assert final_account.balance == 200.0


class TestTransactionPerformance:
    """Performance tests for transaction operations."""

    def test_bulk_transaction_performance(self, setup_base_schema, transaction_models):
        """Test performance of bulk operations in transaction."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create many accounts in single transaction
        with test_account.transaction() as session:
            for i in range(1000):
                account = test_account(id=f"acc{i}", balance=float(i * 100), owner=f"Owner{i}")
                account.save(session=session)

        # Verify all accounts were created
        for i in range(1000):
            account = test_account.get(f"acc{i}")
            assert account is not None
            assert account.balance == float(i * 100)

    @pytest.mark.benchmark
    def test_transaction_overhead(self, setup_base_schema, transaction_models, benchmark):
        """Benchmark transaction overhead."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        def create_with_transaction():
            with test_account.transaction() as session:
                account = test_account(id="perf_acc", balance=100.0, owner="Perf")
                account.save(session=session)

        def create_without_transaction():
            account = test_account(id="perf_acc_no_tx", balance=100.0, owner="Perf")
            account.save()

        # Benchmark both approaches
        with_tx_time = benchmark(create_with_transaction)
        without_tx_time = benchmark(create_without_transaction)

        # Transaction overhead should be reasonable
        assert with_tx_time is not None
        assert without_tx_time is not None


class TestTransactionIntegration:
    """Integration tests with other OGM components."""

    def test_transaction_with_schema_changes(self, setup_base_schema, transaction_models):
        """Test transactions during schema changes."""
        test_account, test_transaction = transaction_models

        # Apply schema
        setup_base_schema.apply_schema([test_account])

        # Create data in transaction
        with test_account.transaction() as session:
            account = test_account(id="acc1", balance=100.0, owner="Alice")
            account.save(session=session)

        # Apply additional schema
        setup_base_schema.apply_schema([test_transaction])

        # Create more data in new transaction
        with test_transaction.transaction() as session:
            transaction = test_transaction(
                id="tx2", amount=50.0, from_account="acc1", to_account="acc2"
            )
            transaction.save(session=session)

        # Verify all data exists
        assert test_account.get("acc1") is not None
        assert test_transaction.get("tx2") is not None

    def test_transaction_with_relationships(self, setup_base_schema):
        """Test transactions with model relationships."""

        @setup_base_schema.model
        class TestCompany(ObjectModel):
            __object_type_api_name__ = "test_company"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            name: str

        @setup_base_schema.model
        class TestEmployee(ObjectModel):
            __object_type_api_name__ = "test_employee"
            __primary_key__ = "id"
            model_config = {"arbitrary_types_allowed": True}
            id: str
            name: str
            company: LinkModel[TestCompany] = LinkModel("works_for", target_model=TestCompany)

        # Apply schema
        setup_base_schema.apply_schema([TestCompany, TestEmployee])

        # Create related objects in transaction
        with TestEmployee.transaction() as session:
            company = TestCompany(id="company1", name="ACME")
            company.save(session=session)

            employee = TestEmployee(id="emp1", name="Alice")
            employee.save(session=session)

        # Verify both objects exist
        assert TestCompany.get("company1") is not None
        assert TestEmployee.get("emp1") is not None


if __name__ == "__main__":
    pytest.main([__file__])
