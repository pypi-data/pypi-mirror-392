# Basic CRUD Example

Simple example demonstrating CRUD operations with Ontologia.

## 📋 Overview

This example shows:
- Object type definition
- Link type definition
- Basic CRUD operations
- Simple queries

## 🗂️ Files

- `schema/objects.yaml` - Object type definitions
- `schema/links.yaml` - Link type definitions
- `scripts/setup.py` - Database setup script
- `ontologia.toml` - Project configuration

## 🚀 Quick Start

```bash
# From examples directory
cp basic-crud my-project
cd my-project

# Setup the project
python scripts/setup.py

# Start using Ontologia
ontologia serve
```

## 📊 Data Location

Project data is stored in:
```
../../.data/development/my-project/
```

This keeps the root clean while isolating project data.
