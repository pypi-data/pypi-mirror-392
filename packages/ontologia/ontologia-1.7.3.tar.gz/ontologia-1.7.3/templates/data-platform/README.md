# Data Platform Template

Built for data teams who need analytics, ETL, and data processing capabilities. This template includes DuckDB for analytics, dbt for transformations, and Dagster for orchestration.

## 🎯 What You Get

- ✅ **DuckDB** for fast analytics queries
- ✅ **dbt** for data transformations (Bronze/Silver/Gold)
- ✅ **Dagster** for pipeline orchestration
- ✅ **PostgreSQL** for operational data
- ✅ **Jupyter** for data exploration
- ✅ **Analytics API** endpoints

## 🚀 Quick Start

### 1. Create Project
```bash
ontologia init --template data-platform my-analytics
cd my-analytics
```

### 2. Start Services
```bash
# Start core services + analytics stack
docker-compose -f docker-compose.analytics.yml up -d

# Wait for services to be ready
docker-compose logs -f dagster-webserver
```

### 3. Access Analytics Tools
- **Dagster UI**: http://localhost:3000
- **dbt Docs**: http://localhost:8080
- **Jupyter Lab**: http://localhost:8888
- **API**: http://localhost:8000/docs

## 📁 Project Structure

```
my-analytics/
├── README.md              # This file
├── pyproject.toml         # Analytics dependencies
├── docker-compose.yml     # Core services
├── docker-compose.analytics.yml  # Analytics stack
├── .env.example          # Environment variables
├── dbt/                  # dbt project
│   ├── models/
│   │   ├── bronze/       # Raw data
│   │   ├── silver/       # Cleaned data
│   │   └── gold/         # Business-ready data
│   └── dbt_project.yml
├── dagster/              # Dagster definitions
│   ├── __init__.py
│   ├── assets.py
│   └── jobs.py
├── notebooks/            # Jupyter notebooks
│   └── exploration.ipynb
└── examples/             # Analytics examples
    ├── etl_pipeline.py
    ├── analytics_queries.py
    └── dashboard_setup.py
```

## 🛠️ Development

### Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Install analytics dependencies
pip install ontologia[analytics]

# Install dbt
pip install dbt-duckdb

# Start in development mode
uv run uvicorn ontologia_api.main:app --reload --host 0.0.0.0 --port 8000
```

### dbt Development
```bash
# Run dbt transformations
cd dbt
dbt run
dbt test
dbt docs generate
dbt docs serve
```

### Dagster Development
```bash
# Start Dagster daemon
dagster dev

# Run specific job
dagster job launch -f dagster/jobs.py my_analytics_job
```

## 📊 Analytics Architecture

### Data Flow
```
PostgreSQL (Operational) → DuckDB (Analytics) → dbt Models → Dashboards
```

### Layers
1. **Bronze**: Raw data from PostgreSQL
2. **Silver**: Cleaned and standardized data
3. **Gold**: Business-ready aggregated data

### Example dbt Models

#### Bronze Layer
```sql
-- models/bronze/employees_raw.sql
SELECT
    id,
    name,
    email,
    department,
    salary,
    created_at,
    updated_at
FROM ontologia.employees
```

#### Silver Layer
```sql
-- models/silver/employees_clean.sql
SELECT
    id,
    name,
    lower(email) as email,
    department,
    salary,
    created_at,
    updated_at
FROM {{ ref('employees_raw') }}
WHERE email IS NOT NULL
```

#### Gold Layer
```sql
-- models/gold/department_stats.sql
SELECT
    department,
    count(*) as employee_count,
    avg(salary) as avg_salary,
    max(salary) as max_salary
FROM {{ ref('employees_clean') }}
GROUP BY department
```

## 📈 Usage Examples

### ETL Pipeline
```python
from dagster import job, op
from ontologia_sdk.client import OntologyClient

@op
def extract_employees():
    """Extract employee data from Ontologia."""
    client = OntologyClient("http://localhost:8000")
    employees = client.search_objects("employee")
    return employees.data

@op
def transform_employees(employees):
    """Transform employee data."""
    # Clean and transform data
    transformed = []
    for emp in employees:
        transformed.append({
            'id': emp['properties']['id'],
            'name': emp['properties']['name'],
            'department': emp['properties']['department'],
            'salary': float(emp['properties']['salary'])
        })
    return transformed

@op
def load_to_duckdb(employees):
    """Load data into DuckDB."""
    import duckdb
    conn = duckdb.connect('data/analytics.duckdb')

    # Create table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id VARCHAR,
            name VARCHAR,
            department VARCHAR,
            salary DOUBLE
        )
    """)

    # Insert data
    conn.execute("INSERT INTO employees VALUES (?, ?, ?, ?)",
                 [(emp['id'], emp['name'], emp['department'], emp['salary'])
                  for emp in employees])

@job
def employee_etl_job():
    """Complete ETL job for employees."""
    load_to_duckdb(transform_employees(extract_employees()))
```

### Analytics Queries
```python
import duckdb
import pandas as pd

def run_department_analysis():
    """Analyze department statistics."""
    conn = duckdb.connect('data/analytics.duckdb')

    # Department statistics
    dept_stats = conn.execute("""
        SELECT
            department,
            COUNT(*) as employee_count,
            AVG(salary) as avg_salary,
            STDDEV(salary) as salary_stddev
        FROM employees
        GROUP BY department
        ORDER BY avg_salary DESC
    """).fetchdf()

    return dept_stats

def salary_distribution():
    """Get salary distribution by department."""
    conn = duckdb.connect('data/analytics.duckdb')

    distribution = conn.execute("""
        SELECT
            department,
            salary,
            COUNT(*) OVER (PARTITION BY department) as dept_size
        FROM employees
        ORDER BY department, salary
    """).fetchdf()

    return distribution
```

### Dashboard Setup
```python
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

def main():
    st.title("Employee Analytics Dashboard")

    # Connect to DuckDB
    conn = duckdb.connect('data/analytics.duckdb')

    # Load data
    employees = conn.execute("SELECT * FROM employees").fetchdf()

    # Department overview
    st.header("Department Overview")
    dept_stats = employees.groupby('department').agg({
        'salary': ['count', 'mean', 'std']
    }).round(2)

    st.dataframe(dept_stats)

    # Salary distribution
    st.header("Salary Distribution")
    fig = px.box(employees, x='department', y='salary')
    st.plotly_chart(fig)

    # Employee count by department
    st.header("Employee Count")
    dept_counts = employees['department'].value_counts()
    fig = px.pie(values=dept_counts.values, names=dept_counts.index)
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Database
DATABASE_URL=postgresql://ontologia:ontologia123@localhost:5432/ontologia

# Analytics
DUCKDB_PATH=./data/analytics.duckdb
ENABLE_ORCHESTRATION=true

# Dagster
DAGSTER_HOME=./dagster
DAGSTER_POSTGRES_DB=postgresql://ontologia:ontologia123@localhost:5432/dagster

# dbt
DBT_PROFILES_DIR=./dbt
DBT_TARGET_PATH=./dbt/target

# Jupyter
JUPYTER_TOKEN=your-jupyter-token
JUPYTER_PORT=8888
```

### dbt Configuration
```yaml
# dbt/dbt_project.yml
name: 'ontologia_analytics'
version: '1.0.0'

profile: 'ontologia'

model-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]

models:
  ontologia_analytics:
    bronze:
      +materialized: table
    silver:
      +materialized: table
    gold:
      +materialized: table
```

## 🚀 Production Deployment

### Docker Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale dagster-worker=3
```

### Monitoring
- **Dagster UI**: Pipeline monitoring and scheduling
- **dbt Docs**: Data documentation and lineage
- **Grafana**: Metrics and dashboards (add-on)
- **Prometheus**: Metrics collection (add-on)

## 📚 Learn More

- **dbt Documentation**: https://docs.getdbt.com/
- **Dagster Documentation**: https://docs.dagster.io/
- **DuckDB Documentation**: https://duckdb.org/docs/
- **Ontologia Analytics Guide**: [../../docs/analytics.md](../../docs/analytics.md)

## 🎉 Success!

You now have a complete data platform with:
- ✅ Operational database (PostgreSQL)
- ✅ Analytics database (DuckDB)
- ✅ Data transformations (dbt)
- ✅ Pipeline orchestration (Dagster)
- ✅ Data exploration (Jupyter)
- ✅ API for integration

Ready to build amazing data products! 🚀
