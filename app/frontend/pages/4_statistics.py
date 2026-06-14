"""CIT Document & Query Statistics."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.frontend.utils.api_client import client

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="cit-header">
        <div class="cit-seal">📊</div>
        <div>
            <h1>CIT Help Agent Statistics</h1>
            <p>Coimbatore Institute of Technology · System Metrics</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Document Corpus ───────────────────────────────────────────────────────────
st.markdown("#### 📁 CIT Document Corpus")

try:
    doc_data = client.get_docs_stats()
    docs = doc_data.get("documents", [])
    total_chunks = doc_data.get("total_chunks", 0)
except Exception as exc:
    st.error(f"Could not load document stats: {exc}")
    docs = []
    total_chunks = 0

col_tc, col_docs = st.columns(2)
col_tc.metric("Total Chunks Indexed", total_chunks)
col_docs.metric("CIT Documents Loaded", len(docs))

if docs:
    df = pd.DataFrame(docs)
    st.dataframe(
        df.rename(columns={"filename": "CIT Document", "chunk_count": "Chunks"}),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("**Chunks per CIT Document**")
    st.bar_chart(df.set_index("filename")["chunk_count"], use_container_width=True)
else:
    st.markdown(
        "<div class='cit-card'>⚠️ No CIT documents indexed yet. "
        "Run <code>python scripts/ingest.py</code> to load documents.</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Query Statistics ──────────────────────────────────────────────────────────
st.markdown("#### 📈 Query Statistics")

try:
    stats = client.get_analytics()
except Exception as exc:
    st.error(f"Could not load analytics: {exc}")
    stats = {}

col1, col2, col3 = st.columns(3)
col1.metric("Total Queries", stats.get("total_queries", 0))
col2.metric("Unique Sessions", stats.get("unique_sessions", 0))
col3.metric("Avg Latency", f"{stats.get('avg_latency_ms', 0):.0f} ms")

col4, col5 = st.columns(2)
col4.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.0%}")
col5.metric("Hallucination Rate", f"{stats.get('hallucination_rate', 0):.1%}")

st.markdown("---")

intent_dist = stats.get("intent_distribution", {})
if intent_dist:
    st.markdown("**Query Intent Distribution**")
    intent_labels = {
        "academic_calendar": "📅 Academic Calendar",
        "examination": "📝 Examination",
        "placement": "💼 Placement",
        "other": "📋 Other",
    }
    renamed = {intent_labels.get(k, k): v for k, v in intent_dist.items()}
    df_intent = pd.DataFrame(
        list(renamed.items()), columns=["Intent", "Count"]
    ).set_index("Intent")
    st.bar_chart(df_intent, use_container_width=True)
