"""Singleton wrapper around embedded ChromaDB."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import settings


@lru_cache(maxsize=1)
def get_embedding_function() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    return Chroma(
        client=get_chroma_client(),
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
    )


def get_collection_stats() -> dict:
    client = get_chroma_client()
    try:
        col = client.get_collection(settings.chroma_collection_name)
        return {"collection": settings.chroma_collection_name, "count": col.count()}
    except Exception:
        return {"collection": settings.chroma_collection_name, "count": 0}
