"""FastAPI application factory with lifespan for resource management."""
from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.backend.api.routes import approvals, feedback, history, query
from app.backend.middleware.rate_limiter import limiter
from app.backend.middleware.security import SecurityMiddleware
from app.database.firestore_db import init_firestore
from app.graph.graph import build_graph
from app.memory.checkpointer import get_checkpointer_context
from app.monitoring.langsmith_setup import configure_langsmith
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Configure tracing
    configure_langsmith()

    # 2. Initialise Firestore
    sa = json.loads(settings.firebase_service_account_json)
    init_firestore(sa)
    print("[Startup] Firestore initialised.")

    # 3. Build the LangGraph agent (checkpointer lives for the app lifetime)
    async with get_checkpointer_context() as checkpointer:
        app.state.graph = build_graph(checkpointer)
        print("[Startup] LangGraph agent compiled and ready.")
        yield

    print("[Shutdown] Resources released.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CIT Help Agent API — Coimbatore Institute of Technology",
        description="RAG-powered student assistant backed by official CIT documents.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS — allow Streamlit frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security headers + latency tracking
    app.add_middleware(SecurityMiddleware)

    # Routes
    app.include_router(query.router, tags=["Query"])
    app.include_router(feedback.router, tags=["Feedback"])
    app.include_router(history.router, tags=["History"])
    app.include_router(approvals.router, tags=["Approvals"])

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False,
    )
