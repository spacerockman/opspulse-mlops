"""FastAPI online anomaly detection inference service (v0.1)."""

from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from opspulse_core.schemas import AnomalyPrediction, MetricWindowInput, ModelInfoResponse
from services.inference_api.detector import BaseAnomalyDetector, build_detector_from_env

PREDICTIONS_TOTAL = Counter(
    "opspulse_predictions_total",
    "Total anomaly predictions served",
    ["result", "model_version"],
)
PREDICTION_LATENCY_SECONDS = Histogram(
    "opspulse_prediction_latency_seconds",
    "Inference API prediction latency in seconds",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)

detector: BaseAnomalyDetector = build_detector_from_env()

app = FastAPI(
    title="OpsPulse Anomaly Detection Inference API",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "opspulse-inference-api"}


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Expose active model metadata for CD smoke tests & rollback verification."""
    return detector.info()


@app.post("/predict", response_model=AnomalyPrediction)
def predict(payload: MetricWindowInput) -> AnomalyPrediction:
    result = detector.predict(payload)
    label = "anomaly" if result.is_anomaly else "normal"
    PREDICTIONS_TOTAL.labels(result=label, model_version=result.model_version).inc()
    PREDICTION_LATENCY_SECONDS.observe(result.latency_ms / 1000.0)
    return result


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
