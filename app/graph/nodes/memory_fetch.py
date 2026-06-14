"""Node 3 — History is persisted by the checkpointer via operator.add.

This node is intentionally a no-op pass-through: on the first turn the
conversation_history starts as [], and on subsequent turns the checkpointer
already restores the accumulated list.  The node exists so the graph topology
matches the specification and to allow future enrichment (e.g., summarising
very long histories before passing them to the LLM).
"""
from __future__ import annotations

from app.graph.state import AgentState


def run(state: AgentState) -> dict:
    return {}
