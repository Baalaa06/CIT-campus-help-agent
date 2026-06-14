"""Node 9 — Human-in-the-loop approval via LangGraph interrupt + Firestore."""
from __future__ import annotations

import asyncio
import concurrent.futures
from uuid import uuid4

from langgraph.types import interrupt

from app.database.firestore_db import create_approval, update_approval
from app.graph.state import AgentState


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


def run(state: AgentState) -> dict:
    approval_id = str(uuid4())

    _run_async(create_approval(
        approval_id=approval_id,
        session_id=state["session_id"],
        query=state["query"],
        answer=state["answer"],
        confidence=state["confidence"],
    ))

    decision: dict = interrupt({
        "approval_id": approval_id,
        "query": state["query"],
        "answer": state["answer"],
        "confidence": state["confidence"],
        "message": "Low-confidence answer requires CIT advisor review.",
    })

    _run_async(update_approval(
        approval_id=approval_id,
        status=decision.get("status", "approved"),
        reviewed_by=decision.get("reviewed_by", "admin"),
    ))

    return {"human_decision": decision.get("status", "approved")}
