"""Tests for evaluation metric functions."""
from __future__ import annotations

from app.evaluation.metrics.hallucination import hallucination_rate, is_hallucinated
from app.evaluation.metrics.latency import latency_stats
from app.evaluation.metrics.retrieval import precision_at_k, recall_at_k


class TestHallucinationMetrics:
    def test_high_confidence_not_hallucinated(self):
        assert not is_hallucinated(0.9)

    def test_low_confidence_hallucinated(self):
        assert is_hallucinated(0.5)

    def test_hallucination_rate_all_good(self):
        assert hallucination_rate([0.9, 0.8, 0.95]) == 0.0

    def test_hallucination_rate_all_bad(self):
        assert hallucination_rate([0.1, 0.2, 0.3]) == 1.0

    def test_hallucination_rate_mixed(self):
        rate = hallucination_rate([0.9, 0.1, 0.8, 0.2])
        assert rate == 0.5

    def test_empty_list(self):
        assert hallucination_rate([]) == 0.0


class TestLatencyStats:
    def test_empty(self):
        stats = latency_stats([])
        assert stats["avg"] == 0

    def test_single_value(self):
        stats = latency_stats([100.0])
        assert stats["p50"] == 100.0
        assert stats["avg"] == 100.0

    def test_percentiles(self):
        latencies = list(range(1, 101))
        stats = latency_stats([float(x) for x in latencies])
        assert stats["p50"] >= 50
        assert stats["p95"] >= 95
        assert stats["max"] == 100.0
