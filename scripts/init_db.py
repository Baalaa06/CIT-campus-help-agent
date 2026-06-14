#!/usr/bin/env python
"""CLI: create all SQLite tables and verify them.

Usage:
    python scripts/init_db.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.migrations.init_db import init_db


if __name__ == "__main__":
    asyncio.run(init_db())
