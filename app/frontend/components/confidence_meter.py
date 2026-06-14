"""Visual confidence score bar for CIT answer grounding."""
from __future__ import annotations

import streamlit as st


def render_confidence(confidence: float) -> None:
    pct = round(confidence * 100)
    if confidence >= 0.8:
        label, note = "High ✅", "Answer is well-grounded in CIT documents."
    elif confidence >= 0.6:
        label, note = "Medium ⚠️", "Answer is mostly grounded; minor uncertainty."
    else:
        label, note = "Low 🔴", "Answer has low grounding — treat with caution."

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Confidence", f"{pct}%")
    with col2:
        st.progress(confidence, text=f"Grounding: {label}")
        st.caption(note)
