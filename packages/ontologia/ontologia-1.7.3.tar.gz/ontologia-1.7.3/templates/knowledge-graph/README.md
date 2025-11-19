# Knowledge Graph Template

Built for applications requiring complex graph traversals and relationship queries. This template includes KùzuDB for high-performance graph operations alongside PostgreSQL for transactional data.

## 🎯 What You Get

- ✅ **KùzuDB** for high-performance graph traversals
- ✅ **PostgreSQL** for transactional operations
- ✅ **Graph API** endpoints for traversals
- ✅ **Relationship queries** with complex patterns
- ✅ **Path finding** algorithms
- ✅ **Graph analytics** capabilities

## 🚀 Quick Start

### 1. Create Project
```bash
ontologia init --template knowledge-graph my-graph
cd my-graph
```

### 2. Start Services
```bash
# Start core services + graph database
docker-compose -f docker-compose.graph.yml up -d

# Wait for services to be ready
docker-compose logs -f kuzu
```

### 3. Access Graph Tools
- **API**: http://localhost:8000/docs
- **Graph Explorer**: http://localhost:8000/graph-explorer
- **KùzuDB Shell**: `docker-compose exec kuzu kuzu-py`

## 📁 Project Structure

```
my-graph/
├── README.md              # This file
├── pyproject.toml         # Graph dependencies
├── docker-compose.yml     # Core services
├── docker-compose.graph.yml  # Graph stack
├── .env.example          # Environment variables
├── examples/             # Graph examples
│   ├── graph_traversals.py
│   ├── relationship_queries.py
│   └── path_finding.py
└── client/               # Graph client examples
    └── graph_client.py
```

## 🛠️ Development

### Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Install graph dependencies
pip install ontologia[graph]

# Enable graph mode
export STORAGE_MODE=sql_kuzu
export KUZU_PATH=./data/graph.kuzu

# Start in development mode
uv run uvicorn ontologia_api.main:app --reload --host 0.0.0.0 --port 8000
```

### KùzuDB Development
```bash
# Connect to KùzuDB shell
docker-compose exec kuzu kuzu-py

# Python interface
import kuzu
conn = kuzu.connect('./data/graph.kuzu')
```

## 🕸️ Graph Architecture

### Data Model
```
PostgreSQL (Transactional) ←→ KùzuDB (Graph)
    ↓                              ↓
CRUD Operations              Graph Traversals
```

### Graph Schema
- **Nodes**: Object types from Ontologia
- **Edges**: Link types from Ontologia
- **Properties**: Object and link properties
- **Indexes**: Optimized for traversal performance

## 📈 Usage Examples

### Basic Graph Traversal
```python
from ontologia_sdk.client import OntologyClient

# Connect to graph-enabled API
client = OntologyClient(
    host="http://localhost:8000",
    ontology="default",
    token="your-token-here"
)

# Find all employees in Engineering department
engineers = client.search_objects("employee", where=[
    {"property": "department", "op": "eq", "value": "Engineering"}
])

# Traverse relationships: employee → projects → skills
for emp in engineers.data:
    projects = client.traverse("employee", emp["properties"]["id"], "works_on")
    for project in projects.data:
        skills = client.traverse("project", project["pkValue"], "requires_skill")
        print(f"{emp['properties']['name']} → {project['properties']['name']} → {len(skills.data)} skills")
```

### Complex Relationship Queries
```python
def find_expertise_paths(employee_id: str, target_skill: str, max_depth: int = 3):
    """Find paths from employee to target skill through colleagues."""

    # Start with the employee
    current_people = [employee_id]
    visited = set(employee_id)
    paths = []

    for depth in range(max_depth):
        next_people = []

        for person_id in current_people:
            # Get projects this person works on
            projects = client.traverse("employee", person_id, "works_on")

            for project in projects.data:
                project_id = project["pkValue"]

                # Get colleagues on the same project
                colleagues = client.traverse("project", project_id, "worked_on_by", direction="reverse")

                for colleague in colleagues.data:
                    colleague_id = colleague["pkValue"]

                    if colleague_id not in visited:
                        visited.add(colleague_id)
                        next_people.append(colleague_id)

                        # Check if colleague has the target skill
                        skills = client.traverse("employee", colleague_id, "has_skill")
                        for skill in skills.data:
                            if skill["properties"]["name"] == target_skill:
                                paths.append({
                                    "depth": depth + 1,
                                    "path": f"{person_id} → {project_id} → {colleague_id}",
                                    "colleague": colleague["properties"]["name"]
                                })

        current_people = next_people

        if not current_people:
            break

    return sorted(paths, key=lambda x: x["depth"])
```

### Path Finding Algorithms
```python
def shortest_path(start_node: str, end_node: str, relationship_type: str):
    """Find shortest path between two nodes."""

    # BFS implementation
    from collections import deque

    queue = deque([(start_node, [])])
    visited = {start_node}

    while queue:
        current, path = queue.popleft()

        if current == end_node:
            return path + [current]

        # Get neighbors
        neighbors = client.traverse("node", current, relationship_type)

        for neighbor in neighbors.data:
            neighbor_id = neighbor["pkValue"]

            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, path + [current]))

    return None  # No path found

def find_cycles(node_type: str, relationship_type: str):
    """Find cycles in the graph using DFS."""

    def dfs(node, path, visited):
        if node in path:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]

        if node in visited:
            return None

        visited.add(node)
        path.append(node)

        # Get neighbors
        neighbors = client.traverse(node_type, node, relationship_type)

        for neighbor in neighbors.data:
            neighbor_id = neighbor["pkValue"]
            cycle = dfs(neighbor_id, path.copy(), visited.copy())
            if cycle:
                return cycle

        return None

    # Check all nodes for cycles
    all_nodes = client.search_objects(node_type)
    cycles = []

    for node in all_nodes.data:
        node_id = node["pkValue"]
        cycle = dfs(node_id, [], set())
        if cycle and len(cycle) > 1:
            cycles.append(cycle)

    return cycles
```

### Graph Analytics
```python
def analyze_network_centrality():
    """Calculate centrality measures for the network."""

    # Get all nodes and edges
    employees = client.search_objects("employee")
    relationships = client.search_links("works_with")

    # Build adjacency list
    adjacency = {}
    for emp in employees.data:
        emp_id = emp["pkValue"]
        adjacency[emp_id] = set()

    for rel in relationships.data:
        from_id = rel["from"]["pkValue"]
        to_id = rel["to"]["pkValue"]
        adjacency[from_id].add(to_id)
        adjacency[to_id].add(from_id)  # Undirected

    # Calculate degree centrality
    centrality = {}
    for node, neighbors in adjacency.items():
        centrality[node] = len(neighbors)

    # Sort by centrality
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    return sorted_centrality[:10]  # Top 10 most connected

def detect_communities():
    """Simple community detection using connected components."""

    def dfs(node, community, visited):
        visited.add(node)
        community.append(node)

        neighbors = client.traverse("employee", node, "works_with")
        for neighbor in neighbors.data:
            neighbor_id = neighbor["pkValue"]
            if neighbor_id not in visited:
                dfs(neighbor_id, community, visited)

    # Find all connected components
    all_employees = client.search_objects("employee")
    visited = set()
    communities = []

    for emp in all_employees.data:
        emp_id = emp["pkValue"]
        if emp_id not in visited:
            community = []
            dfs(emp_id, community, visited)
            communities.append(community)

    return communities
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Database
DATABASE_URL=postgresql://ontologia:ontologia123@localhost:5432/ontologia

# Graph Database
STORAGE_MODE=sql_kuzu
KUZU_PATH=./data/graph.kuzu
KUZU_PORT=8001

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# API Configuration
API_HOST=localhost
API_PORT=8000
API_ONTOLOGY=default

# Feature Flags - Graph mode
ENABLE_SEARCH=false
ENABLE_WORKFLOWS=false
ENABLE_REALTIME=false
ENABLE_ORCHESTRATION=false
```

### KùzuDB Configuration
```python
# Graph schema setup
import kuzu

conn = kuzu.connect('./data/graph.kuzu')

# Create node tables
conn.execute("CREATE NODE TABLE Employee(id STRING, name STRING, department STRING, PRIMARY KEY(id))")
conn.execute("CREATE NODE TABLE Project(id STRING, name STRING, budget DOUBLE, PRIMARY KEY(id))")
conn.execute("CREATE NODE TABLE Skill(id STRING, name STRING, category STRING, PRIMARY KEY(id))")

# Create relationship tables
conn.execute("CREATE REL TABLE works_on(FROM Employee TO Project, since_date DATE)")
conn.execute("CREATE REL TABLE has_skill(FROM Employee TO Skill, proficiency INTEGER)")
conn.execute("CREATE REL TABLE requires_skill(FROM Project TO Skill, required_level INTEGER)")

# Create indexes for performance
conn.execute("CREATE INDEX ON Employee(department)")
conn.execute("CREATE INDEX ON Project(budget)")
conn.execute("CREATE INDEX ON Skill(category)")
```

## 🚀 Production Deployment

### Docker Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale graph services
docker-compose -f docker-compose.prod.yml up -d --scale kuzu=2
```

### Performance Optimization
- **Indexes**: Create indexes on frequently queried properties
- **Batch Operations**: Use bulk inserts for large datasets
- **Connection Pooling**: Reuse connections for better performance
- **Caching**: Cache frequently accessed traversal results

### Monitoring
- **Query Performance**: Monitor traversal query times
- **Graph Statistics**: Track node and edge counts
- **Memory Usage**: Monitor KùzuDB memory consumption
- **Connection Health**: Check database connectivity

## 📚 Learn More

- **KùzuDB Documentation**: https://kuzudb.com/docs/
- **Graph Algorithms**: https://networkx.org/documentation/
- **Ontologia Graph Guide**: [../../docs/graph.md](../../docs/graph.md)
- **Cypher Query Language**: https://opencypher.org/

## 🎉 Success!

You now have a complete knowledge graph platform with:
- ✅ Transactional database (PostgreSQL)
- ✅ Graph database (KùzuDB)
- ✅ Graph traversal APIs
- ✅ Relationship queries
- ✅ Path finding algorithms
- ✅ Graph analytics tools

Ready to build amazing graph applications! 🚀
