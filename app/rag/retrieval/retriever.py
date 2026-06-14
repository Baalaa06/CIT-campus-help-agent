"""ChromaDB similarity-search retriever (top-k=10)."""
from __future__ import annotations

from langchain_core.documents import Document

from app.rag.vectorstore.chroma_store import get_vectorstore
from config.settings import settings


def retrieve_documents(query: str, top_k: int | None = None) -> list[Document]:
    """Return top-k documents most similar to the query."""
    k = top_k or settings.retrieval_top_k
    vs = get_vectorstore()

    try:
        results = vs.similarity_search(query=query, k=k)
    except Exception as exc:
        print(f"[Retriever] ChromaDB error: {exc}")
        return []

    return results
