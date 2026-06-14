"""CIT Admin Panel — approvals, analytics, review history."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.frontend.utils.api_client import client

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="cit-header">
        <div class="cit-seal">🔧</div>
        <div>
            <h1>CIT Admin Panel</h1>
            <p>Coimbatore Institute of Technology · Internal Administration</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_approvals, tab_analytics, tab_history = st.tabs(
    ["📋 Pending Approvals", "📊 Analytics", "🗂️ Review History"]
)

# ── Pending Approvals ─────────────────────────────────────────────────────────
with tab_approvals:
    st.markdown(
        "<div class='cit-card'><b>Pending Human Review</b> — "
        "Responses flagged by the hallucination checker (confidence &lt; 70%) "
        "require a CIT advisor's approval before being shown to students.</div>",
        unsafe_allow_html=True,
    )

    reviewer = st.text_input("Reviewer ID / Name", value="admin", key="reviewer")
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_pending"):
            st.rerun()

    try:
        data = client.list_approvals(status="pending")
        items = data.get("items", [])
    except Exception as exc:
        st.error(f"Could not load approvals: {exc}")
        items = []

    if not items:
        st.info("✅ No pending approvals. All responses have been reviewed.")
    else:
        st.markdown(
            f"<span class='cit-badge'>{len(items)} Pending</span>",
            unsafe_allow_html=True,
        )
        for item in items:
            conf = item["confidence"]
            badge_color = "cit-badge" if conf < 0.5 else "cit-badge cit-badge-gold"
            with st.expander(
                f"[{conf:.0%} confidence]  {item['query'][:90]}…"
            ):
                col_q, col_m = st.columns([3, 1])
                with col_q:
                    st.markdown(f"**Query:**")
                    st.info(item["query"])
                    st.markdown("**Draft Answer:**")
                    st.warning(item["answer"])
                with col_m:
                    st.metric("Confidence Score", f"{conf:.0%}")
                    st.caption(f"Session: `{item['session_id'][:8]}…`")
                    st.caption(f"Created: {item['created_at']}")

                col_approve, col_reject = st.columns(2)
                with col_approve:
                    if st.button("✅ Approve & Publish", key=f"approve_{item['id']}", type="primary"):
                        try:
                            client.approve(
                                approval_id=item["id"],
                                session_id=item["session_id"],
                                status="approved",
                                reviewed_by=reviewer,
                            )
                            st.success("Approved. The answer has been published to the student.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Error: {exc}")
                with col_reject:
                    if st.button("❌ Reject", key=f"reject_{item['id']}"):
                        try:
                            client.approve(
                                approval_id=item["id"],
                                session_id=item["session_id"],
                                status="rejected",
                                reviewed_by=reviewer,
                            )
                            st.warning("Rejected. The student will be notified.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Error: {exc}")

# ── Analytics ─────────────────────────────────────────────────────────────────
with tab_analytics:
    st.markdown(
        "<div class='cit-card'><b>CIT Help Agent — Query Analytics</b></div>",
        unsafe_allow_html=True,
    )

    try:
        stats = client.get_analytics()
    except Exception as exc:
        st.error(f"Could not load analytics: {exc}")
        stats = {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", stats.get("total_queries", 0))
    col2.metric("Unique Sessions", stats.get("unique_sessions", 0))
    col3.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.0%}")
    col4.metric("Hallucination Rate", f"{stats.get('hallucination_rate', 0):.1%}")

    st.metric("Avg Response Latency", f"{stats.get('avg_latency_ms', 0):.0f} ms")

    st.markdown("---")
    intent_dist = stats.get("intent_distribution", {})
    if intent_dist:
        st.markdown("**Queries by Intent Category**")
        st.bar_chart(pd.Series(intent_dist).rename("Queries"), use_container_width=True)

    approval_stats = stats.get("approval_stats", {})
    if approval_stats:
        st.markdown("**Approval Decisions Breakdown**")
        st.bar_chart(pd.Series(approval_stats).rename("Count"), use_container_width=True)

# ── Approval History ──────────────────────────────────────────────────────────
with tab_history:
    st.markdown(
        "<div class='cit-card'><b>Review History</b> — All past approval decisions.</div>",
        unsafe_allow_html=True,
    )

    col_a, col_r = st.columns(2)
    with col_a:
        st.markdown("##### ✅ Approved Responses")
        try:
            approved = client.list_approvals(status="approved")
            st.success(f"Total Approved: {approved.get('total', 0)}")
            if approved.get("items"):
                df = pd.DataFrame(approved["items"])[
                    ["query", "confidence", "reviewed_by", "reviewed_at"]
                ]
                df.columns = ["Query", "Confidence", "Reviewed By", "Reviewed At"]
                st.dataframe(df, use_container_width=True)
        except Exception:
            st.info("No approved items yet.")

    with col_r:
        st.markdown("##### ❌ Rejected Responses")
        try:
            rejected = client.list_approvals(status="rejected")
            st.error(f"Total Rejected: {rejected.get('total', 0)}")
            if rejected.get("items"):
                df = pd.DataFrame(rejected["items"])[
                    ["query", "confidence", "reviewed_by", "reviewed_at"]
                ]
                df.columns = ["Query", "Confidence", "Reviewed By", "Reviewed At"]
                st.dataframe(df, use_container_width=True)
        except Exception:
            st.info("No rejected items yet.")
