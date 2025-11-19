# Data Examples Test - Marimo Notebook
# Test and validate example datasets

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
    # 📊 Data Examples Test

    This notebook validates our example datasets and demonstrates:

    - **CSV Loading**: Customer and product data
    - **Parquet Loading**: Order transactions
    - **Data Validation**: Check data quality and relationships
    - **Preview**: Sample data exploration

    Let's test our example files!
    """
    )
    return


@app.cell
def _():
    import os

    import pandas as pd

    # Define data paths
    DATA_DIR = "../data/examples"

    example_files = {
        "customers": os.path.join(DATA_DIR, "customers.csv"),
        "orders": os.path.join(DATA_DIR, "orders.parquet"),
        "products": os.path.join(DATA_DIR, "products.csv"),
    }

    # Check if files exist
    file_status = {}
    for name, path in example_files.items():
        file_status[name] = {
            "exists": os.path.exists(path),
            "path": path,
            "size": os.path.getsize(path) if os.path.exists(path) else 0,
        }

    return example_files, file_status, pd


@app.cell
def _(file_status, mo):
    # Display file status
    mo.md("### 📁 Example Files Status")

    for name, status in file_status.items():
        if status["exists"]:
            mo.md(f"✅ **{name.title()}**: {status['size']} bytes")
        else:
            mo.md(f"❌ **{name.title()}**: Not found at {status['path']}")

    if all(status["exists"] for status in file_status.values()):
        mo.md("🎉 **All example files are ready!**")
    else:
        mo.md("⚠️ **Some files are missing**")
    return


@app.cell
def _(example_files, file_status, marimo, mo, pd):
    # Load and validate data
    datasets = {}

    if not all(status["exists"] for status in file_status.values()):
        mo.md("❌ Cannot proceed - missing example files")
        raise marimo.Interrupt("Missing example files")

    try:
        # Load CSV files
        datasets["customers"] = pd.read_csv(example_files["customers"])
        datasets["products"] = pd.read_csv(example_files["products"])

        # Load Parquet file
        datasets["orders"] = pd.read_parquet(example_files["orders"])

        mo.md("✅ **All datasets loaded successfully!**")

    except Exception as e:
        mo.md(f"❌ **Error loading datasets**: {e}")
        raise marimo.Interrupt("Data loading failed")

    return (datasets,)


@app.cell
def _(customers_df, datasets, mo):
    mo.md("### 👥 Customers Dataset")
    customers_cell_6_df = datasets["customers"]

    mo.md(f"**Shape**: {customers_df.shape[0]} rows, {customers_df.shape[1]} columns")
    mo.ui.table(customers_df.head())

    # Basic statistics
    mo.md("**Basic Statistics**:")
    stats_text = f"""
    - **Age Range**: {customers_df['age'].min()} - {customers_df['age'].max()} years
    - **Average Score**: {customers_df['score'].mean():.1f}
    - **Cities**: {customers_df['city'].nunique()} unique locations
    - **Registration Period**: {customers_df['registration_date'].min()} to {customers_df['registration_date'].max()}
    """
    mo.md(stats_text)
    return


@app.cell
def _(datasets, mo, products_df):
    mo.md("### 📦 Products Dataset")
    products_cell_7_df = datasets["products"]

    mo.md(f"**Shape**: {products_df.shape[0]} rows, {products_df.shape[1]} columns")
    mo.ui.table(products_df.head())

    # Category analysis
    mo.md("**Category Analysis**:")
    category_counts = products_df["category"].value_counts()
    for category, cell_7_count in category_counts.items():
        mo.md(f"- **{category}**: {cell_7_count} products")

    mo.md(f"**Price Range**: ${products_df['price'].min():.2f} - ${products_df['price'].max():.2f}")
    return


@app.cell
def _(cell_8_count, datasets, mo, orders_df):
    mo.md("### 🛒 Orders Dataset")
    orders_cell_8_df = datasets["orders"]

    mo.md(f"**Shape**: {orders_df.shape[0]} rows, {orders_df.shape[1]} columns")
    mo.ui.table(orders_df.head())

    # Order analysis
    mo.md("**Order Analysis**:")
    stats_text = f"""
    - **Total Orders**: {len(orders_df)}
    - **Order Value Range**: ${orders_df['total_amount'].min():.2f} - ${orders_df['total_amount'].max():.2f}
    - **Average Order Value**: ${orders_df['total_amount'].mean():.2f}
    - **Status Distribution**:
    """

    status_counts = orders_df["status"].value_counts()
    for status, count in status_counts.items():
        stats_text += f"\n      - **{status.title()}**: {cell_8_count} orders"

    mo.md(stats_text)
    return


@app.cell
def _(customers_df, datasets, mo, orders_df, products_df):
    mo.md("### 🔗 Data Relationships")

    customers_cell_9_df = datasets["customers"]
    orders_cell_9_df = datasets["orders"]
    products_cell_9_df = datasets["products"]

    # Check relationships
    mo.md("**Foreign Key Validation**:")

    # Customer orders
    customer_orders = orders_df["customer_id"].nunique()
    total_customers = customers_df["customer_id"].nunique()
    mo.md(
        f"- **Customers with Orders**: {customer_orders}/{total_customers} ({customer_orders/total_customers*100:.1f}%)"
    )

    # Product orders
    ordered_products = orders_df["product_id"].nunique()
    total_products = products_df["product_id"].nunique()
    mo.md(
        f"- **Products with Orders**: {ordered_products}/{total_products} ({ordered_products/total_products*100:.1f}%)"
    )

    # Data consistency
    invalid_customers = set(orders_df["customer_id"]) - set(customers_df["customer_id"])
    invalid_products = set(orders_df["product_id"]) - set(products_df["product_id"])

    if not invalid_customers and not invalid_products:
        mo.md("✅ **All relationships are valid!**")
    else:
        mo.md(
            f"⚠️ **Invalid references found**: {len(invalid_customers)} customers, {len(invalid_products)} products"
        )
    return


@app.cell
def _(customers_df, datasets, mo, orders_df, products_df):
    mo.md("### 📈 Business Insights")

    customers_cell_10_df = datasets["customers"]
    orders_cell_10_df = datasets["orders"]
    products_cell_10_df = datasets["products"]

    # Calculate insights
    total_revenue = orders_df["total_amount"].sum()
    avg_customer_score = customers_df["score"].mean()
    top_category = products_df["category"].value_counts().index[0]

    mo.md("**Key Metrics**:")
    insights_text = f"""
    - **Total Revenue**: ${total_revenue:,.2f}
    - **Average Customer Score**: {avg_customer_score:.1f}
    - **Top Product Category**: {top_category}
    - **Orders per Customer**: {len(orders_df)/len(customers_df):.1f} average
    - **Revenue per Order**: ${total_revenue/len(orders_df):.2f} average
    """

    mo.md(insights_text)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🎯 Ready for AI Agents!

    Your example datasets are validated and ready for use with the **AI Agents notebook** (`05_agents.py`):

    ### **How to Use**:

    1. **Open**: `05_agents.py` in Marimo
    2. **Upload**: Any of these files from `../data/examples/`:
       - `customers.csv` - Customer information
       - `orders.parquet` - Transaction data
       - `products.csv` - Product catalog
    3. **AI Processing**: Let AI detect schema and create ontology
    4. **Natural Queries**: Ask questions about your data

    ### **Example Queries**:
    - "Show me all customers from São Paulo"
    - "What are the total sales by category?"
    - "Which customers have the highest scores?"
    - "What's our average order value?"

    **The datasets are perfectly structured for AI-powered knowledge graph creation!** 🚀
    """
    )
    return


if __name__ == "__main__":
    app.run()
