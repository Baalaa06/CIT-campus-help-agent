"""Approvals, analytics, and docs-stats routes — all backed by Firestore."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command

from app.backend.schemas.approval import (
    ApprovalActionRequest,
    ApprovalActionResponse,
    ApprovalListItem,
    ApprovalListResponse,
)
from app.database.firestore_db import (
    get_analytics,
    get_docs_stats,
    list_approvals,
    update_approval,
)

router = APIRouter()


@router.get("/approvals", response_model=ApprovalListResponse)
async def list_approvals_endpoint(status: str = "pending"):
    records = await list_approvals(status)
    items = [ApprovalListItem(**r) for r in records]
    return ApprovalListResponse(items=items, total=len(items))


@router.post("/approve", response_model=ApprovalActionResponse)
async def approve_request(body: ApprovalActionRequest, request: Request):
    await update_approval(body.approval_id, body.status, body.reviewed_by)

    graph = request.app.state.graph
    thread_config = {"configurable": {"thread_id": body.session_id}}

    try:
        result = await graph.ainvoke(
            Command(resume={"status": body.status, "reviewed_by": body.reviewed_by}),
            config=thread_config,
        )
        answer = result.get("answer", "")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume error: {exc}") from exc

    return ApprovalActionResponse(
        message=f"Approval {body.status} successfully.", answer=answer
    )


@router.get("/analytics")
async def analytics_endpoint():
    return await get_analytics()


@router.get("/docs-stats")
async def docs_stats_endpoint():
    return await get_docs_stats()
