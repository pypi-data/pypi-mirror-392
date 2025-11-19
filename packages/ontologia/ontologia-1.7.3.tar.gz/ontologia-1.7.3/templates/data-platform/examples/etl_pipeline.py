#!/usr/bin/env python3
"""
ETL Pipeline Example

This example shows how to build a complete ETL pipeline using
Dagster for orchestration, DuckDB for analytics, and Ontologia for data.
"""

import os
from datetime import datetime
from typing import Any

import duckdb
import pandas as pd
from dagster import (
    job,
    op,
)
from ontologia_sdk.client import OntologyClient

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://{API_HOST}:{API_PORT}"
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "./data/analytics.duckdb")


@op
def extract_employees() -> list[dict[str, Any]]:
    """Extract employee data from Ontologia API."""
    print("🔍 Extracting employee data from Ontologia...")

    client = OntologyClient(BASE_URL)

    try:
        # Get all employees
        response = client.search_objects("employee")
        employees = response.data

        print(f"✅ Extracted {len(employees)} employees")

        # Transform to clean format
        clean_employees = []
        for emp in employees:
            props = emp.get("properties", {})
            clean_employees.append(
                {
                    "id": props.get("id"),
                    "name": props.get("name"),
                    "email": props.get("email"),
                    "department": props.get("department"),
                    "salary": float(props.get("salary", 0)),
                    "created_at": emp.get("createdAt"),
                    "updated_at": emp.get("updatedAt"),
                }
            )

        return clean_employees

    except Exception as e:
        print(f"❌ Failed to extract employees: {e}")
        raise


@op
def extract_departments() -> list[dict[str, Any]]:
    """Extract department data from Ontologia API."""
    print("🔍 Extracting department data from Ontologia...")

    client = OntologyClient(BASE_URL)

    try:
        # Get all departments
        response = client.search_objects("department")
        departments = response.data

        print(f"✅ Extracted {len(departments)} departments")

        # Transform to clean format
        clean_departments = []
        for dept in departments:
            props = dept.get("properties", {})
            clean_departments.append(
                {
                    "id": props.get("id"),
                    "name": props.get("name"),
                    "manager": props.get("manager"),
                    "budget": float(props.get("budget", 0)),
                    "created_at": dept.get("createdAt"),
                    "updated_at": dept.get("updatedAt"),
                }
            )

        return clean_departments

    except Exception as e:
        print(f"❌ Failed to extract departments: {e}")
        raise


@op
def clean_employee_data(employees: list[dict[str, Any]]) -> pd.DataFrame:
    """Clean and validate employee data."""
    print("🧹 Cleaning employee data...")

    if not employees:
        print("⚠️ No employee data to clean")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(employees)

    # Data quality checks
    initial_count = len(df)

    # Remove duplicates
    df = df.drop_duplicates(subset=["id"])

    # Remove records with missing critical fields
    df = df.dropna(subset=["id", "name", "department"])

    # Validate email format
    df = df[df["email"].str.contains("@", na=False)]

    # Validate salary is positive
    df = df[df["salary"] > 0]

    # Standardize department names
    df["department"] = df["department"].str.strip().str.title()

    # Parse dates
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    final_count = len(df)

    print(f"✅ Cleaned employee data: {initial_count} → {final_count} records")

    # Add metadata
    quality_metrics = {
        "initial_records": initial_count,
        "final_records": final_count,
        "duplicates_removed": initial_count - len(df.drop_duplicates(subset=["id"])),
        "missing_data_removed": initial_count - final_count,
        "data_quality_score": final_count / initial_count if initial_count > 0 else 0,
    }

    print(f"📊 Data quality: {quality_metrics['data_quality_score']:.2%}")

    return df


@op
def clean_department_data(departments: list[dict[str, Any]]) -> pd.DataFrame:
    """Clean and validate department data."""
    print("🧹 Cleaning department data...")

    if not departments:
        print("⚠️ No department data to clean")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(departments)

    # Data quality checks
    initial_count = len(df)

    # Remove duplicates
    df = df.drop_duplicates(subset=["id"])

    # Remove records with missing critical fields
    df = df.dropna(subset=["id", "name"])

    # Validate budget is non-negative
    df = df[df["budget"] >= 0]

    # Standardize names
    df["name"] = df["name"].str.strip().str.title()

    # Parse dates
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    final_count = len(df)

    print(f"✅ Cleaned department data: {initial_count} → {final_count} records")

    return df


@op
def load_to_duckdb(employees_df: pd.DataFrame, departments_df: pd.DataFrame) -> dict[str, Any]:
    """Load cleaned data into DuckDB analytics database."""
    print("📊 Loading data into DuckDB...")

    # Connect to DuckDB
    conn = duckdb.connect(DUCKDB_PATH)

    try:
        # Create employees table
        if not employees_df.empty:
            conn.execute(
                """
                CREATE OR REPLACE TABLE employees AS
                SELECT * FROM employees_df
            """
            )

            # Create indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees(salary)")

            print(f"✅ Loaded {len(employees_df)} employees")

        # Create departments table
        if not departments_df.empty:
            conn.execute(
                """
                CREATE OR REPLACE TABLE departments AS
                SELECT * FROM departments_df
            """
            )

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name)")

            print(f"✅ Loaded {len(departments_df)} departments")

        # Get table statistics
        employee_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        department_count = conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0]

        stats = {
            "employees_loaded": employee_count,
            "departments_loaded": department_count,
            "database_path": DUCKDB_PATH,
            "loaded_at": datetime.now().isoformat(),
        }

        print(f"📈 Database statistics: {stats}")

        return stats

    except Exception as e:
        print(f"❌ Failed to load data to DuckDB: {e}")
        raise
    finally:
        conn.close()


@op
def create_analytics_views() -> dict[str, Any]:
    """Create analytics views in DuckDB."""
    print("🔧 Creating analytics views...")

    conn = duckdb.connect(DUCKDB_PATH)

    try:
        # Department statistics view
        conn.execute(
            """
            CREATE OR REPLACE VIEW department_stats AS
            SELECT
                d.name as department_name,
                d.manager,
                d.budget as department_budget,
                COUNT(e.id) as employee_count,
                AVG(e.salary) as avg_salary,
                MEDIAN(e.salary) as median_salary,
                MIN(e.salary) as min_salary,
                MAX(e.salary) as max_salary,
                STDDEV(e.salary) as salary_stddev
            FROM departments d
            LEFT JOIN employees e ON d.name = e.department
            GROUP BY d.name, d.manager, d.budget
            ORDER BY avg_salary DESC
        """
        )

        # Salary distribution view
        conn.execute(
            """
            CREATE OR REPLACE VIEW salary_distribution AS
            SELECT
                department,
                CASE
                    WHEN salary < 50000 THEN '0-50k'
                    WHEN salary < 75000 THEN '50k-75k'
                    WHEN salary < 100000 THEN '75k-100k'
                    WHEN salary < 150000 THEN '100k-150k'
                    ELSE '150k+'
                END as salary_range,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary_in_range
            FROM employees
            GROUP BY department, salary_range
            ORDER BY department, avg_salary_in_range
        """
        )

        # Budget vs salary view
        conn.execute(
            """
            CREATE OR REPLACE VIEW budget_analysis AS
            SELECT
                d.name as department,
                d.budget as total_budget,
                COALESCE(SUM(e.salary), 0) as total_salary_cost,
                d.budget - COALESCE(SUM(e.salary), 0) as remaining_budget,
                ROUND((COALESCE(SUM(e.salary), 0) / NULLIF(d.budget, 0)) * 100, 2) as budget_utilization_percent
            FROM departments d
            LEFT JOIN employees e ON d.name = e.department
            GROUP BY d.name, d.budget
            ORDER BY budget_utilization_percent DESC
        """
        )

        # Get view statistics
        view_stats = {}
        for view_name in ["department_stats", "salary_distribution", "budget_analysis"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
            view_stats[view_name] = count

        print(f"✅ Created analytics views: {view_stats}")

        return {
            "views_created": list(view_stats.keys()),
            "view_records": view_stats,
            "created_at": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ Failed to create analytics views: {e}")
        raise
    finally:
        conn.close()


@op
def generate_data_quality_report(
    employees_df: pd.DataFrame, departments_df: pd.DataFrame
) -> dict[str, Any]:
    """Generate data quality report."""
    print("📋 Generating data quality report...")

    report = {
        "generated_at": datetime.now().isoformat(),
        "employees": {},
        "departments": {},
        "overall": {},
    }

    # Employee data quality
    if not employees_df.empty:
        report["employees"] = {
            "total_records": len(employees_df),
            "unique_ids": employees_df["id"].nunique(),
            "complete_names": employees_df["name"].notna().sum(),
            "valid_emails": employees_df["email"].str.contains("@").sum(),
            "departments_represented": employees_df["department"].nunique(),
            "avg_salary": float(employees_df["salary"].mean()),
            "salary_range": {
                "min": float(employees_df["salary"].min()),
                "max": float(employees_df["salary"].max()),
                "median": float(employees_df["salary"].median()),
            },
        }

    # Department data quality
    if not departments_df.empty:
        report["departments"] = {
            "total_records": len(departments_df),
            "unique_ids": departments_df["id"].nunique(),
            "complete_names": departments_df["name"].notna().sum(),
            "with_manager": departments_df["manager"].notna().sum(),
            "with_budget": (departments_df["budget"] > 0).sum(),
            "total_budget": float(departments_df["budget"].sum()),
            "avg_budget": float(departments_df["budget"].mean()),
        }

    # Overall quality metrics
    report["overall"] = {
        "data_freshness": "Recent",  # Could be calculated from timestamps
        "completeness_score": 0.95,  # Could be calculated
        "consistency_score": 0.98,  # Could be calculated
        "validity_score": 0.97,  # Could be calculated
    }

    print("✅ Data quality report generated")

    return report


@job
def employee_analytics_etl():
    """Complete ETL job for employee analytics."""
    # Extract
    employees = extract_employees()
    departments = extract_departments()

    # Transform
    clean_employees = clean_employee_data(employees)
    clean_departments = clean_department_data(departments)

    # Load
    load_stats = load_to_duckdb(clean_employees, clean_departments)

    # Create analytics views
    view_stats = create_analytics_views()

    # Generate reports
    quality_report = generate_data_quality_report(clean_employees, clean_departments)

    return {"load_stats": load_stats, "view_stats": view_stats, "quality_report": quality_report}


def main():
    """Run the ETL pipeline manually."""
    print("🚀 Starting Employee Analytics ETL Pipeline")
    print("=" * 50)

    try:
        # Run the job
        result = employee_analytics_etl.execute_in_process()

        if result.success:
            print("\n🎉 ETL Pipeline completed successfully!")
            print(f"📊 Job ID: {result.run_id}")

            # Print summary
            output_data = result.output_for_node("load_to_duckdb")
            print("\n📈 Summary:")
            print(f"   Employees loaded: {output_data['employees_loaded']}")
            print(f"   Departments loaded: {output_data['departments_loaded']}")
            print(f"   Database: {output_data['database_path']}")

        else:
            print("\n❌ ETL Pipeline failed!")
            for failure in result.failure_chain:
                print(f"   Error: {failure}")

    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
