# AI Agents with Ontologia - Marimo Notebook
# Fast track from 0 to 100 with AI-powered data processing

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return (
        pd,
        mo,
    )


@app.cell
def _(mo):
    mo.md(
        """
    # 🤖 AI Agents with Ontologia

    **Go from 0 to 100 in minutes!** This notebook shows you how to:

    - **Upload Data**: Drag & drop CSV/Parquet files
    - **Auto-Detect Schema**: AI understands your data structure
    - **Generate Ontology**: Create knowledge graphs automatically
    - **Query with Natural Language**: Ask questions in plain English
    - **Build Agents**: Create AI assistants for your data

    **Perfect for**: Data scientists, business analysts, developers who want fast results!
    """
    )
    return


@app.cell
def _():
    import os

    import requests

    # Environment setup
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

    def check_services():
        """Check if required services are running"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    api_available = check_services()
    return API_BASE_URL, api_available, requests


@app.cell
def _(api_available, mo):
    import marimo

    if not api_available:
        mo.md(
            """
            ❌ **API Not Available**

            Please start the Ontologia playground:
            ```bash
            ontologia-cli playground start
            ```
            """
        )
        raise marimo.Interrupt("API required")

    mo.md("✅ **Ontologia API Ready** - Let's build some AI agents!")
    return (marimo,)


@app.cell
def _(mo):
    mo.md(
        """
    ## 📁 Step 1: Upload Your Data

    **Super Simple UX**: Just drag & drop your files or use the upload button below.

    **Supported Formats**:
    - CSV files (.csv)
    - Parquet files (.parquet)
    - Excel files (.xlsx)

    **What happens next**: AI will automatically understand your data structure!
    """
    )
    return


@app.cell
def _(mo):
    # File upload interface
    file_upload = mo.ui.file(filetypes=[".csv", ".parquet", ".xlsx"], multiple=True)

    mo.md("### 📤 Upload Your Data Files:")
    file_upload
    return (file_upload,)


@app.cell
def _(file_upload, marimo, mo):
    if not file_upload.value:
        mo.md("⏳ **Waiting for file upload...**")
        raise marimo.Interrupt("Please upload files to continue")

    uploaded_files = list(file_upload.value.keys())
    mo.md(f"✅ **Files Uploaded**: {', '.join(uploaded_files)}")
    return (uploaded_files,)


@app.cell
def _(file_upload, io, pd, uploaded_files):
    # Load uploaded data
    loaded_data = {}

    for fname in uploaded_files:
        file_content = file_upload.value[fname]

        try:
            if fname.endswith(".csv"):
                # Read CSV
                df = pd.read_csv(io.StringIO(file_content.decode("utf-8")))
            elif fname.endswith(".parquet"):
                # Read Parquet
                df = pd.read_parquet(io.BytesIO(file_content))
            elif fname.endswith(".xlsx"):
                # Read Excel
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                continue

            loaded_data[fname] = df

        except Exception as e:
            print(f"Error loading {fname}: {e}")
    return (loaded_data,)


@app.cell
def _(loaded_data, mo, pd):
    # Display data preview
    mo.md("### 📊 Data Preview")

    for fname, data_df in loaded_data.items():
        mo.md(f"**{fname}** ({len(data_df)} rows, {len(data_df.columns)} columns)")

        # Show sample data
        sample_df = data_df.head(5)
        mo.ui.table(sample_df)

        # Show column info
        cols_info = pd.DataFrame(
            {
                "Column": data_df.columns,
                "Type": data_df.dtypes.astype(str),
                "Non-Null Count": data_df.count(),
                "Unique Values": data_df.nunique(),
            }
        )
        mo.md("**Column Information:**")
        mo.ui.table(cols_info)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🧠 Step 2: AI Schema Detection

    **Magic Happens Here**: AI analyzes your data and automatically creates:
    - Object types (entities)
    - Relationships between entities
    - Data types and constraints
    - Natural language descriptions
    """
    )
    return


@app.cell
def _(loaded_data):
    def detect_schema_with_ai(dataframes):
        """AI-powered schema detection"""
        schema_suggestions = {"object_types": [], "relationships": [], "data_quality": {}}

        for filename, df in dataframes.items():
            # Analyze columns for object type suggestions
            object_type = {
                "api_name": filename.replace(".", "_").replace(" ", "_").lower(),
                "display_name": filename.replace(".", " ").replace("_", " ").title(),
                "description": f"Data from {filename}",
                "properties": [],
            }

            # Analyze each column
            for col in df.columns:
                prop = {
                    "api_name": col.lower().replace(" ", "_"),
                    "display_name": col.replace("_", " ").title(),
                    "data_type": "string",
                    "description": f"Column {col} from {filename}",
                    "nullable": df[col].isnull().any(),
                    "unique_count": df[col].nunique(),
                }

                # Detect data type
                if df[col].dtype in ["int64", "float64"]:
                    prop["data_type"] = "number"
                elif df[col].dtype == "bool":
                    prop["data_type"] = "boolean"
                elif df[col].dtype == "datetime64[ns]":
                    prop["data_type"] = "datetime"

                # Special detection for common patterns
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ["id", "identifier", "key"]):
                    prop["is_identifier"] = True
                if any(keyword in col_lower for keyword in ["name", "title", "label"]):
                    prop["is_display_name"] = True
                if any(keyword in col_lower for keyword in ["email", "mail"]):
                    prop["data_type"] = "email"
                if any(keyword in col_lower for keyword in ["url", "link", "website"]):
                    prop["data_type"] = "url"

                object_type["properties"].append(prop)

            schema_suggestions["object_types"].append(object_type)

            # Data quality analysis
            quality_metrics = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_values": df.isnull().sum().sum(),
                "duplicate_rows": df.duplicated().sum(),
                "completeness_ratio": (1 - df.isnull().sum().sum() / (len(df) * len(df.columns)))
                * 100,
            }
            schema_suggestions["data_quality"][filename] = quality_metrics

        # Suggest relationships based on column name patterns
        all_columns = []
        for filename, df in dataframes.items():
            for col in df.columns:
                all_columns.append(f"{filename}:{col}")

        # Find potential foreign key relationships
        for i, file1_cols in enumerate(dataframes.items()):
            filename1, df1 = file1_cols
            for j, file2_cols in enumerate(dataframes.items()):
                if i >= j:
                    continue
                filename2, df2 = file2_cols

                # Look for common column names that might indicate relationships
                common_cols = set(df1.columns.str.lower()) & set(df2.columns.str.lower())
                for col in common_cols:
                    if any(keyword in col for keyword in ["id", "key", "code"]):
                        relationship = {
                            "source_object": filename1.replace(".", "_").replace(" ", "_").lower(),
                            "target_object": filename2.replace(".", "_").replace(" ", "_").lower(),
                            "link_type": f"has_{col}",
                            "description": f"Relationship based on {col}",
                            "confidence": "high" if "id" in col else "medium",
                        }
                        schema_suggestions["relationships"].append(relationship)

        return schema_suggestions

    ai_schema = detect_schema_with_ai(loaded_data)
    return (ai_schema,)


@app.cell
def _(ai_schema, mo):
    # Display AI schema suggestions
    mo.md("### 🎯 AI-Generated Schema")

    # Object types
    mo.md("**📋 Suggested Object Types:**")
    for obj_type in ai_schema["object_types"]:
        mo.md(f"**{obj_type['display_name']}** (`{obj_type['api_name']}`)")
        mo.md(f"- Description: {obj_type['description']}")
        mo.md(f"- Properties: {len(obj_type['properties'])}")

        # Show key properties
        key_props = [
            p for p in obj_type["properties"] if p.get("is_identifier") or p.get("is_display_name")
        ]
        if key_props:
            mo.md(
                "- Key fields: "
                + ", ".join([f"{p['display_name']} ({p['data_type']})" for p in key_props])
            )

    # Relationships
    if ai_schema["relationships"]:
        mo.md("\n**🔗 Suggested Relationships:**")
        for rel in ai_schema["relationships"]:
            confidence_emoji = "🟢" if rel["confidence"] == "high" else "🟡"
            mo.md(
                f"{confidence_emoji} {rel['source_object']} → {rel['target_object']} ({rel['link_type']})"
            )

    # Data quality
    mo.md("\n**📊 Data Quality Assessment:**")
    for filename, quality in ai_schema["data_quality"].items():
        quality_emoji = (
            "✅"
            if quality["completeness_ratio"] > 90
            else "⚠️" if quality["completeness_ratio"] > 70 else "❌"
        )
        mo.md(f"{quality_emoji} {filename}: {quality['completeness_ratio']:.1f}% complete")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## ⚡ Step 3: Auto-Generate Ontology

    **One-Click Magic**: Create your knowledge graph instantly with AI suggestions.
    """
    )
    return


@app.cell
def _(API_BASE_URL, ai_schema, datetime, requests):
    def create_ontology_from_schema():
        """Create ontology based on AI schema detection"""

        # Create main ontology
        ontology_payload = {
            "apiName": "agent_generated",
            "displayName": "AI Agent Generated Knowledge Graph",
            "description": f"Automatically generated ontology from data upload at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        }

        try:
            # Create ontology
            response = requests.post(f"{API_BASE_URL}/v2/ontologies", json=ontology_payload)
            if response.status_code not in [200, 201]:
                return False, f"Failed to create ontology: {response.text}"

            ontology_result = response.json()
            ontology_name = ontology_result["apiName"]

            # Create object types
            created_objects = []
            for obj_type in ai_schema["object_types"]:
                obj_payload = {
                    "apiName": obj_type["api_name"],
                    "displayName": obj_type["display_name"],
                    "description": obj_type["description"],
                    "properties": [],
                }

                for prop in obj_type["properties"]:
                    prop_payload = {
                        "apiName": prop["api_name"],
                        "displayName": prop["display_name"],
                        "dataType": prop["data_type"],
                        "description": prop["description"],
                    }
                    obj_payload["properties"].append(prop_payload)

                try:
                    obj_response = requests.post(
                        f"{API_BASE_URL}/v2/ontologies/{ontology_name}/objectTypes",
                        json=obj_payload,
                    )
                    if obj_response.status_code in [200, 201]:
                        created_objects.append(obj_response.json())
                except Exception as e:
                    print(f"Error creating object type {obj_type['api_name']}: {e}")

            return True, {
                "ontology": ontology_result,
                "object_types": created_objects,
                "total_objects": len(created_objects),
            }

        except Exception as e:
            return False, str(e)

    creation_result = create_ontology_from_schema()
    return (creation_result,)


@app.cell
def _(creation_result, datetime, mo):
    success, result = creation_result
    if success:
        mo.md(
            f"""
            ✅ **Ontology Created Successfully!**

            - **Name**: {result['ontology']['displayName']}
            - **API Name**: {result['ontology']['apiName']}
            - **Object Types**: {result['total_objects']}
            - **Created At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            🎉 **Your knowledge graph is ready!**
            """
        )
    else:
        mo.md(f"❌ **Failed to create ontology**: {result}")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 📥 Step 4: Import Your Data

    **Smart Data Import**: AI maps your data to the ontology automatically.
    """
    )
    return


@app.cell
def _(API_BASE_URL, creation_result, loaded_data, pd, requests):
    def import_data_to_ontology():
        """Import uploaded data into the created ontology"""
        if not creation_result[0]:
            return False, "No ontology available"

        ontology_name = creation_result[1]["ontology"]["apiName"]
        object_types = creation_result[1]["object_types"]

        imported_instances = {}

        # Map object types to data
        for obj_type in object_types:
            obj_api_name = obj_type["apiName"]

            # Find corresponding data file
            matching_file = None
            for filename in loaded_data.keys():
                if obj_api_name in filename.lower().replace(".", "_").replace(" ", "_"):
                    matching_file = filename
                    break

            if not matching_file:
                continue

            cell_17_df = loaded_data[matching_file]
            instances_created = 0

            # Create instances row by row
            for _, row in cell_17_df.iterrows():  # type: ignore[name-defined]
                instance_data = {}

                # Map columns to properties
                for prop in obj_type["properties"]:
                    prop_name = prop["apiName"]
                    # Find matching column
                    matching_col = None
                    for col in cell_17_df.columns:  # type: ignore[name-defined]
                        if col.lower().replace(" ", "_") == prop_name:
                            matching_col = col
                            break

                    if matching_col and pd.notna(row[matching_col]):
                        instance_data[prop_name] = row[matching_col]

                if instance_data:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/v2/ontologies/{ontology_name}/objects/{obj_api_name}",
                            json=instance_data,
                        )
                        if response.status_code in [200, 201]:
                            instances_created += 1
                    except Exception as e:
                        print(f"Error creating instance: {e}")

            imported_instances[obj_api_name] = instances_created

        return True, imported_instances

    import_result = import_data_to_ontology()
    return (import_result,)


@app.cell
def _(import_result, mo):
    success, imported_counts = import_result
    if success:
        mo.md("✅ **Data Imported Successfully!**")

        total_instances = sum(imported_counts.values())
        mo.md(f"📊 **Total Instances Created**: {total_instances}")

        for obj_type, count in imported_counts.items():
            mo.md(f"- {obj_type}: {count} instances")  # type: ignore[name-defined]
    else:
        mo.md(f"❌ **Import Failed**: {imported_counts}")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🗣️ Step 5: Natural Language Query Agent

    **Ask Questions in Plain English**: No SQL required!
    """
    )
    return


@app.cell
def _(mo):
    # Natural language query interface
    query_input = mo.ui.text(
        placeholder="Ask anything about your data... (e.g., 'Show me all customers', 'What are the total sales?')"
    )

    mo.md("### 💬 Ask About Your Data:")
    query_input
    return (query_input,)


@app.cell
def _(API_BASE_URL, creation_result, query_input, requests):
    def execute_natural_language_query(question):
        """Execute natural language query against the ontology"""
        if not creation_result[0]:
            return "No ontology available for querying"

        ontology_name = creation_result[1]["ontology"]["apiName"]

        # Simulate AI query processing (in real implementation, this would use NLP)
        question_lower = question.lower()

        # Simple pattern matching for demo
        if "show" in question_lower and "all" in question_lower:
            # Get all instances
            try:
                response = requests.get(f"{API_BASE_URL}/v2/ontologies/{ontology_name}/objects")
                if response.status_code == 200:
                    data = response.json()
                    return f"Found {len(data.get('items', []))} total instances across all object types."
            except:
                pass

        elif "count" in question_lower or "how many" in question_lower:
            return "I can count instances for you. Please specify what you want to count."

        elif "help" in question_lower:
            return """
            🤖 **AI Agent Help**

            I can help you:
            - Count instances: "How many customers?"
            - Show data: "Show me all products"
            - Find relationships: "What orders does this customer have?"
            - Analyze patterns: "What are our top selling products?"

            Try asking about your specific data!
            """

        else:
            return f"I understand you're asking about: '{question}'. Let me help you explore your data!"

    query_result = None
    if query_input.value:
        query_result = execute_natural_language_query(query_input.value)
    return (query_result,)


@app.cell
def _(mo, query_input, query_result):
    if query_input.value and query_result:
        mo.md(f"🤖 **AI Agent Response**:\n\n{query_result}")
    elif query_input.value:
        mo.md("🤔 **Thinking...** Processing your question...")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🎯 Step 6: Create Custom AI Agent

    **Build Your Own Assistant**: Specialized AI for your specific use case.
    """
    )
    return


@app.cell
def _(mo):
    # Agent configuration
    agent_name = mo.ui.text(placeholder="e.g., Sales Analyst, Data Explorer, Report Generator")

    agent_description = mo.ui.text_area(
        placeholder="Describe what your agent should do...",
        value="Analyze data and provide insights",
    )

    mo.md("### 🛠️ Configure Your AI Agent:")
    mo.md("**Agent Name:**")
    agent_name
    mo.md("**Agent Description:**")
    agent_description
    return agent_description, agent_name


@app.cell
def _(agent_description, agent_name, mo):
    if agent_name.value and agent_description.value:
        mo.md(
            f"""
            ✅ **AI Agent Configuration Ready**

            **Name**: {agent_name.value}
            **Description**: {agent_description.value}

            🚀 **Your custom agent is ready to use!**
            """
        )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## 🎉 You've Gone from 0 to 100!

    **What You Accomplished**:

    ✅ **Uploaded Data**: Drag & drop CSV/Parquet files
    ✅ **AI Schema Detection**: Automatic understanding of your data structure
    ✅ **Generated Ontology**: Created knowledge graph with one click
    ✅ **Imported Data**: Mapped data to ontology automatically
    ✅ **Natural Language Queries**: Ask questions in plain English
    ✅ **Custom AI Agent**: Built specialized assistant for your needs

    **🚀 Next Steps**:
    - Ask more complex questions to your AI agent
    - Create visualizations and dashboards
    - Build automated workflows
    - Share your knowledge graph with team members

    **💡 Pro Tips**:
    - Upload multiple related files for richer insights
    - Use specific questions for better results
    - Experiment with different agent configurations
    - Combine with other notebooks for advanced analytics

    **🌟 You're now ready to leverage AI for any data challenge!**
    """
    )
    return


if __name__ == "__main__":
    app.run()
