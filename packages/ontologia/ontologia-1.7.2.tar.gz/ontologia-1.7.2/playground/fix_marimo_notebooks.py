#!/usr/bin/env python3
"""Fix all Marimo notebooks to follow proper structure"""

import os
import re


def fix_marimo_notebook(filepath):
    """Fix a single Marimo notebook to follow proper structure"""

    with open(filepath) as f:
        content = f.read()

    # Check if already has proper structure
    if "import marimo as mo" in content and "__generated_with" in content:
        print(f"✅ {filepath} already has proper structure")
        return True

    print(f"🔧 Fixing {filepath}...")

    # Extract imports
    imports = []
    non_import_lines = []

    lines = content.split("\n")
    i = 0

    # Extract imports at the top
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line)
            i += 1
        elif (
            line == "" and i < len(lines) and lines[i + 1].strip().startswith(("import ", "from "))
        ):
            imports.append(line)
            i += 1
        else:
            break

    # Find the rest of the content
    rest_content = "\n".join(lines[i:])

    # Build new content with proper Marimo structure
    new_content = f"""# {os.path.basename(filepath).replace('.py', '').replace('_', ' ').title()} - Marimo Notebook

import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


"""

    # Add the rest of the content, fixing function signatures
    rest_content = re.sub(
        r"@app\.cell\s+def __\((.*?)\):", r"@app.cell\ndef _(mo, \1):", rest_content
    )
    rest_content = re.sub(r"@app\.cell\s+def __\(\):", r"@app.cell\ndef _(mo):", rest_content)

    new_content += rest_content

    # Write back
    with open(filepath, "w") as f:
        f.write(new_content)

    print(f"✅ Fixed {filepath}")
    return True


def main():
    """Fix all notebooks"""
    notebooks_dir = "notebooks"

    if not os.path.exists(notebooks_dir):
        print(f"❌ Directory {notebooks_dir} not found")
        return

    notebooks = [f for f in os.listdir(notebooks_dir) if f.endswith(".py")]

    print(f"🔍 Found {len(notebooks)} notebooks to fix")

    for notebook in notebooks:
        filepath = os.path.join(notebooks_dir, notebook)
        fix_marimo_notebook(filepath)

    print("🎉 All notebooks fixed!")


if __name__ == "__main__":
    main()
