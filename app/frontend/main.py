"""Streamlit application entry point — CIT Help Agent."""
import streamlit as st

st.set_page_config(
    page_title="CIT Help Agent — Coimbatore Institute of Technology",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global Classic UI Styles ──────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
    }

    /* Deep navy background */
    .stApp {
        background-color: #f4f1eb;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2744 0%, #0f1a33 100%);
        border-right: 3px solid #c9a84c;
    }
    [data-testid="stSidebar"] * {
        color: #e8dfc8 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: #c9a84c;
        color: #1a2744 !important;
        border: none;
        font-weight: 700;
        border-radius: 4px;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #e0be6a;
    }

    /* Top header banner */
    .cit-header {
        background: linear-gradient(135deg, #1a2744 0%, #0f1a33 100%);
        border-bottom: 4px solid #c9a84c;
        padding: 1.2rem 2rem;
        margin-bottom: 1.5rem;
        border-radius: 6px;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .cit-header h1 {
        color: #fff;
        font-family: 'Merriweather', serif;
        font-size: 1.6rem;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .cit-header p {
        color: #c9a84c;
        margin: 0;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .cit-seal {
        font-size: 3rem;
        line-height: 1;
    }

    /* Cards */
    .cit-card {
        background: #fff;
        border: 1px solid #d4c9a8;
        border-left: 5px solid #1a2744;
        border-radius: 6px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 8px;
        margin-bottom: 0.6rem;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: #1a2744;
        color: #fff;
        border: 2px solid #1a2744;
        font-weight: 600;
        border-radius: 4px;
        padding: 0.4rem 1.4rem;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: #c9a84c;
        border-color: #c9a84c;
        color: #1a2744;
    }

    /* Divider gold */
    hr {
        border: none;
        border-top: 2px solid #c9a84c;
        margin: 1.2rem 0;
    }

    /* Tabs */
    [data-testid="stTabs"] button {
        font-weight: 600;
        color: #1a2744;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 3px solid #c9a84c;
        color: #1a2744;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid #d4c9a8;
        border-top: 3px solid #1a2744;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }

    /* Input fields */
    .stTextInput input, .stChatInput textarea {
        border: 1.5px solid #1a2744;
        border-radius: 4px;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #d4c9a8;
        border-radius: 6px;
        background: #faf8f3;
    }

    /* Badge */
    .cit-badge {
        display: inline-block;
        background: #1a2744;
        color: #c9a84c;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 2px 10px;
        border-radius: 12px;
        margin-right: 6px;
    }
    .cit-badge-gold {
        background: #c9a84c;
        color: #1a2744;
    }

    /* Footer */
    .cit-footer {
        text-align: center;
        color: #888;
        font-size: 0.78rem;
        padding: 2rem 0 0.5rem;
        border-top: 1px solid #d4c9a8;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

from app.auth.firebase_auth import init_auth_state, is_logged_in, logout, current_user
from app.auth.login_page import render_auth_page

init_auth_state()

if not is_logged_in():
    render_auth_page()
    st.stop()

# ── Logged-in app ─────────────────────────────────────────────────────────────
user = current_user()
role = user.get("role", "student")

chat = st.Page("pages/1_chat.py", title="Student Assistant", icon="💬", default=True)
statistics = st.Page("pages/4_statistics.py", title="Statistics", icon="📊")

if role == "admin":
    admin = st.Page("pages/2_admin.py", title="Admin Panel", icon="🔧")
    diagnostics = st.Page("pages/3_diagnostics.py", title="RAG Diagnostics", icon="🔍")
    pages = [chat, admin, diagnostics, statistics]
else:
    pages = [chat, statistics]

pg = st.navigation(pages)

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="font-size:2.8rem;">🏛️</div>
            <div style="font-family:'Merriweather',serif; font-size:1.1rem;
                        color:#fff; font-weight:700; margin-top:4px;">
                CIT Help Agent
            </div>
            <div style="color:#c9a84c; font-size:0.72rem; letter-spacing:1.5px;
                        text-transform:uppercase; margin-top:2px;">
                Coimbatore Institute of Technology
            </div>
        </div>
        <hr style="border-top:1px solid #c9a84c; margin: 0.8rem 0;"/>
        <div style="font-size:0.8rem; color:#e8dfc8; padding: 0 0.5rem;">
            👤 <b>{user.get('displayName', 'Student')}</b><br/>
            <span style="color:#c9a84c; font-size:0.72rem;">{user.get('email','')}</span><br/>
            <span style="font-size:0.68rem; text-transform:uppercase; letter-spacing:1px;
                         color:#aaa;">{role}</span>
        </div>
        <hr style="border-top:1px solid #c9a84c; margin: 0.8rem 0;"/>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()
        st.rerun()

pg.run()

st.markdown(
    '<div class="cit-footer">© Coimbatore Institute of Technology · Official Document Assistant · For academic use only</div>',
    unsafe_allow_html=True,
)
