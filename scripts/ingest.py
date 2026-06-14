#!/usr/bin/env python
"""CLI: run the full PDF ingestion pipeline.

Usage:
    python scripts/ingest.py
    python scripts/ingest.py --data-dir ./data
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.firestore_db import init_firestore
from app.rag.ingestion.pipeline import run_ingestion
from config.settings import settings


async def main(data_dir: str) -> None:
    print("[Ingest] Initialising Firestore…")
    import os
    sa_path = settings.firebase_service_account_path
    if os.path.exists(sa_path):
        with open(sa_path, "r") as f:
            sa = json.load(f)
    else:
        sa = json.loads(settings.firebase_service_account_json)
    init_firestore(sa)

    print(f"[Ingest] Starting ingestion from: {data_dir}")
    result = await run_ingestion(data_dir=data_dir)

    print("\n[Ingest] Complete!")
    print(f"  Pages loaded  : {result['total_pages']}")
    print(f"  Chunks stored : {result['total_chunks']}")
    print("  By source:")
    for src, cnt in result["by_source"].items():
        print(f"    {src}: {cnt} chunks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CIT PDFs into ChromaDB + Firestore")
    parser.add_argument("--data-dir", default="./data", help="Directory containing PDF files")
    args = parser.parse_args()
    asyncio.run(main(args.data_dir))
