"""GET /history/{session_id} — retrieve conversation history for a session."""
from __future__ import annotations

from fastapi import APIRouter

from app.backend.schemas.history import HistoryMessage, HistoryResponse
from app.database.firestore_db import get_conversation_history

router = APIRouter()


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    records = await get_conversation_history(session_id)
    messages = [
        HistoryMessage(
            role=r["role"],
            content=r["content"],
            intent=r.get("intent", ""),
            created_at=r["createdAt"],
        )
        for r in records
    ]
    return HistoryResponse(session_id=session_id, messages=messages, total=len(messages))
