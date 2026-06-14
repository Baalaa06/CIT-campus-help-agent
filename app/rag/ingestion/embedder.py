"""Embed and upsert chunks into ChromaDB."""
from __future__ import annotations

from langchain_core.documents import Document

from app.rag.vectorstore.chroma_store import get_vectorstore


def embed_and_store(chunks: list[Document]) -> int:
    """Upsert chunks into ChromaDB. Returns number of chunks stored."""
    if not chunks:
        return 0

    vs = get_vectorstore()

    # ChromaDB deduplicates by ID; use chunk_id as the stable document ID
    ids = [c.metadata["chunk_id"] for c in chunks]
    vs.add_documents(documents=chunks, ids=ids)

    return len(chunks)
