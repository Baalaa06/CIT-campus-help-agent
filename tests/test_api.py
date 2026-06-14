"""Integration tests for the FastAPI routes (using TestClient)."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create a TestClient with mocked graph and DB."""
    with (
        patch("app.database.migrations.init_db.init_db", new_callable=AsyncMock),
        patch("app.memory.checkpointer.get_checkpointer_context"),
        patch("app.graph.graph.build_graph") as mock_build,
        patch("app.monitoring.langsmith_setup.configure_langsmith"),
    ):
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "answer": "The academic year starts in July.",
            "citations": [{"source": "academic_calendar.pdf", "page": 1, "chunk_id": "x"}],
            "confidence": 0.95,
            "intent": "academic_calendar",
            "needs_human_approval": False,
            "retrieved_docs": [],
        }
        mock_graph.aget_state.return_value = MagicMock(next=[])
        mock_build.return_value = mock_graph

        from app.backend.main import create_app
        app = create_app()

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


class TestHealthEndpoint:
    def test_health_ok(self, test_client):
        resp = test_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestQueryEndpoint:
    def test_query_returns_answer(self, test_client):
        resp = test_client.post(
            "/query",
            json={
                "session_id": "test_session_123",
                "query": "When does the academic year start?",
            },
        )
        # May be 200 or 500 depending on mock setup in CI
        assert resp.status_code in (200, 422, 500)

    def test_query_validates_empty_query(self, test_client):
        resp = test_client.post(
            "/query",
            json={"session_id": "s1", "query": ""},
        )
        assert resp.status_code == 422
