"""Render CIT document citation chips below an answer."""
from __future__ import annotations

import streamlit as st


def render_citations(citations: list[dict]) -> None:
    if not citations:
        st.caption("No source citations available.")
        return
    st.markdown("**CIT Source Documents:**")
    for c in citations:
        source = c.get("source", "unknown")
        page = c.get("page", "?")
        st.markdown(
            f"<span class='cit-badge cit-badge-gold'>📄 CIT Document</span> "
            f"`{source}` &nbsp;—&nbsp; Page **{page}**",
            unsafe_allow_html=True,
        )
