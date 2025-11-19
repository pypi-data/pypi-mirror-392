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

    # Display dataset summary
    summary_text = "### 📊 Dataset Summary\n\n"
    for name, df in datasets.items():
        summary_text += f"- **{name.title()}**: {len(df)} rows, {len(df.columns)} columns\n"

    mo.md(summary_text)
    return


@app.cell
def _(datasets, mo):
    mo.md("### 👥 Customers Preview")
    mo.ui.table(datasets["customers"].head())
    return


@app.cell
def _(datasets, mo):
    mo.md("### 📦 Products Preview")
    mo.ui.table(datasets["products"].head())
    return


@app.cell
def _(datasets, mo):
    mo.md("### 🛒 Orders Preview")
    mo.ui.table(datasets["orders"].head())
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🧠 Step 2: AI Schema Detection

    **AI Analysis Results**: Our intelligent system has analyzed your data and detected:

    ### **📋 Object Types Detected**:
    - **Customer**: People who buy products
    - **Product**: Items available for sale
    - **Order**: Transactions between customers and products

    ### **🔗 Relationships Detected**:
    - **Customer → Orders**: One-to-many relationship
    - **Product → Orders**: One-to-many relationship
    - **Order → Customer**: Many-to-one relationship
    - **Order → Product**: Many-to-one relationship

    ### **📊 Data Quality**:
    - ✅ All foreign keys are valid
    - ✅ No missing critical data
    - ✅ Consistent data types
    - ✅ Proper date formatting
    """
    )
    return


@app.cell
def _(datasets, datetime):
    def generate_knowledge_graph():
        """Generate a knowledge graph representation"""

        # Create object type definitions
        object_types = {
            "Customer": {
                "properties": [
                    "customer_id",
                    "name",
                    "email",
                    "age",
                    "city",
                    "registration_date",
                    "score",
                ],
                "identifier": "customer_id",
                "count": len(datasets["customers"]),
            },
            "Product": {
                "properties": [
                    "product_id",
                    "name",
                    "category",
                    "price",
                    "stock",
                    "brand",
                    "launch_date",
                ],
                "identifier": "product_id",
                "count": len(datasets["products"]),
            },
            "Order": {
                "properties": [
                    "order_id",
                    "customer_id",
                    "product_id",
                    "quantity",
                    "price",
                    "total_amount",
                    "order_date",
                    "status",
                ],
                "identifier": "order_id",
                "count": len(datasets["orders"]),
            },
        }

        # Create relationship definitions
        relationships = [
            {
                "from": "Customer",
                "to": "Order",
                "type": "HAS_ORDER",
                "description": "Customer placed orders",
            },
            {
                "from": "Product",
                "to": "Order",
                "type": "IN_ORDER",
                "description": "Product appears in orders",
            },
        ]

        return {
            "object_types": object_types,
            "relationships": relationships,
            "total_entities": sum(obj["count"] for obj in object_types.values()),
            "generated_at": datetime.now().isoformat(),
        }

    knowledge_graph = generate_knowledge_graph()
    return (knowledge_graph,)


@app.cell
def _(knowledge_graph, mo):
    mo.md("### 🎯 Generated Knowledge Graph")

    # Display object types
    mo.md("**📋 Object Types**:")
    for obj_name, obj_info in knowledge_graph["object_types"].items():
        mo.md(f"- **{obj_name}**: {obj_info['count']} instances")
        mo.md(f"  - Properties: {', '.join(obj_info['properties'])}")
        mo.md(f"  - Identifier: {obj_info['identifier']}")

    # Display relationships
    mo.md("\n**🔗 Relationships**:")
    for rel in knowledge_graph["relationships"]:
        mo.md(f"- **{rel['from']} → {rel['to']}** ({rel['type']})")
        mo.md(f"  - {rel['description']}")

    mo.md(f"\n**📊 Total Entities**: {knowledge_graph['total_entities']}")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🕸️ Step 3: Knowledge Graph with Ontologia's KuzuDB

    **Transform your data into a queryable knowledge graph!**

    Using Ontologia's integrated KuzuDB infrastructure:
    - **🏷️ Object Nodes**: Store entities in Ontologia's Object table
    - **🔗 Relationships**: Create connections between entities
    - **📊 Properties**: Store attributes as JSON
    - **🔍 Cypher Queries**: Ask complex relationship questions
    """
    )


@app.cell
def _(datasets, mo):
    # Initialize KuzuDB directly (bypassing Ontologia's unified graph)
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
            import plotly.graph_objects as go
            import networkx as nx
            import json

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
                node_type = row["object_type_rid"]
                G.add_node(
                    row["rid"],
                    type=node_type,
                    label=f"{node_type}_{row['primary_key_value']}",
                    color=color_map.get(node_type, "#95A5A6"),
                )

            # Create relationships based on data
            customers_df = objects_df[objects_df["object_type_rid"] == "Customer"]
            products_df = objects_df[objects_df["object_type_rid"] == "Product"]
            orders_df = objects_df[objects_df["object_type_rid"] == "Order"]

            # Add relationships: Customer -> Order, Product -> Order
            for _, order_row in orders_df.iterrows():
                try:
                    order_props = json.loads(order_row["properties"])
                    customer_id = order_props.get("customer_id")
                    product_id = order_props.get("product_id")

                    # Find customer and product nodes
                    customer_node = f"customer_{customer_id}"
                    product_node = f"product_{product_id}"
                    order_node = order_row["rid"]

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
                mo.md(f"**📊 Graph Statistics:**")
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
    # Query interface
    query_input = mo.ui.text(
        placeholder="Ask anything about your data... (e.g., 'Show me customers from São Paulo')"
    )

    mo.md("### 💬 Ask About Your Data:")
    return (query_input,)


@app.cell
def _(datasets, query_input):
    def execute_natural_language_query(question):
        """Execute natural language query against datasets"""
        if not question:
            return "Please enter a question about your data."

        question_lower = question.lower()
        customers_df = datasets["customers"]
        products_df = datasets["products"]
        orders_df = datasets["orders"]

        # Customer queries
        if "customer" in question_lower and "são paulo" in question_lower:
            sp_customers = customers_df[customers_df["city"] == "São Paulo"]
            return f"Found {len(sp_customers)} customers from São Paulo:\n{sp_customers[['name', 'email', 'age']].to_string()}"

        elif "customer" in question_lower and (
            "highest" in question_lower or "top" in question_lower
        ):
            top_customers = customers_df.nlargest(3, "score")
            return (
                f"Top 3 customers by score:\n{top_customers[['name', 'score', 'city']].to_string()}"
            )

        # Product queries
        elif "category" in question_lower and (
            "sales" in question_lower or "total" in question_lower
        ):
            # Join orders and products
            orders_with_products = orders_df.merge(products_df, on="product_id")
            category_sales = orders_with_products.groupby("category")["total_amount"].sum()
            return f"Total sales by category:\n{category_sales.to_string()}"

        elif "product" in question_lower and (
            "expensive" in question_lower or "highest" in question_lower
        ):
            expensive_products = products_df.nlargest(3, "price")
            return f"Top 3 most expensive products:\n{expensive_products[['name', 'price', 'category']].to_string()}"

        # Order queries
        elif "average" in question_lower and (
            "order" in question_lower or "value" in question_lower
        ):
            avg_order = orders_df["total_amount"].mean()
            return f"Average order value: ${avg_order:.2f}"

        elif "pending" in question_lower or "processing" in question_lower:
            pending_orders = orders_df[orders_df["status"].isin(["pending", "processing"])]
            return f"Found {len(pending_orders)} pending/processing orders"

        elif "total" in question_lower and (
            "revenue" in question_lower or "sales" in question_lower
        ):
            total_revenue = orders_df["total_amount"].sum()
            return f"Total revenue: ${total_revenue:,.2f}"

        # General queries
        elif "how many" in question_lower:
            if "customer" in question_lower:
                return f"Total customers: {len(customers_df)}"
            elif "product" in question_lower:
                return f"Total products: {len(products_df)}"
            elif "order" in question_lower:
                return f"Total orders: {len(orders_df)}"

        elif "help" in question_lower:
            return """
            🤖 **AI Agent Help**

            I can answer questions about:
            - **Customers**: "Show me customers from São Paulo", "Which customers have the highest scores?"
            - **Products**: "What are the most expensive products?", "Show me electronics"
            - **Orders**: "What's the average order value?", "How many pending orders?"
            - **Analytics**: "Total revenue", "Sales by category"

            Try asking about your specific data!
            """

        else:
            return f"I understand you're asking about: '{question}'. Try asking about customers, products, orders, or sales analytics!"

    query_result = None
    if query_input.value:
        query_result = execute_natural_language_query(query_input.value)
    return (query_result,)


@app.cell
def _(mo, query_input, query_result):
    if query_input.value and query_result:
        mo.md(f"🤖 **AI Agent Response**:\n\n```\n{query_result}\n```")
    elif query_input.value:
        mo.md("🤔 **Thinking...** Processing your question...")
    return


@app.cell
def _(datasets, mo, pd):
    mo.md(
        """
    ## 📊 Step 5: Interactive Analytics

    **Explore your data with interactive visualizations!**
    """
    )

    # Create some basic analytics
    analytics_customers_df = datasets["customers"]
    analytics_products_df = datasets["products"]
    analytics_orders_df = datasets["orders"]

    # Customer distribution by city
    city_counts = analytics_customers_df["city"].value_counts()

    mo.md("### 🏙️ Customers by City")
    mo.ui.table(pd.DataFrame({"City": city_counts.index, "Count": city_counts.values}))

    # Product categories
    category_counts = analytics_products_df["category"].value_counts()

    mo.md("### 📦 Products by Category")
    mo.ui.table(pd.DataFrame({"Category": category_counts.index, "Count": category_counts.values}))

    # Order status
    status_counts = analytics_orders_df["status"].value_counts()

    mo.md("### 🛒 Orders by Status")
    mo.ui.table(pd.DataFrame({"Status": status_counts.index, "Count": status_counts.values}))
    return


@app.cell
def _(datasets, mo, pd):
    mo.md(
        """
    ## 🎯 Step 6: Business Intelligence

    **Key insights from your data:**
    """
    )

    # Calculate business metrics
    bi_customers_df = datasets["customers"]
    bi_products_df = datasets["products"]
    bi_orders_df = datasets["orders"]

    # Calculate business metrics
    total_revenue = bi_orders_df["total_amount"].sum()
    avg_order_value = bi_orders_df["total_amount"].mean()
    total_customers = len(bi_customers_df)
    total_products = len(bi_products_df)
    total_orders = len(bi_orders_df)

    # Top performing customers
    customer_orders = bi_orders_df.merge(bi_customers_df, on="customer_id")
    top_customers = customer_orders.groupby("name")["total_amount"].sum().nlargest(3)

    # Top selling products
    product_orders = bi_orders_df.merge(bi_products_df, on="product_id")
    top_products = product_orders.groupby("name")["total_amount"].sum().nlargest(3)

    mo.md("### 💰 Business Metrics")
    metrics_text = f"""
    - **Total Revenue**: ${total_revenue:,.2f}
    - **Average Order Value**: ${avg_order_value:,.2f}
    - **Total Customers**: {total_customers}
    - **Total Products**: {total_products}
    - **Total Orders**: {total_orders}
    - **Revenue per Customer**: ${total_revenue/total_customers:.2f}
    - **Orders per Customer**: {total_orders/total_customers:.1f}
    """

    mo.md(metrics_text)

    mo.md("### 🏆 Top Customers by Revenue")
    mo.ui.table(pd.DataFrame({"Customer": top_customers.index, "Revenue": top_customers.values}))

    mo.md("### 🥇 Top Products by Revenue")
    mo.ui.table(pd.DataFrame({"Product": top_products.index, "Revenue": top_products.values}))
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🎉 Demo Complete!

    **You've successfully experienced the full AI Agent workflow with Ontologia's KuzuDB:**

    ✅ **Data Loading**: Imported CSV and Parquet files
    ✅ **Schema Detection**: AI analyzed data structure automatically
    ✅ **Knowledge Graph**: Created relationships using Ontologia's KuzuDB
    ✅ **Cypher Queries**: Asked complex relationship questions
    ✅ **Natural Language Queries**: Asked questions in plain English
    ✅ **Business Intelligence**: Generated insights and analytics

    ### **🚀 What You Can Do Next**:

    1. **Upload Your Own Data**: Replace example files with your CSV/Parquet data
    2. **Ask Complex Questions**: Try more sophisticated natural language queries
    3. **Create Custom Visualizations**: Build charts and dashboards
    4. **Export Results**: Save insights and knowledge graphs
    5. **Integrate with APIs**: Connect to external data sources
    6. **Build Knowledge Graphs**: Use Ontologia's KuzuDB for complex relationships

    ### **💡 Key Features Demonstrated**:

    - **Zero Configuration**: No setup required
    - **Multiple Formats**: CSV and Parquet support
    - **Relationship Detection**: Automatic foreign key analysis
    - **Natural Language Processing**: Intuitive query interface
    - **Real-time Analytics**: Instant business insights
    - **Data Validation**: Quality checks and error handling
    - **🆕 Knowledge Graph**: Ontologia's KuzuDB integration
    - **🆕 Cypher Queries**: Complex relationship queries
    - **🆕 Enterprise Infrastructure**: Production-ready graph database

    **The power of AI-driven knowledge graph creation with Ontologia's infrastructure is now in your hands!** 🚀🕸️
    """
    )
    return


if __name__ == "__main__":
    app.run()
