#!/usr/bin/env python3
"""Test script for example datasets"""


import pandas as pd

print("🧪 Testing Example Datasets")
print("=" * 40)

# Test customers.csv
try:
    customers = pd.read_csv("data/examples/customers.csv")
    print(f"✅ customers.csv: {len(customers)} rows, {len(customers.columns)} columns")
    print(f"   Columns: {list(customers.columns)}")
except Exception as e:
    print(f"❌ customers.csv: {e}")

# Test products.csv
try:
    products = pd.read_csv("data/examples/products.csv")
    print(f"✅ products.csv: {len(products)} rows, {len(products.columns)} columns")
    print(f"   Columns: {list(products.columns)}")
except Exception as e:
    print(f"❌ products.csv: {e}")

# Test orders.parquet
try:
    orders = pd.read_parquet("data/examples/orders.parquet")
    print(f"✅ orders.parquet: {len(orders)} rows, {len(orders.columns)} columns")
    print(f"   Columns: {list(orders.columns)}")
except Exception as e:
    print(f"❌ orders.parquet: {e}")

print("\n🔗 Testing Relationships")
print("=" * 40)

# Test data relationships
try:
    customers = pd.read_csv("data/examples/customers.csv")
    products = pd.read_csv("data/examples/products.csv")
    orders = pd.read_parquet("data/examples/orders.parquet")

    # Check customer references
    invalid_customers = set(orders["customer_id"]) - set(customers["customer_id"])
    print(f"Customer references: {len(invalid_customers)} invalid")

    # Check product references
    invalid_products = set(orders["product_id"]) - set(products["product_id"])
    print(f"Product references: {len(invalid_products)} invalid")

    if not invalid_customers and not invalid_products:
        print("✅ All relationships are valid!")
    else:
        print("⚠️ Some invalid relationships found")

except Exception as e:
    print(f"❌ Relationship test failed: {e}")

print("\n📊 Data Quality Summary")
print("=" * 40)
try:
    print(f"Total Customers: {len(customers)}")
    print(f"Total Products: {len(products)}")
    print(f"Total Orders: {len(orders)}")
    print(f'Total Revenue: ${orders["total_amount"].sum():,.2f}')
    print(f'Cities: {customers["city"].nunique()}')
    print(f'Product Categories: {products["category"].nunique()}')
except:
    print("Could not generate summary")

print("\n🎯 Test Complete!")
