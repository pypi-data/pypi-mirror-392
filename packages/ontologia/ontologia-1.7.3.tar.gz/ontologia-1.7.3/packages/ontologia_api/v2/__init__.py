"""API v2 - Foundry-compatible REST API."""

__all__ = ["BOUNDED_CONTEXTS"]


def __getattr__(name: str):  # pragma: no cover - lazy import helper
    if name == "BOUNDED_CONTEXTS":
        from .bounded_contexts import BOUNDED_CONTEXTS

        return BOUNDED_CONTEXTS
    raise AttributeError(name)
