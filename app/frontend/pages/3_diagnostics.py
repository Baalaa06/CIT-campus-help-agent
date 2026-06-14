"""CIT RAG Diagnostics — inspect retrieval pipeline for any query."""
from __future__ import annotations

import uuid

import streamlit as st

from app.frontend.utils.api_client import client

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="cit-header">
        <div class="cit-seal">🔍</div>
        <div>
            <h1>RAG Diagnostics</h1>
            <p>Coimbatore Institute of Technology · Pipeline Inspection Tool</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='cit-card'>Run any query and inspect the full retrieval pipeline — "
    "which CIT documents were fetched, reranking scores, final answer, "
    "and hallucination confidence.</div>",
    unsafe_allow_html=True,
)

query = st.text_input(
    "Test Query",
    placeholder="e.g. What is the last date to register for end semester exams at CIT?",
)
run_btn = st.button("▶ Run Diagnostic", type="primary")

if run_btn and query:
    diag_session = f"diag_{uuid.uuid4().hex[:8]}"

    with st.spinner("Running CIT RAG pipeline…"):
        try:
            result = client.query(
                user_id="diagnostics",
                session_id=diag_session,
                query=query,
            )
        except Exception as exc:
            st.error(f"Error: {exc}")
            st.stop()

    st.markdown("---")

    # ── Intent ────────────────────────────────────────────────────────────────
    st.markdown("#### Intent Classification")
    intent = result.get("intent", "unknown")
    intent_map = {
        "academic_calendar": ("📅", "blue", "Academic Calendar"),
        "examination":       ("📝", "orange", "Examination"),
        "placement":         ("💼", "green", "Placement"),
        "other":             ("📋", "gray", "Other"),
    }
    icon, color, label = intent_map.get(intent, ("📋", "gray", intent))
    st.markdown(
        f"<span class='cit-badge'>{icon} {label}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Answer ────────────────────────────────────────────────────────────────
    st.markdown("#### Generated Answer")
    st.markdown(
        f"<div class='cit-card'>{result.get('answer', '')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Citations ─────────────────────────────────────────────────────────────
    st.markdown("#### Source Citations")
    citations = result.get("citations", [])
    if citations:
        for c in citations:
            st.markdown(
                f"<span class='cit-badge cit-badge-gold'>CIT Document</span> "
                f"`{c['source']}` — Page **{c['page']}** &nbsp;·&nbsp; "
                f"Chunk `{c['chunk_id']}`",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No citations returned — no relevant CIT documents were found.")

    st.markdown("---")

    # ── Confidence ────────────────────────────────────────────────────────────
    st.markdown("#### Hallucination Confidence")
    conf = result.get("confidence", 0.0)
    col_m, col_p = st.columns([1, 3])
    with col_m:
        st.metric("Score", f"{conf:.0%}")
    with col_p:
        color_label = "High ✅" if conf >= 0.8 else ("Medium ⚠️" if conf >= 0.6 else "Low 🔴")
        st.progress(conf, text=f"Grounding: {color_label}")

    if result.get("needs_human_approval"):
        st.warning(
            "⚠️ This response was flagged for human review by a CIT advisor "
            "(confidence below threshold)."
        )

    st.markdown("---")

    # ── Latency ───────────────────────────────────────────────────────────────
    st.markdown("#### Pipeline Latency")
    st.metric("Total Response Time", f"{result.get('latency_ms', 0):.0f} ms")
