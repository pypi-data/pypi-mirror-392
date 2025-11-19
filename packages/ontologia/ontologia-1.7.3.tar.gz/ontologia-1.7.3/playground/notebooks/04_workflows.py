# 04 Workflows - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


# Workflows with Ontologia - Marimo Notebook
# Explore Temporal workflows and automation

import os
from datetime import datetime

import marimo
import pandas as pd
import requests

# Initialize Marimo app
app = marimo.App()


@app.cell
def _(mo):
    mo.md(
        """
        # ⚙️ Workflows with Ontologia

        This notebook demonstrates how to:

        - **Temporal Integration**: Connect to Temporal workflow engine
        - **Workflow Design**: Create and manage workflows
        - **Activity Execution**: Run background activities
        - **Process Monitoring**: Track workflow execution and status
        - **Automation**: Build automated data pipelines

        Let's explore the power of workflow orchestration!
        """
    )
    return


@app.cell
def _(mo):
    # Environment configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_UI_URL = "http://localhost:7233"

    def check_workflow_services():
        """Check if workflow services are available"""
        services = {"API": False, "Temporal UI": False}

        # Check API
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            services["API"] = response.status_code == 200
        except:
            pass

        # Check Temporal UI
        try:
            response = requests.get(f"{TEMPORAL_UI_URL}/api/v1/namespaces/default", timeout=5)
            services["Temporal UI"] = response.status_code == 200
        except:
            pass

        return services

    service_status = check_workflow_services()
    return API_BASE_URL, TEMPORAL_ADDRESS, TEMPORAL_UI_URL, check_workflow_services, service_status


@app.cell
def _(mo, service_status, temporal_ui_url):
    # Display service status
    status_text = "## 🔧 Workflow Service Status\n\n"

    for service, status in service_status.items():
        status_icon = "✅" if status else "❌"
        status_text += f"**{service}**: {status_icon} {'Running' if status else 'Not Available'}\n"

    if service_status["Temporal UI"]:
        status_text += f"\n🌐 **Temporal UI**: [Open Dashboard]({temporal_ui_url})\n"

    if not all(service_status.values()):
        status_text += "\n⚠️ Some services are not available. Start with: `docker-compose up -d`"

    mo.md(status_text)
    return


@app.cell
def _(mo, service_status):
    if not service_status["API"]:
        raise marimo.Interrupt("API is required for workflow operations")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🏗️ Understanding Workflows in Ontologia

        **Workflows** are sequences of activities that can be:
        - **Orchestrated**: Managed by Temporal
        - **Reliable**: Automatic retries and error handling
        - **Scalable**: Distributed execution
        - **Monitorable**: Real-time status tracking

        **Activities** are individual units of work that can include:
        - Data processing
        - API calls
        - Database operations
        - External integrations
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def get_workflow_status():
        """Get current workflow system status"""
        try:
            response = requests.get(f"{API_BASE_URL}/v2/workflows/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status endpoint returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    workflow_status = get_workflow_status()
    return get_workflow_status, workflow_status


@app.cell
def _(mo, workflow_status):
    if "error" in workflow_status:
        mo.md(f"⚠️ Workflow status check failed: {workflow_status['error']}")
    else:
        status_info = workflow_status.get("status", {})
        mo.md(
            f"""
            ## 📊 Workflow System Status

            - **Temporal Enabled**: {status_info.get('temporal_enabled', 'Unknown')}
            - **Active Workflows**: {status_info.get('active_workflows', 0)}
            - **Completed Workflows**: {status_info.get('completed_workflows', 0)}
            - **Failed Workflows**: {status_info.get('failed_workflows', 0)}
            - **Worker Status**: {status_info.get('worker_status', 'Unknown')}
            """
        )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎯 Sample Workflow: Data Sync Pipeline

        Let's create a workflow that synchronizes data between different systems.
        This is a common pattern in Ontologia for keeping data consistent.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def create_data_sync_workflow():
        """Create a sample data synchronization workflow"""
        workflow_definition = {
            "name": "data_sync_pipeline",
            "description": "Synchronize data between PostgreSQL and Elasticsearch",
            "workflow_id": f"data-sync-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "activities": [
                {
                    "name": "extract_from_postgres",
                    "type": "data_extraction",
                    "config": {
                        "source": "postgresql",
                        "query": "SELECT * FROM objects WHERE updated_at > $last_sync",
                    },
                },
                {
                    "name": "transform_data",
                    "type": "data_transformation",
                    "config": {"format": "elasticsearch", "enrich": True},
                },
                {
                    "name": "load_to_elasticsearch",
                    "type": "data_loading",
                    "config": {"target": "elasticsearch", "index": "ontologia_objects"},
                },
                {
                    "name": "update_sync_status",
                    "type": "status_update",
                    "config": {"last_sync": datetime.now().isoformat()},
                },
            ],
        }

        try:
            response = requests.post(f"{API_BASE_URL}/v2/workflows", json=workflow_definition)
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)

    workflow_result = create_data_sync_workflow()
    return create_data_sync_workflow, workflow_result


@app.cell
def _(mo, workflow_result):
    success, result = workflow_result
    if success:
        mo.md(
            f"""
            ✅ **Workflow Created Successfully!**

            - **Workflow ID**: {result.get('workflow_id', 'Unknown')}
            - **Name**: {result.get('name', 'Unknown')}
            - **Status**: {result.get('status', 'Unknown')}
            - **Created**: {result.get('created_at', 'Unknown')}
            """
        )
    else:
        mo.md(f"❌ Failed to create workflow: {result}")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 📋 Workflow Templates

        Ontologia provides several workflow templates for common use cases.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def get_workflow_templates():
        """Get available workflow templates"""
        templates = [
            {
                "id": "data_pipeline",
                "name": "Data Pipeline",
                "description": "ETL pipeline for data processing",
                "activities": ["extract", "transform", "load", "validate"],
            },
            {
                "id": "graph_sync",
                "name": "Graph Synchronization",
                "description": "Sync graph data between databases",
                "activities": ["export_graph", "transform_nodes", "import_graph", "verify_links"],
            },
            {
                "id": "analytics_report",
                "name": "Analytics Report",
                "description": "Generate automated analytics reports",
                "activities": [
                    "gather_metrics",
                    "calculate_kpis",
                    "generate_report",
                    "send_notification",
                ],
            },
            {
                "id": "data_cleanup",
                "name": "Data Cleanup",
                "description": "Clean and archive old data",
                "activities": [
                    "identify_old_data",
                    "archive_data",
                    "cleanup_indexes",
                    "update_metadata",
                ],
            },
        ]

        return templates

    workflow_templates = get_workflow_templates()
    return get_workflow_templates, workflow_templates


@app.cell
def _(mo, workflow_templates):
    # Display workflow templates
    templates_cell_14_df = pd.DataFrame(
        [
            {
                "Template ID": t["id"],
                "Name": t["name"],
                "Description": t["description"],
                "Activities": len(t["activities"]),
            }
            for t in workflow_templates
        ]
    )

    mo.md("### Available Workflow Templates")
    mo.ui.table(templates_cell_14_df)  # type: ignore[name-defined]
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🔄 Workflow Execution Patterns

        Let's explore different workflow execution patterns.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def demonstrate_workflow_patterns():
        """Demonstrate different workflow execution patterns"""

        patterns = {
            "sequential": {
                "name": "Sequential Processing",
                "description": "Activities run one after another",
                "use_case": "Data pipelines where order matters",
            },
            "parallel": {
                "name": "Parallel Processing",
                "description": "Activities run simultaneously",
                "use_case": "Independent data processing tasks",
            },
            "fan_out_fan_in": {
                "name": "Fan-Out/Fan-In",
                "description": "Split work, process in parallel, then aggregate",
                "use_case": "Batch processing large datasets",
            },
            "conditional": {
                "name": "Conditional Branching",
                "description": "Different paths based on conditions",
                "use_case": "Error handling and data validation",
            },
        }

        return patterns

    workflow_patterns = demonstrate_workflow_patterns()
    return demonstrate_workflow_patterns, workflow_patterns


@app.cell
def _(mo, workflow_patterns):
    # Display workflow patterns
    patterns_cell_17_df = pd.DataFrame(
        [
            {
                "Pattern": pattern_info["name"],
                "Description": pattern_info["description"],
                "Use Case": pattern_info["use_case"],
            }
            for pattern_info in workflow_patterns.values()
        ]
    )

    mo.md("### Workflow Execution Patterns")
    mo.ui.table(patterns_cell_17_df)  # type: ignore[name-defined]
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 📊 Monitoring Workflows

        Let's explore how to monitor and track workflow execution.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def get_workflow_metrics():
        """Get workflow execution metrics"""
        # Simulate workflow metrics (in real implementation, this would query Temporal)
        metrics = {
            "total_workflows": 25,
            "active_workflows": 3,
            "completed_today": 12,
            "failed_today": 1,
            "avg_execution_time": 45.2,  # seconds
            "success_rate": 95.8,  # percentage
            "throughput_per_hour": 8.5,
        }

        return metrics

    workflow_metrics = get_workflow_metrics()
    return get_workflow_metrics, workflow_metrics


@app.cell
def _(mo, workflow_metrics):
    # Display workflow metrics
    mo.md(
        f"""
        ### 📈 Workflow Performance Metrics

        - **Total Workflows**: {workflow_metrics['total_workflows']}
        - **Currently Active**: {workflow_metrics['active_workflows']}
        - **Completed Today**: {workflow_metrics['completed_today']}
        - **Failed Today**: {workflow_metrics['failed_today']}
        - **Average Execution Time**: {workflow_metrics['avg_execution_time']}s
        - **Success Rate**: {workflow_metrics['success_rate']}%
        - **Throughput**: {workflow_metrics['throughput_per_hour']}/hour
        """
    )
    return


@app.cell
def _(mo, workflow_metrics):
    import plotly.express as px
    import plotly.graph_objects as go

    # Create workflow status chart
    status_data = {
        "Status": ["Active", "Completed Today", "Failed Today"],
        "Count": [
            workflow_metrics["active_workflows"],
            workflow_metrics["completed_today"],
            workflow_metrics["failed_today"],
        ],
    }

    fig_workflow_status = px.bar(
        status_data,
        x="Status",
        y="Count",
        title="Workflow Status Overview",
        color="Status",
        color_discrete_map={
            "Active": "#2E86AB",
            "Completed Today": "#A23B72",
            "Failed Today": "#F18F01",
        },
    )

    return fig_workflow_status, go, px, status_data


@app.cell
def _(mo, fig_workflow_status):
    # Display workflow status chart
    mo.ui.plotly(fig_workflow_status)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🛠️ Building Custom Workflows

        Let's create a custom workflow for a real-world use case.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def create_knowledge_graph_workflow():
        """Create a workflow for knowledge graph maintenance"""
        workflow = {
            "name": "knowledge_graph_maintenance",
            "description": "Automated knowledge graph cleanup and optimization",
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "activities": [
                {
                    "name": "identify_orphaned_nodes",
                    "type": "graph_analysis",
                    "config": {"find_unconnected": True, "min_connections": 1},
                },
                {
                    "name": "validate_relationships",
                    "type": "data_validation",
                    "config": {"check_integrity": True, "update_invalid": False},
                },
                {
                    "name": "optimize_indexes",
                    "type": "database_optimization",
                    "config": {"rebuild_indexes": True, "analyze_statistics": True},
                },
                {
                    "name": "generate_report",
                    "type": "reporting",
                    "config": {"include_metrics": True, "send_email": False},
                },
            ],
            "retry_policy": {"max_attempts": 3, "backoff": "exponential"},
        }

        return workflow

    kg_workflow = create_knowledge_graph_workflow()
    return create_knowledge_graph_workflow, kg_workflow


@app.cell
def _(mo, kg_workflow):
    # Display the knowledge graph workflow
    mo.md("### Knowledge Graph Maintenance Workflow")

    workflow_text = "🔄 **Workflow Activities**:\n\n"
    for i, activity in enumerate(kg_workflow["activities"], 1):
        workflow_text += f"{i}. **{activity['name']}** ({activity['type']})\n"
        workflow_text += f"   - {activity.get('config', {})}\n"

    workflow_text += f"\n⏰ **Schedule**: {kg_workflow['schedule']}\n"
    workflow_text += f"🔄 **Retry Policy**: {kg_workflow['retry_policy']}\n"

    mo.md(workflow_text)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎯 Best Practices for Workflow Design

        **Key Principles**:

        1. **Idempotency**: Activities should be safe to retry
        2. **Timeouts**: Set appropriate timeouts for each activity
        3. **Error Handling**: Implement proper error handling and logging
        4. **Monitoring**: Include metrics and status reporting
        5. **Testing**: Test workflows in isolation before production

        **Common Patterns**:
        - **Saga Pattern**: For distributed transactions
        - **Compensating Actions**: For rollback scenarios
        - **Circuit Breaker**: For external service calls
        - **Dead Letter Queue**: For failed message handling
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎉 Workflow Summary

        You've explored Ontologia's workflow capabilities:

        ✅ **Temporal Integration**: Connected to workflow orchestration
        ✅ **Workflow Creation**: Designed custom workflows
        ✅ **Execution Patterns**: Understood different execution models
        ✅ **Monitoring**: Tracked workflow performance and status
        ✅ **Best Practices**: Learned workflow design principles

        **Key Features**:
        - Reliable workflow execution
        - Automatic retries and error handling
        - Real-time monitoring and metrics
        - Scalable distributed processing
        - Integration with Ontologia data models

        **Next Steps**:
        - Visit Temporal UI: http://localhost:7233
        - Check Dagster pipelines: http://localhost:3000
        - Explore API documentation: http://localhost:8000/docs
        - Try the other notebooks in this series

        **Advanced Workflow Features**:
        - Multi-region workflow execution
        - Event-driven workflows
        - Machine learning pipeline orchestration
        - Real-time data synchronization
        """
    )
    return


if __name__ == "__main__":
    app.run()
