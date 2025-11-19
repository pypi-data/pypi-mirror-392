# 🚀 Ontologia Introduction - Marimo Notebook
# Explore the Ontologia platform with reactive notebooks

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
        # 🚀 Welcome to Ontologia!

        **The next-generation knowledge graph platform** that transforms your data into intelligent insights.

        ## 🎯 What You'll Learn:

        - **📊 Data Integration**: Connect CSV, Parquet, and databases
        - **🧠 AI-Powered Schema**: Automatic ontology generation
        - **🔗 Knowledge Graphs**: Create relationships between entities
        - **🗣️ Natural Language**: Query data in plain English
        - **🤖 AI Agents**: Build intelligent data assistants

        ## 🛠️ Technologies Used:

        - **Marimo**: Reactive notebooks for interactive development
        - **FastAPI**: High-performance API backend
        - **PostgreSQL**: Reliable data storage
        - **Redis**: Real-time caching and updates
        - **Temporal**: Workflow orchestration
        - **DuckDB**: Analytics database
        - **Elasticsearch**: Full-text search

        **Let's start building knowledge from data!** 🚀
        """
    )
    return


@app.cell
def _(mo):
    import json
    import os
    from datetime import datetime

    import pandas as pd
    import requests

    # Environment setup
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    def check_api_health():
        """Check if Ontologia API is available"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    api_available = check_api_health()
    return API_BASE_URL, api_available, check_api_health, datetime, json, os, pd, requests


@app.cell
def _(api_available, mo):
    if not api_available:
        mo.md(
            """
            ❌ **API Not Available**

            Please start the Ontologia playground:
            ```bash
            ontologia-cli playground start
            ```

            Or use the standalone notebooks that work without API!
            """
        )
    else:
        mo.md("✅ **Ontologia API Ready** - Let's explore the platform!")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🏗️ Platform Architecture

        ### **Core Components**:

        1. **API Layer**: RESTful endpoints for data operations
        2. **Domain Layer**: Business logic and entity management
        3. **Infrastructure Layer**: Databases and external services
        4. **Application Layer**: Use cases and workflows

        ### **Data Flow**:

        ```
        Raw Data → AI Processing → Knowledge Graph → Natural Language Queries
        ```

        ### **Key Features**:

        - **🔄 Real-time Updates**: Live data synchronization
        - **🔍 Smart Search**: Full-text and semantic search
        - **📈 Analytics**: Built-in business intelligence
        - **🛡️ Type Safety**: Full type annotations with Pydantic
        - **⚡ High Performance**: Optimized for large datasets
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎯 Getting Started Checklist

        ### **✅ Prerequisites**:
        - [ ] Python 3.11+ installed
        - [ ] Docker for containerized services
        - [ ] Git for version control

        ### **✅ Setup Complete**:
        - [ ] Ontologia playground running
        - [ ] Example datasets loaded
        - [ ] Marimo notebooks accessible

        ### **🚀 Next Steps**:
        1. **Try the examples**: Upload CSV/Parquet files
        2. **Create ontologies**: Let AI detect your schema
        3. **Query naturally**: Ask questions in plain English
        4. **Build agents**: Create custom AI assistants

        **Ready to transform your data into knowledge?** Let's go! 🎯
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 📚 Available Notebooks

        ### **🔰 Beginner**:
        - `00_data_examples.py` - Validate example datasets
        - `01_introduction.py` - Platform overview (this notebook)

        ### **🚀 Intermediate**:
        - `02_graph_traversals.py` - Explore knowledge graphs
        - `03_analytics.py` - Data analysis and visualization

        ### **🤖 Advanced**:
        - `04_workflows.py` - Automation with Temporal
        - `05_agents.py` - AI-powered data processing

        ### **🎯 Standalone** (No API required):
        - `demo_standalone.py` - Complete working demo
        - `05_agents_standalone.py` - AI agents without API

        **Choose your adventure and start building!** 🚀
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎉 Congratulations!

        You've successfully set up the Ontologia development environment!

        ### **🏆 What You've Accomplished**:
        - ✅ Environment configured
        - ✅ Services running
        - ✅ Notebooks accessible
        - ✅ Example data ready

        ### **🌟 What's Next**:
        - Explore the other notebooks
        - Upload your own data
        - Create custom ontologies
        - Build AI agents

        **The future of knowledge management is in your hands!** 🚀

        ---

        **Need help?** Check the documentation or ask the AI assistant in any notebook!
        """
    )
    return


if __name__ == "__main__":
    app.run()
