#!/usr/bin/env python3
"""Fix all duplicate 'mo' arguments in Marimo notebooks"""

import os
import re


def fix_all_duplicate_mo(filepath):
    """Fix all duplicate mo arguments in function definitions"""

    with open(filepath) as f:
        content = f.read()

    print(f"🔧 Fixing {filepath}...")

    # Fix all patterns of duplicate mo in function definitions
    # Pattern 1: def _(mo, mo): -> def _(mo):
    content = re.sub(r"def _\(mo, mo\):", "def _(mo):", content)

    # Pattern 2: def _(mo, mo, x): -> def _(mo, x):
    content = re.sub(r"def _\(mo, mo,([^)]*)\):", r"def _(mo,\1):", content)

    # Pattern 3: def _(mo, x, mo): -> def _(mo, x):
    content = re.sub(r"def _\(mo,([^)]*), mo\):", r"def _(mo,\1):", content)

    # Pattern 4: def _(x, mo, mo): -> def _(mo, x):
    content = re.sub(r"def _\(([^,]*), mo, mo\):", r"def _(mo,\1):", content)

    # Pattern 5: def _(x, mo, y, mo): -> def _(mo, x, y):
    content = re.sub(r"def _\(([^,]*), mo,([^)]*), mo\):", r"def _(mo,\1,\2):", content)

    # Pattern 6: def _(mo, x, mo, y): -> def _(mo, x, y):
    content = re.sub(r"def _\(mo,([^)]*), mo,([^)]*)\):", r"def _(mo,\1,\2):", content)

    # General pattern: remove duplicate mo from any position
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if "def _(" in line and "mo, mo" in line:
            # Find the function definition
            match = re.search(r"def _\((.*?)\):", line)
            if match:
                args = match.group(1)
                # Remove duplicate mo
                args_list = [arg.strip() for arg in args.split(",")]
                # Keep only one mo and maintain order
                seen_mo = False
                new_args = []
                for arg in args_list:
                    if arg == "mo":
                        if not seen_mo:
                            new_args.append(arg)
                            seen_mo = True
                    else:
                        new_args.append(arg)

                # Rebuild the function definition
                new_args_str = ", ".join(new_args)
                line = line.replace(match.group(0), f"def _({new_args_str}):")

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

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
            fix_all_duplicate_mo(filepath)
        else:
            print(f"⚠️ {filepath} not found")

    print("🎉 All duplicate mo issues fixed!")


if __name__ == "__main__":
    main()
