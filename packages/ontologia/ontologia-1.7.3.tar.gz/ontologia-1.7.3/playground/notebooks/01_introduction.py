# 01 Introduction - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


# Ontologia Introduction - Marimo Notebook
# Explore the Ontologia platform with reactive notebooks

import os
from datetime import datetime

import marimo
import pandas as pd
import requests

# Initialize Marimo app
app = marimo.App()


@app.cell
def _(mo):
    # Title and introduction
    mo.md(
        """
        # 🚀 Ontologia Introduction

        Welcome to the Ontologia platform! This interactive notebook will help you explore:

        - **API Connection**: Test your connection to the Ontologia API
        - **Data Models**: Explore ontologies, object types, and instances
        - **Graph Queries**: Try basic graph traversals
        - **Analytics**: Run analytics with DuckDB

        Let's start by checking your connection status!
        """
    )
    return


@app.cell
def _(mo):
    # Connection status check
    mo.md(
        """
        ## 🔗 Connection Status

        Testing connection to Ontologia API...
        """
    )
    return


@app.cell
def _(
    mo,
):
    import requests

    # API configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    def check_api_health():
        """Check if the Ontologia API is running"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Status code: {response.status_code}"
        except Exception as e:
            return False, str(e)

    # Test connection
    is_healthy, health_info = check_api_health()

    return API_BASE_URL, check_api_health, health_info, is_healthy


@app.cell
def _(mo, health_info, is_healthy):
    # Display connection status
    if is_healthy:
        mo.md(
            f"""
            ✅ **API Connected Successfully!**

            - **URL**: {health_info.get('url', 'Unknown')}
            - **Status**: {health_info.get('status', 'Unknown')}
            - **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        )
    else:
        mo.md(
            f"""
            ❌ **API Connection Failed**

            **Error**: {health_info}

            **Troubleshooting**:
            1. Make sure the playground is running: `docker-compose up -d`
            2. Check API status: `docker-compose logs api`
            3. Verify port 8000 is available
            """
        )
    return


@app.cell
def _(mo, is_healthy):
    # Only proceed if API is healthy
    if not is_healthy:
        mo.md("⚠️ Please fix the API connection before proceeding.")
        raise marimo.Interrupt("API connection required")

    mo.md(
        """
        ## 📊 Exploring Ontologies

        Let's explore the available ontologies and their structure.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def get_ontologies():
        """Get list of available ontologies"""
        try:
            response = requests.get(f"{API_BASE_URL}/v2/ontologies")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch ontologies: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    ontologies_data = get_ontologies()
    return get_ontologies, ontologies_data


@app.cell
def _(mo, ontologies_data):
    # Display ontologies
    if "error" in ontologies_data:
        mo.md(f"❌ Error fetching ontologies: {ontologies_data['error']}")
    else:
        ontologies = ontologies_data.get("items", [])
        if ontologies:
            # Create a table of ontologies
            ontology_cell_8_df = pd.DataFrame(
                [
                    {
                        "Name": ont.get("apiName", "Unknown"),
                        "Display Name": ont.get("displayName", "Unknown"),
                        "Description": ont.get("description", "No description"),
                        "Object Types": len(ont.get("objectTypes", [])),
                        "Link Types": len(ont.get("linkTypes", [])),
                    }
                    for ont in ontologies
                ]
            )

            mo.md("### Available Ontologies:")
            mo.ui.table(ontology_cell_8_df)  # type: ignore[name-defined]
        else:
            mo.md("No ontologies found. Let's create a sample one!")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🏗️ Creating a Sample Ontology

        Let's create a simple knowledge graph about companies and employees.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def create_sample_ontology():
        """Create a sample ontology for demonstration"""
        ontology_payload = {
            "apiName": "company",
            "displayName": "Company Knowledge Graph",
            "description": "A simple ontology for managing company and employee information",
        }

        try:
            response = requests.post(f"{API_BASE_URL}/v2/ontologies", json=ontology_payload)
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)

    # Create the ontology
    success, result = create_sample_ontology()
    return create_sample_ontology, result, success


@app.cell
def _(mo, result, success):
    if success:
        mo.md(
            f"""
            ✅ **Sample Ontology Created!**

            - **API Name**: {result.get('apiName', 'Unknown')}
            - **Display Name**: {result.get('displayName', 'Unknown')}
            - **ID**: {result.get('id', 'Unknown')}
            """
        )
    else:
        mo.md(f"❌ Error creating ontology: {result}")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎯 What's Next?

        Now that you have a basic understanding of the Ontologia platform:

        1. **Explore Graph Traversals**: Check out `02_graph_traversals.py`
        2. **Try Analytics**: See `03_analytics.py` for DuckDB examples
        3. **Build Workflows**: Learn about Temporal in `04_workflows.py`
        4. **API Documentation**: Visit http://localhost:8000/docs

        **Tips for using Marimo**:
        - Cells run automatically when you change them
        - Use the sidebar to navigate between notebooks
        - Export your work as Python scripts or HTML
        - All notebooks are version-controlled as `.py` files
        """
    )
    return


if __name__ == "__main__":
    app.run()
