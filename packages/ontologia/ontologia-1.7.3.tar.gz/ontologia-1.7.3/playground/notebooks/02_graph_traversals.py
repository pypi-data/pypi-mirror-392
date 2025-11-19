# 02 Graph Traversals - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


# Graph Traversals with Ontologia - Marimo Notebook
# Explore graph queries and relationship analysis

import os

import marimo
import networkx as nx
import pandas as pd
import requests

# Initialize Marimo app
app = marimo.App()


@app.cell
def _(mo):
    mo.md(
        """
        # 🔍 Graph Traversals with Ontologia

        This notebook demonstrates how to:

        - **Query Graph Structure**: Explore object types and relationships
        - **Path Finding**: Find connections between entities
        - **Graph Visualization**: Visualize your knowledge graph
        - **Advanced Queries**: Use KùzuDB for complex traversals

        Let's start by exploring the graph structure!
        """
    )
    return


@app.cell
def _(mo):
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    def check_api_connection():
        """Verify API is accessible"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    if not check_api_connection():
        mo.md("❌ API not accessible. Please ensure Ontologia is running.")
        raise marimo.Interrupt("API connection required")

    mo.md("✅ API connection verified")
    return API_BASE_URL, check_api_connection


@app.cell
def _(mo, API_BASE_URL):
    def get_ontology_details(ontology_name="company"):
        """Get detailed information about an ontology"""
        try:
            response = requests.get(f"{API_BASE_URL}/v2/ontologies/{ontology_name}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching ontology: {e}")
            return None

    ontology_details = get_ontology_details()
    return get_ontology_details, ontology_details


@app.cell
def _(mo, ontology_details):
    if not ontology_details:
        mo.md("❌ Could not fetch ontology details. Please run the introduction notebook first.")
    else:
        object_types = ontology_details.get("objectTypes", [])
        link_types = ontology_details.get("linkTypes", [])

        mo.md(
            f"""
            ## 📊 Ontology Structure

            - **Object Types**: {len(object_types)}
            - **Link Types**: {len(link_types)}
            """
        )
    return link_types, object_types


@app.cell
def _(mo, object_types):
    if object_types:
        # Display object types
        ot_cell_6_df = pd.DataFrame(
            [
                {
                    "API Name": ot.get("apiName", "Unknown"),
                    "Display Name": ot.get("displayName", "Unknown"),
                    "Description": ot.get("description", "No description"),
                    "Properties": len(ot.get("properties", [])),
                }
                for ot in object_types
            ]
        )

        mo.md("### Object Types:")
        mo.ui.table(ot_cell_6_df)  # type: ignore[name-defined]
    else:
        mo.md("No object types found. Let's create some sample data!")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🏗️ Creating Sample Data

        Let's create object types and instances for our company graph.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def create_object_types():
        """Create sample object types"""
        object_types = [
            {
                "apiName": "person",
                "displayName": "Person",
                "description": "Individual person in the organization",
                "properties": [
                    {"apiName": "name", "displayName": "Name", "dataType": "string"},
                    {"apiName": "email", "displayName": "Email", "dataType": "string"},
                    {"apiName": "role", "displayName": "Role", "dataType": "string"},
                ],
            },
            {
                "apiName": "company",
                "displayName": "Company",
                "description": "Organization or company",
                "properties": [
                    {"apiName": "name", "displayName": "Name", "dataType": "string"},
                    {"apiName": "industry", "displayName": "Industry", "dataType": "string"},
                    {"apiName": "founded", "displayName": "Founded Year", "dataType": "integer"},
                ],
            },
            {
                "apiName": "project",
                "displayName": "Project",
                "description": "Project within the organization",
                "properties": [
                    {"apiName": "name", "displayName": "Name", "dataType": "string"},
                    {"apiName": "status", "displayName": "Status", "dataType": "string"},
                    {"apiName": "budget", "displayName": "Budget", "dataType": "float"},
                ],
            },
        ]

        created_types = []
        for ot in object_types:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objectTypes", json=ot
                )
                if response.status_code in [200, 201]:
                    created_types.append(response.json())
            except Exception as e:
                print(f"Error creating {ot['apiName']}: {e}")

        return created_types

    created_object_types = create_object_types()
    return create_object_types, created_object_types


@app.cell
def _(mo, API_BASE_URL):
    def create_link_types():
        """Create sample link types"""
        link_types = [
            {
                "apiName": "works_for",
                "displayName": "Works For",
                "description": "Person works for a company",
                "sourceObjectTypeApiName": "person",
                "targetObjectTypeApiName": "company",
            },
            {
                "apiName": "manages",
                "displayName": "Manages",
                "description": "Person manages another person",
                "sourceObjectTypeApiName": "person",
                "targetObjectTypeApiName": "person",
            },
            {
                "apiName": "assigned_to",
                "displayName": "Assigned To",
                "description": "Project assigned to person",
                "sourceObjectTypeApiName": "project",
                "targetObjectTypeApiName": "person",
            },
        ]

        created_links = []
        for lt in link_types:
            try:
                response = requests.post(f"{API_BASE_URL}/v2/ontologies/company/linkTypes", json=lt)
                if response.status_code in [200, 201]:
                    created_links.append(response.json())
            except Exception as e:
                print(f"Error creating {lt['apiName']}: {e}")

        return created_links

    created_link_types = create_link_types()
    return create_link_types, created_link_types


@app.cell
def _(mo):
    mo.md(
        """
        ## 📝 Creating Sample Instances

        Now let's create some actual data to work with.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL):
    def create_sample_instances():
        """Create sample instances for our graph"""
        instances = {
            "companies": [
                {"name": "TechCorp", "industry": "Technology", "founded": 2010},
                {"name": "DataInc", "industry": "Data Analytics", "founded": 2015},
            ],
            "people": [
                {"name": "Alice Johnson", "email": "alice@techcorp.com", "role": "CEO"},
                {"name": "Bob Smith", "email": "bob@techcorp.com", "role": "CTO"},
                {"name": "Carol Davis", "email": "carol@datainc.com", "role": "Data Scientist"},
            ],
            "projects": [
                {"name": "AI Platform", "status": "Active", "budget": 1000000.0},
                {"name": "Data Pipeline", "status": "Planning", "budget": 500000.0},
            ],
        }

        created_instances = {}

        # Create companies
        company_ids = []
        for company in instances["companies"]:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objects/company", json=company
                )
                if response.status_code in [200, 201]:
                    company_ids.append(response.json()["id"])
            except Exception as e:
                print(f"Error creating company: {e}")

        # Create people
        person_ids = []
        for person in instances["people"]:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objects/person", json=person
                )
                if response.status_code in [200, 201]:
                    person_ids.append(response.json()["id"])
            except Exception as e:
                print(f"Error creating person: {e}")

        # Create projects
        project_ids = []
        for project in instances["projects"]:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objects/project", json=project
                )
                if response.status_code in [200, 201]:
                    project_ids.append(response.json()["id"])
            except Exception as e:
                print(f"Error creating project: {e}")

        return {"companies": company_ids, "people": person_ids, "projects": project_ids}

    instance_ids = create_sample_instances()
    return create_sample_instances, instance_ids


@app.cell
def _(mo):
    mo.md(
        """
        ## 🔗 Creating Relationships

        Let's connect our instances with relationships.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL, instance_ids):
    def create_relationships():
        """Create relationships between instances"""
        relationships = []

        # Alice works for TechCorp
        if len(instance_ids["people"]) >= 1 and len(instance_ids["companies"]) >= 1:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objects/person/{instance_ids['people'][0]}/works_for/{instance_ids['companies'][0]}"
                )
                if response.status_code in [200, 201]:
                    relationships.append("Alice -> TechCorp")
            except Exception as e:
                print(f"Error creating works_for relationship: {e}")

        # Bob works for TechCorp
        if len(instance_ids["people"]) >= 2 and len(instance_ids["companies"]) >= 1:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/v2/ontologies/company/objects/person/{instance_ids['people'][1]}/works_for/{instance_ids['companies'][0]}"
                )
                if response.status_code in [200, 201]:
                    relationships.append("Bob -> TechCorp")
            except Exception as e:
                print(f"Error creating works_for relationship: {e}")

        return relationships

    created_relationships = create_relationships()
    return create_relationships, created_relationships


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎯 Graph Traversal Examples

        Now let's explore different ways to traverse our graph.
        """
    )
    return


@app.cell
def _(mo, API_BASE_URL, instance_ids):
    def traverse_from_person(person_id):
        """Find all connections from a person"""
        try:
            # Get outgoing links
            response = requests.get(
                f"{API_BASE_URL}/v2/ontologies/company/objects/person/{person_id}/links"
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to traverse: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    # Example: Traverse from first person
    if instance_ids["people"]:
        traversal_result = traverse_from_person(instance_ids["people"][0])
    else:
        traversal_result = {"error": "No people found"}

    return instance_ids, traverse_from_person, traversal_result


@app.cell
def _(mo, traversal_result):
    if "error" in traversal_result:
        mo.md(f"❌ Traversal error: {traversal_result['error']}")
    else:
        links = traversal_result.get("items", [])
        if links:
            links_cell_16_df = pd.DataFrame(
                [
                    {
                        "Link Type": link.get("linkTypeApiName", "Unknown"),
                        "Target Object": link.get("targetObjectTypeApiName", "Unknown"),
                        "Target ID": link.get("targetObjectId", "Unknown"),
                    }
                    for link in links
                ]
            )

            mo.md("### Traversal Results:")
            mo.ui.table(links_cell_16_df)  # type: ignore[name-defined]
        else:
            mo.md("No outgoing links found from this person.")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 📈 Graph Visualization

        Let's create a visual representation of our knowledge graph.
        """
    )
    return


@app.cell
def _(mo, traversal_result):
    def create_graph_visualization(traversal_data):
        """Create a NetworkX graph from traversal results"""
        G = nx.DiGraph()

        # Add nodes and edges from traversal results
        if "items" in traversal_data:
            for link in traversal_data["items"]:
                source = f"person:{link.get('sourceObjectId', 'unknown')}"
                target = f"{link.get('targetObjectTypeApiName', 'unknown')}:{link.get('targetObjectId', 'unknown')}"
                edge_type = link.get("linkTypeApiName", "unknown")

                G.add_node(source, type="person")
                G.add_node(target, type=link.get("targetObjectTypeApiName", "unknown"))
                G.add_edge(source, target, label=edge_type)

        return G

    graph = create_graph_visualization(traversal_result)
    return create_graph_visualization, graph


@app.cell
def _(mo, graph):
    if graph.nodes():
        # Create a simple text representation of the graph
        graph_text = "📊 Graph Structure:\n\n"

        for node in graph.nodes():
            node_type = graph.nodes[node].get("type", "unknown")
            graph_text += f"🔹 {node} (Type: {node_type})\n"

            for neighbor in graph.neighbors(node):
                edge_data = graph.get_edge_data(node, neighbor)
                edge_label = edge_data.get("label", "related to") if edge_data else "related to"
                graph_text += f"   └─ {edge_label} → {neighbor}\n"

        mo.md(graph_text)
    else:
        mo.md("No graph data to visualize. Please ensure instances and relationships were created.")
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 🎉 Summary

        You've learned how to:

        ✅ **Create Object Types**: Define the structure of your entities
        ✅ **Create Link Types**: Define relationships between entities
        ✅ **Create Instances**: Add actual data to your graph
        ✅ **Traverse Graph**: Find connections and relationships
        ✅ **Visualize Structure**: Understand your knowledge graph layout

        **Next Steps**:
        - Try `03_analytics.py` for data analysis with DuckDB
        - Explore `04_workflows.py` for automation with Temporal
        - Check the API docs at http://localhost:8000/docs

        **Advanced Features**:
        - Complex path finding algorithms
        - Graph analytics with NetworkX
        - Real-time graph updates
        - Multi-hop traversals
        """
    )
    return


if __name__ == "__main__":
    app.run()
