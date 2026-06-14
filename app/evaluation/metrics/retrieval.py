"""Retrieval precision: did the expected source appear in the returned citations?"""
from __future__ import annotations


def precision_at_k(citations: list[dict], expected_source: str | None) -> float:
    """1.0 if expected_source is in citations, 0.0 if not (or no expectation)."""
    if not expected_source:
        return 1.0  # No ground truth — cannot penalise
    sources = {c.get("source", "") for c in citations}
    return 1.0 if expected_source in sources else 0.0


def recall_at_k(citations: list[dict], expected_source: str | None) -> float:
    """Same definition as precision for single-source queries."""
    return precision_at_k(citations, expected_source)
