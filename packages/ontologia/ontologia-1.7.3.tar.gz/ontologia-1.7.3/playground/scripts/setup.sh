#!/bin/bash
# Ontologia Playground Setup Script
# Sets up the complete development environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME=${PROJECT_NAME:-ontologia-playground}
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-ontologia-playground}

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    log_info "Checking Docker installation..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Docker and Docker Compose are ready"
}

# Check system resources
check_resources() {
    log_info "Checking system resources..."

    # Check available memory
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        TOTAL_MEM=$(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024}')
    else
        # Linux
        TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    fi

    if (( $(echo "$TOTAL_MEM < 8" | bc -l) )); then
        log_warning "System has less than 8GB of RAM. Some services may be slow."
        log_warning "Consider increasing memory allocation in Docker Desktop."
    else
        log_success "System has sufficient memory (${TOTAL_MEM}GB)"
    fi

    # Check available disk space
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if (( AVAILABLE_SPACE < 10 )); then
        log_warning "Less than 10GB of disk space available. Consider freeing up space."
    else
        log_success "Sufficient disk space available (${AVAILABLE_SPACE}GB)"
    fi
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."

    if [[ ! -f .env ]]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_success "Environment file created from template"
        log_warning "Please review and customize .env file as needed"
    else
        log_info "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    directories=(
        "data/postgres"
        "data/elasticsearch"
        "data/redis"
        "data/kuzu"
        "data/duckdb"
        "data/rabbitmq"
        "logs"
        "notebooks"
        "examples"
        "workflows"
        "search"
        "realtime"
        "dagster"
        "analytics"
        "dashboards"
        "monitoring/grafana/dashboards"
        "monitoring/grafana/provisioning"
        "monitoring/prometheus"
        "temporal/config"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done

    log_success "All necessary directories created"
}

# Setup monitoring configuration
setup_monitoring() {
    log_info "Setting up monitoring configuration..."

    # Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'ontologia-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']

  - job_name: 'temporal'
    static_configs:
      - targets: ['temporal:7233']

  - job_name: 'dagster'
    static_configs:
      - targets: ['dagster-webserver:3000']
EOF

    # Grafana provisioning
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log_success "Monitoring configuration created"
}

# Setup Jupyter notebooks
setup_notebooks() {
    log_info "Setting up Jupyter notebooks..."

    # Create basic notebooks
    cat > notebooks/01_introduction.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Ontologia Playground - Introduction\n",
    "\n",
    "Welcome to the Ontologia Playground! This notebook will help you get started with the platform.\n",
    "\n",
    "## What is Ontologia?\n",
    "\n",
    "Ontologia is a powerful platform for building knowledge graphs and data applications with:\n",
    "- **Graph Database** (KùzuDB) for complex relationships\n",
    "- **Search Engine** (Elasticsearch) for full-text search\n",
    "- **Workflow Engine** (Temporal) for process automation\n",
    "- **Data Pipelines** (Dagster) for analytics\n",
    "- **Real-time Updates** (Redis) for live data\n",
    "\n",
    "## Setup\n",
    "\n",
    "Let's start by connecting to the Ontologia API."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Install required packages\n",
    "!pip install ontologia-sdk pandas plotly networkx"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import ontologia_sdk\n",
    "import pandas as pd\n",
    "import networkx as nx\n",
    "import plotly.express as px\n",
    "from datetime import datetime\n",
    "\n",
    "# Connect to Ontologia API\n",
    "client = ontologia_sdk.OntologyClient(\n",
    "    host=\"http://localhost:8000\",\n",
    "    ontology=\"default\"\n",
    ")\n",
    "\n",
    "print(\"✅ Connected to Ontologia API\")\n",
    "print(f\"API Version: {client.get_version()}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Basic Operations\n",
    "\n",
    "Let's explore some basic operations with the Ontologia API."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# List available object types\n",
    "object_types = client.list_object_types()\n",
    "print(\"Available Object Types:\")\n",
    "for obj_type in object_types:\n",
    "    print(f\"  - {obj_type['displayName']} ({obj_type['name']})\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a simple object type\n",
    "person_type = {\n",
    "    \"displayName\": \"Person\",\n",
    "    \"primaryKey\": \"id\",\n",
    "    \"properties\": {\n",
    "        \"id\": {\"dataType\": \"string\", \"required\": True},\n",
    "        \"name\": {\"dataType\": \"string\", \"required\": False},\n",
    "        \"email\": {\"dataType\": \"string\", \"required\": False},\n",
    "        \"age\": {\"dataType\": \"integer\", \"required\": False}\n",
    "    },\n",
    "    \"implements\": []\n",
    "}\n",
    "\n",
    "try:\n",
    "    client.create_object_type(\"person\", person_type)\n",
    "    print(\"✅ Created Person object type\")\n",
    "except Exception as e:\n",
    "    print(f\"Person type might already exist: {e}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create some sample people\n",
    "people = [\n",
    "    {\"id\": \"person1\", \"name\": \"Alice\", \"email\": \"alice@example.com\", \"age\": 30},\n",
    "    {\"id\": \"person2\", \"name\": \"Bob\", \"email\": \"bob@example.com\", \"age\": 25},\n",
    "    {\"id\": \"person3\", \"name\": \"Carol\", \"email\": \"carol@example.com\", \"age\": 35}\n",
    "]\n",
    "\n",
    "for person in people:\n",
    "    try:\n",
    "        client.create_object(\"person\", person[\"id\"], {\"properties\": person})\n",
    "        print(f\"✅ Created {person['name']}\")\n",
    "    except Exception as e:\n",
    "        print(f\"Person might already exist: {e}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Search for people\n",
    "search_results = client.search_objects(\"person\")\n",
    "print(f\"Found {len(search_results.data)} people:\")\n",
    "\n",
    "df = pd.DataFrame([person['properties'] for person in search_results.data])\n",
    "print(df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Next Steps\n",
    "\n",
    "Congratulations! You've completed the introduction to Ontologia.\n",
    "\n",
    "### What's Next?\n",
    "1. **Graph Traversals**: Check out `02_graph_traversals.ipynb`\n",
    "2. **Analytics**: Explore `03_analytics.ipynb`\n",
    "3. **Workflows**: Learn about `04_workflows.ipynb`\n",
    "4. **API Documentation**: Visit http://localhost:8000/docs\n",
    "5. **Dashboards**: Check out http://localhost:8501\n",
    "\n",
    "### Available Services\n",
    "- **API**: http://localhost:8000/docs\n",
    "- **Jupyter**: http://localhost:8888\n",
    "- **Temporal UI**: http://localhost:7233\n",
    "- **Dagster UI**: http://localhost:3000\n",
    "- **Kibana**: http://localhost:5601\n",
    "- **Grafana**: http://localhost:3001\n",
    "\n",
    "Happy coding with Ontologia! 🚀"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

    log_success "Jupyter notebooks created"
}

# Setup example files
setup_examples() {
    log_info "Setting up example files..."

    # Create basic CRUD example
    cat > examples/basic_crud.py << 'EOF'
#!/usr/bin/env python3
"""
Basic CRUD Operations Example

This example demonstrates basic Create, Read, Update, Delete operations
with the Ontologia API.
"""

import ontologia_sdk
import json
from datetime import datetime

def main():
    """Demonstrate basic CRUD operations."""

    # Connect to Ontologia API
    client = ontologia_sdk.OntologyClient(
        host="http://localhost:8000",
        ontology="default"
    )

    print("🚀 Ontologia Basic CRUD Example")
    print("=" * 40)

    # 1. Create object type
    print("\n1. Creating object type...")
    task_type = {
        "displayName": "Task",
        "primaryKey": "id",
        "properties": {
            "id": {"dataType": "string", "required": True},
            "title": {"dataType": "string", "required": False},
            "description": {"dataType": "string", "required": False},
            "status": {"dataType": "string", "required": False},
            "priority": {"dataType": "integer", "required": False},
            "created_at": {"dataType": "datetime", "required": False}
        },
        "implements": []
    }

    try:
        client.create_object_type("task", task_type)
        print("✅ Created Task object type")
    except Exception as e:
        print(f"Task type might already exist: {e}")

    # 2. Create objects
    print("\n2. Creating tasks...")
    tasks = [
        {
            "id": "task1",
            "title": "Setup Ontologia",
            "description": "Install and configure Ontologia playground",
            "status": "completed",
            "priority": 1,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "task2",
            "title": "Learn Graph Traversals",
            "description": "Study KùzuDB graph traversal patterns",
            "status": "in_progress",
            "priority": 2,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "task3",
            "title": "Build Analytics Pipeline",
            "description": "Create data pipeline with Dagster",
            "status": "pending",
            "priority": 3,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    for task in tasks:
        try:
            client.create_object("task", task["id"], {"properties": task})
            print(f"✅ Created task: {task['title']}")
        except Exception as e:
            print(f"Task might already exist: {e}")

    # 3. Read objects
    print("\n3. Reading tasks...")
    all_tasks = client.search_objects("task")
    print(f"Found {len(all_tasks.data)} tasks:")

    for task in all_tasks.data:
        props = task["properties"]
        print(f"  - {props['title']} ({props['status']}) - Priority: {props['priority']}")

    # 4. Update object
    print("\n4. Updating task...")
    try:
        update_data = {
            "status": "completed",
            "description": "Study KùzuDB graph traversal patterns - COMPLETED!"
        }
        client.update_object("task", "task2", {"properties": update_data})
        print("✅ Updated task2 status to completed")
    except Exception as e:
        print(f"Error updating task: {e}")

    # 5. Search with filters
    print("\n5. Searching tasks...")
    completed_tasks = client.search_objects("task", where=[
        {"property": "status", "op": "eq", "value": "completed"}
    ])

    print(f"Completed tasks ({len(completed_tasks.data)}):")
    for task in completed_tasks.data:
        print(f"  - {task['properties']['title']}")

    # 6. Delete object
    print("\n6. Deleting task...")
    try:
        client.delete_object("task", "task3")
        print("✅ Deleted task3")
    except Exception as e:
        print(f"Error deleting task: {e}")

    # 7. Verify deletion
    print("\n7. Verifying deletion...")
    remaining_tasks = client.search_objects("task")
    print(f"Remaining tasks: {len(remaining_tasks.data)}")

    print("\n🎉 Basic CRUD example completed!")

if __name__ == "__main__":
    main()
EOF

    log_success "Example files created"
}

# Setup dashboard
setup_dashboard() {
    log_info "Setting up Streamlit dashboard..."

    cat > dashboards/playground.py << 'EOF'
import streamlit as st
import ontologia_sdk
import pandas as pd
import plotly.express as px
import networkx as nx
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Ontologia Playground Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 Ontologia Playground Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎛️ Controls")
st.sidebar.markdown("Connect to Ontologia API and explore your data.")

# API Connection
def connect_to_api():
    """Connect to Ontologia API."""
    try:
        client = ontologia_sdk.OntologyClient(
            host="http://localhost:8000",
            ontology="default"
        )
        # Test connection
        client.get_version()
        return client
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        return None

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Object Types", "0")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🔗 Links", "0")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🔍 Searches", "0")
    st.markdown('</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Explorer", "📈 Analytics", "⚙️ Settings"])

with tab1:
    st.markdown("### 🎯 Welcome to Ontologia Playground")

    st.markdown("""
    This dashboard provides a comprehensive view of your Ontologia instance.

    **Features Available:**
    - 📊 **Data Overview**: See statistics about your ontology
    - 🔍 **Data Explorer**: Browse and search your data
    - 📈 **Analytics**: Visualize relationships and patterns
    - ⚙️ **Settings**: Configure dashboard options

    **Available Services:**
    - **API**: http://localhost:8000/docs
    - **Jupyter**: http://localhost:8888
    - **Temporal UI**: http://localhost:7233
    - **Dagster UI**: http://localhost:3000
    - **Kibana**: http://localhost:5601
    - **Grafana**: http://localhost:3001
    """)

    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()

with tab2:
    st.markdown("### 🔍 Data Explorer")

    # Object type selector
    object_types = ["person", "task", "project"]  # This would be dynamic
    selected_type = st.selectbox("Select Object Type:", object_types)

    if selected_type:
        st.markdown(f"#### Exploring {selected_type.title()} Objects")

        # Search input
        search_term = st.text_input("Search:", placeholder="Enter search term...")

        if st.button("🔍 Search"):
            if search_term:
                st.info(f"Searching for '{search_term}' in {selected_type}...")
            else:
                st.info(f"Loading all {selected_type} objects...")

        # Results table (placeholder)
        if search_term or True:
            # Sample data
            sample_data = pd.DataFrame({
                'ID': ['item1', 'item2', 'item3'],
                'Name': ['Sample Item 1', 'Sample Item 2', 'Sample Item 3'],
                'Created': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'Status': ['Active', 'Pending', 'Completed']
            })
            st.dataframe(sample_data, use_container_width=True)

with tab3:
    st.markdown("### 📈 Analytics")

    # Chart selector
    chart_type = st.selectbox("Select Chart Type:", ["Bar Chart", "Line Chart", "Pie Chart", "Network Graph"])

    if chart_type == "Bar Chart":
        st.markdown("#### Object Types Distribution")
        # Sample bar chart
        fig = px.bar(
            x=["Person", "Task", "Project"],
            y=[10, 25, 5],
            labels={'x': 'Object Type', 'y': 'Count'},
            title="Objects by Type"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Network Graph":
        st.markdown("#### Relationship Network")
        st.info("Network visualization coming soon! This will show the graph structure of your data.")

    else:
        st.info(f"{chart_type} visualization coming soon!")

with tab4:
    st.markdown("### ⚙️ Dashboard Settings")

    st.markdown("#### Configuration")

    # API Settings
    st.markdown("**API Configuration**")
    api_host = st.text_input("API Host:", value="http://localhost:8000")
    ontology_name = st.text_input("Ontology Name:", value="default")

    # Display Settings
    st.markdown("**Display Settings**")
    items_per_page = st.slider("Items per page:", min_value=10, max_value=100, value=25)
    auto_refresh = st.checkbox("Auto Refresh", value=False)

    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds):", min_value=5, max_value=300, value=30)

    st.markdown("---")

    if st.button("💾 Save Settings", type="secondary"):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🚀 Ontologia Playground Dashboard | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True
)
EOF

    log_success "Streamlit dashboard created"
}

# Setup Temporal configuration
setup_temporal() {
    log_info "Setting up Temporal configuration..."

    cat > temporal/config/dynamicconfig/development.yaml << EOF
system:
  history:
    numHistoryShards: 4
  blobSizeLimit: 2097152
  persistence:
    defaultStore: default
    visibilityStore: visibility
    datastores:
      default:
        sql:
          driver: postgres
          host: postgres
          port: 5432
          user: ontologia
          password: ontologia123
          database: ontologia
          maxConns: 20
          maxConnLifetime: "1h"
      visibility:
        sql:
          driver: postgres
          host: postgres
          port: 5432
          user: ontologia
          password: ontologia123
          database: ontologia_visibility
          maxConns: 20
          maxConnLifetime: "1h"
  namespace:
    default:
      retention: "7d"
EOF

    log_success "Temporal configuration created"
}

# Main setup function
main() {
    log_info "🚀 Starting Ontologia Playground Setup..."

    check_docker
    check_resources
    setup_environment
    create_directories
    setup_monitoring
    setup_notebooks
    setup_examples
    setup_dashboard
    setup_temporal

    log_success "✅ Ontologia Playground setup completed!"
    echo
    log_info "Next steps:"
    echo "1. Review and customize .env file"
    echo "2. Start the playground: docker-compose up -d"
    echo "3. Wait for services to be ready: docker-compose logs -f"
    echo "4. Access the dashboard: http://localhost:8501"
    echo "5. Explore the API: http://localhost:8000/docs"
    echo
    log_info "For more information, check the README.md file"
}

# Run setup
main "$@"
EOF

Permissões para o script:
<tool_call>bash
<arg_key>CommandLine</arg_key>
<arg_value>chmod +x /Users/kevinsaltarelli/Documents/GitHub/ontologia/playground/scripts/setup.sh
