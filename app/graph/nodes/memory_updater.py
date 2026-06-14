"""Node 11 — Append turn to conversation_history state and write to Firestore."""
from __future__ import annotations

from app.database.firestore_db import save_conversation_turn
from app.graph.state import AgentState, Message


async def run(state: AgentState) -> dict:
    await save_conversation_turn(
        session_id=state["session_id"],
        user_id=state["user_id"],
        query=state["query"],
        answer=state.get("answer", ""),
        intent=state.get("intent", ""),
    )

    new_messages: list[Message] = [
        {"role": "user", "content": state["query"]},
        {"role": "assistant", "content": state.get("answer", "")},
    ]
    return {"conversation_history": new_messages}
