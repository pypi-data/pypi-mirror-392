from __future__ import annotations

from ontologia.application.actions_service import ActionsService as DomainActionsService
from ontologia_api.services.instances_service import InstancesService


class ActionsService(DomainActionsService):
    """API-facing ActionsService that preserves legacy instance access patterns."""

    def __init__(self, session, service="api", instance="default", **kwargs):
        super().__init__(session, service=service, instance=instance, **kwargs)
        event_bus = kwargs.get("event_bus")
        self.instances = InstancesService(
            session,
            service=service,
            instance=instance,
            principal=kwargs.get("principal"),
            event_bus=event_bus,
        )


__all__ = ["ActionsService"]
