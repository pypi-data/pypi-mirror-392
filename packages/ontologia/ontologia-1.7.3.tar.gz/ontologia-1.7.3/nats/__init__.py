"""Lightweight test stub for the `nats` package.

This module exists to satisfy imports in environments where `nats-py`
is not installed. Tests patch `nats.connect` to provide an AsyncMock,
so the default implementation here is minimal.
"""

from __future__ import annotations

from typing import Any


async def connect(**kwargs: Any):  # pragma: no cover - test stub
    raise RuntimeError(
        "nats.connect called on stub. Tests should patch nats.connect to a mock."
    )

