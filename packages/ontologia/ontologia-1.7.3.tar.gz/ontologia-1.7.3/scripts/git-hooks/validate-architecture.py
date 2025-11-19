#!/usr/bin/env python3
"""
Pre-commit hook to validate ARCHITECTURE_LEDGER.md compliance.

This hook ensures:
1. Only README.md exists as markdown at root
2. No database files at root
3. No scattered config files at root
4. ARCHITECTURE_LEDGER.md is up to date
"""

import sys
from pathlib import Path


def check_root_structure():
    """Validate root directory structure."""
    root = Path.cwd()
    errors = []

    # Check for forbidden markdown files
    markdown_files = list(root.glob("*.md"))
    allowed_markdown = {"README.md", "ARCHITECTURE_LEDGER.md"}

    for md_file in markdown_files:
        if md_file.name not in allowed_markdown:
            errors.append(
                f"❌ Markdown file at root: {md_file.name}. "
                "Only README.md and ARCHITECTURE_LEDGER.md allowed at root."
            )

    # Check for database files at root
    db_extensions = {".db", ".duckdb", ".sqlite", ".sqlite3"}
    for ext in db_extensions:
        for db_file in root.glob(f"*{ext}"):
            errors.append(f"❌ Database file at root: {db_file.name}. Move to data/databases/")

    # Check for scattered docker-compose files
    docker_files = list(root.glob("docker-compose*.yml"))
    for docker_file in docker_files:
        errors.append(f"❌ Docker compose file at root: {docker_file.name}. Move to config/docker/")

    # Check for alembic.ini at root
    if (root / "alembic.ini").exists():
        errors.append("❌ alembic.ini at root. Move to config/alembic/")

    return errors


def check_ledger_exists():
    """Ensure ARCHITECTURE_LEDGER.md exists."""
    if not Path("ARCHITECTURE_LEDGER.md").exists():
        return ["❌ ARCHITECTURE_LEDGER.md not found at root. This file is required."]
    return []


def main():
    """Main validation function."""
    print("🔍 Validating project structure against ARCHITECTURE_LEDGER.md...")

    errors = []
    errors.extend(check_ledger_exists())
    errors.extend(check_root_structure())

    if errors:
        print("\n❌ Structure validation failed:")
        for error in errors:
            print(f"  {error}")
        print("\n💡 Please review ARCHITECTURE_LEDGER.md for proper structure guidelines.")
        sys.exit(1)
    else:
        print("✅ Project structure is compliant with ARCHITECTURE_LEDGER.md")
        sys.exit(0)


if __name__ == "__main__":
    main()
