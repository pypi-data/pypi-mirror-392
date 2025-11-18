#!/usr/bin/env python3
"""Fix all notebooks to work as Python scripts"""

import os
import subprocess


def fix_variable_duplicates(filepath):
    """Fix duplicate variable names by prefixing with cell names"""

    with open(filepath) as f:
        content = f.read()

    print(f"🔧 Fixing duplicates in {filepath}...")

    # Find all cells and their variable definitions
    lines = content.split("\n")
    fixed_lines = []
    cell_counter = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if "@app.cell" in line:
            cell_counter += 1
            cell_name = f"cell_{cell_counter}"

            # Add the cell line
            fixed_lines.append(line)
            i += 1

            # Process the cell content
            cell_lines = []
            while i < len(lines) and not lines[i].startswith("@app.cell"):
                cell_lines.append(lines[i])
                i += 1

            # Fix variable names in this cell
            cell_content = "\n".join(cell_lines)

            # Common problematic variables
            replacements = {
                "df =": f"{cell_name}_df =",
                "customers_df =": f"{cell_name}_customers_df =",
                "products_df =": f"{cell_name}_products_df =",
                "orders_df =": f"{cell_name}_orders_df =",
                "count =": f"{cell_name}_count =",
                "for category, count in": f"for category, {cell_name}_count in",
                ": {count}": f": {{{cell_name}_count}}",
            }

            for old, new in replacements.items():
                cell_content = cell_content.replace(old, new)

            fixed_lines.extend(cell_content.split("\n"))
            i -= 1  # Adjust because we'll increment at the end of loop
        else:
            fixed_lines.append(line)

        i += 1

    fixed_content = "\n".join(fixed_lines)

    with open(filepath, "w") as f:
        f.write(fixed_content)

    print(f"✅ Fixed duplicates in {filepath}")


def fix_missing_imports(filepath):
    """Add missing imports to the first cell"""

    with open(filepath) as f:
        content = f.read()

    print(f"🔧 Checking imports in {filepath}...")

    # Check if pandas is imported
    if "import pandas" not in content and "pd." in content:
        print(f"   Adding pandas import to {filepath}")

        # Find the first cell and add pandas import
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "@app.cell" in line and "def _():" in lines[i + 1]:
                # Find the return statement in this cell
                j = i + 2
                while j < len(lines) and not lines[j].strip().startswith("return"):
                    j += 1

                if j < len(lines):
                    # Add pandas import before return
                    lines.insert(j, "    import pandas as pd")

                    # Add pd to return if it exists
                    if "return (" in lines[j + 1]:
                        lines[j + 1] = lines[j + 1].replace("return (", "return (pd, ")
                    elif "return " in lines[j + 1]:
                        lines[j + 1] = lines[j + 1].replace("return ", "return pd, ")

                    content = "\n".join(lines)
                    break

    with open(filepath, "w") as f:
        f.write(content)


def install_missing_packages():
    """Install missing packages"""
    print("📦 Installing missing packages...")

    packages = ["matplotlib", "openpyxl"]

    for package in packages:
        try:
            result = subprocess.run(["uv", "add", package], capture_output=True, text=True, cwd=".")

            if result.returncode == 0:
                print(f"✅ Installed {package}")
            else:
                print(f"⚠️ Could not install {package}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")


def main():
    """Fix all notebooks"""
    notebooks_dir = "notebooks"

    print("🚀 Starting complete notebook fix...")

    # Install missing packages first
    install_missing_packages()

    # List all notebooks
    notebooks = [f for f in os.listdir(notebooks_dir) if f.endswith(".py")]

    # Skip the ones that already work
    working = ["demo_standalone.py", "01_introduction_fixed.py"]
    to_fix = [n for n in notebooks if n not in working]

    print(f"📝 Fixing {len(to_fix)} notebooks...")

    for notebook in to_fix:
        filepath = os.path.join(notebooks_dir, notebook)

        # Fix duplicates
        fix_variable_duplicates(filepath)

        # Fix imports
        fix_missing_imports(filepath)

    print("🎉 All notebooks fixed!")

    # Test all notebooks
    print("\n🧪 Testing all notebooks...")
    for notebook in notebooks:
        filepath = os.path.join(notebooks_dir, notebook)
        print(f"🔍 Testing {notebook}...")

        result = subprocess.run(
            ["uv", "run", "python", filepath], capture_output=True, text=True, cwd="."
        )

        if result.returncode == 0:
            print(f"✅ {notebook}: WORKS!")
        else:
            print(f"❌ {notebook}: Still has issues")
            print(f"   Error: {result.stderr[:200]}...")


if __name__ == "__main__":
    main()
