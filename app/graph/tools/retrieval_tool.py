"""LangChain Tool wrapper around the ChromaDB retriever."""
from __future__ import annotations

from langchain_core.tools import tool

from app.rag.retrieval.retriever import retrieve_documents
from config.settings import settings


@tool
def campus_doc_retriever(query: str) -> str:
    """Search official university documents for information related to the query.

    Use this tool to look up academic calendar dates, examination regulations,
    attendance policies, placement statistics, and other campus information.
    """
    docs = retrieve_documents(query=query, top_k=settings.retrieval_top_k)
    if not docs:
        return "No relevant documents found."

    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        parts.append(
            f"[{i}] Source: {meta.get('source','?')}, Page: {meta.get('page','?')}\n"
            f"{doc.page_content[:500]}"
        )
    return "\n\n".join(parts)
