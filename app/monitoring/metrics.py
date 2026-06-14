"""Write structured query metrics to the query_logs table after each graph run."""
from __future__ import annotations

from app.database.connection import AsyncSessionLocal
from app.database.models.query_log import QueryLog


async def record_query(
    session_id: str,
    user_id: str,
    query: str,
    intent: str,
    answer: str,
    confidence: float,
    retrieval_latency_ms: float,
    generation_latency_ms: float,
    total_latency_ms: float,
    hallucination_flag: bool,
    num_docs_retrieved: int,
) -> None:
    async with AsyncSessionLocal() as db:
        log = QueryLog(
            session_id=session_id,
            user_id=user_id,
            query=query,
            intent=intent,
            answer=answer,
            confidence=confidence,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            total_latency_ms=total_latency_ms,
            hallucination_flag=hallucination_flag,
            num_docs_retrieved=num_docs_retrieved,
        )
        db.add(log)
        await db.commit()
