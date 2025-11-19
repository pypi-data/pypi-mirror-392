---
title: "Getting Started Overview"
description: "Introduction to ontologia platform and how to get started quickly"
audience: ["user", "designer", "operator"]
level: ["beginner"]
tags: ["getting-started", "overview", "tutorial"]
estimated_read_time: "10 min"
last_updated: "2024-10-26"
---

# 📖 Getting Started Overview

> **🎯 Purpose**: Understand what ontologia is and how to get started with your first ontology project.

## 🌟 What is Ontologia?

Ontologia is an **ontology-as-code platform** that helps you:

- **🏗️ Design** business domain models using simple YAML
- **🔧 Generate** complete APIs, databases, and SDKs automatically
- **⚡ Query** complex relationships with familiar SQL
- **🚀 Deploy** multi-tenant systems that scale
- **📊 Analyze** data with integrated BI tools

### **Why Ontologia?**

#### **🔄 Traditional Approach**
```bash
# ❌ Multiple disconnected systems
1. Design database schema (SQL DDL)
2. Create API endpoints (REST/GraphQL)
3. Write business logic (application code)
4. Build client SDKs (multiple languages)
5. Set up data pipelines (ETL tools)
6. Configure monitoring (separate systems)
```

#### **🚀 Ontologia Approach**
```bash
# ✅ Single source of truth
1. Define domain model (YAML)
2. ontologia build  # Generates everything
3. ontologia serve  # Ready to use!
```

## 🎯 Who Should Use Ontologia?

### **🧬 Ontology Designers**
- **Role**: Business analysts, domain experts
- **Goal**: Model business concepts without coding
- **Skills**: YAML, business domain knowledge
- **Outcome**: Complete API and database from domain model

### **🏢 System Implementers**
- **Role**: DevOps engineers, system architects
- **Goal**: Deploy production systems for customers
- **Skills**: Docker, configuration, monitoring
- **Outcome**: Multi-tenant, secure, scalable deployment

### **👨‍💻 Framework Developers**
- **Role**: Software engineers, platform developers
- **Goal**: Extend and contribute to the core platform
- **Skills**: Python, APIs, database design
- **Outcome**: Enhanced platform with new features

### **📊 Data Analysts**
- **Role**: Business analysts, data scientists
- **Goal**: Query and analyze complex relationships
- **Skills**: SQL, data analysis, visualization
- **Outcome**: Insights from connected data

## 🚀 Quick Start Journey

### **Step 1: Installation (5 minutes)**
```bash
# Install ontologia
pip install ontologia

# Verify installation
ontologia --version
# → ontologia 0.2.4
```

### **Step 2: Create Your First Ontology (10 minutes)**
```bash
# Create a new ontology project
ontologia init customer-management
cd customer-management

# Explore the generated structure
tree .
# ├── schema/
# │   ├── objects.yaml
# │   ├── links.yaml
# │   └── actions.yaml
# ├── config/
# │   └── ontologia.toml
# ├── alembic/
# └── README.md
```

### **Step 3: Define Your Domain Model (15 minutes)**
```yaml
# schema/objects.yaml
object_types:
  Customer:
    description: "Business customer account"
    properties:
      name:
        type: string
        required: true
        display_name: "Full Name"
      email:
        type: string
        format: email
        required: true
        display_name: "Email Address"
      tier:
        type: enum
        values: [basic, premium, enterprise]
        default: basic
        display_name: "Customer Tier"

  Product:
    description: "Products we sell"
    properties:
      sku:
        type: string
        required: true
        pattern: "^[A-Z0-9]{8}$"
        display_name: "Product SKU"
      name:
        type: string
        required: true
        display_name: "Product Name"
      price:
        type: decimal
        required: true
        min_value: 0
        display_name: "Price"
```

```yaml
# schema/links.yaml
link_types:
  Customer_Purchases:
    description: "Customer purchases products"
    source: Customer
    target: Product
    properties:
      quantity:
        type: integer
        required: true
        min_value: 1
        display_name: "Quantity"
      purchase_date:
        type: datetime
        required: true
        display_name: "Purchase Date"
      unit_price:
        type: decimal
        required: true
        display_name: "Unit Price"
```

### **Step 4: Generate and Run (5 minutes)**
```bash
# Validate your schema
ontologia validate

# Generate API, database, and SDK
ontologia build

# Start the development server
ontologia serve
# → 🚀 Ontologia server running on http://localhost:8000
# → 📚 API docs available at http://localhost:8000/docs
# → 🗄️ Database created at .data/development/ontology.db
```

### **Step 5: Explore Your API (10 minutes)**
```bash
# Create a customer
curl -X POST "http://localhost:8000/v2/objects" \
  -H "Content-Type: application/json" \
  -d '{
    "object_type": "Customer",
    "properties": {
      "name": "John Doe",
      "email": "john@example.com",
      "tier": "premium"
    }
  }'

# Create a product
curl -X POST "http://localhost:8000/v2/objects" \
  -H "Content-Type: application/json" \
  -d '{
    "object_type": "Product",
    "properties": {
      "sku": "PROD12345",
      "name": "Wireless Mouse",
      "price": "29.99"
    }
  }'

# Link customer to product (purchase)
curl -X POST "http://localhost:8000/v2/links" \
  -H "Content-Type: application/json" \
  -d '{
    "link_type": "Customer_Purchases",
    "source_object_id": "CUSTOMER_ID",
    "target_object_id": "PRODUCT_ID",
    "properties": {
      "quantity": 2,
      "purchase_date": "2024-10-26T12:00:00Z",
      "unit_price": "29.99"
    }
  }'
```

## 🎯 What You Get Automatically

### **🔧 Generated Components**
```bash
# API Endpoints
GET    /v2/object-types          # List all object types
POST   /v2/object-types          # Create new object type
GET    /v2/objects               # List objects
POST   /v2/objects               # Create object
GET    /v2/links                 # List relationships
POST   /v2/links                 # Create relationship

# Database Schema
CREATE TABLE customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  tier TEXT DEFAULT 'basic',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
  id TEXT PRIMARY KEY,
  sku TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL
);

CREATE TABLE customer_purchases (
  id TEXT PRIMARY KEY,
  source_customer_id TEXT NOT NULL,
  target_product_id TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  purchase_date TIMESTAMP NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (source_customer_id) REFERENCES customers(id),
  FOREIGN KEY (target_product_id) REFERENCES products(id)
);

# Type-Safe SDK (Python example)
from ontologia_sdk import OntologiaClient

client = OntologiaClient("http://localhost:8000")

# Create objects with type safety
customer = client.objects.create(
    object_type="Customer",
    properties={
        "name": "John Doe",
        "email": "john@example.com",
        "tier": "premium"
    }
)

# Query with SQL
results = client.query.execute("""
  SELECT c.name, p.name, cp.quantity
  FROM Customer c
  JOIN Customer_Purchases cp ON c.id = cp.source_id
  JOIN Product p ON cp.target_id = p.id
  WHERE c.tier = 'premium'
""")
```

## 📊 Query Examples

### **Basic Queries**
```sql
-- List all premium customers
SELECT name, email, tier
FROM Customer
WHERE tier = 'premium';

-- Find products over $100
SELECT sku, name, price
FROM Product
WHERE price > 100.00;
```

### **Graph Queries**
```sql
-- Find what premium customers bought
SELECT c.name, p.name, cp.quantity, cp.purchase_date
FROM Customer c
JOIN Customer_Purchases cp ON c.id = cp.source_id
JOIN Product p ON cp.target_id = p.id
WHERE c.tier = 'premium'
  AND cp.purchase_date >= '2024-01-01'
ORDER BY cp.purchase_date DESC;

-- Find customers who bought electronics
SELECT DISTINCT c.name, c.email
FROM Customer c
JOIN Customer_Purchases cp ON c.id = cp.source_id
JOIN Product p ON cp.target_id = p.id
WHERE p.category = 'electronics';
```

### **Analytics Queries**
```sql
-- Customer spending analysis
SELECT
  c.tier,
  COUNT(DISTINCT c.id) as customer_count,
  SUM(cp.quantity * cp.unit_price) as total_spending,
  AVG(cp.quantity * cp.unit_price) as avg_spending
FROM Customer c
JOIN Customer_Purchases cp ON c.id = cp.source_id
GROUP BY c.tier
ORDER BY total_spending DESC;

-- Popular products
SELECT
  p.name,
  SUM(cp.quantity) as total_sold,
  SUM(cp.quantity * cp.unit_price) as revenue
FROM Product p
JOIN Customer_Purchases cp ON p.id = cp.target_id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 10;
```

## 🎯 Next Steps in Your Journey

### **🌱 If you're new to ontologies:**
1. [⚡ Quick Start Guide](quick-start.md) - Step-by-step tutorial
2. [🧬 Schema Basics](../ontology-design/schema-basics.md) - Learn core concepts
3. [🎨 Design Patterns](../ontology-design/design-patterns.md) - Common patterns

### **🏗️ If you want to design business models:**
1. [🧬 Schema Design Guide](../ontology-design/schema-basics.md) - Detailed design principles
2. [📋 Business Rules](../ontology-design/business-rules.md) - Validation and constraints
3. [🎨 Real Examples](../ontology-design/examples/) - Industry-specific examples

### **🚀 If you need production deployment:**
1. [📦 Installation Guide](../deployment/installation.md) - Production setup
2. [⚙️ Configuration](../deployment/configuration.md) - System configuration
3. [🏢 Multi-Tenancy](../deployment/multi-tenancy.md) - Multi-tenant setup

### **🔧 If you want to extend the platform:**
1. [🏗️ Architecture Overview](../framework-development/architecture.md) - System design
2. [🤝 Contribution Guide](../framework-development/contribution-guide.md) - How to contribute
3. [🧪 Testing Strategy](../framework-development/testing-strategy.md) - Testing approach

## 🛠️ Development Tools

### **🔧 CLI Commands**
```bash
# Project management
ontologia init <name>           # Create new project
ontologia build                # Generate code
ontologia serve                # Start development server
ontologia validate             # Validate schema

# Database operations
ontologia db migrate           # Run database migrations
ontologia db reset             # Reset database
ontologia db seed              # Load sample data

# Code generation
ontologia generate sdk         # Generate client SDKs
ontologia generate docs        # Generate documentation
ontologia generate types       # Generate type definitions
```

### **🌐 Web Interface**
When you run `ontologia serve`, you get access to:

- **📚 API Documentation**: `/docs` - Interactive API docs
- **🔍 Query Interface**: `/query` - SQL query playground
- **📊 Dashboard**: `/dashboard` - System overview
- **🗄️ Schema Explorer**: `/schema` - Visual schema browser

## 🎯 Success Metrics

### **⏱️ Time to First Value**
- **Installation**: < 5 minutes
- **First Schema**: < 15 minutes
- **Running API**: < 30 minutes
- **First Query**: < 45 minutes

### **📈 Learning Progression**
1. **Day 1**: Basic schema and API
2. **Week 1**: Complex relationships and queries
3. **Month 1**: Production deployment
4. **Quarter 1**: Custom extensions and contributions

---

## 🎉 Ready to Start?

**🚀 [Begin with the Quick Start Guide](quick-start.md)**

Or explore specific paths based on your role:

- **🧬 [I want to design ontologies](../ontology-design/schema-basics.md)**
- **🚀 [I need to deploy production](../deployment/installation.md)**
- **🔧 [I want to contribute code](../framework-development/contribution-guide.md)**

> **💡 Need help?** [Join our community](https://github.com/kevinqz/ontologia/discussions) or [create an issue](https://github.com/kevinqz/ontologia/issues) for support.
