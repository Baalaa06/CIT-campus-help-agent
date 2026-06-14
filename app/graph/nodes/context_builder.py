"""Node 6 — Format reranked docs into an LLM-ready context string + citations."""
from __future__ import annotations

from app.graph.state import AgentState, Citation


def run(state: AgentState) -> dict:
    docs = state.get("reranked_docs", [])

    if not docs:
        return {"context": "", "citations": []}

    context_parts: list[str] = []
    citations: list[Citation] = []

    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        source = meta.get("source", "unknown")
        page = meta.get("page", 0)
        chunk_id = meta.get("chunk_id", f"chunk_{i}")
        score = meta.get("rerank_score", "")
        score_note = f" (relevance: {score})" if score else ""

        header = f"[Document {i} — Source: {source}, Page {page}{score_note}]"
        context_parts.append(f"{header}\n{doc.page_content}")

        citations.append(Citation(source=source, page=page, chunk_id=chunk_id))

    context = "\n\n".join(context_parts)
    return {"context": context, "citations": citations}
