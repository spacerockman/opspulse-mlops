"""Simulated Japanese B2B SaaS `order-service` (v0.1 PoC target system).

Exposes:
- Business API: POST /orders, GET /orders/{order_id}
- Observability: GET /metrics (Prometheus), structured JSON application logs
- Fault Control Plane: POST /admin/fault, GET /admin/fault, GET /admin/telemetry

Design Goal:
Generate realistic, physically grounded metrics & error logs for 5 scenarios so
the team can reproduce why static threshold rules fail (false positives on
legitimate traffic spikes; missed early warnings on slow memory leaks).
"""

from __future__ import annotations

import json
import logging
import random
import time
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

from opspulse_core.schemas import FaultScenario, MetricWindowInput

# ---------------------------------------------------------------------------
# Structured JSON logging (used by Sprint 1 ETL & Sprint 4 SRE Triage Agent)
# ---------------------------------------------------------------------------
logger = logging.getLogger("opspulse.target_app")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)


def emit_json_log(
    level: str,
    request_id: str,
    endpoint: str,
    status_code: int,
    latency_ms: float,
    message: str,
    error_code: str | None = None,
) -> None:
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": level,
        "service": "order-service",
        "request_id": request_id,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "error_code": error_code,
        "message": message,
    }
    logger.info(json.dumps(payload, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Prometheus Metrics
# ---------------------------------------------------------------------------
HTTP_REQUESTS_TOTAL = Counter(
    "order_service_http_requests_total",
    "Total HTTP requests handled by order-service",
    ["endpoint", "status_code"],
)
HTTP_LATENCY_SECONDS = Histogram(
    "order_service_http_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=(0.02, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
SIM_CPU_PERCENT = Gauge("order_service_cpu_percent", "Simulated CPU usage (%)")
SIM_MEMORY_PERCENT = Gauge("order_service_memory_percent", "Simulated memory usage (%)")
SIM_DB_POOL_UTIL = Gauge("order_service_db_pool_utilization", "Simulated DB pool utilization (0-1)")
SIM_P95_LATENCY_MS = Gauge("order_service_p95_latency_ms", "Simulated P95 latency (ms)")
SIM_ERROR_RATE = Gauge("order_service_error_rate", "Simulated 5xx error ratio (0-1)")
SIM_REQUEST_RPS = Gauge("order_service_request_rate_rps", "Simulated request rate (RPS)")
SIM_ACTIVE_FAULT = Gauge("order_service_active_fault_flag", "1 if ground-truth fault active else 0")


# ---------------------------------------------------------------------------
# Internal Simulation State
# ---------------------------------------------------------------------------
class FaultState:
    def __init__(self) -> None:
        self.scenario: FaultScenario = FaultScenario.NORMAL
        self.started_at: float = time.time()
        self.step: int = 0

    def set_scenario(self, scenario: FaultScenario) -> None:
        self.scenario = scenario
        self.started_at = time.time()
        self.step = 0

    def sample_telemetry(self, rng: random.Random | None = None) -> MetricWindowInput:
        """Produce one realistic telemetry snapshot based on the active scenario."""
        r = rng or random
        self.step += 1
        elapsed_min = max((time.time() - self.started_at) / 60.0, self.step * 0.08)

        if self.scenario == FaultScenario.NORMAL:
            cpu = r.gauss(34.0, 4.5)
            mem = r.gauss(48.0, 2.0)
            rps = r.gauss(120.0, 12.0)
            err = abs(r.gauss(0.002, 0.0015))
            p95 = r.gauss(68.0, 10.0)
            db_pool = r.gauss(0.32, 0.05)
            mem_slope = r.gauss(0.0, 0.12)

        elif self.scenario == FaultScenario.MEMORY_LEAK:
            # Slow memory creep + subtle GC pause latency rise BEFORE CPU hits 85%.
            # Naive static CPU/error threshold misses the early warning window!
            creep = min(elapsed_min * 3.8, 38.0)
            cpu = r.gauss(46.0 + creep * 0.45, 3.5)
            mem = r.gauss(56.0 + creep, 1.5)
            rps = r.gauss(118.0, 10.0)
            err = abs(r.gauss(0.006 + (0.025 if mem > 86 else 0.0), 0.004))
            p95 = r.gauss(140.0 + creep * 8.5, 20.0)
            db_pool = r.gauss(0.38, 0.06)
            mem_slope = r.gauss(3.5, 0.5)

        elif self.scenario == FaultScenario.DB_POOL_EXHAUSTION:
            # Classic I/O bottleneck: CPU stays LOW while DB pool & latency explode.
            cpu = r.gauss(22.0, 4.0)
            mem = r.gauss(54.0, 2.5)
            rps = r.gauss(135.0, 15.0)
            err = abs(r.gauss(0.14, 0.04))
            p95 = r.gauss(1850.0, 260.0)
            db_pool = r.gauss(0.96, 0.025)
            mem_slope = r.gauss(0.1, 0.15)

        elif self.scenario == FaultScenario.DOWNSTREAM_TIMEOUT:
            # External payment gateway timeout: elevated latency & 5xx, normal DB pool.
            cpu = r.gauss(38.0, 5.0)
            mem = r.gauss(51.0, 2.5)
            rps = r.gauss(115.0, 14.0)
            err = abs(r.gauss(0.11, 0.03))
            p95 = r.gauss(2300.0, 320.0)
            db_pool = r.gauss(0.41, 0.07)
            mem_slope = r.gauss(0.05, 0.12)

        else:  # FaultScenario.TRAFFIC_SURGE_NORMAL
            # Legitimate promotional campaign (e.g. seasonal sale):
            # High RPS + high CPU (~87%), yet healthy latency & low error rate!
            # Static CPU > 85% threshold fires false alarms (false positives).
            cpu = r.gauss(87.0, 2.8)
            mem = r.gauss(63.0, 2.5)
            rps = r.gauss(340.0, 28.0)
            err = abs(r.gauss(0.003, 0.0015))
            p95 = r.gauss(125.0, 16.0)
            db_pool = r.gauss(0.64, 0.06)
            mem_slope = r.gauss(0.15, 0.2)

        snapshot = MetricWindowInput(
            service="order-service",
            cpu_percent=round(min(max(cpu, 1.0), 100.0), 2),
            memory_percent=round(min(max(mem, 5.0), 100.0), 2),
            request_rate_rps=round(max(rps, 1.0), 2),
            error_rate=round(min(max(err, 0.0), 1.0), 4),
            p95_latency_ms=round(max(p95, 5.0), 2),
            db_pool_utilization=round(min(max(db_pool, 0.0), 1.0), 4),
            memory_slope_per_min=round(mem_slope, 3),
            latency_ratio_to_baseline=round(max(p95, 5.0) / 70.0, 4),
        )

        # Update Prometheus gauges
        SIM_CPU_PERCENT.set(snapshot.cpu_percent)
        SIM_MEMORY_PERCENT.set(snapshot.memory_percent)
        SIM_DB_POOL_UTIL.set(snapshot.db_pool_utilization)
        SIM_P95_LATENCY_MS.set(snapshot.p95_latency_ms)
        SIM_ERROR_RATE.set(snapshot.error_rate)
        SIM_REQUEST_RPS.set(snapshot.request_rate_rps)
        SIM_ACTIVE_FAULT.set(1.0 if self.scenario.is_fault else 0.0)
        return snapshot


state = FaultState()


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OpsPulse Target Order Service (Simulated SaaS App)",
    version="0.1.0",
)


class OrderRequest(BaseModel):
    customer_id: str = Field(default="cust-jp-001")
    item_sku: str = Field(default="SKU-SAAS-PRO")
    amount_jpy: int = Field(default=12000, ge=1)


class FaultUpdateRequest(BaseModel):
    scenario: FaultScenario


class TelemetryResponse(BaseModel):
    scenario: FaultScenario
    is_fault_ground_truth: bool
    metrics: MetricWindowInput


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "order-service", "version": "0.1.0"}


@app.post("/orders")
def create_order(order: OrderRequest) -> dict[str, object]:
    req_id = f"req-{uuid.uuid4().hex[:8]}"
    snapshot = state.sample_telemetry()
    latency_ms = max(15.0, random.gauss(snapshot.p95_latency_ms * 0.75, 15.0))
    HTTP_LATENCY_SECONDS.labels(endpoint="/orders").observe(latency_ms / 1000.0)

    if random.random() < snapshot.error_rate:
        if state.scenario == FaultScenario.DB_POOL_EXHAUSTION:
            err_code = "ERR_DB_POOL_TIMEOUT"
            msg = "Database connection pool exhausted (active=50/50, wait_timeout=3000ms)"
        elif state.scenario == FaultScenario.DOWNSTREAM_TIMEOUT:
            err_code = "ERR_PAYMENT_GATEWAY_TIMEOUT"
            msg = "Upstream payment gateway did not respond within 2000ms"
        else:
            err_code = "ERR_INTERNAL_ORDER_FAILED"
            msg = "Transient order processing error"

        HTTP_REQUESTS_TOTAL.labels(endpoint="/orders", status_code="500").inc()
        emit_json_log("ERROR", req_id, "/orders", 500, latency_ms, msg, error_code=err_code)
        raise HTTPException(status_code=500, detail={"error_code": err_code, "message": msg})

    HTTP_REQUESTS_TOTAL.labels(endpoint="/orders", status_code="200").inc()
    emit_json_log(
        "INFO",
        req_id,
        "/orders",
        200,
        latency_ms,
        f"Order accepted for {order.customer_id} ({order.amount_jpy} JPY)",
    )
    return {
        "order_id": f"ord-{uuid.uuid4().hex[:8]}",
        "status": "accepted",
        "latency_ms": round(latency_ms, 2),
    }


@app.post("/admin/fault")
def set_fault(payload: FaultUpdateRequest) -> dict[str, object]:
    state.set_scenario(payload.scenario)
    emit_json_log(
        "WARN" if payload.scenario.is_fault else "INFO",
        "admin-control",
        "/admin/fault",
        200,
        1.0,
        f"Fault simulation switched to scenario={payload.scenario.value}",
    )
    return {
        "scenario": state.scenario.value,
        "is_fault_ground_truth": state.scenario.is_fault,
    }


@app.get("/admin/fault")
def get_fault() -> dict[str, object]:
    return {
        "scenario": state.scenario.value,
        "is_fault_ground_truth": state.scenario.is_fault,
    }


@app.get("/admin/telemetry", response_model=TelemetryResponse)
def get_telemetry() -> TelemetryResponse:
    snapshot = state.sample_telemetry()
    return TelemetryResponse(
        scenario=state.scenario,
        is_fault_ground_truth=state.scenario.is_fault,
        metrics=snapshot,
    )


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
