"""Cohere Rerank API — replaces local BGE cross-encoder, zero RAM cost."""
from __future__ import annotations

import cohere
from langchain_core.documents import Document

from config.settings import settings


def rerank_documents(
    query: str,
    docs: list[Document],
    top_k: int | None = None,
) -> list[Document]:
    if not docs:
        return []

    k = top_k or settings.rerank_top_k
    co = cohere.Client(api_key=settings.cohere_api_key)

    results = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[doc.page_content for doc in docs],
        top_n=k,
    )

    reranked: list[Document] = []
    for hit in results.results:
        doc = docs[hit.index]
        doc.metadata["rerank_score"] = round(hit.relevance_score, 4)
        reranked.append(doc)

    return reranked
