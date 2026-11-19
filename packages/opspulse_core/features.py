"""Shared feature engineering logic used by BOTH training and online inference.

Design Note (ADR-002):
Keeping feature extraction inside `packages/opspulse_core` guarantees that
offline training and online FastAPI inference compute identical numerical
features from raw telemetry inputs (no Train-Serving Skew).
"""

from __future__ import annotations

from opspulse_core.schemas import MetricWindowInput

HEALTHY_BASELINE_LATENCY_MS = 70.0

FEATURE_NAMES: list[str] = [
    "cpu_percent",
    "memory_percent",
    "request_rate_rps",
    "error_rate",
    "p95_latency_ms",
    "db_pool_utilization",
    "memory_slope_per_min",
    "latency_ratio_to_baseline",
    "latency_per_cpu",
    "error_burst_index",
]


def extract_features(sample: MetricWindowInput) -> dict[str, float]:
    """Convert a validated MetricWindowInput into a deterministic feature dict.

    TODO(Sprint 1, Member B, Issue #4):
    1. Add Pandera DataFrame schema validation for batch training inputs.
    2. Evaluate additional interaction features (e.g., db_pool * latency,
       rps_per_cpu efficiency ratio to separate legitimate traffic surges from faults).
    3. Keep `FEATURE_NAMES` and `extract_features` strictly deterministic and
       verified by `tests/test_train_serving_consistency.py` (Issue #12).
    """
    safe_cpu = max(sample.cpu_percent, 1.0)
    latency_ratio = (
        sample.latency_ratio_to_baseline
        if sample.latency_ratio_to_baseline != 1.0
        else round(sample.p95_latency_ms / HEALTHY_BASELINE_LATENCY_MS, 4)
    )

    return {
        "cpu_percent": float(sample.cpu_percent),
        "memory_percent": float(sample.memory_percent),
        "request_rate_rps": float(sample.request_rate_rps),
        "error_rate": float(sample.error_rate),
        "p95_latency_ms": float(sample.p95_latency_ms),
        "db_pool_utilization": float(sample.db_pool_utilization),
        "memory_slope_per_min": float(sample.memory_slope_per_min),
        "latency_ratio_to_baseline": float(latency_ratio),
        # High latency while CPU is low strongly hints at I/O wait (DB pool / downstream timeout)
        "latency_per_cpu": round(sample.p95_latency_ms / safe_cpu, 4),
        # Combines request volume with error ratio to quantify user-facing blast radius
        "error_burst_index": round(sample.request_rate_rps * sample.error_rate, 4),
    }


def extract_feature_vector(sample: MetricWindowInput) -> list[float]:
    """Return ordered float vector matching `FEATURE_NAMES`."""
    feats = extract_features(sample)
    return [feats[name] for name in FEATURE_NAMES]
