# 📚 Project Examples

This directory contains example projects and templates for different use cases.

## 🎯 Available Examples

### `basic-crud/`
Simple CRUD operations with basic object types and relationships.

### `analytics-pipeline/`
Data pipeline example with analytics and reporting.

### `real-time-sync/`
Real-time data synchronization example.

### `multi-tenant/`
Multi-tenant architecture example.

## 🚀 Getting Started

1. Copy an example directory:
```bash
cp examples/basic-crud my-project
cd my-project
```

2. Configure your project:
```bash
# Edit ontologia.toml with your settings
```

3. Initialize the project:
```bash
ontologia init
```

## 📁 Project Structure

Each example project follows this structure:
```
my-project/
├── ontologia.toml          # Project configuration
├── schema/                 # Object and link type definitions
├── data/                   # Project-specific data
├── scripts/                # Project scripts
└── README.md              # Project documentation
```

## 🔧 Data Management

- **Local data**: Stored in `.data/{environment}/`
- **Shared data**: Use `.data/shared/` for cross-project data
- **Environment isolation**: Each environment has separate data
