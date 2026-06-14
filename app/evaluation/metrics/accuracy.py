"""LLM-as-judge: score whether the generated answer correctly addresses the question."""
from __future__ import annotations

import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings

_SYSTEM = """You are an impartial evaluator. Given a question and a generated answer,
score the accuracy of the answer from 0.0 to 1.0.

1.0 = Fully accurate and complete answer
0.5 = Partially correct or incomplete
0.0 = Incorrect, hallucinated, or "not found" when info is likely available

Also say whether the answer correctly identified it could not find the information
when the question is unanswerable from the documents.

Respond ONLY with JSON: {"score": <float>, "reason": "<one sentence>"}"""


def score_accuracy(question: str, answer: str) -> float:
    llm = ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        max_tokens=150,
        temperature=0.0,
    )
    human = f"Question: {question}\n\nAnswer: {answer}"
    response = llm.invoke([SystemMessage(content=_SYSTEM), HumanMessage(content=human)])
    try:
        data = json.loads(response.content)
        return float(data.get("score", 0.5))
    except Exception:
        return 0.5
