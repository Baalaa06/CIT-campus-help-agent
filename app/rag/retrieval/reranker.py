"""BAAI/bge-reranker-base cross-encoder reranker (top-k=3)."""
from __future__ import annotations

from functools import lru_cache

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from config.settings import settings


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder(settings.reranker_model)


def rerank_documents(
    query: str,
    docs: list[Document],
    top_k: int | None = None,
) -> list[Document]:
    """Score all docs against the query and return the top-k highest-scoring."""
    if not docs:
        return []

    k = top_k or settings.rerank_top_k
    reranker = _get_reranker()

    pairs = [(query, doc.page_content) for doc in docs]
    scores: list[float] = reranker.predict(pairs).tolist()

    scored = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)

    results: list[Document] = []
    for score, doc in scored[:k]:
        doc.metadata["rerank_score"] = round(float(score), 4)
        results.append(doc)

    return results
