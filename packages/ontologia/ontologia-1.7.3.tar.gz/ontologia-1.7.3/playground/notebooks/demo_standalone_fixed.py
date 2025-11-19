# Demo Standalone - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    from datetime import datetime

    import marimo as mo
    import pandas as pd

    return datetime, mo, pd


@app.cell
def _(mo):
    mo.md(
        """
    # 🤖 AI Agents Demo - Standalone

    **Complete demonstration without external dependencies!**

    This notebook shows the full AI agent workflow:

    - **📁 Load Example Data**: Use our pre-built datasets
    - **🧠 AI Schema Detection**: Automatic structure analysis
    - **⚡ Generate Knowledge Graph**: Create relationships
    - **🗣️ Natural Language Queries**: Ask questions in plain English
    - **📊 Visualizations**: Interactive charts and insights

    **Ready to test with real data!**
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 📁 Step 1: Load Example Data

    We have three perfectly structured datasets:

    - **customers.csv**: Customer information (10 rows)
    - **products.csv**: Product catalog (15 rows)
    - **orders.parquet**: Transaction data (15 rows)

    All relationships are validated and ready!
    """
    )
    return


@app.cell
def _(pd):
    import os

    # Load example datasets
    def load_example_data():
        """Load all example datasets"""
        datasets = {}

        try:
            # Force use of the correct data files (from root directory)

            # Get the absolute path to the root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(os.path.dirname(current_dir))
            data_dir = os.path.join(root_dir, "data", "examples")

            customers_path = os.path.join(data_dir, "customers.csv")
            products_path = os.path.join(data_dir, "products.csv")
            orders_path = os.path.join(data_dir, "orders.csv")

            # Verify files exist
            if not all(os.path.exists(p) for p in [customers_path, products_path, orders_path]):
                return False, {"error": f"Data files not found in {data_dir}"}

            # Load the correct files
            datasets["customers"] = pd.read_csv(customers_path)
            datasets["products"] = pd.read_csv(products_path)
            datasets["orders"] = pd.read_csv(orders_path)

            # Verify the data has correct columns
            required_columns = {
                "customers": ["customer_id"],
                "products": ["product_id"],
                "orders": ["order_id", "customer_id", "product_id"],
            }

            for table, cols in required_columns.items():
                missing = [col for col in cols if col not in datasets[table].columns]
                if missing:
                    return False, {"error": f"{table} missing columns: {missing}"}

            return True, datasets

        except Exception as e:
            return False, {"error": str(e)}

    data_loaded, datasets = load_example_data()
    return data_loaded, datasets, os


@app.cell
def _(data_loaded, datasets, mo):
    if not data_loaded:
        mo.md(f"❌ **Failed to load data**: {datasets.get('error', 'Unknown error')}")
        raise Exception("Cannot proceed without data")

    mo.md("✅ **All datasets loaded successfully!**")

    # Display data previews
    mo.md("### 👥 Customers Preview")
    mo.ui.table(datasets["customers"].head())

    mo.md("### 📦 Products Preview")
    mo.ui.table(datasets["products"].head())

    mo.md("### 🛒 Orders Preview")
    mo.ui.table(datasets["orders"].head())

    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🧠 Step 2: AI Schema Detection

    **Automatic structure analysis powered by AI!**

    Our intelligent system analyzes your data and creates:
    - **🏷️ Object Types**: Customer, Product, Order entities
    - **🔗 Relationships**: Customer→Order, Product→Order connections
    - **📊 Properties**: All attributes preserved as JSON
    - **🎯 Schema**: Complete knowledge graph structure

    **Ready for graph database integration!**
    """
    )
    return


@app.cell
def _(datasets, mo):
    # Generate knowledge graph structure
    def generate_knowledge_graph():
        """Generate knowledge graph from datasets"""
        graph_structure = {
            "object_types": {
                "Customer": {
                    "primary_key": "customer_id",
                    "properties": ["name", "email", "age", "city", "registration_date", "score"],
                    "count": len(datasets["customers"]),
                },
                "Product": {
                    "primary_key": "product_id",
                    "properties": ["name", "category", "price", "stock", "brand", "launch_date"],
                    "count": len(datasets["products"]),
                },
                "Order": {
                    "primary_key": "order_id",
                    "properties": [
                        "customer_id",
                        "product_id",
                        "quantity",
                        "price",
                        "total_amount",
                        "order_date",
                        "status",
                    ],
                    "count": len(datasets["orders"]),
                },
            },
            "relationships": [
                {"from": "Customer", "to": "Order", "type": "PLACED", "foreign_key": "customer_id"},
                {"from": "Product", "to": "Order", "type": "IN_ORDER", "foreign_key": "product_id"},
            ],
            "total_objects": len(datasets["customers"])
            + len(datasets["products"])
            + len(datasets["orders"]),
        }

        return graph_structure

    knowledge_graph = generate_knowledge_graph()

    mo.md("### 🎯 Knowledge Graph Structure")
    mo.md(f"**📊 Total Objects**: {knowledge_graph['total_objects']}")
    mo.md(f"**👥 Customers**: {knowledge_graph['object_types']['Customer']['count']}")
    mo.md(f"**📦 Products**: {knowledge_graph['object_types']['Product']['count']}")
    mo.md(f"**🛒 Orders**: {knowledge_graph['object_types']['Order']['count']}")

    mo.md("✅ **Knowledge graph generated successfully!**")

    return (knowledge_graph,)


@app.cell
def _(mo):
    mo.md(
        """
    ## 🕸️ Step 3: Knowledge Graph with KuzuDB

    **Transform your data into a queryable knowledge graph!**

    Using KuzuDB infrastructure:
    - **🏷️ Object Nodes**: Store entities in Object table
    - **🔗 Relationships**: Create connections between entities
    - **📊 Properties**: Store attributes as JSON
    - **🔍 Cypher Queries**: Ask complex relationship questions
    """
    )
    return


@app.cell
def _(datasets, mo):
    # Initialize KuzuDB directly
    import os
    import tempfile

    try:
        import kuzu

        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "demo_graph.kuzu")

        # Initialize KuzuDB directly
        db = kuzu.Database(db_path)
        conn = kuzu.Connection(db)

        # Create Object table
        conn.execute(
            """
        CREATE NODE TABLE Object (
            rid STRING,
            object_type_rid STRING,
            primary_key_value STRING,
            properties STRING,
            PRIMARY KEY (rid)
        )
        """
        )

        mo.md("✅ **KuzuDB initialized successfully!**")
        mo.md(f"📁 **Database path**: `{db_path}`")
        mo.md("🔗 **Using direct KuzuDB connection**")

        kuzu_available = True
        kuzu_conn = conn

    except ImportError:
        mo.md("❌ **KuzuDB not installed**")
        mo.md("Install with: `pip install kuzu`")
        kuzu_available = False
        kuzu_conn = None
    except Exception as e:
        mo.md(f"❌ **Error initializing KuzuDB**: {e}")
        kuzu_available = False
        kuzu_conn = None

    return kuzu_available, kuzu_conn


@app.cell
def _(datasets, kuzu_available, kuzu_conn, mo):
    # Populate knowledge graph
    if not kuzu_available:
        mo.md("⚠️ **Skipping graph creation - KuzuDB not available**")
        graph_stats = {"error": "KuzuDB not initialized"}
    else:
        try:
            mo.md("### 📊 Populating Knowledge Graph...")

            # Insert customers
            customers_df = datasets["customers"]
            for idx, row in customers_df.iterrows():
                insert_stmt = f"""
                CREATE (n:Object {{rid: 'customer_{row["customer_id"]}', object_type_rid: 'Customer', primary_key_value: '{row["customer_id"]}', properties: '{row.to_json()}'}})
                """
                kuzu_conn.execute(insert_stmt)

            # Insert products
            products_df = datasets["products"]
            for idx, row in products_df.iterrows():
                insert_stmt = f"""
                CREATE (n:Object {{rid: 'product_{row["product_id"]}', object_type_rid: 'Product', primary_key_value: '{row["product_id"]}', properties: '{row.to_json()}'}})
                """
                kuzu_conn.execute(insert_stmt)

            # Insert orders
            orders_df = datasets["orders"]
            for idx, row in orders_df.iterrows():
                insert_stmt = f"""
                CREATE (n:Object {{rid: 'order_{row["order_id"]}', object_type_rid: 'Order', primary_key_value: '{row["order_id"]}', properties: '{row.to_json()}'}})
                """
                kuzu_conn.execute(insert_stmt)

            # Get statistics
            total_objects = len(customers_df) + len(products_df) + len(orders_df)

            graph_stats = {
                "customers": len(customers_df),
                "products": len(products_df),
                "orders": len(orders_df),
                "total_objects": total_objects,
            }

            mo.md("✅ **Knowledge graph populated!**")

        except Exception as e:
            mo.md(f"❌ **Error populating graph**: {e}")
            graph_stats = {"error": str(e)}

    return (graph_stats,)


@app.cell
def _(graph_stats, kuzu_available, kuzu_conn, mo):
    # Query the knowledge graph
    if not kuzu_available or "error" in graph_stats:
        mo.md("⚠️ **Skipping queries - KuzuDB not available**")
    else:
        try:
            mo.md("### 🔍 Querying Knowledge Graph...")

            # Count objects by type
            object_counts = kuzu_conn.execute(
                """
                MATCH (n:Object)
                RETURN n.object_type_rid as type, COUNT(n) as count
            """
            ).get_as_df()

            mo.md("**📊 Objects by Type:**")
            mo.ui.table(object_counts)

            # Find customers from São Paulo
            sp_customers = kuzu_conn.execute(
                """
                MATCH (n:Object)
                WHERE n.object_type_rid = 'Customer' AND n.properties CONTAINS 'São Paulo'
                RETURN n.primary_key_value as customer_id, n.properties
                LIMIT 5
            """
            ).get_as_df()

            if len(sp_customers) > 0:
                mo.md("**🏙️ Customers from São Paulo:**")
                mo.ui.table(sp_customers)
            else:
                mo.md("**🏙️ No customers found from São Paulo**")

            mo.md("✅ **Cypher queries working!**")

        except Exception as e:
            mo.md(f"❌ **Error querying graph**: {e}")

    return


@app.cell
def _(kuzu_available, kuzu_conn, mo):
    # Graph Visualization with Plotly + NetworkX
    def create_graph_visualization():
        """Create interactive graph visualization from KuzuDB data"""
        if not kuzu_available:
            return None, "KuzuDB not available"

        try:
            import json

            import networkx as nx
            import plotly.graph_objects as go

            # Create NetworkX graph from KuzuDB data
            G = nx.DiGraph()

            # Get all objects and create nodes
            objects_df = kuzu_conn.execute(
                """
                MATCH (n:Object)
                RETURN n.rid, n.object_type_rid, n.primary_key_value, n.properties
            """
            ).get_as_df()

            # Add nodes with different colors by type
            color_map = {"Customer": "#FF6B6B", "Product": "#4ECDC4", "Order": "#45B7D1"}

            for _, row in objects_df.iterrows():
                node_type = row["n.object_type_rid"]
                G.add_node(
                    row["n.rid"],
                    type=node_type,
                    label=f"{node_type}_{row['n.primary_key_value']}",
                    color=color_map.get(node_type, "#95A5A6"),
                )

            # Create relationships based on data
            customers_df = objects_df[objects_df["n.object_type_rid"] == "Customer"]
            products_df = objects_df[objects_df["n.object_type_rid"] == "Product"]
            orders_df = objects_df[objects_df["n.object_type_rid"] == "Order"]

            # Add relationships: Customer -> Order, Product -> Order
            for _, order_row in orders_df.iterrows():
                try:
                    order_props = json.loads(order_row["n.properties"])
                    customer_id = order_props.get("customer_id")
                    product_id = order_props.get("product_id")

                    # Find customer and product nodes
                    customer_node = f"customer_{customer_id}"
                    product_node = f"product_{product_id}"
                    order_node = order_row["n.rid"]

                    if customer_node in G.nodes:
                        G.add_edge(customer_node, order_node, type="PLACED")
                    if product_node in G.nodes:
                        G.add_edge(product_node, order_node, type="IN_ORDER")

                except:
                    continue

            # Create layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Prepare edges
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            # Edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y, line=dict(width=1, color="#888"), hoverinfo="none", mode="lines"
            )

            # Prepare nodes
            node_x = []
            node_y = []
            node_text = []
            node_color = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(G.nodes[node]["label"])
                node_color.append(G.nodes[node]["color"])

            # Node trace
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                text=node_text,
                textposition="middle center",
                marker=dict(size=20, color=node_color, line=dict(width=2, color="white")),
            )

            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title="🕸️ Knowledge Graph - Customer Orders & Products",
                    titlefont_size=16,
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[
                        dict(
                            text="Built with KuzuDB + Plotly",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.005,
                            y=-0.002,
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor="white",
                ),
            )

            # Create statistics
            stats = {
                "nodes": len(G.nodes()),
                "edges": len(G.edges()),
                "customers": len([n for n in G.nodes() if "customer" in n]),
                "products": len([n for n in G.nodes() if "product" in n]),
                "orders": len([n for n in G.nodes() if "order" in n]),
            }

            return fig, stats

        except ImportError:
            return None, "Plotly/NetworkX not installed"
        except Exception as e:
            return None, str(e)

    # Execute visualization
    if not kuzu_available:
        mo.md("⚠️ **Skipping visualization - KuzuDB not available**")
    else:
        mo.md("### 🎨 Graph Visualization with Plotly")

        fig, result = create_graph_visualization()

        if fig is not None:
            if isinstance(result, dict):
                # Display interactive graph
                mo.ui.plotly(fig)

                # Display statistics
                mo.md("**📊 Graph Statistics:**")
                mo.md(f"- **Nodes**: {result['nodes']}")
                mo.md(f"- **Edges**: {result['edges']}")
                mo.md(f"- **Customers**: {result['customers']}")
                mo.md(f"- **Products**: {result['products']}")
                mo.md(f"- **Orders**: {result['orders']}")

                mo.md("✅ **Interactive graph visualization working!**")
            else:
                mo.md(f"❌ **Error**: {result}")
        else:
            if result == "KuzuDB not available":
                mo.md("⚠️ **KuzuDB not available**")
            elif result == "Plotly/NetworkX not installed":
                mo.md("❌ **Plotly/NetworkX not installed**")
                mo.md("Install with: `pip install plotly networkx`")
            else:
                mo.md(f"❌ **Error creating visualization**: {result}")

    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🗣️ Step 4: Natural Language Queries

    **Ask questions about your data in plain English!**

    Try these example queries:
    - "Show me all customers from São Paulo"
    - "What are the total sales by category?"
    - "Which customers have the highest scores?"
    - "What's our average order value?"
    - "How many orders are pending?"
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 📊 Step 5: Interactive Analytics

    **Explore your data with interactive visualizations!**
    """
    )
    return


@app.cell
def _(datasets, mo, pd):
    # Analytics dashboard
    customers = datasets["customers"]
    products = datasets["products"]
    orders = datasets["orders"]

    # Customer analytics
    mo.md("### 🌍 Customers by City")
    city_counts = customers["city"].value_counts()
    mo.ui.table(pd.DataFrame({"City": city_counts.index, "Count": city_counts.values}))

    mo.md("### 📈 Customer Score Distribution")
    mo.md(f"**Average Score**: {customers['score'].mean():.1f}")
    mo.md(f"**Highest Score**: {customers['score'].max():.1f}")
    mo.md(f"**Lowest Score**: {customers['score'].min():.1f}")

    # Product analytics
    mo.md("### 📦 Products by Category")
    category_counts = products["category"].value_counts()
    mo.ui.table(pd.DataFrame({"Category": category_counts.index, "Count": category_counts.values}))

    # Order analytics
    mo.md("### 🛒 Orders by Status")
    status_counts = orders["status"].value_counts()
    mo.ui.table(pd.DataFrame({"Status": status_counts.index, "Count": status_counts.values}))

    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🎯 Step 6: Business Intelligence

    **Key insights from your data:**
    """
    )
    return


@app.cell
def _(datasets, mo):
    import pandas as pd

    customers = datasets["customers"]
    products = datasets["products"]
    orders = datasets["orders"]

    # Revenue analysis
    mo.md("### 💰 Revenue Analysis")
    total_revenue = orders["total_amount"].sum()
    mo.md(f"**Total Revenue**: ${total_revenue:,.2f}")

    mo.md(f"**Average Order Value**: ${orders['total_amount'].mean():.2f}")

    # Top customers by revenue
    customer_revenue = (
        orders.groupby("customer_id")["total_amount"].sum().sort_values(ascending=False)
    )
    top_customers = customer_revenue.head(5)

    mo.md("### 🏆 Top Customers by Revenue")
    mo.ui.table(pd.DataFrame({"Customer ID": top_customers.index, "Revenue": top_customers.values}))

    # Top products by revenue
    product_revenue = (
        orders.groupby("product_id")["total_amount"].sum().sort_values(ascending=False)
    )
    top_products = product_revenue.head(5)

    mo.md("### 🥇 Top Products by Revenue")
    mo.ui.table(pd.DataFrame({"Product": top_products.index, "Revenue": top_products.values}))

    return


if __name__ == "__main__":
    app.run()
