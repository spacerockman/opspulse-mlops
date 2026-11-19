"""Pydantic v2 data contracts shared across simulator, ETL, training, and inference."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class FaultScenario(StrEnum):
    """Supported simulation modes for the target order-service."""

    NORMAL = "normal"
    MEMORY_LEAK = "memory_leak"
    DB_POOL_EXHAUSTION = "db_pool_exhaustion"
    DOWNSTREAM_TIMEOUT = "downstream_timeout"
    # Legitimate business traffic surge (e.g. seasonal sale).
    # Ground truth is NOT a fault, designed to expose static-threshold false positives
    # and simulate data/covariate drift!
    TRAFFIC_SURGE_NORMAL = "traffic_surge_normal"

    @property
    def is_fault(self) -> bool:
        return self in {
            FaultScenario.MEMORY_LEAK,
            FaultScenario.DB_POOL_EXHAUSTION,
            FaultScenario.DOWNSTREAM_TIMEOUT,
        }


class MetricWindowInput(BaseModel):
    """Single observation window of service telemetry fed into the anomaly detector."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    service: str = Field(default="order-service", min_length=1, max_length=64)

    # Core infrastructure & application telemetry
    cpu_percent: float = Field(..., ge=0.0, le=100.0, description="CPU usage (%)")
    memory_percent: float = Field(..., ge=0.0, le=100.0, description="Memory usage (%)")
    request_rate_rps: float = Field(..., ge=0.0, description="Requests per second")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="HTTP 5xx ratio (0.0-1.0)")
    p95_latency_ms: float = Field(..., ge=0.0, description="95th percentile latency (ms)")
    db_pool_utilization: float = Field(
        ..., ge=0.0, le=1.0, description="DB connection pool utilization (0.0-1.0)"
    )

    # Optional rolling-window trend metrics (populated by ETL / telemetry buffer)
    memory_slope_per_min: float = Field(
        default=0.0, description="Rate of memory growth (% per minute)"
    )
    latency_ratio_to_baseline: float = Field(
        default=1.0, ge=0.0, description="Current P95 latency divided by healthy baseline (70ms)"
    )


class AnomalyPrediction(BaseModel):
    """Standard prediction response returned by inference_api."""

    is_anomaly: bool
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    severity: str = Field(..., pattern="^(normal|warning|critical)$")
    model_name: str
    model_version: str
    model_alias: str
    triggered_reasons: list[str] = Field(default_factory=list)
    latency_ms: float = Field(..., ge=0.0)


class ModelInfoResponse(BaseModel):
    """Metadata exposed by GET /model-info for deployment & rollback verification."""

    backend: str
    model_name: str
    model_version: str
    model_alias: str
    feature_names: list[str]
