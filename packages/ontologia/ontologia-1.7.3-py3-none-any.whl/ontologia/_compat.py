from __future__ import annotations

"""Compatibility helpers for typing features across Python versions.

Exports:
- override: decorator available in typing (3.12+) or typing_extensions; no-op fallback.
"""

try:  # Python 3.12+
    from typing import override as override  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    try:  # Python <3.12 with typing_extensions installed
        from typing_extensions import override as override  # type: ignore[assignment]
    except Exception:
        # Graceful fallback – preserves runtime behavior; type checkers may flag without extensions
        def override(func):  # type: ignore[no-redef]
            return func
