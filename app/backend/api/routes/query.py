"""POST /query — run the LangGraph agent and return a grounded answer."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.backend.middleware.request_logger import LatencyTimer
from app.backend.schemas.query import CitationSchema, QueryRequest, QueryResponse
from app.database.firestore_db import log_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(body: QueryRequest, request: Request):
    graph = request.app.state.graph
    timer = LatencyTimer()

    thread_config = {"configurable": {"thread_id": body.session_id}}

    initial_state = {
        "user_id": body.user_id,
        "session_id": body.session_id,
        "query": body.query,
        "intent": "",
        "retrieved_docs": [],
        "reranked_docs": [],
        "context": "",
        "answer": "",
        "citations": [],
        "confidence": 0.0,
        "needs_human_approval": False,
        "human_decision": None,
        "feedback": None,
        "conversation_history": [],
    }

    try:
        result = await graph.ainvoke(initial_state, config=thread_config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    graph_state = await graph.aget_state(thread_config)
    is_interrupted = bool(graph_state.next)

    total_ms = timer.elapsed_ms()
    citations = [CitationSchema(**c) for c in result.get("citations", [])]

    await log_query(
        session_id=body.session_id,
        user_id=body.user_id,
        query=body.query,
        intent=result.get("intent", ""),
        answer=result.get("answer", ""),
        confidence=result.get("confidence", 0.0),
        total_latency_ms=total_ms,
        hallucination_flag=result.get("needs_human_approval", False),
        num_docs_retrieved=len(result.get("retrieved_docs", [])),
    )

    return QueryResponse(
        session_id=body.session_id,
        answer=(
            "Your query is under human review by a CIT advisor. You will be notified once approved."
            if is_interrupted
            else result.get("answer", "")
        ),
        citations=citations,
        confidence=result.get("confidence", 0.0),
        intent=result.get("intent", ""),
        needs_human_approval=is_interrupted,
        latency_ms=round(total_ms, 1),
    )
