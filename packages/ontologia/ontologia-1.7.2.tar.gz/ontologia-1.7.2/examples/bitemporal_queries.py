"""
Demonstration of bitemporal queries in the Ontologia system.

This example shows how to use the new bitemporal capabilities for:
1. Point-in-time queries using valid_at()
2. Temporal range queries using temporal_range()
3. Historical analysis of object and link evolution
"""

from datetime import datetime

from ontologia.ogm import ObjectModel


# Define an OGM model for demonstration
class Person(ObjectModel):
    __primary_key__ = "id"
    __object_type_api_name__ = "person"

    # Standard fields
    id: str
    name: str
    email: str

    # Temporal fields (can be managed by the system or explicitly set)
    # valid_from, valid_to, transaction_from, transaction_to are automatic


class Employee(ObjectModel):
    __primary_key__ = "employee_id"
    __object_type_api_name__ = "employee"

    employee_id: str
    department: str
    salary: float


# === 1. Basic Point-in-Time Queries ===
def query_person_as_of(timestamp):
    """Query people as they existed at a specific point in time."""
    # Using fluent API
    people_at_time = (
        Person.query()
        .valid_at(timestamp)  # or timestamp.isoformat()
        .filter("department", "eq", "Engineering")
        .order_by("name")
        .all()
    )
    return people_at_time


# Alternative syntax
def query_alternative_syntax():
    """Show alternative syntax for temporal queries."""
    timestamp = datetime(2023, 6, 15)

    # Using as_of() alias
    engineers = Person.query().as_of(timestamp).filter("role", "eq", "engineer").all()

    # Using raw ISO string
    managers = Person.query().valid_at("2023-06-15T10:30:00").filter("role", "eq", "manager").all()

    return engineers, managers


# === 2. Complex Temporal Range Queries ===
def query_historical_changes():
    """Query for objects within specific temporal ranges."""
    # Find all people who were valid during Q1 2023
    q1_2023_start = datetime(2023, 1, 1)
    q1_2023_end = datetime(2023, 3, 31)

    people_in_q1 = (
        Person.query().temporal_range(valid_from=q1_2023_start, valid_to=q1_2023_end).all()
    )

    # Find all changes made in the system during January 2023
    jan_2023_start = datetime(2023, 1, 1)
    jan_2023_end = datetime(2023, 1, 31)

    changes_in_jan = (
        Employee.query()
        .temporal_range(transaction_from=jan_2023_start, transaction_to=jan_2023_end)
        .all()
    )

    # Full bitemporal query: What was the state on Jan 15 according to what we knew in March?
    historical_state_on_jan_15 = (
        Person.query()
        .temporal_range(
            valid_from=datetime(2023, 1, 15),  # Valid on this day
            valid_to=datetime(2023, 1, 15),
            transaction_from=datetime(2023, 3, 1),  # Known as of March
            transaction_to=datetime(2023, 3, 31),
        )
        .all()
    )

    return people_in_q1, changes_in_jan, historical_state_on_jan_15


# === 3. Advanced Use Cases ===
def audit_salary_changes():
    """Audit salary changes over time with full temporal context."""
    # Find all salary revisions for a specific employee
    original_query = Employee.query().filter("employee_id", "eq", "emp123")

    # Get the complete temporal history
    full_history = (
        original_query.temporal_range(
            transaction_from=datetime(2022, 1, 1), transaction_to=datetime(2023, 12, 31)
        )
        .order_by("transaction_from")
        .all()
    )

    # Analyze salary progression
    progression = []
    for record in full_history:
        progression.append(
            {
                "salary": record.salary,
                "valid_from": record.valid_from,
                "transaction_from": record.transaction_from,
                "known_since": record.transaction_from,
            }
        )

    return progression


def temporal_reporting():
    """Generate temporal reports showing evolution."""

    # Report 1: Department headcount over time
    def department_headcount_at_time(timestamp):
        """Get department headcount at specific timestamp."""
        return Person.query().valid_at(timestamp).filter("status", "eq", "active").all()

    # Report 2: Reorganizations - track department changes
    def track_department_changes():
        """Find when departments changed."""
        changes = (
            Employee.query()
            .temporal_range(valid_from=datetime(2023, 1, 1), valid_to=datetime(2023, 12, 31))
            .order_by("department", "valid_from")
            .all()
        )
        return changes

    # Report 3: Data quality - when was information known?
    def information_latency_report():
        """Track how long it took for information to enter the system."""
        # Find all records where transaction time is significantly later than valid time
        delayed_records = (
            Employee.query()
            .filter(
                "transaction_from", "gt", "valid_from"
            )  # Transaction happened after valid period
            .temporal_range(valid_from=datetime(2023, 1, 1))
            .all()
        )

        delays = []
        for record in delayed_records:
            delay_days = (record.transaction_from - record.valid_from).days
            if delay_days > 0:
                delays.append(
                    {
                        "employee_id": record.employee_id,
                        "delay_days": delay_days,
                        "valid_from": record.valid_from,
                        "known_since": record.transaction_from,
                    }
                )

        return delays


# === Usage Examples ===
if __name__ == "__main__":
    # Example 1: Query current engineering team
    current_engineers = query_person_as_of(datetime.now())
    print(f"Current engineers: {len(current_engineers)}")

    # Example 2: Compare team sizes over time
    jan_2023_team = query_person_as_of(datetime(2023, 1, 15))
    dec_2023_team = query_person_as_of(datetime(2023, 12, 15))
    growth = len(dec_2023_team) - len(jan_2023_team)
    print(f"Team grew by {growth} people from Jan to Dec 2023")

    # Example 3: Generate audit report
    salary_progression = audit_salary_changes()
    print("Salary progression for emp123:")
    for entry in salary_progression:
        print(
            f"  ${entry['salary']:,.0f} - valid from {entry['valid_from']} (known {entry['known_since']})"
        )

    # Example 4: Check data quality
    delays = information_latency_report()
    if delays:
        print(f"Found {len(delays)} delayed information entries")
    else:
        print("All information appears to be captured promptly")
