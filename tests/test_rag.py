"""Tests for RAG pipeline components."""
from __future__ import annotations

import pytest

from app.rag.ingestion.cleaner import clean_text
from app.rag.ingestion.chunker import chunk_documents
from app.evaluation.metrics.retrieval import precision_at_k, recall_at_k


class TestCleaner:
    def test_removes_control_chars(self):
        result = clean_text("hello\x00world\x1ftest")
        assert "\x00" not in result
        assert "\x1f" not in result

    def test_collapses_whitespace(self):
        result = clean_text("hello    world")
        assert "    " not in result

    def test_removes_empty_lines(self):
        text = "line1\n\n\n\nline2"
        result = clean_text(text)
        assert "\n\n\n" not in result

    def test_returns_empty_for_whitespace_only(self):
        result = clean_text("   \n  \t  ")
        assert result == ""


class TestChunker:
    def test_chunks_with_metadata(self, sample_docs):
        chunks = chunk_documents(sample_docs)
        assert all("chunk_id" in c.metadata for c in chunks)
        assert all("chunk_index" in c.metadata for c in chunks)
        assert all("source" in c.metadata for c in chunks)
        assert all("page" in c.metadata for c in chunks)

    def test_chunk_ids_unique(self, sample_docs):
        chunks = chunk_documents(sample_docs)
        ids = [c.metadata["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))


class TestRetrievalMetrics:
    def test_precision_hit(self):
        citations = [{"source": "academic_calendar.pdf", "page": 1, "chunk_id": "x"}]
        assert precision_at_k(citations, "academic_calendar.pdf") == 1.0

    def test_precision_miss(self):
        citations = [{"source": "placements.pdf", "page": 2, "chunk_id": "y"}]
        assert precision_at_k(citations, "academic_calendar.pdf") == 0.0

    def test_precision_no_expectation(self):
        assert precision_at_k([], None) == 1.0
