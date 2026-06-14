"""Split cleaned documents into overlapping chunks with metadata."""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings


def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks: list[Document] = []
    for doc in docs:
        splits = splitter.split_documents([doc])
        for idx, split in enumerate(splits):
            source = split.metadata.get("source", "unknown")
            page = split.metadata.get("page", 0)
            chunk_id = f"{source}_p{page}_c{idx}"
            split.metadata["chunk_id"] = chunk_id
            split.metadata["chunk_index"] = idx
            chunks.append(split)

    return chunks
