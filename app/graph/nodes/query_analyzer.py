"""Node 1 — Normalize and sanitize the raw user query."""
from __future__ import annotations

import re

from app.graph.state import AgentState
from config.settings import settings


def run(state: AgentState) -> dict:
    query = state["query"].strip()

    # Collapse internal whitespace runs
    query = re.sub(r"[ \t]+", " ", query)

    # Remove control characters that could cause issues downstream
    query = re.sub(r"[\x00-\x1f\x7f]", "", query)

    # Enforce maximum length
    query = query[: settings.max_query_length]

    # Detect and reject obvious prompt-injection attempts
    injection_patterns = [
        r"ignore previous instructions",
        r"disregard (all|your) (previous|prior|system)",
        r"you are now",
        r"act as (if you are|a|an)",
        r"forget everything",
        r"pretend (to be|you are)",
        r"jailbreak",
        r"<\s*script",
    ]
    lowered = query.lower()
    for pattern in injection_patterns:
        if re.search(pattern, lowered):
            return {
                "query": "[BLOCKED: prompt injection detected]",
                "intent": "other",
                "answer": "I cannot process this request as it appears to contain an injection attempt.",
                "confidence": 1.0,
                "needs_human_approval": False,
                "citations": [],
                "retrieved_docs": [],
                "reranked_docs": [],
                "context": "",
            }

    return {"query": query}
