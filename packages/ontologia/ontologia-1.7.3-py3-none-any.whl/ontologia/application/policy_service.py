from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ontologia.application.settings import get_settings


class PolicyService:
    """Evaluates role-based attribute access policies."""

    def __init__(self, principal: Any | None) -> None:
        settings = get_settings()
        mapping = dict(settings.abac_role_allowed_tags)
        self._enabled = bool(settings.abac_enabled)
        self._mapping = {role.lower(): set(tags or []) for role, tags in mapping.items()}
        self._principal = principal

    def is_enabled(self) -> bool:
        return self._enabled

    def allowed_tags(self) -> set[str]:
        if not self._principal:
            return set()
        roles = getattr(self._principal, "roles", None)
        if not roles:
            return set()
        tags: set[str] = set()
        for role in roles:
            allowed = self._mapping.get(str(role).lower())
            if not allowed:
                continue
            if "*" in allowed:
                return {"*"}
            tags.update(allowed)
        return tags

    def is_property_allowed(self, property_tags: Iterable[str]) -> bool:
        if not self._enabled:
            return True
        tags = list(property_tags or [])
        if not tags:
            return True
        principal_tags = self.allowed_tags()
        if "*" in principal_tags:
            return True
        return any(tag in principal_tags for tag in tags)
