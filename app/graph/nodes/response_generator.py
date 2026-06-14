"""Node 7 — Generate a grounded answer using the LLM + retrieved context."""
from __future__ import annotations

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import AgentState, Message
from config.settings import settings

_SYSTEM = """You are the official Help Agent for CIT — Coimbatore Institute of Technology.
You answer student questions EXCLUSIVELY from the official CIT documents provided below.

STRICT RULES:
1. Use ONLY information from the Context section. Do not use prior training knowledge.
2. If the context does not contain enough information to answer, respond with EXACTLY:
   "I could not find this information in the official CIT documents."
3. Be precise, concise, and factual.
4. When referencing information, naturally indicate the source CIT document.
5. Never fabricate dates, numbers, names, or policies.
6. Always refer to the institution as CIT or Coimbatore Institute of Technology."""


def _format_history(history: list[Message]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:  # last 3 turns
        prefix = "Student" if msg["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {msg['content']}")
    return "\n".join(lines)


def run(state: AgentState) -> dict:
    # Propagate blocked queries without calling the LLM
    if state["query"].startswith("[BLOCKED"):
        return {"answer": state.get("answer", "I cannot process this request.")}

    context = state.get("context", "")
    history_text = _format_history(state.get("conversation_history", []))

    human_text = ""
    if history_text:
        human_text += f"Conversation so far:\n{history_text}\n\n"
    if context:
        human_text += f"Context from Official Documents:\n{context}\n\n"
    else:
        human_text += "Context from Official Documents: [No relevant documents found]\n\n"
    human_text += f"Current Question: {state['query']}"

    llm = ChatGroq(
        model=settings.response_llm_model,
        api_key=settings.groq_api_key,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
    )

    response = llm.invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=human_text)]
    )
    return {"answer": response.content.strip()}
