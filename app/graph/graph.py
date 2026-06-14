"""Assemble the full LangGraph StateGraph with all 11 nodes."""
from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.graph.edges.routing import route_after_hallucination_check
from app.graph.nodes import (
    context_builder,
    feedback_collector,
    hallucination_checker,
    human_approval,
    intent_classifier,
    memory_fetch,
    memory_updater,
    query_analyzer,
    reranker,
    response_generator,
    retriever,
)
from app.graph.state import AgentState


def build_graph(checkpointer: BaseCheckpointSaver):
    """Build and compile the campus help agent graph.

    Graph topology:
      START
        → query_analyzer       (sanitize & injection-check query)
        → intent_classifier    (LLM: academic_calendar | examination | placement | other)
        → memory_fetch         (no-op; history is in checkpointer state)
        → retriever            (ChromaDB similarity search, top-10)
        → reranker             (BGE cross-encoder, top-3)
        → context_builder      (format docs + citations)
        → response_generator   (Claude answer)
        → hallucination_checker (confidence score)
        → [conditional]
             if needs_human_approval → human_approval (interrupt)
             else                    → feedback_collector
        → feedback_collector   (persist user rating)
        → memory_updater       (append turn to history + SQLite audit)
        → END
    """
    workflow = StateGraph(AgentState)

    # Register nodes (mix of sync and async — LangGraph handles both)
    workflow.add_node("query_analyzer", query_analyzer.run)
    workflow.add_node("intent_classifier", intent_classifier.run)
    workflow.add_node("memory_fetch", memory_fetch.run)
    workflow.add_node("retriever", retriever.run)
    workflow.add_node("reranker", reranker.run)
    workflow.add_node("context_builder", context_builder.run)
    workflow.add_node("response_generator", response_generator.run)
    workflow.add_node("hallucination_checker", hallucination_checker.run)
    workflow.add_node("human_approval", human_approval.run)
    workflow.add_node("feedback_collector", feedback_collector.run)
    workflow.add_node("memory_updater", memory_updater.run)

    # Linear edges (happy path)
    workflow.add_edge(START, "query_analyzer")
    workflow.add_edge("query_analyzer", "intent_classifier")
    workflow.add_edge("intent_classifier", "memory_fetch")
    workflow.add_edge("memory_fetch", "retriever")
    workflow.add_edge("retriever", "reranker")
    workflow.add_edge("reranker", "context_builder")
    workflow.add_edge("context_builder", "response_generator")
    workflow.add_edge("response_generator", "hallucination_checker")

    # Conditional branch after hallucination check
    workflow.add_conditional_edges(
        "hallucination_checker",
        route_after_hallucination_check,
        {
            "human_approval": "human_approval",
            "feedback_collector": "feedback_collector",
        },
    )

    # After human approval (or direct path), converge at feedback_collector
    workflow.add_edge("human_approval", "feedback_collector")
    workflow.add_edge("feedback_collector", "memory_updater")
    workflow.add_edge("memory_updater", END)

    return workflow.compile(checkpointer=checkpointer)
