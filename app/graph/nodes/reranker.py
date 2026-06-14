"""Node 5 — Re-rank retrieved docs with BGE cross-encoder → keep top 3."""
from __future__ import annotations

from app.graph.state import AgentState
from app.rag.retrieval.reranker import rerank_documents
from config.settings import settings


def run(state: AgentState) -> dict:
    docs = state.get("retrieved_docs", [])
    if not docs:
        return {"reranked_docs": []}

    reranked = rerank_documents(
        query=state["query"],
        docs=docs,
        top_k=settings.rerank_top_k,
    )
    return {"reranked_docs": reranked}
