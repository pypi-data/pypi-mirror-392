from __future__ import annotations

import json
from typing import Any


def canonicalize(
    payload: dict[str, Any], *, mode: str = "json", exclude: tuple[str, ...] = ("signature",)
) -> bytes:
    data = {k: v for k, v in payload.items() if k not in exclude}
    m = (mode or "json").lower()
    if m == "cbor":
        try:
            import cbor2  # type: ignore

            # cbor2 dumps is canonical when sort_keys=True
            return cbor2.dumps(data, canonical=True)
        except ModuleNotFoundError:
            # Fallback to JSON if CBOR not available
            pass
    # Default: canonical JSON
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


__all__ = ["canonicalize"]
