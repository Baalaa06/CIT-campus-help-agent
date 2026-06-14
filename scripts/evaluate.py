#!/usr/bin/env python
"""CLI: run the full evaluation suite and write a JSON report.

Usage:
    python scripts/evaluate.py
    python scripts/evaluate.py --output my_report.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.evaluation.framework import run_evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Campus Help Agent evaluation")
    parser.add_argument("--output", default="eval_report.json", help="Output JSON path")
    args = parser.parse_args()

    run_evaluation(output_path=args.output)
