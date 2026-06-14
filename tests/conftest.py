"""Shared fixtures for the test suite."""
from __future__ import annotations

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

# Use in-memory SQLite for tests
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("CHECKPOINT_DB_PATH", ":memory:")
os.environ.setdefault("CHROMA_PERSIST_DIR", "/tmp/test_chroma")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-dummy-key")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_response():
    """Return a mock ChatAnthropic that always echoes a fixed string."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Mock LLM response.")
    return mock


@pytest.fixture
def sample_docs():
    from langchain_core.documents import Document

    return [
        Document(
            page_content="The academic year begins in July every year.",
            metadata={
                "source": "academic_calendar.pdf",
                "page": 1,
                "chunk_id": "academic_calendar.pdf_p1_c0",
                "chunk_index": 0,
            },
        ),
        Document(
            page_content="Minimum attendance of 75% is required to appear in examinations.",
            metadata={
                "source": "examination_regulations.pdf",
                "page": 5,
                "chunk_id": "examination_regulations.pdf_p5_c0",
                "chunk_index": 0,
            },
        ),
    ]
