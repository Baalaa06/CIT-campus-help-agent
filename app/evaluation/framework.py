"""Evaluation framework — runs all questions, computes metrics, prints report."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from app.evaluation.metrics.accuracy import score_accuracy
from app.evaluation.metrics.hallucination import hallucination_rate
from app.evaluation.metrics.latency import latency_stats
from app.evaluation.metrics.retrieval import precision_at_k, recall_at_k
from app.frontend.utils.api_client import client


def load_questions(path: str | None = None) -> list[dict]:
    p = Path(path or "app/evaluation/datasets/eval_questions.json")
    with p.open() as f:
        return json.load(f)["questions"]


def run_evaluation(
    questions: list[dict] | None = None,
    output_path: str = "eval_report.json",
) -> dict:
    qs = questions or load_questions()

    accuracy_scores: list[float] = []
    precision_scores: list[float] = []
    recall_scores: list[float] = []
    confidences: list[float] = []
    latencies: list[float] = []
    results: list[dict] = []

    session_id = f"eval_{uuid.uuid4().hex[:8]}"

    print(f"[Eval] Running {len(qs)} questions…")

    for q in qs:
        t0 = time.perf_counter()
        try:
            resp = client.query(
                user_id="evaluator",
                session_id=session_id,
                query=q["question"],
            )
        except Exception as exc:
            print(f"  [!] {q['id']} failed: {exc}")
            continue
        elapsed_ms = (time.perf_counter() - t0) * 1000

        answer = resp.get("answer", "")
        citations = resp.get("citations", [])
        confidence = resp.get("confidence", 0.0)
        expected_src = q.get("expected_source")

        acc = score_accuracy(q["question"], answer)
        prec = precision_at_k(citations, expected_src)
        rec = recall_at_k(citations, expected_src)

        accuracy_scores.append(acc)
        precision_scores.append(prec)
        recall_scores.append(rec)
        confidences.append(confidence)
        latencies.append(elapsed_ms)

        results.append(
            {
                "id": q["id"],
                "question": q["question"],
                "category": q.get("category"),
                "answer": answer,
                "citations": citations,
                "confidence": confidence,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "latency_ms": round(elapsed_ms, 1),
            }
        )
        print(f"  {q['id']}: acc={acc:.2f} prec={prec:.1f} conf={confidence:.2f} lat={elapsed_ms:.0f}ms")

    report = {
        "summary": {
            "total_questions": len(results),
            "avg_accuracy": round(sum(accuracy_scores) / max(len(accuracy_scores), 1), 3),
            "avg_precision": round(sum(precision_scores) / max(len(precision_scores), 1), 3),
            "avg_recall": round(sum(recall_scores) / max(len(recall_scores), 1), 3),
            "hallucination_rate": round(hallucination_rate(confidences), 3),
            "latency": latency_stats(latencies),
        },
        "results": results,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== Evaluation Report ===")
    for k, v in report["summary"].items():
        print(f"  {k}: {v}")
    print(f"\nFull report saved to {output_path}")
    return report
