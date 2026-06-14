"""Node 8 — LLM-based hallucination / grounding verification."""
from __future__ import annotations

import json
import re

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import AgentState
from config.settings import settings

_SYSTEM = """You are a strict fact-checker. Given retrieved context and a generated answer,
determine whether every factual claim in the answer is supported by the context.

Respond with ONLY a JSON object (no markdown, no explanation outside JSON):
{
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<one sentence>"
}

Confidence guide:
- 1.0 : every claim is explicitly present in the context, or the answer correctly states it cannot find info
- 0.8 : mostly grounded, minor paraphrase
- 0.6 : some claims not directly supported
- 0.4 : significant unsupported claims
- 0.0 : answer is fabricated / contradicts context"""


def _parse_confidence(text: str) -> float:
    try:
        data = json.loads(text)
        return float(data.get("confidence", 0.5))
    except Exception:
        # Fallback: look for a float in the text
        match = re.search(r'"confidence"\s*:\s*([\d.]+)', text)
        if match:
            return float(match.group(1))
        return 0.5


def run(state: AgentState) -> dict:
    answer = state.get("answer", "")
    context = state.get("context", "")

    # If answer says "could not find", it's honest — treat as fully grounded
    if "could not find this information" in answer.lower():
        return {"confidence": 1.0, "needs_human_approval": False}

    # If there was no context, any non-"could not find" answer is suspicious
    if not context:
        return {
            "confidence": 0.3,
            "needs_human_approval": True,
        }

    llm = ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        max_tokens=256,
        temperature=0.0,
    )

    human_text = (
        f"Context:\n{context[:3000]}\n\n"
        f"Generated Answer:\n{answer}"
    )

    response = llm.invoke(
        [SystemMessage(content=_SYSTEM), HumanMessage(content=human_text)]
    )

    confidence = _parse_confidence(response.content)
    needs_approval = confidence < settings.confidence_threshold

    return {
        "confidence": round(confidence, 4),
        "needs_human_approval": needs_approval,
    }
