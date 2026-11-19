"""Anomaly detector backends for `inference_api`.

v0.1 ships with `StaticThresholdDetector` (the noisy legacy rule-based baseline).
In Sprint 2 (Issue #11), Member B will implement `MLflowChampionDetector` to load
`models:/opspulse-anomaly-detector@champion` from MLflow Model Registry.
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod

from opspulse_core.features import FEATURE_NAMES, extract_features
from opspulse_core.schemas import AnomalyPrediction, MetricWindowInput, ModelInfoResponse


class BaseAnomalyDetector(ABC):
    """Common interface for rule-based and MLflow-backed detectors."""

    @abstractmethod
    def predict(self, payload: MetricWindowInput) -> AnomalyPrediction:
        raise NotImplementedError

    @abstractmethod
    def info(self) -> ModelInfoResponse:
        raise NotImplementedError


class StaticThresholdDetector(BaseAnomalyDetector):
    """Legacy v0.1 rule-based detector (our Baseline to beat!).

    Known Limitations (reproduced in tests & Day 1 Onboarding):
    1. False Positives (オオカミ少年アラート): Fires critical alerts during healthy
       promotional traffic surges simply because `cpu_percent > 85%`.
    2. False Negatives (見逃し): Misses early-stage `memory_leak` where memory is
       rising rapidly (`memory_slope_per_min > 3%/min`) while CPU & error rate
       are still below static thresholds.
    """

    CPU_THRESHOLD = 85.0
    ERROR_RATE_THRESHOLD = 0.05
    LATENCY_THRESHOLD_MS = 1000.0

    def predict(self, payload: MetricWindowInput) -> AnomalyPrediction:
        t0 = time.perf_counter()
        feats = extract_features(payload)

        reasons: list[str] = []
        if feats["cpu_percent"] > self.CPU_THRESHOLD:
            reasons.append(f"cpu_percent={feats['cpu_percent']:.1f}% > {self.CPU_THRESHOLD}%")
        if feats["error_rate"] > self.ERROR_RATE_THRESHOLD:
            reasons.append(f"error_rate={feats['error_rate']:.3f} > {self.ERROR_RATE_THRESHOLD}")
        if feats["p95_latency_ms"] > self.LATENCY_THRESHOLD_MS:
            reasons.append(
                f"p95_latency_ms={feats['p95_latency_ms']:.1f}ms > {self.LATENCY_THRESHOLD_MS}ms"
            )

        is_anomaly = len(reasons) > 0
        # Naive heuristic score for baseline comparison
        score = min(
            1.0,
            max(
                feats["cpu_percent"] / 100.0 if feats["cpu_percent"] > 80 else 0.1,
                min(feats["error_rate"] * 5.0, 1.0),
                min(feats["p95_latency_ms"] / 2000.0, 1.0),
            ),
        )
        if len(reasons) >= 2:
            severity = "critical"
        elif len(reasons) == 1:
            severity = "warning"
        else:
            severity = "normal"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return AnomalyPrediction(
            is_anomaly=is_anomaly,
            anomaly_score=round(score, 4),
            severity=severity,
            model_name="legacy-static-threshold",
            model_version="0.1.0",
            model_alias="legacy",
            triggered_reasons=reasons,
            latency_ms=round(elapsed_ms, 3),
        )

    def info(self) -> ModelInfoResponse:
        return ModelInfoResponse(
            backend="static_threshold",
            model_name="legacy-static-threshold",
            model_version="0.1.0",
            model_alias="legacy",
            feature_names=FEATURE_NAMES,
        )


class MLflowChampionDetector(BaseAnomalyDetector):
    """Stub for Sprint 2 (Member B, Issue #11): Load `@champion` from MLflow Registry."""

    def __init__(self, tracking_uri: str, model_name: str, model_alias: str = "champion") -> None:
        self.tracking_uri = tracking_uri
        self.model_name = model_name
        self.model_alias = model_alias
        # TODO(Sprint 2, Member B, Issue #11):
        # 1. Connect to MLflow via `mlflow.set_tracking_uri(self.tracking_uri)`
        # 2. Load `models:/{self.model_name}@{self.model_alias}`
        # 3. Record resolved concrete `model_version` via MlflowClient.get_model_version_by_alias
        raise NotImplementedError(
            "MLflowChampionDetector is scheduled for Sprint 2 (Issue #11). "
            "Set DETECTOR_BACKEND=static_threshold for v0.1 PoC."
        )

    def predict(self, payload: MetricWindowInput) -> AnomalyPrediction:
        raise NotImplementedError

    def info(self) -> ModelInfoResponse:
        raise NotImplementedError


def build_detector_from_env() -> BaseAnomalyDetector:
    backend = os.getenv("DETECTOR_BACKEND", "static_threshold").strip().lower()
    if backend == "static_threshold":
        return StaticThresholdDetector()
    if backend == "mlflow_champion":
        return MLflowChampionDetector(
            tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
            model_name=os.getenv("MLFLOW_MODEL_NAME", "opspulse-anomaly-detector"),
            model_alias=os.getenv("MLFLOW_MODEL_ALIAS", "champion"),
        )
    raise ValueError(f"Unsupported DETECTOR_BACKEND={backend!r}")
