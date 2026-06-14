"""Thumbs-up / thumbs-down feedback widget for CIT Help Agent."""
from __future__ import annotations

import streamlit as st

from app.frontend.utils.api_client import client


def render_feedback(
    session_id: str,
    user_id: str,
    query: str,
    answer: str,
    key_prefix: str,
) -> None:
    st.markdown(
        "<span style='font-size:0.8rem; color:#666;'>Was this answer helpful?</span>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if st.button("👍 Yes", key=f"{key_prefix}_up", help="This answer was helpful"):
            try:
                client.submit_feedback(session_id, user_id, query, answer, "positive")
                st.success("Thank you for your feedback!", icon="✅")
            except Exception:
                st.error("Could not save feedback.")
    with col2:
        if st.button("👎 No", key=f"{key_prefix}_down", help="This answer was not helpful"):
            try:
                client.submit_feedback(session_id, user_id, query, answer, "negative")
                st.info("Thank you. We'll use this to improve CIT Help Agent.", icon="📝")
            except Exception:
                st.error("Could not save feedback.")
