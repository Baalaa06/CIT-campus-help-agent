"""CIT Student Chat Assistant — main chat page."""
from __future__ import annotations

import uuid

import streamlit as st

from app.auth.firebase_auth import current_user
from app.frontend.components.chat_message import render_message
from app.frontend.components.citation_card import render_citations
from app.frontend.components.confidence_meter import render_confidence
from app.frontend.components.feedback_buttons import render_feedback
from app.frontend.utils.api_client import client

# ── Session initialisation ────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

user = current_user()
user_id = user.get("uid", "student")
display_name = user.get("displayName", "Student")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"#### 🎓 Welcome, {display_name}")
    st.caption(f"Session `{st.session_state.session_id[:8]}…`")
    st.markdown("---")
    if st.button("➕ New Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.78rem; color:#c9a84c; line-height:1.7;">
        <b>Topics I can help with:</b><br/>
        📅 Academic Calendar<br/>
        📝 Examination Rules<br/>
        💼 Placement Information<br/>
        📋 Regulations &amp; Policies
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="cit-header">
        <div class="cit-seal">🏛️</div>
        <div>
            <h1>CIT Student Assistant</h1>
            <p>Coimbatore Institute of Technology · Official Document Q&amp;A</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Backend health check ──────────────────────────────────────────────────────
if not client.health():
    st.error(
        "⚠️ The CIT Help Agent backend is not reachable. "
        "Please start the FastAPI server and refresh."
    )
    st.stop()

# ── Welcome message ───────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        """
        <div class="cit-card">
            <b>Welcome to the CIT Help Agent.</b><br/>
            Ask any question about CIT's academic calendar, examination regulations,
            placement records, or institutional policies. All answers are sourced
            exclusively from official CIT documents.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Render existing messages ──────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    render_message(msg["role"], msg["content"])
    if msg["role"] == "assistant":
        with st.expander("📄 Sources & Confidence", expanded=False):
            render_citations(msg.get("citations", []))
            render_confidence(msg.get("confidence", 0.0))
        render_feedback(
            session_id=st.session_state.session_id,
            user_id=user_id,
            query=msg.get("query", ""),
            answer=msg["content"],
            key_prefix=f"fb_{i}",
        )

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about CIT academics, exams, placements…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    with st.spinner("Searching CIT documents…"):
        try:
            result = client.query(
                user_id=user_id,
                session_id=st.session_state.session_id,
                query=prompt,
            )
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            st.stop()

    answer = result.get("answer", "No answer returned.")
    citations = result.get("citations", [])
    confidence = result.get("confidence", 0.0)
    needs_approval = result.get("needs_human_approval", False)

    if needs_approval:
        answer = (
            "⏳ **Your query is under review by a CIT advisor.** "
            "The answer will be made available once approved."
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "citations": citations,
            "confidence": confidence,
            "query": prompt,
        }
    )
    render_message("assistant", answer)

    if not needs_approval:
        with st.expander("📄 Sources & Confidence", expanded=True):
            render_citations(citations)
            render_confidence(confidence)
        render_feedback(
            session_id=st.session_state.session_id,
            user_id=user_id,
            query=prompt,
            answer=answer,
            key_prefix="fb_latest",
        )
