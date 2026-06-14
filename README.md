# Campus Help Agent

A production-ready RAG-powered campus assistant built with LangGraph, LangChain, ChromaDB, and Claude. Answers student questions **exclusively** from official university documents.

## Architecture

```
START
  ↓ query_analyzer       (sanitize, injection-check)
  ↓ intent_classifier    (LLM: calendar/exam/placement/other)
  ↓ memory_fetch         (history from LangGraph checkpointer)
  ↓ retriever            (ChromaDB, top-10)
  ↓ reranker             (BGE cross-encoder, top-3)
  ↓ context_builder      (format context + citations)
  ↓ response_generator   (Claude — grounded answer)
  ↓ hallucination_checker (confidence score)
  ↓ [conditional]
       confidence < 0.7 → human_approval (interrupt)
       else             → feedback_collector
  ↓ feedback_collector   (persist user rating)
  ↓ memory_updater       (append turn to history)
END
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent | LangGraph 0.2+ |
| RAG | LangChain + ChromaDB (embedded) |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Reranker | BAAI/bge-reranker-base |
| LLM | Anthropic Claude (Haiku + Sonnet) |
| Database | SQLite (via aiosqlite + SQLAlchemy async) |
| Checkpointer | LangGraph AsyncSqliteSaver |
| Backend | FastAPI |
| Frontend | Streamlit |
| Monitoring | LangSmith |
| Deployment | Docker Compose |

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Ingest documents

```bash
python scripts/ingest.py --data-dir ./data
```

### 4. Start backend

```bash
python -m uvicorn app.backend.main:app --reload --port 8000
```

### 5. Start frontend (new terminal)

```bash
python -m streamlit run app/frontend/main.py
```

Open http://localhost:8501

## Docker (full stack)

```bash
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env
docker-compose up --build
```

Services:
- `ingestion` runs once, then exits
- `backend` starts at http://localhost:8000
- `frontend` starts at http://localhost:8501

## Project Structure

```
campus-help-agent/
├── data/                          # PDF source documents
├── data_store/                    # SQLite files + ChromaDB (auto-created)
├── config/settings.py             # All configuration
├── app/
│   ├── frontend/                  # Streamlit UI
│   ├── backend/                   # FastAPI API
│   ├── graph/                     # LangGraph agent
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── graph.py               # Graph assembly
│   │   └── nodes/                 # 11 node functions
│   ├── rag/                       # Ingestion + retrieval
│   ├── database/                  # SQLAlchemy models + migrations
│   ├── memory/                    # Checkpointer + store
│   ├── monitoring/                # LangSmith setup + metrics
│   └── evaluation/                # Eval framework + metrics
├── scripts/                       # CLI tools
├── tests/                         # pytest suite
├── docker/                        # Dockerfiles
└── docker-compose.yml
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/query` | Submit a question |
| POST | `/feedback` | Submit thumbs up/down |
| GET | `/history/{session_id}` | Conversation history |
| GET | `/approvals?status=pending` | List approval queue |
| POST | `/approve` | Approve/reject + resume graph |
| GET | `/analytics` | Aggregate stats |
| GET | `/docs-stats` | Document chunk counts |
| GET | `/health` | Health check |

## Human Approval Workflow

When the hallucination checker assigns `confidence < 0.7`:

1. The LangGraph graph calls `interrupt()` — execution pauses.
2. The approval record is written to `approval_requests` (SQLite).
3. The API returns `needs_human_approval: true`.
4. An admin visits the Admin Dashboard and clicks **Approve** or **Reject**.
5. The frontend calls `POST /approve`.
6. The backend resumes the graph with `Command(resume={status})`.
7. The graph continues and the final answer is returned.

## Evaluation

```bash
# Run eval suite (requires backend running)
python scripts/evaluate.py --output eval_report.json
```

Metrics computed:
- **Answer accuracy** — LLM-as-judge (0.0–1.0)
- **Retrieval precision** — expected source in citations
- **Hallucination rate** — fraction of low-confidence responses
- **Latency** — P50/P95/P99/avg/max

## Environment Variables

See `.env.example` for the full list. Required:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Optional (LangSmith tracing):
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=campus-help-agent
```

## Testing

```bash
pytest tests/ -v
```
