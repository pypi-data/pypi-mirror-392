#!/usr/bin/env python3
"""
🛡️ Architecture Guardrails for Ontologia

Enforces architectural rules by preventing disallowed imports
outside of allowed locations. This helps maintain clean architecture
and prevents circular dependencies.

Usage:
    python scripts/guardrails_arch.py

Exit Codes:
    0 - Guardrails passed (no violations)
    1 - Guardrails failed (violations detected)

Configuration:
    The script uses hardcoded rules for disallowed imports and
    allowed paths. Modify the constants at the top of the file
    to adjust the rules.
"""

from __future__ import annotations

import ast
import os
from collections.abc import Iterable
from fnmatch import fnmatch

from scripts.utils import BaseCLI, ExitCode

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(REPO_ROOT, os.pardir))

# Disallow importing these modules outside allowed paths
DISALLOWED_PREFIXES = (
    "ontologia_api.services",
    "ontologia_api.repositories",
)

# Allowed locations (globs, relative to repo root)
ALLOWED_PATHS = (
    "packages/ontologia_api/**",
    "packages/ontologia_mcp/**",
    "tests/**",
    "docs/**",
    "example_project/**",
    "templates/project/examples/**",
    # Specific core exception needed for test monkeypatch compatibility
    "ontologia/application/instances_service.py",
)

# Ignore these directories during scan
IGNORE_DIRS = {
    ".git",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
}


def is_allowed(path: str) -> bool:
    rel = os.path.relpath(path, REPO_ROOT)
    for pat in ALLOWED_PATHS:
        if fnmatch(rel, pat):
            return True
    return False


def iter_py_files(root: str) -> Iterable[str]:
    for base, dirs, files in os.walk(root):
        # prune ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(base, f)


def check_file(path: str) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    if is_allowed(path):
        return violations
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src, filename=path)
    except Exception:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod == p or mod.startswith(p + ".") for p in DISALLOWED_PREFIXES):
                violations.append((path, mod))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if any(mod == p or mod.startswith(p + ".") for p in DISALLOWED_PREFIXES):
                    violations.append((path, mod))
    return violations


class GuardrailsCLI(BaseCLI):
    """CLI for architecture guardrails checking."""

    def __init__(self) -> None:
        super().__init__(
            name="guardrails_arch",
            description="Enforce architectural rules and prevent disallowed imports",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be checked without actually running",
        )
        parser.add_argument(
            "--list-allowed",
            action="store_true",
            help="List allowed paths and exit",
        )
        parser.add_argument(
            "--list-disallowed",
            action="store_true",
            help="List disallowed import prefixes and exit",
        )

    def run(self, args) -> ExitCode:
        if args.list_allowed:
            self._list_allowed_paths()
            return ExitCode.SUCCESS

        if args.list_disallowed:
            self._list_disallowed_prefixes()
            return ExitCode.SUCCESS

        if args.dry_run:
            self.logger.info("Dry run mode - would scan for violations")
            return ExitCode.SUCCESS

        return self._check_guardrails()

    def _list_allowed_paths(self) -> None:
        """List all allowed paths."""
        self.console.print("📁 Allowed paths:")
        for path in ALLOWED_PATHS:
            self.console.print(f"  - {path}")

    def _list_disallowed_prefixes(self) -> None:
        """List all disallowed import prefixes."""
        self.console.print("🚫 Disallowed import prefixes:")
        for prefix in DISALLOWED_PREFIXES:
            self.console.print(f"  - {prefix}")

    def _check_guardrails(self) -> ExitCode:
        """Perform the actual guardrails check."""
        self.logger.info("Starting architecture guardrails check")

        violations: list[tuple[str, str]] = []
        for path in iter_py_files(REPO_ROOT):
            violations.extend(check_file(path))

        if violations:
            self._report_violations(violations)
            return ExitCode.GENERAL_ERROR

        self.console.print("✅ Guardrails passed: no disallowed imports found.")
        self.logger.info("Guardrails check completed successfully")
        return ExitCode.SUCCESS

    def _report_violations(self, violations: list[tuple[str, str]]) -> None:
        """Report found violations."""
        self.console.print("\n❌ Guardrails failed: disallowed imports detected:\n")

        for path, mod in violations:
            rel = os.path.relpath(path, REPO_ROOT)
            self.console.print(f"- {rel}: imports '{mod}'")

        self.console.print("\n📁 Allowed locations:")
        for pat in ALLOWED_PATHS:
            self.console.print(f"  - {pat}")


def main() -> ExitCode:
    """Main entry point for the guardrails script."""
    cli = GuardrailsCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
