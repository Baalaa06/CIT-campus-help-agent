"""Firebase Firestore database layer — replaces SQLite for all user-facing data.

Collections:
  users/              — user profiles (uid, email, displayName, role, createdAt)
  conversations/      — chat history per session
  query_logs/         — analytics per query
  feedback/           — thumbs up/down
  approval_requests/  — low-confidence answers pending review
  documents/          — indexed PDF chunk metadata
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.async_client import AsyncClient

_app: firebase_admin.App | None = None
_db: AsyncClient | None = None


def init_firestore(service_account_dict: dict) -> AsyncClient:
    """Initialise Firebase Admin SDK and return async Firestore client."""
    global _app, _db
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_dict)
        _app = firebase_admin.initialize_app(cred)
    _db = firestore.AsyncClient(
        project=service_account_dict["project_id"],
        credentials=firebase_admin.get_app().credential.get_credential(),
    )
    return _db


def get_db() -> AsyncClient:
    if _db is None:
        raise RuntimeError("Firestore not initialised. Call init_firestore() first.")
    return _db


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Users ─────────────────────────────────────────────────────────────────────

async def upsert_user(uid: str, email: str, display_name: str, role: str = "student") -> None:
    db = get_db()
    ref = db.collection("users").document(uid)
    doc = await ref.get()
    if not doc.exists:
        await ref.set({
            "uid": uid,
            "email": email,
            "displayName": display_name,
            "role": role,
            "createdAt": _now(),
            "lastLogin": _now(),
        })
    else:
        await ref.update({"lastLogin": _now()})


async def get_user(uid: str) -> dict | None:
    db = get_db()
    doc = await db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None


async def get_user_role(uid: str) -> str:
    user = await get_user(uid)
    return user.get("role", "student") if user else "student"


# ── Conversations ─────────────────────────────────────────────────────────────

async def save_conversation_turn(
    session_id: str, user_id: str, query: str, answer: str, intent: str
) -> None:
    db = get_db()
    col = db.collection("conversations")
    for role, content in [("user", query), ("assistant", answer)]:
        await col.add({
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "intent": intent,
            "createdAt": _now(),
        })


async def get_conversation_history(session_id: str) -> list[dict]:
    db = get_db()
    docs = (
        db.collection("conversations")
        .where("session_id", "==", session_id)
        .order_by("createdAt")
    )
    results = []
    async for doc in docs.stream():
        results.append(doc.to_dict())
    return results


# ── Query Logs ────────────────────────────────────────────────────────────────

async def log_query(
    session_id: str,
    user_id: str,
    query: str,
    intent: str,
    answer: str,
    confidence: float,
    total_latency_ms: float,
    hallucination_flag: bool,
    num_docs_retrieved: int,
) -> None:
    db = get_db()
    await db.collection("query_logs").add({
        "id": str(uuid4()),
        "session_id": session_id,
        "user_id": user_id,
        "query": query,
        "intent": intent,
        "answer": answer,
        "confidence": confidence,
        "total_latency_ms": total_latency_ms,
        "hallucination_flag": hallucination_flag,
        "num_docs_retrieved": num_docs_retrieved,
        "createdAt": _now(),
    })


async def get_analytics() -> dict:
    db = get_db()
    docs = [d.to_dict() async for d in db.collection("query_logs").stream()]

    if not docs:
        return {
            "total_queries": 0, "unique_sessions": 0,
            "avg_confidence": 0.0, "hallucination_rate": 0.0,
            "avg_latency_ms": 0.0, "intent_distribution": {}, "approval_stats": {},
        }

    total = len(docs)
    unique_sessions = len({d["session_id"] for d in docs})
    avg_conf = sum(d.get("confidence", 0) for d in docs) / total
    avg_lat = sum(d.get("total_latency_ms", 0) for d in docs) / total
    hall_rate = sum(1 for d in docs if d.get("hallucination_flag")) / total

    intent_dist: dict[str, int] = {}
    for d in docs:
        k = d.get("intent") or "unknown"
        intent_dist[k] = intent_dist.get(k, 0) + 1

    # Approval stats
    approval_docs = [d.to_dict() async for d in db.collection("approval_requests").stream()]
    approval_stats: dict[str, int] = {}
    for d in approval_docs:
        k = d.get("status", "unknown")
        approval_stats[k] = approval_stats.get(k, 0) + 1

    return {
        "total_queries": total,
        "unique_sessions": unique_sessions,
        "avg_confidence": round(avg_conf, 3),
        "hallucination_rate": round(hall_rate, 3),
        "avg_latency_ms": round(avg_lat, 1),
        "intent_distribution": intent_dist,
        "approval_stats": approval_stats,
    }


# ── Feedback ──────────────────────────────────────────────────────────────────

async def save_feedback(
    session_id: str, user_id: str, query: str, answer: str, rating: str
) -> str:
    db = get_db()
    fid = str(uuid4())
    await db.collection("feedback").document(fid).set({
        "id": fid,
        "session_id": session_id,
        "user_id": user_id,
        "query": query,
        "answer": answer,
        "rating": rating,
        "createdAt": _now(),
    })
    return fid


# ── Approval Requests ─────────────────────────────────────────────────────────

async def create_approval(
    approval_id: str, session_id: str, query: str, answer: str, confidence: float
) -> None:
    db = get_db()
    await db.collection("approval_requests").document(approval_id).set({
        "id": approval_id,
        "session_id": session_id,
        "query": query,
        "answer": answer,
        "confidence": confidence,
        "status": "pending",
        "reviewed_by": None,
        "reviewed_at": None,
        "createdAt": _now(),
    })


async def update_approval(approval_id: str, status: str, reviewed_by: str) -> None:
    db = get_db()
    await db.collection("approval_requests").document(approval_id).update({
        "status": status,
        "reviewed_by": reviewed_by,
        "reviewed_at": _now(),
    })


async def list_approvals(status: str = "pending") -> list[dict]:
    db = get_db()
    docs = (
        db.collection("approval_requests")
        .where("status", "==", status)
        .order_by("createdAt", direction="DESCENDING")
    )
    return [d.to_dict() async for d in docs.stream()]


# ── Document Stats ────────────────────────────────────────────────────────────

async def save_chunks_metadata(chunks: list[dict]) -> None:
    """chunks: list of {filename, chunk_id, page_number, chunk_index}"""
    db = get_db()
    col = db.collection("documents")
    batch = db.batch()
    for chunk in chunks:
        ref = col.document(chunk["chunk_id"])
        batch.set(ref, {**chunk, "createdAt": _now()})
    await batch.commit()


async def get_docs_stats() -> dict:
    db = get_db()
    counts: dict[str, int] = {}
    pages: dict[str, int] = {}
    async for doc in db.collection("documents").stream():
        d = doc.to_dict()
        fn = d.get("filename", "unknown")
        counts[fn] = counts.get(fn, 0) + 1
        pages[fn] = max(pages.get(fn, 0), d.get("page_number", 0))

    documents = [
        {"filename": fn, "chunk_count": counts[fn], "page_count": pages.get(fn, 0)}
        for fn in counts
    ]
    return {"documents": documents, "total_chunks": sum(counts.values())}
