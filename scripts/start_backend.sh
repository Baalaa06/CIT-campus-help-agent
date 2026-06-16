#!/bin/sh
if [ ! -d "./data_store/chroma_db" ] || [ -z "$(ls -A ./data_store/chroma_db 2>/dev/null)" ]; then
    echo "ChromaDB empty — running ingestion..."
    python scripts/ingest.py --data-dir ./data
fi
exec python -m uvicorn app.backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
