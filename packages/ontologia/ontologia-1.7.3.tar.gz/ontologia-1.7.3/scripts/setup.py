#!/usr/bin/env python3
"""
🚀 Ontologia Setup Script

Guided setup for different deployment modes:
- core: Minimal setup (PostgreSQL + API)
- analytics: Adds DuckDB + dbt + Dagster
- full: Complete enterprise stack

Usage:
    python scripts/setup.py --mode core
    python scripts/setup.py --mode analytics
    python scripts/setup.py --mode full
    python scripts/setup.py --interactive

This script now uses the modular setup system for better
maintainability and extensibility.
"""

from __future__ import annotations

from scripts.setup import main as setup_main


# Re-export the main function from the modular setup system
def main() -> int:
    """Main entry point for backward compatibility."""
    return setup_main()


if __name__ == "__main__":
    raise SystemExit(main())
