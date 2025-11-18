"""
Setup module main entry point.

Provides the main function for the modular setup system.
"""

from __future__ import annotations

import sys
from typing import NoReturn

from scripts.setup.cli import SetupCLI


def main() -> NoReturn:
    """Main entry point for the setup system."""
    cli = SetupCLI()
    sys.exit(cli.main())


if __name__ == "__main__":
    main()
