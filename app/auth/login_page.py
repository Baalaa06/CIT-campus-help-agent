"""CIT Login / Register / Password Reset UI."""
from __future__ import annotations

import streamlit as st

from app.auth.firebase_auth import (
    init_auth_state,
    is_logged_in,
    login,
    logout,
    register,
    send_password_reset,
)

_FORM_CSS = """
<style>
.auth-wrapper {
    max-width: 420px;
    margin: 3rem auto 0;
    background: #fff;
    border: 1px solid #d4c9a8;
    border-top: 5px solid #1a2744;
    border-radius: 8px;
    padding: 2.5rem 2.5rem 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.10);
}
.auth-logo {
    text-align: center;
    margin-bottom: 0.3rem;
    font-size: 3rem;
}
.auth-title {
    text-align: center;
    font-family: 'Merriweather', serif;
    font-size: 1.3rem;
    color: #1a2744;
    font-weight: 700;
    margin-bottom: 0.1rem;
}
.auth-sub {
    text-align: center;
    color: #c9a84c;
    font-size: 0.75rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 1.8rem;
}
.auth-divider {
    border: none;
    border-top: 1px solid #e0d9c8;
    margin: 1.2rem 0;
}
</style>
"""


def render_auth_page() -> None:
    init_auth_state()
    st.markdown(_FORM_CSS, unsafe_allow_html=True)

    page = st.session_state.auth_page

    # Center column
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            """
            <div class="auth-wrapper">
                <div class="auth-logo">🏛️</div>
                <div class="auth-title">CIT Help Agent</div>
                <div class="auth-sub">Coimbatore Institute of Technology</div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
        if st.session_state.auth_success:
            st.success(st.session_state.auth_success)

        if page == "login":
            _render_login()
        elif page == "register":
            _render_register()
        elif page == "reset":
            _render_reset()

        st.markdown("</div>", unsafe_allow_html=True)


def _render_login() -> None:
    st.markdown("#### Sign In")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("CIT Email", placeholder="yourname@citchennai.net")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

    if submitted:
        st.session_state.auth_error = ""
        st.session_state.auth_success = ""
        if not email or not password:
            st.session_state.auth_error = "Please enter your email and password."
            st.rerun()
        else:
            try:
                data = login(email, password)
                st.session_state.auth_user = {
                    "uid": data["localId"],
                    "email": data["email"],
                    "displayName": data.get("displayName", email.split("@")[0]),
                    "idToken": data["idToken"],
                    "refreshToken": data["refreshToken"],
                    "role": data.get("role", "student"),
                }
                st.session_state.auth_success = ""
                st.rerun()
            except ValueError as e:
                st.session_state.auth_error = _friendly_error(str(e))
                st.rerun()

    st.markdown('<hr class="auth-divider"/>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Account", use_container_width=True):
            st.session_state.auth_page = "register"
            st.session_state.auth_error = ""
            st.rerun()
    with col2:
        if st.button("Forgot Password", use_container_width=True):
            st.session_state.auth_page = "reset"
            st.session_state.auth_error = ""
            st.rerun()


def _render_register() -> None:
    st.markdown("#### Create Account")
    with st.form("register_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="e.g. Arjun Kumar")
        email = st.text_input("CIT Email", placeholder="yourname@citchennai.net")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

    if submitted:
        st.session_state.auth_error = ""
        if not all([name, email, password, confirm]):
            st.session_state.auth_error = "All fields are required."
        elif password != confirm:
            st.session_state.auth_error = "Passwords do not match."
        elif len(password) < 6:
            st.session_state.auth_error = "Password must be at least 6 characters."
        else:
            try:
                register(email, password, name)
                st.session_state.auth_success = (
                    "Account created! Please sign in."
                )
                st.session_state.auth_page = "login"
                st.rerun()
            except ValueError as e:
                st.session_state.auth_error = _friendly_error(str(e))
                st.rerun()

    st.markdown('<hr class="auth-divider"/>', unsafe_allow_html=True)
    if st.button("← Back to Sign In", use_container_width=True):
        st.session_state.auth_page = "login"
        st.session_state.auth_error = ""
        st.rerun()


def _render_reset() -> None:
    st.markdown("#### Reset Password")
    st.caption("Enter your CIT email and we'll send a reset link.")
    with st.form("reset_form", clear_on_submit=False):
        email = st.text_input("CIT Email", placeholder="yourname@citchennai.net")
        submitted = st.form_submit_button("Send Reset Link", type="primary", use_container_width=True)

    if submitted:
        if not email:
            st.session_state.auth_error = "Please enter your email."
            st.rerun()
        else:
            try:
                send_password_reset(email)
                st.session_state.auth_success = (
                    f"Password reset email sent to {email}. Check your inbox."
                )
                st.session_state.auth_page = "login"
                st.rerun()
            except ValueError as e:
                st.session_state.auth_error = _friendly_error(str(e))
                st.rerun()

    st.markdown('<hr class="auth-divider"/>', unsafe_allow_html=True)
    if st.button("← Back to Sign In", use_container_width=True):
        st.session_state.auth_page = "login"
        st.session_state.auth_error = ""
        st.rerun()


def _friendly_error(msg: str) -> str:
    mapping = {
        "EMAIL_EXISTS": "This email is already registered. Please sign in.",
        "INVALID_EMAIL": "Invalid email address.",
        "WEAK_PASSWORD": "Password is too weak. Use at least 6 characters.",
        "EMAIL_NOT_FOUND": "No account found with this email.",
        "INVALID_PASSWORD": "Incorrect password.",
        "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Please try again later.",
        "USER_DISABLED": "This account has been disabled. Contact CIT admin.",
    }
    for key, friendly in mapping.items():
        if key in msg:
            return friendly
    return msg
