# 03 Analytics - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


# Analytics with Ontologia - Marimo Notebook
# Data analysis using DuckDB and Dagster pipelines

import os

import duckdb
import marimo
import plotly.express as px
import plotly.graph_objects as go
import requests

# Initialize Marimo app
app = marimo.App()


@app.cell
def _(mo):
    mo.md(
        """
        # 📊 Analytics with Ontologia

        This notebook demonstrates how to:

        - **Connect to DuckDB**: Query your analytics data warehouse
        - **Run SQL Queries**: Perform complex analytics operations
        - **Create Visualizations**: Build interactive charts and dashboards
        - **Pipeline Integration**: Use Dagster for data pipelines

        Let's start by setting up our analytics environment!
        """
    )
    return


@app.cell
def _(mo):
    # Environment setup
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/app/data/analytics.duckdb")

    def check_services():
        """Check if required services are running"""
        checks = {"API": False, "DuckDB": False}

        # Check API
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            checks["API"] = response.status_code == 200
        except:
            pass

        # Check DuckDB file
        try:
            conn = duckdb.connect(DUCKDB_PATH)
            conn.execute("SELECT 1")
            checks["DuckDB"] = True
            conn.close()
        except:
            pass

        return checks

    service_status = check_services()
    return API_BASE_URL, DUCKDB_PATH, check_services, service_status


@app.cell
def _(mo, service_status):
    # Display service status
    status_emojis = {"API": "🌐", "DuckDB": "🦆"}

    status_text = "## 🔧 Service Status\n\n"
    for service, status in service_status.items():
        emoji = status_emojis.get(service, "📦")
        status_icon = "✅" if status else "❌"
        status_text += (
            f"{emoji} **{service}**: {status_icon} {'Running' if status else 'Not Available'}\n"
        )

    if not all(service_status.values()):
        status_text += "\n⚠️ Some services are not available. Please start the playground: `docker-compose up -d`"

    mo.md(status_text)
    return


@app.cell
def _(mo, service_status):
    if not service_status["DuckDB"]:
        raise marimo.Interrupt("DuckDB is required for analytics")
    return


@app.cell
def _(mo, DUCKDB_PATH):
    # Initialize DuckDB connection
    def get_duckdb_connection():
        """Create and return a DuckDB connection"""
        conn = duckdb.connect(DUCKDB_PATH)

        # Install and load extensions
        conn.execute("INSTALL httpfs")
        conn.execute("LOAD httpfs")
        conn.execute("INSTALL json")
        conn.execute("LOAD json")

        return conn

    conn = get_duckdb_connection()
    return conn, get_duckdb_connection


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 🗄️ Setting up Analytics Tables

        Let's create some sample tables for our analytics demonstrations.
        """
    )
    return


@app.cell
def _(mo, conn):
    def create_sample_tables():
        """Create sample analytics tables"""

        # Create companies table
        conn.execute(
            """
            CREATE OR REPLACE TABLE companies AS
            SELECT * FROM VALUES
                ('TechCorp', 'Technology', 2010, 50000000, 250),
                ('DataInc', 'Data Analytics', 2015, 25000000, 100),
                ('CloudSoft', 'Cloud Computing', 2012, 75000000, 400),
                ('AI Labs', 'Artificial Intelligence', 2018, 15000000, 75),
                ('FinTech Pro', 'Financial Technology', 2016, 30000000, 150)
            AS t(name, industry, founded_year, revenue, employees)
        """
        )

        # Create employees table
        conn.execute(
            """
            CREATE OR REPLACE TABLE employees AS
            SELECT * FROM VALUES
                ('Alice Johnson', 'TechCorp', 'CEO', 250000, 'San Francisco'),
                ('Bob Smith', 'TechCorp', 'CTO', 200000, 'San Francisco'),
                ('Carol Davis', 'DataInc', 'Data Scientist', 120000, 'New York'),
                ('David Wilson', 'CloudSoft', 'Software Engineer', 110000, 'Seattle'),
                ('Eva Brown', 'AI Labs', 'ML Engineer', 130000, 'Boston'),
                ('Frank Miller', 'FinTech Pro', 'Backend Developer', 105000, 'Chicago'),
                ('Grace Lee', 'TechCorp', 'Product Manager', 140000, 'San Francisco'),
                ('Henry Taylor', 'DataInc', 'Data Analyst', 85000, 'New York')
            AS t(name, company, role, salary, location)
        """
        )

        # Create projects table
        conn.execute(
            """
            CREATE OR REPLACE TABLE projects AS
            SELECT * FROM VALUES
                ('AI Platform', 'TechCorp', 'Active', 1000000, '2023-01-15', '2024-06-30'),
                ('Data Pipeline', 'DataInc', 'Planning', 500000, '2023-03-01', '2024-12-31'),
                ('Cloud Migration', 'CloudSoft', 'Active', 2000000, '2022-11-01', '2023-12-31'),
                ('ML Research', 'AI Labs', 'Active', 750000, '2023-02-01', '2024-08-31'),
                ('Payment System', 'FinTech Pro', 'Completed', 800000, '2022-05-01', '2023-10-31')
            AS t(name, company, status, budget, start_date, end_date)
        """
        )

        return True

    tables_created = create_sample_tables()
    return create_sample_tables, tables_created


@app.cell
def _(mo, tables_created):
    if tables_created:
        mo.md("✅ Sample analytics tables created successfully!")
    else:
        mo.md("❌ Failed to create sample tables")
    return


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 📈 Basic Analytics Queries

        Let's run some basic analytics queries on our data.
        """
    )
    return


@app.cell
def _(mo, conn):
    def get_company_summary():
        """Get summary statistics by company"""
        query = """
            SELECT
                c.name,
                c.industry,
                c.employees,
                c.revenue,
                COUNT(e.name) as employee_count,
                AVG(e.salary) as avg_salary,
                COUNT(p.name) as project_count,
                SUM(p.budget) as total_project_budget
            FROM companies c
            LEFT JOIN employees e ON c.name = e.company
            LEFT JOIN projects p ON c.name = p.company
            GROUP BY c.name, c.industry, c.employees, c.revenue
            ORDER BY c.revenue DESC
        """

        result = conn.execute(query).fetchdf()
        return result

    company_summary = get_company_summary()
    return company_summary, get_company_summary


@app.cell
def _(mo, company_summary):
    # Display company summary
    mo.md("### Company Performance Summary")
    mo.ui.table(company_summary)
    return


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 📊 Industry Analysis

        Let's analyze performance by industry.
        """
    )
    return


@app.cell
def _(mo, conn):
    def get_industry_analysis():
        """Analyze metrics by industry"""
        query = """
            SELECT
                industry,
                COUNT(*) as company_count,
                SUM(employees) as total_employees,
                SUM(revenue) as total_revenue,
                AVG(revenue) as avg_revenue_per_company,
                AVG(avg_salary) as avg_industry_salary
            FROM (
                SELECT
                    c.industry,
                    c.employees,
                    c.revenue,
                    AVG(e.salary) as avg_salary
                FROM companies c
                LEFT JOIN employees e ON c.name = e.company
                GROUP BY c.name, c.industry, c.employees, c.revenue
            )
            GROUP BY industry
            ORDER BY total_revenue DESC
        """

        result = conn.execute(query).fetchdf()
        return result

    industry_analysis = get_industry_analysis()
    return get_industry_analysis, industry_analysis


@app.cell
def _(mo, industry_analysis):
    # Display industry analysis
    mo.md("### Industry Performance Analysis")
    mo.ui.table(industry_analysis)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎨 Interactive Visualizations

        Let's create some interactive charts using Plotly.
        """
    )
    return


@app.cell
def _(mo, company_summary):
    import plotly.express as px

    # Create revenue vs employees scatter plot
    fig_revenue_employees = px.scatter(
        company_summary,
        x="employees",
        y="revenue",
        size="project_count",
        color="industry",
        hover_name="name",
        title="Company Revenue vs Employees (Size = Project Count)",
        labels={
            "employees": "Number of Employees",
            "revenue": "Revenue ($)",
            "project_count": "Number of Projects",
        },
    )

    fig_revenue_employees.update_layout(
        xaxis_title="Number of Employees", yaxis_title="Revenue ($)", showlegend=True
    )

    return fig_revenue_employees, go, px


@app.cell
def _(mo, fig_revenue_employees):
    # Display the scatter plot
    mo.md("### Revenue vs Employees Analysis")
    mo.ui.plotly(fig_revenue_employees)
    return


@app.cell
def _(mo, industry_analysis):
    # Create industry revenue bar chart
    fig_industry_revenue = px.bar(
        industry_analysis,
        x="industry",
        y="total_revenue",
        title="Total Revenue by Industry",
        labels={"industry": "Industry", "total_revenue": "Total Revenue ($)"},
        color="avg_industry_salary",
        color_continuous_scale="Viridis",
    )

    fig_industry_revenue.update_layout(
        xaxis_title="Industry", yaxis_title="Total Revenue ($)", showlegend=False
    )

    return (fig_industry_revenue,)


@app.cell
def _(mo, fig_industry_revenue):
    # Display industry revenue chart
    mo.md("### Industry Revenue Comparison")
    mo.ui.plotly(fig_industry_revenue)
    return


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 🔍 Advanced Analytics

        Let's run some more complex analytical queries.
        """
    )
    return


@app.cell
def _(mo, conn):
    def get_salary_analysis():
        """Analyze salary distribution and trends"""
        query = """
            SELECT
                role,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary,
                STDDEV(salary) as salary_stddev,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median_salary
            FROM employees
            GROUP BY role
            ORDER BY avg_salary DESC
        """

        result = conn.execute(query).fetchdf()
        return result

    salary_analysis = get_salary_analysis()
    return get_salary_analysis, salary_analysis


@app.cell
def _(mo, salary_analysis):
    # Display salary analysis
    mo.md("### Salary Analysis by Role")
    mo.ui.table(salary_analysis)
    return


@app.cell
def _(mo, salary_analysis):
    # Create salary distribution box plot
    fig_salary_dist = px.box(
        salary_analysis,
        x="role",
        y="avg_salary",
        title="Salary Distribution by Role",
        labels={"role": "Job Role", "avg_salary": "Average Salary ($)"},
    )

    fig_salary_dist.update_layout(
        xaxis_title="Job Role", yaxis_title="Average Salary ($)", xaxis_tickangle=-45
    )

    return (fig_salary_dist,)


@app.cell
def _(mo, fig_salary_dist):
    # Display salary distribution
    mo.md("### Salary Distribution by Role")
    mo.ui.plotly(fig_salary_dist)
    return


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 📅 Time Series Analysis

        Let's analyze project timelines and trends.
        """
    )
    return


@app.cell
def _(mo, conn):
    def get_project_timeline_analysis():
        """Analyze project timelines and completion"""
        query = """
            SELECT
                company,
                status,
                COUNT(*) as project_count,
                SUM(budget) as total_budget,
                AVG(budget) as avg_budget,
                AVG(EXTRACT(DAYS FROM (end_date - start_date))) as avg_duration_days
            FROM projects
            GROUP BY company, status
            ORDER BY total_budget DESC
        """

        result = conn.execute(query).fetchdf()
        return result

    project_timeline = get_project_timeline_analysis()
    return get_project_timeline_analysis, project_timeline


@app.cell
def _(mo, project_timeline):
    # Display project timeline analysis
    mo.md("### Project Timeline Analysis")
    mo.ui.table(project_timeline)
    return


@app.cell
def _(mo, project_timeline):
    # Create project status pie chart
    fig_project_status = px.pie(
        project_timeline.groupby("status")["total_budget"].sum().reset_index(),
        values="total_budget",
        names="status",
        title="Project Budget by Status",
        labels={"status": "Project Status", "total_budget": "Total Budget ($)"},
    )

    return (fig_project_status,)


@app.cell
def _(mo, fig_project_status):
    # Display project status chart
    mo.md("### Project Budget Distribution by Status")
    mo.ui.plotly(fig_project_status)
    return


@app.cell
def _(mo, conn):
    mo.md(
        """
        ## 🎯 Custom Analytics Functions

        Let's create some reusable analytics functions.
        """
    )
    return


@app.cell
def _(mo, conn):
    def calculate_roi_metrics():
        """Calculate ROI metrics for companies"""
        query = """
            WITH company_costs AS (
                SELECT
                    c.name,
                    c.revenue,
                    COALESCE(SUM(p.budget), 0) as total_project_costs,
                    COALESCE(AVG(e.salary) * c.employees, 0) as estimated_annual_salary_costs
                FROM companies c
                LEFT JOIN projects p ON c.name = p.company
                LEFT JOIN employees e ON c.name = e.company
                GROUP BY c.name, c.revenue, c.employees
            )
            SELECT
                name,
                revenue,
                total_project_costs,
                estimated_annual_salary_costs,
                (total_project_costs + estimated_annual_salary_costs) as total_estimated_costs,
                (revenue / NULLIF(total_estimated_costs, 1)) as roi_ratio,
                ((revenue - total_estimated_costs) / NULLIF(total_estimated_costs, 1)) * 100 as profit_margin_pct
            FROM company_costs
            ORDER BY revenue DESC
        """

        result = conn.execute(query).fetchdf()
        return result

    roi_metrics = calculate_roi_metrics()
    return calculate_roi_metrics, roi_metrics


@app.cell
def _(mo, roi_metrics):
    # Display ROI metrics
    mo.md("### ROI and Profitability Analysis")
    mo.ui.table(roi_metrics)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎉 Analytics Summary

        You've successfully explored Ontologia's analytics capabilities:

        ✅ **DuckDB Integration**: Connected to the analytics data warehouse
        ✅ **SQL Queries**: Ran complex analytical queries
        ✅ **Data Visualization**: Created interactive charts with Plotly
        ✅ **Business Metrics**: Calculated ROI, profit margins, and KPIs
        ✅ **Time Series Analysis**: Analyzed project timelines and trends

        **Key Features Demonstrated**:
        - Multi-table joins and aggregations
        - Statistical functions (AVG, STDDEV, PERCENTILE)
        - Interactive visualizations
        - Business intelligence calculations

        **Next Steps**:
        - Try `04_workflows.py` for automation with Temporal
        - Explore the Dagster UI at http://localhost:3000
        - Check API documentation at http://localhost:8000/docs

        **Advanced Analytics**:
        - Machine learning with DuckDB
        - Real-time dashboards
        - Automated report generation
        - Integration with external data sources
        """
    )
    return


if __name__ == "__main__":
    app.run()
