"""Load PDF files page-by-page using PyMuPDF, preserving page numbers."""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.documents import Document


def load_pdf(file_path: str | Path) -> list[Document]:
    """Return one Document per page with source + page metadata."""
    path = Path(file_path)
    docs: list[Document] = []

    with fitz.open(str(path)) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text("text")
            if text.strip():
                docs.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": path.name,
                            "page": page_num + 1,  # 1-indexed
                            "file_path": str(path),
                        },
                    )
                )
    return docs


def load_directory(data_dir: str | Path) -> list[Document]:
    """Load all PDFs from a directory."""
    data_dir = Path(data_dir)
    all_docs: list[Document] = []
    for pdf_file in sorted(data_dir.glob("*.pdf")):
        print(f"[Loader] Loading {pdf_file.name}")
        all_docs.extend(load_pdf(pdf_file))
    return all_docs
