"""Offline Baseline Evaluator for v0.1 `StaticThresholdDetector`.

Generates a deterministic synthetic benchmark covering all 5 business/fault
scenarios and reports Precision, Recall, F1, and False Positive Rate (FPR)
for the legacy static-threshold baseline.

Member B (Sprint 1, Issue #5 & #6):
Your first ML models (IsolationForest / LightGBM) MUST be evaluated on the
same scenario mix (plus ETL-collected Parquet data) and beat this baseline!
"""

from __future__ import annotations

import random

from opspulse_core.schemas import FaultScenario
from services.inference_api.detector import StaticThresholdDetector
from services.target_app.app import FaultState


def run_benchmark(samples_per_scenario: int = 200, seed: int = 42) -> dict[str, float]:
    rng = random.Random(seed)
    detector = StaticThresholdDetector()
    sim = FaultState()

    tp = fp = tn = fn = 0
    per_scenario_stats: dict[str, tuple[int, int]] = {}

    for scenario in FaultScenario:
        sim.set_scenario(scenario)
        hits = 0
        for _ in range(samples_per_scenario):
            # Advance step cleanly to simulate progression (especially memory_leak)
            sample = sim.sample_telemetry(rng=rng)
            pred = detector.predict(sample)
            gt = scenario.is_fault
            if pred.is_anomaly == gt:
                hits += 1
            if gt and pred.is_anomaly:
                tp += 1
            elif not gt and pred.is_anomaly:
                fp += 1
            elif not gt and not pred.is_anomaly:
                tn += 1
            else:
                fn += 1
        per_scenario_stats[scenario.value] = (hits, samples_per_scenario)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    print("=== v0.1 Legacy StaticThresholdDetector Offline Benchmark ===")
    for name, (ok, total) in per_scenario_stats.items():
        print(f"  - {name:24s}: {ok:3d}/{total} correct ({ok / total * 100:5.1f}%)")
    print("-" * 60)
    print(f"TP={tp}  FP={fp}  TN={tn}  FN={fn}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"FPR (誤報率): {fpr:.4f}")
    print("=" * 60)
    print("Notice how `traffic_surge_normal` triggers massive False Positives,")
    print("while early `memory_leak` windows are missed (False Negatives)!")

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
    }


if __name__ == "__main__":
    run_benchmark()
