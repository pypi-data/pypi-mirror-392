"""
Warnings Configuration for Ontologia

State-of-the-Art warning handling strategy:
1. Document all known warnings with their impact assessment
2. Categorize by severity and action required
3. Provide migration paths for deprecated features
4. Enable strict warnings for new code development
"""

from __future__ import annotations

import os
import warnings


class WarningRegistry:
    """Central registry for all warnings in the project."""

    # Known external dependency warnings - use proper filter format
    EXTERNAL_FILTERS = (
        # Keep this conservative; prefer module filters over class names that may not exist across versions
        {"action": "ignore", "category": UserWarning, "module": r"pydantic\."},
        {"action": "ignore", "category": DeprecationWarning, "module": r"\btyper\b"},
    )

    # Internal warnings that should be errors
    INTERNAL_ERRORS = (UserWarning, SyntaxWarning, RuntimeWarning, FutureWarning, ImportWarning)

    @classmethod
    def configure_warnings(cls, *, strict_mode: bool = False) -> None:
        """
        Configure warnings based on environment.

        Args:
            strict_mode: If True, treat more warnings as errors (for CI/development)
        """
        # Ignore known external warnings
        for f in cls.EXTERNAL_FILTERS:
            warnings.filterwarnings(f["action"], category=f["category"], module=f.get("module"))

        # In strict mode, be more aggressive about warnings
        if strict_mode:
            for cat in cls.INTERNAL_ERRORS:
                warnings.filterwarnings("error", category=cat)

        # Always ignore legacy deprecation warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"distutils|imp")


def setup_warnings(*, strict_mode: bool | None = None) -> None:
    """Setup warning configuration for the application."""
    if strict_mode is None:
        strict_mode = os.getenv("ONTOLOGIA_STRICT_WARNINGS", "0") == "1"
    WarningRegistry.configure_warnings(strict_mode=strict_mode)


# Nota: não auto-aplica em import. Deixe o app chamar setup_warnings()
