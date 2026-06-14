"""Full ingestion pipeline: PDF → clean → chunk → embed → ChromaDB + Firestore."""
from __future__ import annotations

import asyncio
from pathlib import Path

from app.database.firestore_db import save_chunks_metadata
from app.rag.ingestion.cleaner import clean_documents
from app.rag.ingestion.chunker import chunk_documents
from app.rag.ingestion.embedder import embed_and_store
from app.rag.ingestion.loader import load_directory
from config.settings import settings


async def run_ingestion(data_dir: str | None = None) -> dict:
    data_dir = data_dir or settings.data_dir
    print(f"[Pipeline] Loading PDFs from {data_dir}")

    raw_docs = load_directory(data_dir)
    print(f"[Pipeline] Loaded {len(raw_docs)} pages")

    cleaned = clean_documents(raw_docs)
    print(f"[Pipeline] Cleaned: {len(cleaned)} non-empty pages")

    chunks = chunk_documents(cleaned)
    print(f"[Pipeline] Created {len(chunks)} chunks")

    stored = embed_and_store(chunks)
    print(f"[Pipeline] Embedded and stored {stored} chunks in ChromaDB")

    chunk_meta = [
        {
            "filename": c.metadata.get("source", "unknown"),
            "chunk_id": c.metadata["chunk_id"],
            "page_number": c.metadata.get("page", 0),
            "chunk_index": c.metadata.get("chunk_index", 0),
        }
        for c in chunks
    ]
    await save_chunks_metadata(chunk_meta)
    print(f"[Pipeline] Saved {len(chunk_meta)} chunk records to Firestore")

    from collections import Counter
    source_counts = Counter(c.metadata.get("source") for c in chunks)

    return {
        "total_pages": len(raw_docs),
        "total_chunks": len(chunks),
        "by_source": dict(source_counts),
    }


if __name__ == "__main__":
    result = asyncio.run(run_ingestion())
    print(f"[Pipeline] Done: {result}")
