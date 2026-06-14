"""Conditional edge functions for the LangGraph graph."""
from __future__ import annotations

from app.graph.state import AgentState


def route_after_hallucination_check(state: AgentState) -> str:
    """Route to human approval when confidence is below threshold, else proceed."""
    if state.get("needs_human_approval", False):
        return "human_approval"
    return "feedback_collector"
