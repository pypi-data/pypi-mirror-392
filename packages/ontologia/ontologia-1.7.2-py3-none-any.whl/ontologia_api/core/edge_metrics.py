from __future__ import annotations

try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
except Exception:  # pragma: no cover - optional dependency fallback for tests
    # Lightweight no-op fallbacks to keep the API importable in environments
    # without prometheus_client installed (e.g., constrained CI sandboxes).
    class CollectorRegistry:  # type: ignore[override]
        pass

    class _NoopMetric:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *_args, **_kwargs):  # noqa: D401 - no-op
            """Increment"""
            return None

        def set(self, *_args, **_kwargs):  # noqa: D401 - no-op
            """Set"""
            return None

    class Counter(_NoopMetric):  # type: ignore[override]
        pass

    class Gauge(_NoopMetric):  # type: ignore[override]
        pass

    def generate_latest(_registry: CollectorRegistry) -> bytes:  # type: ignore[override]
        return b""

    CONTENT_TYPE_LATEST = "text/plain"

registry = CollectorRegistry()

edge_hello_total = Counter("edge_hello_total", "HELLO messages received", registry=registry)
edge_state_total = Counter("edge_state_total", "STATE messages received", registry=registry)
edge_event_total = Counter("edge_event_total", "EVENT messages received", registry=registry)
edge_signature_failures_total = Counter(
    "edge_signature_failures_total", "Signature verification failures", registry=registry
)

edge_commands_enqueued_total = Counter(
    "edge_commands_enqueued_total", "Commands enqueued", registry=registry
)
edge_commands_delivered_total = Counter(
    "edge_commands_delivered_total", "Commands delivered to nodes", registry=registry
)
edge_commands_acked_total = Counter(
    "edge_commands_acked_total", "Commands acknowledged by nodes", registry=registry
)
edge_commands_retried_total = Counter(
    "edge_commands_retried_total", "Commands retried due to missing ACK", registry=registry
)
edge_commands_expired_total = Counter(
    "edge_commands_expired_total", "Commands expired/failed", registry=registry
)

edge_rate_limit_rejections_total = Counter(
    "edge_rate_limit_rejections_total", "Requests rejected due to rate limiting", registry=registry
)
edge_acl_denied_total = Counter(
    "edge_acl_denied_total", "Command enqueues denied by ACL", registry=registry
)


def metrics_response() -> tuple[bytes, str]:
    payload = generate_latest(registry)
    return payload, CONTENT_TYPE_LATEST
