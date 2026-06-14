"""Firebase Authentication + Firestore user profile via REST API."""
from __future__ import annotations

import requests
import streamlit as st

FIREBASE_AUTH_API = "https://identitytoolkit.googleapis.com/v1/accounts"


def _api_key() -> str:
    return st.secrets["FIREBASE_WEB_API_KEY"]


def _project_id() -> str:
    return st.secrets["FIREBASE_PROJECT_ID"]


def _auth_post(endpoint: str, payload: dict) -> dict:
    resp = requests.post(
        f"{FIREBASE_AUTH_API}:{endpoint}?key={_api_key()}",
        json=payload,
        timeout=10,
    )
    data = resp.json()
    if "error" in data:
        raise ValueError(data["error"].get("message", "Authentication error"))
    return data


# ── Firestore REST helpers ────────────────────────────────────────────────────

def _fs_url(collection: str, doc_id: str) -> str:
    pid = _project_id()
    return (
        f"https://firestore.googleapis.com/v1/projects/{pid}"
        f"/databases/(default)/documents/{collection}/{doc_id}"
    )


def _fs_get(collection: str, doc_id: str, id_token: str) -> dict | None:
    resp = requests.get(
        _fs_url(collection, doc_id),
        headers={"Authorization": f"Bearer {id_token}"},
        timeout=10,
    )
    if resp.status_code == 404:
        return None
    data = resp.json()
    if "error" in data:
        return None
    # Convert Firestore typed values → plain strings
    return {k: list(v.values())[0] for k, v in data.get("fields", {}).items()}


def _fs_set(collection: str, doc_id: str, payload: dict, id_token: str) -> None:
    fields = {k: {"stringValue": str(v)} for k, v in payload.items()}
    requests.patch(
        _fs_url(collection, doc_id),
        json={"fields": fields},
        headers={"Authorization": f"Bearer {id_token}"},
        timeout=10,
    )


# ── Auth functions ────────────────────────────────────────────────────────────

def register(email: str, password: str, display_name: str) -> dict:
    """Create Firebase user, set display name, create Firestore user doc with role=student."""
    data = _auth_post("signUp", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })
    _auth_post("update", {
        "idToken": data["idToken"],
        "displayName": display_name,
        "returnSecureToken": False,
    })
    # Write user doc → this creates the 'users' collection automatically
    _fs_set("users", data["localId"], {
        "uid": data["localId"],
        "email": email,
        "displayName": display_name,
        "role": "student",
    }, data["idToken"])
    return data


def login(email: str, password: str) -> dict:
    """Sign in and fetch role from Firestore."""
    data = _auth_post("signInWithPassword", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })
    # Read role from Firestore; create doc if it doesn't exist yet
    user_doc = _fs_get("users", data["localId"], data["idToken"])
    if user_doc is None:
        _fs_set("users", data["localId"], {
            "uid": data["localId"],
            "email": email,
            "displayName": data.get("displayName", email.split("@")[0]),
            "role": "student",
        }, data["idToken"])
        role = "student"
    else:
        role = user_doc.get("role", "student")

    data["role"] = role
    return data


def send_password_reset(email: str) -> None:
    _auth_post("sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})


# ── Streamlit session helpers ─────────────────────────────────────────────────

def init_auth_state() -> None:
    for key, default in [
        ("auth_user", None),
        ("auth_page", "login"),
        ("auth_error", ""),
        ("auth_success", ""),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def is_logged_in() -> bool:
    return st.session_state.get("auth_user") is not None


def current_user() -> dict:
    return st.session_state.get("auth_user", {})


def logout() -> None:
    st.session_state.auth_user = None
    st.session_state.auth_error = ""
    st.session_state.auth_success = ""
    for key in ["session_id", "messages"]:
        if key in st.session_state:
            del st.session_state[key]
