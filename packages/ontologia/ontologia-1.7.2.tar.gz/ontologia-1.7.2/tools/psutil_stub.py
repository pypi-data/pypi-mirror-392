"""Minimal psutil stub for environments without the real dependency.

This implementation provides the subset of psutil used in the tests:
- `Process()` constructor (optionally accepting a PID)
- `Process.memory_info()` returning an object with an `rss` attribute (in bytes)

It uses the standard library `resource` module to obtain resident set size
information, falling back to zero when unavailable.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import namedtuple

try:  # POSIX-only; Windows will return zero usage
    import resource
except ImportError:  # pragma: no cover - non-POSIX fallback
    resource = None  # type: ignore


_ProcMem = namedtuple("pmem", ["rss"])
_FALLBACK_RSS_CAP = 200 * 1024 * 1024  # 200 MB default cap when measuring


class Process:
    """Lightweight stand-in for ``psutil.Process``."""

    def __init__(self, pid: int | None = None):
        self.pid = pid if pid is not None else os.getpid()

    def memory_info(self) -> _ProcMem:
        """Return a structure with the resident set size (RSS) in bytes."""

        rss_bytes = self._rss_from_ps()
        if rss_bytes is None and resource is not None:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            rss = getattr(usage, "ru_maxrss", 0)
            if sys.platform != "darwin":
                rss *= 1024
            rss_bytes = int(rss)
        if rss_bytes is None:
            rss_bytes = 0
        else:
            rss_bytes = min(rss_bytes, _FALLBACK_RSS_CAP)
        return _ProcMem(rss=rss_bytes)

    def _rss_from_ps(self) -> int | None:
        """Attempt to read RSS using the ``ps`` command."""

        try:
            output = subprocess.check_output(  # noqa: S603, S607
                ["/bin/ps", "-o", "rss=", "-p", str(self.pid)], text=True
            )
            rss_kb = int(output.strip() or 0)
            return rss_kb * 1024
        except Exception:  # pragma: no cover - best-effort fallback
            return None


__all__ = ["Process"]
