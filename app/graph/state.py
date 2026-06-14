"""LangGraph agent state — single source of truth for the entire graph."""
from __future__ import annotations

import operator
from typing import Annotated, Optional, TypedDict

from langchain_core.documents import Document


class Citation(TypedDict):
    source: str   # PDF filename, e.g. "academic_calendar.pdf"
    page: int     # 1-indexed page number inside the source PDF
    chunk_id: str # Unique chunk identifier (source_pN_cM)


class Message(TypedDict):
    role: str     # "user" | "assistant"
    content: str


class AgentState(TypedDict):
    # ── Identity ──────────────────────────────────────────────────────────────
    # Identifies which human is talking; used for per-user analytics.
    user_id: str

    # Maps to LangGraph thread_id; the checkpointer uses this to persist
    # and restore the full state across multiple turns in the same session.
    session_id: str

    # ── Input ─────────────────────────────────────────────────────────────────
    # Raw (then normalized) user query for the current turn.
    query: str

    # ── Classification ────────────────────────────────────────────────────────
    # One of: academic_calendar | examination | placement | other
    intent: str

    # ── Retrieval ─────────────────────────────────────────────────────────────
    # Top-10 documents returned by ChromaDB similarity search.
    retrieved_docs: list[Document]

    # Top-3 documents after BGE cross-encoder reranking.
    reranked_docs: list[Document]

    # ── Generation ────────────────────────────────────────────────────────────
    # Formatted string assembled from reranked_docs, injected into the LLM prompt.
    context: str

    # Final answer produced by the LLM, grounded in context.
    answer: str

    # Source citations extracted from the reranked documents.
    citations: list[Citation]

    # ── Quality control ───────────────────────────────────────────────────────
    # Grounding confidence from the hallucination checker (0.0 = hallucinated,
    # 1.0 = fully grounded). If below settings.confidence_threshold, the graph
    # routes to the human approval node.
    confidence: float

    # Set to True by hallucination_checker when confidence < threshold.
    needs_human_approval: bool

    # Written by human_approval node after the interrupt is resumed.
    # "approved" means the answer is published as-is; "rejected" triggers a retry.
    human_decision: Optional[str]

    # ── Feedback ──────────────────────────────────────────────────────────────
    # User's explicit rating submitted via the UI: "positive" | "negative" | None
    feedback: Optional[str]

    # ── Memory ────────────────────────────────────────────────────────────────
    # Full conversation turns for this session. Uses operator.add so that each
    # call to return {"conversation_history": [...]} appends to (not replaces)
    # the accumulated list. The checkpointer persists this across turns.
    conversation_history: Annotated[list[Message], operator.add]
