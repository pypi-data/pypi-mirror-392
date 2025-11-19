# Ontologia Core Mode - First 15 Minutes

Get Ontologia running in **15 minutes** with minimal dependencies. Perfect for simple APIs, learning, and getting started.

## 🚀 What You'll Get

- ✅ **REST API** for ontology management
- ✅ **SQL database** (PostgreSQL)
- ✅ **Authentication** with JWT tokens
- ✅ **Basic CRUD** for objects and relationships
- ✅ **Generated Python SDK**

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Python 3.11+** (if not using Docker)
- **5 minutes** of your time ⏰

---

## ⚡ Option 1: Docker Setup (5 minutes)

### Step 1: Install Core Package
```bash
pip install ontologia[core]
```

### Step 2: Start Services
```bash
# Clone the repository
git clone https://github.com/kevinqz/ontologia.git
cd ontologia

# Start core services (PostgreSQL + API)
docker-compose -f docker-compose.core.yml up -d
```

### Step 3: Wait for Ready
```bash
# Check if services are up
curl http://localhost:8000/health

# Should return: {"status": "healthy", ...}
```

### Step 4: Get Access Token
```bash
curl -X POST http://localhost:8000/v2/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"
```

Copy the `access_token` from the response - you'll need it for API calls.

---

## 🛠️ Option 2: Automated Setup (3 minutes)

### Step 1: Run Setup Script
```bash
# Clone and run setup
git clone https://github.com/kevinqz/ontologia.git
cd ontologia
python scripts/setup.py --mode core
```

The script will:
- ✅ Detect dependencies
- ✅ Generate configuration
- ✅ Start Docker services
- ✅ Run database migrations
- ✅ Generate SDK
- ✅ Show you the exact next steps

---

## 🎯 Your First API Calls (8 minutes)

Once services are running, let's create your first ontology:

### 1. Create an Object Type
```bash
# Replace YOUR_TOKEN with the token from Step 4
TOKEN="YOUR_TOKEN"

curl -X PUT http://localhost:8000/v2/ontologies/default/objectTypes/employee \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "displayName": "Employee",
       "primaryKey": "id",
       "properties": {
         "id": {"dataType": "string", "displayName": "ID", "required": true},
         "name": {"dataType": "string", "displayName": "Name", "required": false},
         "department": {"dataType": "string", "displayName": "Department", "required": false}
       },
       "implements": []
     }'
```

### 2. Create an Object
```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/objects/employee/emp1 \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "properties": {
         "id": "emp1",
         "name": "Alice",
         "department": "Engineering"
       }
     }'
```

### 3. Query Your Data
```bash
curl -X POST http://localhost:8000/v2/ontologies/default/objects/search \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "objectTypeApiName": "employee"
     }'
```

---

## 🐍 Use the Python SDK (10 minutes)

### Step 1: Install SDK
```bash
pip install ontologia[core]
```

### Step 2: Generate SDK (if not using setup script)
```bash
ontologia-cli generate-sdk --source local
```

### Step 3: Use in Python
```python
from ontologia_sdk.client import OntologyClient
from ontologia_sdk.ontology.objects import Employee

# Connect to your API
client = OntologyClient(
    host="http://localhost:8000",
    ontology="default",
    token="YOUR_TOKEN"
)

# Create an employee
emp = Employee(
    id="emp2",
    name="Bob",
    department="Product"
)
emp.save(client)

# Search employees
engineers = Employee.search(client, where=[
    {"property": "department", "op": "eq", "value": "Engineering"}
])

for emp in engineers.data:
    print(f"Employee: {emp.name}, Dept: {emp.department}")
```

---

## 📚 What's Next? (15 minutes)

### 🎯 Learning Path

**If you want to add data processing:**
```bash
pip install ontologia[analytics]
# Adds DuckDB + dbt + Dagster for data pipelines
```

**If you need graph traversals:**
```bash
pip install ontologia[graph]
# Adds KùzuDB for high-performance graph queries
```

**If you want full enterprise features:**
```bash
pip install ontologia[full]
# Everything: search, workflows, orchestration, real-time
```

### 📖 Explore More

- **📖 Full Documentation**: `docs/index.md`
- **🔧 Advanced Configuration**: `docs/configuration.md`
- **📊 Analytics Guide**: `docs/analytics-guide.md`
- **🕸️ Graph Queries**: `docs/graph-queries.md`
- **⚙️ Production Deployment**: `docs/deployment.md`

### 🎪 Try Examples

```bash
# Run interactive examples
python templates/project/examples/quickstarts/api_quickstart.py

# Data platform example
python templates/project/examples/cookbook/cookbook_01_dsl_search.py
```

### 🐳 Docker Commands

```bash
# View logs
docker-compose -f docker-compose.core.yml logs -f

# Stop services
docker-compose -f docker-compose.core.yml down

# Restart with changes
docker-compose -f docker-compose.core.yml up --force-recreate
```

---

## 🆘 Troubleshooting

### Port Already in Use?
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.core.yml up -d --scale api=1
```

### Database Connection Issues?
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.core.yml ps postgres

# View PostgreSQL logs
docker-compose -f docker-compose.core.yml logs postgres

# Restart database
docker-compose -f docker-compose.core.yml restart postgres
```

### Token Expired?
```bash
# Get a new token
curl -X POST http://localhost:8000/v2/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"
```

---

## 🎉 Success!

You now have:
- ✅ Running Ontologia API
- ✅ Working authentication
- ✅ Object types and instances
- ✅ Python SDK integration
- ✅ Foundation for scaling up

**Time elapsed: ~15 minutes** 🚀

Ready for more? [Upgrade to Analytics Mode](ANALYTICS_SETUP.md) or [explore the full documentation](index.md).
