"""Unit tests for shared Pydantic schemas and feature extraction (`opspulse_core`)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from opspulse_core.features import FEATURE_NAMES, extract_feature_vector, extract_features
from opspulse_core.schemas import FaultScenario, MetricWindowInput


def test_metric_window_validation_accepts_valid_payload() -> None:
    sample = MetricWindowInput(
        cpu_percent=42.5,
        memory_percent=55.0,
        request_rate_rps=125.0,
        error_rate=0.004,
        p95_latency_ms=72.0,
        db_pool_utilization=0.35,
    )
    feats = extract_features(sample)
    vec = extract_feature_vector(sample)

    assert len(vec) == len(FEATURE_NAMES)
    assert feats["cpu_percent"] == 42.5
    assert feats["latency_per_cpu"] == pytest.approx(72.0 / 42.5, rel=1e-3)
    assert feats["error_burst_index"] == pytest.approx(125.0 * 0.004, rel=1e-3)


def test_metric_window_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        MetricWindowInput(
            cpu_percent=140.0,  # Invalid (> 100%)
            memory_percent=50.0,
            request_rate_rps=100.0,
            error_rate=0.01,
            p95_latency_ms=60.0,
            db_pool_utilization=0.3,
        )


def test_fault_scenario_ground_truth_flags() -> None:
    assert FaultScenario.NORMAL.is_fault is False
    assert FaultScenario.TRAFFIC_SURGE_NORMAL.is_fault is False
    assert FaultScenario.MEMORY_LEAK.is_fault is True
    assert FaultScenario.DB_POOL_EXHAUSTION.is_fault is True
    assert FaultScenario.DOWNSTREAM_TIMEOUT.is_fault is True
