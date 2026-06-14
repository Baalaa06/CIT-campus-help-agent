"""Singleton wrapper around embedded ChromaDB using HuggingFace Inference API for embeddings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from config.settings import settings


@lru_cache(maxsize=1)
def get_embedding_function() -> HuggingFaceEndpointEmbeddings:
    return HuggingFaceEndpointEmbeddings(
        model=f"https://api-inference.huggingface.co/models/{settings.embedding_model}",
        huggingfacehub_api_token=settings.huggingface_api_key,
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
