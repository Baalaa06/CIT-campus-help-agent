"""In-memory store for cross-thread facts (e.g., user preferences)."""
from __future__ import annotations

from functools import lru_cache

from langgraph.store.memory import InMemoryStore


@lru_cache(maxsize=1)
def get_store() -> InMemoryStore:
    return InMemoryStore()
