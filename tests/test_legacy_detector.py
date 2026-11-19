"""Baseline tests for v0.1 `StaticThresholdDetector`.

These tests lock in the exact behavior (including known blind spots!) of the
legacy rule-based detector so Sprint 1-2 ML models have a clear baseline to beat.
"""

from __future__ import annotations

from opspulse_core.schemas import MetricWindowInput
from services.inference_api.detector import StaticThresholdDetector


def test_static_detector_normal_traffic() -> None:
    detector = StaticThresholdDetector()
    sample = MetricWindowInput(
        cpu_percent=35.0,
        memory_percent=48.0,
        request_rate_rps=120.0,
        error_rate=0.002,
        p95_latency_ms=65.0,
        db_pool_utilization=0.30,
    )
    pred = detector.predict(sample)
    assert pred.is_anomaly is False
    assert pred.severity == "normal"


def test_static_detector_catches_severe_db_pool_exhaustion() -> None:
    detector = StaticThresholdDetector()
    sample = MetricWindowInput(
        cpu_percent=22.0,
        memory_percent=54.0,
        request_rate_rps=130.0,
        error_rate=0.15,
        p95_latency_ms=1900.0,
        db_pool_utilization=0.97,
    )
    pred = detector.predict(sample)
    assert pred.is_anomaly is True
    assert pred.severity == "critical"


def test_static_detector_known_flaw_false_positive_on_healthy_traffic_surge() -> None:
    """Documents why v0.1 needs ML: healthy campaign traffic triggers a false alert."""
    detector = StaticThresholdDetector()
    sample = MetricWindowInput(
        cpu_percent=88.5,  # High CPU due to legitimate 3x sales traffic
        memory_percent=63.0,
        request_rate_rps=350.0,
        error_rate=0.003,  # Healthy error rate
        p95_latency_ms=120.0,  # Healthy latency
        db_pool_utilization=0.62,
    )
    pred = detector.predict(sample)
    # Static rule mistakenly flags this healthy window as an anomaly!
    assert pred.is_anomaly is True


def test_static_detector_known_flaw_misses_early_memory_leak() -> None:
    """Documents why v0.1 needs ML: early memory leak goes undetected by static thresholds."""
    detector = StaticThresholdDetector()
    sample = MetricWindowInput(
        cpu_percent=52.0,
        memory_percent=74.0,
        request_rate_rps=115.0,
        error_rate=0.008,
        p95_latency_ms=260.0,
        db_pool_utilization=0.38,
        memory_slope_per_min=3.8,  # Strong leak signal ignored by v0.1 rules!
    )
    pred = detector.predict(sample)
    assert pred.is_anomaly is False
