#!/usr/bin/env python3
"""Fix duplicate 'mo' arguments in Marimo notebooks"""

import os
import re


def fix_duplicate_mo(filepath):
    """Fix duplicate mo arguments in function definitions"""

    with open(filepath) as f:
        content = f.read()

    print(f"🔧 Fixing {filepath}...")

    # Fix duplicate mo arguments: def _(mo, mo): -> def _(mo):
    content = re.sub(r"def _\(mo, mo\):", "def _(mo):", content)

    # Fix other duplicate patterns like def _(mo, x, mo):
    content = re.sub(r"def _\(mo,([^)]*), mo\):", r"def _(mo,\1):", content)
    content = re.sub(r"def _\(([^,]*), mo, mo\):", r"def _(mo,\1):", content)

    # Write back
    with open(filepath, "w") as f:
        f.write(content)

    print(f"✅ Fixed {filepath}")


def main():
    """Fix all notebooks with duplicate mo issues"""
    notebooks_dir = "notebooks"

    # Notebooks that need fixing
    problem_notebooks = [
        "01_introduction.py",
        "02_graph_traversals.py",
        "03_analytics.py",
        "04_workflows.py",
        "05_agents_standalone.py",
        "demo_standalone.py",
    ]

    for notebook in problem_notebooks:
        filepath = os.path.join(notebooks_dir, notebook)
        if os.path.exists(filepath):
            fix_duplicate_mo(filepath)
        else:
            print(f"⚠️ {filepath} not found")

    print("🎉 All duplicate mo issues fixed!")


if __name__ == "__main__":
    main()
