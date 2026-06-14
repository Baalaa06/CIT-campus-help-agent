"""Node 4 — Retrieve top-10 documents from ChromaDB."""
from __future__ import annotations

from app.graph.state import AgentState
from app.rag.retrieval.retriever import retrieve_documents
from config.settings import settings


def run(state: AgentState) -> dict:
    # Skip retrieval if the query was blocked by injection detection
    if state["query"].startswith("[BLOCKED"):
        return {"retrieved_docs": []}

    docs = retrieve_documents(
        query=state["query"],
        top_k=settings.retrieval_top_k,
    )
    return {"retrieved_docs": docs}
