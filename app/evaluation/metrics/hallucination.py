"""Track hallucination rate across an eval run."""
from __future__ import annotations


def is_hallucinated(confidence: float, threshold: float = 0.7) -> bool:
    return confidence < threshold


def hallucination_rate(confidences: list[float], threshold: float = 0.7) -> float:
    if not confidences:
        return 0.0
    flagged = sum(1 for c in confidences if is_hallucinated(c, threshold))
    return flagged / len(confidences)
