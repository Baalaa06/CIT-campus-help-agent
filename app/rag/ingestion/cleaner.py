"""Text cleaning: remove artifacts, normalize whitespace, drop junk lines."""
from __future__ import annotations

import re

from langchain_core.documents import Document


def clean_text(text: str) -> str:
    # Replace form feeds and other control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    # Collapse runs of whitespace (preserve single newlines as sentence breaks)
    text = re.sub(r"[ \t]+", " ", text)
    # Remove lines that are pure whitespace or very short noise
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if len(ln) > 3]
    text = "\n".join(lines)
    # Collapse 3+ consecutive newlines into two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_documents(docs: list[Document]) -> list[Document]:
    cleaned: list[Document] = []
    for doc in docs:
        text = clean_text(doc.page_content)
        if text:
            cleaned.append(Document(page_content=text, metadata=doc.metadata))
    return cleaned
