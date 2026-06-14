"""Configure LangSmith tracing via environment variables.

LangChain reads LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY automatically,
so we only need to ensure they are set before any LLM call happens.
"""
from __future__ import annotations

import os

from config.settings import settings


def configure_langsmith() -> bool:
    """Set LangSmith env vars and return True if tracing is enabled."""
    enabled = settings.langchain_tracing_v2.lower() == "true"

    os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

    if settings.langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

    if enabled:
        print(f"[LangSmith] Tracing enabled → project: {settings.langchain_project}")
    else:
        print("[LangSmith] Tracing disabled (set LANGCHAIN_TRACING_V2=true to enable)")

    return enabled
