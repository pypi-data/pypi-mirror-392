"""Metrics utilities for ontologia-core.

Provides aggregation and reporting of operational metrics.
"""

from __future__ import annotations

from typing import Any

from ontologia.actions.registry import ACTION_REGISTRY


class CoreMetrics:
    """Aggregates metrics from core components."""

    def __init__(self) -> None:
        self._handler_stats: dict[str, dict[str, int]] = {}

    def register_handler_stats(self, handler_name: str, stats: dict[str, int]) -> None:
        """Register statistics from a handler."""
        self._handler_stats[handler_name] = dict(stats)

    def get_action_metrics(self) -> dict[str, Any]:
        """Get metrics about registered actions."""
        return {
            "total_actions": len(ACTION_REGISTRY),
            "action_keys": sorted(ACTION_REGISTRY.keys()),
        }

    def get_handler_metrics(self) -> dict[str, dict[str, int]]:
        """Get aggregated handler statistics."""
        return dict(self._handler_stats)

    def get_summary_metrics(self) -> dict[str, Any]:
        """Get summary of all core metrics."""
        handler_totals = {
            "total_invalidations": 0,
            "total_index_operations": 0,
            "total_failed_operations": 0,
            "total_skipped_operations": 0,
        }

        for stats in self._handler_stats.values():
            for key, value in stats.items():
                if key in handler_totals:
                    handler_totals[key] += value

        return {
            "actions": self.get_action_metrics(),
            "handlers": {
                "summary": handler_totals,
                "details": self._handler_stats,
            },
        }

    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self._handler_stats.clear()


# Global metrics instance
_core_metrics = CoreMetrics()


def get_core_metrics() -> CoreMetrics:
    """Get the global core metrics instance."""
    return _core_metrics


def register_handler_metrics(handler_name: str, stats: dict[str, int]) -> None:
    """Register handler metrics with the global instance."""
    _core_metrics.register_handler_stats(handler_name, stats)


def get_metrics_summary() -> dict[str, Any]:
    """Get summary of all core metrics."""
    return _core_metrics.get_summary_metrics()
