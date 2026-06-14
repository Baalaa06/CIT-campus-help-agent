"""Render a single chat message bubble."""
from __future__ import annotations

import streamlit as st


def render_message(role: str, content: str) -> None:
    avatar = "🏛️" if role == "assistant" else "🎓"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
