"""Node 2 — Classify user intent into one of four categories."""
from __future__ import annotations

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.graph.state import AgentState
from config.settings import settings

_PROMPT = ChatPromptTemplate.from_template(
    """Classify the CIT (Coimbatore Institute of Technology) student query below into exactly one category.

Categories:
- academic_calendar : dates, deadlines, semesters, holidays, schedules, registration windows
- examination       : exam rules, attendance policy, grading, re-exams, malpractice, procedures
- placement         : campus recruitment, companies, salary packages, internships, placement stats
- other             : anything not covered above

Query: {query}

Reply with ONLY the category name and nothing else."""
)


def run(state: AgentState) -> dict:
    # Short query blocked by injection detector → skip LLM call
    if state["query"].startswith("[BLOCKED"):
        return {"intent": "other"}

    llm = ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        max_tokens=20,
        temperature=0.0,
    )
    chain = _PROMPT | llm | StrOutputParser()
    raw = chain.invoke({"query": state["query"]}).strip().lower()

    valid = {"academic_calendar", "examination", "placement", "other"}
    intent = raw if raw in valid else "other"
    return {"intent": intent}
