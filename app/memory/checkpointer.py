"""Async SQLite checkpointer factory for LangGraph."""
from __future__ import annotations

from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from config.settings import settings


def get_checkpointer_context():
    """Return an async context manager that yields an AsyncSqliteSaver.

    Usage inside FastAPI lifespan:
        async with get_checkpointer_context() as checkpointer:
            app.state.graph = build_graph(checkpointer)
            yield
    """
    Path(settings.checkpoint_db_path).parent.mkdir(parents=True, exist_ok=True)
    return AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path)
