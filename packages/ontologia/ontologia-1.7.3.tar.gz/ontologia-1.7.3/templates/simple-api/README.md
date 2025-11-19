# Simple API Template

The perfect starting point for Ontologia! This template gives you a clean, minimal setup with just the essentials.

## 🎯 What You Get

- ✅ **REST API** for ontology management
- ✅ **PostgreSQL** database
- ✅ **JWT Authentication**
- ✅ **Basic CRUD** operations
- ✅ **Python SDK** integration
- ✅ **Docker** setup

## 🚀 Quick Start

### 1. Create Project
```bash
ontologia init --template simple-api my-api-project
cd my-api-project
```

### 2. Start Services
```bash
# Start PostgreSQL + API
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f api
```

### 3. Test Your API
```bash
# Get authentication token
curl -X POST http://localhost:8000/v2/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"

# Use the token in subsequent requests
TOKEN="your-token-here"
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/v2/ontologies/default/objectTypes
```

## 📁 Project Structure

```
my-api-project/
├── README.md              # This file
├── pyproject.toml         # Project dependencies
├── docker-compose.yml     # PostgreSQL + API
├── .env.example          # Environment variables
├── examples/             # Usage examples
│   ├── basic_crud.py     # Simple CRUD operations
│   ├── authentication.py # Auth examples
│   └── queries.py        # Query examples
└── client/               # Client application examples
    └── simple_client.py  # Basic client usage
```

## 🛠️ Development

### Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Install dependencies
pip install ontologia[core]

# Start in development mode
uv run uvicorn ontologia_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_basic_crud.py

# Run with coverage
python -m pytest --cov=ontologia tests/
```

## 📖 Examples

### Basic CRUD
```python
from ontologia_sdk.client import OntologyClient

# Connect to your API
client = OntologyClient(
    host="http://localhost:8000",
    ontology="default",
    token="your-token-here"
)

# Create object type
client.put_object_type("employee", {
    "displayName": "Employee",
    "primaryKey": "id",
    "properties": {
        "id": {"dataType": "string", "required": True},
        "name": {"dataType": "string", "required": False}
    }
})

# Create object
client.put_object("employee", "emp1", {
    "properties": {
        "id": "emp1",
        "name": "Alice"
    }
})

# Query objects
employees = client.search_objects("employee")
print(employees.data)
```

### Authentication
```python
import httpx

# Get token
response = httpx.post(
    "http://localhost:8000/v2/auth/token",
    data={"username": "admin", "password": "admin"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = httpx.get(
    "http://localhost:8000/v2/ontologies/default/objectTypes",
    headers=headers
)
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://ontologia:ontologia123@localhost:5432/ontologia

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# API
API_HOST=localhost
API_PORT=8000

# Features (all disabled for simple mode)
STORAGE_MODE=sql_only
ENABLE_SEARCH=false
ENABLE_WORKFLOWS=false
ENABLE_REALTIME=false
ENABLE_ORCHESTRATION=false
```

### Docker Compose
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ontologia
      POSTGRES_USER: ontologia
      POSTGRES_PASSWORD: ontologia123
    ports:
      - "5432:5432"

  api:
    image: ontologia:latest
    environment:
      DATABASE_URL: postgresql://ontologia:ontologia123@postgres:5432/ontologia
    ports:
      - "8000:8000"
    depends_on:
      - postgres
```

## 📊 What's Next?

When you're ready to add more features:

### Add Analytics
```bash
# Upgrade to data platform template
ontologia upgrade --template data-platform

# Or manually add analytics
pip install ontologia[analytics]
```

### Add Search
```bash
pip install ontologia[search]
# Set ENABLE_SEARCH=true in .env
```

### Add Graph Queries
```bash
pip install ontologia[graph]
# Set STORAGE_MODE=sql_kuzu in .env
```

## 🚨 Common Issues

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
export API_PORT=8001
docker-compose up -d
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Authentication Issues
```bash
# Get fresh token
curl -X POST http://localhost:8000/v2/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"
```

## 📚 Learn More

- **Full Documentation**: [../../docs/index.md](../../docs/index.md)
- **API Reference**: http://localhost:8000/docs
- **More Examples**: [../project/examples/](../project/examples/)
- **Upgrade Guide**: [../README.md](../README.md)

## 🎉 Success!

You now have a running Ontologia API with:
- ✅ Database connectivity
- ✅ Authentication system
- ✅ CRUD operations
- ✅ Python SDK
- ✅ Docker deployment

Ready to build something amazing! 🚀
