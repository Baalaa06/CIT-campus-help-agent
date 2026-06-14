"""Async request logger: writes query metrics to query_logs after each /query call."""
from __future__ import annotations

# This module provides a helper used by the /query route handler to record
# post-invocation metrics.  It is intentionally thin so that the route handler
# controls timing boundaries.

import time


class LatencyTimer:
    def __init__(self):
        self._start = time.perf_counter()
        self.checkpoints: dict[str, float] = {}

    def checkpoint(self, name: str) -> None:
        self.checkpoints[name] = (time.perf_counter() - self._start) * 1000

    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start) * 1000
