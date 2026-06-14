"""Node 10 — Persist user feedback to Firestore (optional)."""
from __future__ import annotations

from app.database.firestore_db import save_feedback
from app.graph.state import AgentState


async def run(state: AgentState) -> dict:
    rating = state.get("feedback")
    if not rating:
        return {}

    await save_feedback(
        session_id=state["session_id"],
        user_id=state["user_id"],
        query=state["query"],
        answer=state.get("answer", ""),
        rating=rating,
    )
    return {}
