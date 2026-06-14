"""POST /feedback — record user thumbs-up / thumbs-down."""
from __future__ import annotations

from fastapi import APIRouter

from app.backend.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.database.firestore_db import save_feedback

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(body: FeedbackRequest):
    fid = await save_feedback(
        session_id=body.session_id,
        user_id=body.user_id,
        query=body.query,
        answer=body.answer,
        rating=body.rating,
    )
    return FeedbackResponse(message="Feedback recorded.", id=fid)
