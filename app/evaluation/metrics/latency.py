"""Latency percentile statistics."""
from __future__ import annotations

import statistics


def latency_stats(latencies_ms: list[float]) -> dict:
    if not latencies_ms:
        return {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "max": 0}

    sorted_lat = sorted(latencies_ms)
    n = len(sorted_lat)

    def percentile(p: float) -> float:
        idx = int(n * p / 100)
        return sorted_lat[min(idx, n - 1)]

    return {
        "p50": round(percentile(50), 1),
        "p95": round(percentile(95), 1),
        "p99": round(percentile(99), 1),
        "avg": round(statistics.mean(sorted_lat), 1),
        "max": round(sorted_lat[-1], 1),
    }
