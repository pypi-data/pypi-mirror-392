# Ontologia Project Templates

Quick-start templates for different use cases. Each template includes everything you need to get running in minutes.

## 🚀 Available Templates

### **simple-api**
Perfect for getting started with basic ontology CRUD operations.
- **Mode**: Core (SQL-only)
- **Features**: REST API, authentication, basic CRUD
- **Setup Time**: 5 minutes
- **Dependencies**: PostgreSQL + FastAPI

```bash
ontologia init --template simple-api my-project
cd my-project
docker-compose up -d
```

### **data-platform**
For data teams needing analytics and ETL capabilities.
- **Mode**: Analytics (SQL + DuckDB + dbt)
- **Features**: Data pipelines, analytics, Dagster orchestration
- **Setup Time**: 10 minutes
- **Dependencies**: PostgreSQL + DuckDB + dbt + Dagster

```bash
ontologia init --template data-platform my-analytics
cd my-analytics
docker-compose -f docker-compose.analytics.yml up -d
```

### **knowledge-graph**
For applications requiring complex graph traversals and relationships.
- **Mode**: Graph (SQL + KùzuDB)
- **Features**: High-performance graph queries, traversals
- **Setup Time**: 15 minutes
- **Dependencies**: PostgreSQL + KùzuDB

```bash
ontologia init --template knowledge-graph my-graph
cd my-graph
docker-compose -f docker-compose.graph.yml up -d
```

### **enterprise-workflows**
Complete enterprise stack with all features.
- **Mode**: Full (everything)
- **Features**: Search, workflows, real-time, orchestration
- **Setup Time**: 20 minutes
- **Dependencies**: Full stack (6+ services)

```bash
ontologia init --template enterprise-workflows my-enterprise
cd my-enterprise
docker-compose -f docker-compose.full.yml up -d
```

## 📁 Template Structure

Each template includes:

```
template-name/
├── README.md              # Template-specific guide
├── pyproject.toml         # Dependencies for this template
├── docker-compose.yml     # Services needed
├── .env.example          # Environment variables
├── examples/             # Usage examples
│   ├── basic_setup.py
│   ├── advanced_features.py
│   └── tests/
└── docs/                 # Template-specific documentation
```

## 🛠️ Using Templates

### Option 1: CLI (Recommended)
```bash
# Create new project from template
ontologia init --template simple-api my-project

# Interactive template selection
ontologia init my-project

# List available templates
ontologia init --list-templates
```

### Option 2: Manual Copy
```bash
# Copy template manually
cp -r templates/simple-api ~/my-project
cd ~/my-project
# Follow template README
```

## 🎯 Choosing the Right Template

| Use Case | Recommended Template | Why |
|----------|---------------------|-----|
| **Learning Ontologia** | `simple-api` | Minimal complexity, focus on basics |
| **Simple CRUD API** | `simple-api` | All you need, nothing extra |
| **Data Analytics** | `data-platform` | DuckDB + dbt for data processing |
| **Knowledge Management** | `knowledge-graph` | Graph traversals for complex relationships |
| **Enterprise Application** | `enterprise-workflows` | All features for production use |
| **Microservice** | `simple-api` | Lightweight, easy to containerize |
| **Data Pipeline** | `data-platform` | Built-in ETL and orchestration |

## 🔄 Upgrading Between Templates

You can start simple and upgrade:

```bash
# Start with simple-api
ontologia init --template simple-api my-project

# Later upgrade to data-platform
ontologia upgrade --template data-platform

# Or go all the way to enterprise
ontologia upgrade --template enterprise-workflows
```

## 🎨 Customizing Templates

Templates are designed to be customized:

```bash
# After creating project
cd my-project

# Add your own dependencies
pip install additional-package

# Modify docker-compose.yml for your needs
vim docker-compose.yml

# Add your examples
cp examples/basic_setup.py examples/my_use_case.py
```

## 📚 Learning Path

1. **Start with `simple-api`** - Learn the basics
2. **Try `data-platform`** - Add analytics capabilities
3. **Explore `knowledge-graph`** - Understand graph traversals
4. **Master `enterprise-workflows`** - Full production setup

Each template builds on concepts from the previous ones.

## 🆘 Need Help?

- **Template Issues**: Check template-specific README
- **General Questions**: See [main documentation](../../docs/index.md)
- **Examples**: Browse [examples directory](../project/examples/)
- **Community**: Open an issue on GitHub
