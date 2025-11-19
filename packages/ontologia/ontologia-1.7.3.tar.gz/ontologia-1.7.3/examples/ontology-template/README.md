# 🧬 Ontology Repository Template

> **🎯 PURPOSE**: Starting template for business-specific ontology repositories.

## 📋 Repository Structure

```bash
customer-abc-ontology/
├── README.md                    # 📖 This file
├── pyproject.toml              # 📦 Python dependencies
├── .gitignore                  # 🚫 Git ignore patterns
├── schema/                     # 🧬 Business domain models
│   ├── objects.yaml           # Business object types
│   ├── links.yaml             # Business link types
│   └── actions.yaml           # Business actions
├── config/                     # ⚙️ Ontology configuration
│   ├── ontologia.toml         # Main configuration
│   └── alembic.ini            # Database migration config
├── alembic/                    # 🗄️ Database migrations
│   ├── env.py                 # Migration environment
│   ├── migrations/            # Migration scripts
│   └── script.py.mako         # Migration template
├── scripts/                    # 🛠️ Ontology utilities
│   ├── setup.py               # Database setup
│   ├── seed.py                # Data seeding
│   └── validate.py            # Schema validation
├── tests/                      # 🧪 Ontology tests
│   ├── test_schema.py         # Schema validation tests
│   ├── test_migrations.py     # Migration tests
│   └── test_business_rules.py # Business logic tests
└── .data/                      # 🗄️ Ontology data (gitignored)
    ├── development/           # Development data
    ├── staging/              # Staging data
    └── production/           # Production data
```

## 🚀 Getting Started

### 1. **Create New Ontology Repository**
```bash
# Clone this template
git clone https://github.com/your-org/ontologia-template customer-abc-ontology
cd customer-abc-ontology

# Customize for your customer
echo "# Customer ABC Ontology" > README.md
edit pyproject.toml  # Update project metadata
```

### 2. **Define Business Models**
```yaml
# schema/objects.yaml
object_types:
  Customer:
    description: "Business customer"
    properties:
      name: {type: string, required: true}
      email: {type: string, format: email}
      tier: {type: enum, values: [basic, premium, enterprise]}

  Product:
    description: "Products we sell"
    properties:
      sku: {type: string, required: true}
      name: {type: string, required: true}
      price: {type: decimal, precision: 10, scale: 2}
```

```yaml
# schema/links.yaml
link_types:
  Customer_Purchases:
    description: "Customer purchases products"
    source: Customer
    target: Product
    properties:
      quantity: {type: integer, min: 1}
      purchase_date: {type: datetime, required: true}
      amount: {type: decimal, precision: 10, scale: 2}
```

### 3. **Configure Ontology**
```toml
# config/ontologia.toml
[ontology]
name = "customer-abc-ontology"
version = "1.0.0"
description = "Customer ABC business domain ontology"

[database]
url = "sqlite:///.data/development/ontology.db"
echo = true

[api]
host = "localhost"
port = 8000
debug = true

[business]
customer_tiers = ["basic", "premium", "enterprise"]
default_currency = "USD"
tax_rate = 0.0875
```

### 4. **Setup Database**
```bash
# Install dependencies
pip install -e .

# Setup database
python scripts/setup.py

# Create initial migration
alembic -c config/alembic/alembic.ini revision --autogenerate -m "Initial schema"

# Run migrations
alembic -c config/alembic/alembic.ini upgrade head
```

### 5. **Seed Initial Data**
```bash
# Load sample data
python scripts/seed.py
```

### 6. **Run Tests**
```bash
# Validate schema
python scripts/validate.py

# Run tests
pytest tests/ -v
```

### 7. **Start Development Server**
```bash
# Start API server
ontologia serve --config config/ontologia.toml
```

## 📋 Development Workflow

### **Daily Development**
```bash
# 1. Make changes to schema
edit schema/objects.yaml
edit schema/links.yaml

# 2. Generate migration
alembic -c config/alembic/alembic.ini revision --autogenerate -m "Add new feature"

# 3. Apply migration
alembic -c config/alembic/alembic.ini upgrade head

# 4. Test changes
pytest tests/ -v

# 5. Commit changes
git add .
git commit -m "feat: add new business feature"
```

### **Environment Management**
```bash
# Development (default)
export ONTOLOGIA_ENV=development
ontologia serve

# Staging
export ONTOLOGIA_ENV=staging
ontologia serve --config config/staging.toml

# Production
export ONTOLOGIA_ENV=production
ontologia serve --config config/production.toml
```

## 🧪 Testing Strategy

### **Schema Validation**
```python
# tests/test_schema.py
def test_customer_object_type():
    """Validate customer object type definition"""
    schema = load_schema()
    customer_type = schema.object_types["Customer"]

    assert "name" in customer_type.properties
    assert customer_type.properties["name"].required
    assert "email" in customer_type.properties
```

### **Business Rules**
```python
# tests/test_business_rules.py
def test_customer_tier_validation():
    """Validate customer tier business rules"""
    customer = Customer(name="Test", email="test@example.com", tier="invalid")

    with pytest.raises(ValidationError):
        customer.validate()
```

### **Migration Testing**
```python
# tests/test_migrations.py
def test_migration_upgrade_downgrade():
    """Test migration can be upgraded and downgraded"""
    # Test upgrade
    alembic_upgrade("head")

    # Test downgrade
    alembic_downgrade("base")

    # Test upgrade again
    alembic_upgrade("head")
```

## 🚀 Deployment

### **Development Deployment**
```bash
# Use development data
export ONTOLOGIA_ENV=development
ontologia serve --host 0.0.0.0 --port 8000
```

### **Staging Deployment**
```bash
# Use staging data
export ONTOLOGIA_ENV=staging
ontologia serve --config config/staging.toml
```

### **Production Deployment**
```bash
# Use production data
export ONTOLOGIA_ENV=production
ontologia serve --config config/production.toml
```

## 📊 Monitoring and Maintenance

### **Health Checks**
```bash
# Check database connection
ontologia health --database

# Check schema consistency
ontologia health --schema

# Check API endpoints
ontologia health --api
```

### **Backup and Recovery**
```bash
# Backup database
ontologia backup --output backup_$(date +%Y%m%d).db

# Restore database
ontologia restore --input backup_20241026.db
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Database
export DATABASE_URL="sqlite:///.data/development/ontology.db"

# API
export API_HOST="localhost"
export API_PORT="8000"
export API_DEBUG="true"

# Business
export DEFAULT_CURRENCY="USD"
export TAX_RATE="0.0875"
```

### **Configuration Files**
```toml
# config/development.toml
[database]
url = "sqlite:///.data/development/ontology.db"
echo = true

[api]
debug = true
host = "localhost"
port = 8000

# config/production.toml
[database]
url = "postgresql://user:pass@prod-db:5432/ontology"
echo = false

[api]
debug = false
host = "0.0.0.0"
port = 8000
```

## 📚 Best Practices

### **Schema Design**
- ✅ Use clear, descriptive names
- ✅ Define required vs optional properties
- ✅ Include validation rules
- ✅ Document business meaning

### **Migration Management**
- ✅ Use descriptive migration messages
- ✅ Test migrations on sample data
- ✅ Keep migrations reversible
- ✅ Review migrations before deploying

### **Testing**
- ✅ Test schema validation
- ✅ Test business rules
- ✅ Test migration upgrades/downgrades
- ✅ Test API endpoints

### **Security**
- ✅ Never commit sensitive data
- ✅ Use environment variables for secrets
- ✅ Validate all inputs
- ✅ Implement proper authentication

---

## 🎯 **Next Steps**

1. **Customize** the template for your business domain
2. **Define** your object and link types
3. **Implement** business rules and validation
4. **Create** comprehensive tests
5. **Deploy** to your target environment

**🚀 This template provides a solid foundation for business-specific ontology development!**
