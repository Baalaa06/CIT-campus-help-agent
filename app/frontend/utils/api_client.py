"""Synchronous HTTP client for the FastAPI backend."""
from __future__ import annotations

import streamlit as st

import requests

# Read backend URL from Streamlit secrets (set on Streamlit Cloud)
# Falls back to localhost for local dev
try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
except Exception:
    BACKEND_URL = "http://localhost:8000"

TIMEOUT = 90


class BackendClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base = base_url.rstrip("/")

    def query(self, user_id: str, session_id: str, query: str) -> dict:
        resp = requests.post(
            f"{self.base}/query",
            json={"user_id": user_id, "session_id": session_id, "query": query},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def submit_feedback(
        self, session_id: str, user_id: str, query: str, answer: str, rating: str
    ) -> dict:
        resp = requests.post(
            f"{self.base}/feedback",
            json={
                "session_id": session_id,
                "user_id": user_id,
                "query": query,
                "answer": answer,
                "rating": rating,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_history(self, session_id: str) -> dict:
        resp = requests.get(f"{self.base}/history/{session_id}", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def list_approvals(self, status: str = "pending") -> dict:
        resp = requests.get(
            f"{self.base}/approvals", params={"status": status}, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def approve(
        self, approval_id: str, session_id: str, status: str, reviewed_by: str
    ) -> dict:
        resp = requests.post(
            f"{self.base}/approve",
            json={
                "approval_id": approval_id,
                "session_id": session_id,
                "status": status,
                "reviewed_by": reviewed_by,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self) -> dict:
        resp = requests.get(f"{self.base}/analytics", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_docs_stats(self) -> dict:
        resp = requests.get(f"{self.base}/docs-stats", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> bool:
        try:
            resp = requests.get(f"{self.base}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


client = BackendClient()
