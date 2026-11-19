"""Integration tests for v0.1 `target_app` and `inference_api` FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.inference_api.app import app as inference_app
from services.target_app.app import app as target_app

target_client = TestClient(target_app)
inference_client = TestClient(inference_app)


def test_health_and_model_info_endpoints() -> None:
    t_resp = target_client.get("/health")
    assert t_resp.status_code == 200
    assert t_resp.json()["status"] == "ok"

    i_resp = inference_client.get("/health")
    assert i_resp.status_code == 200
    assert i_resp.json()["status"] == "ok"

    info_resp = inference_client.get("/model-info")
    assert info_resp.status_code == 200
    body = info_resp.json()
    assert body["backend"] == "static_threshold"
    assert body["model_alias"] == "legacy"
    assert len(body["feature_names"]) >= 8


def test_end_to_end_fault_injection_to_inference_prediction() -> None:
    # 1. Switch target_app to db_pool_exhaustion
    set_resp = target_client.post("/admin/fault", json={"scenario": "db_pool_exhaustion"})
    assert set_resp.status_code == 200
    assert set_resp.json()["is_fault_ground_truth"] is True

    # 2. Fetch simulated telemetry
    tel_resp = target_client.get("/admin/telemetry")
    assert tel_resp.status_code == 200
    metrics_payload = tel_resp.json()["metrics"]

    # 3. Call inference API /predict
    pred_resp = inference_client.post("/predict", json=metrics_payload)
    assert pred_resp.status_code == 200
    pred = pred_resp.json()
    assert pred["is_anomaly"] is True
    assert pred["severity"] in {"warning", "critical"}

    # 4. Reset target_app back to normal
    reset_resp = target_client.post("/admin/fault", json={"scenario": "normal"})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["is_fault_ground_truth"] is False


def test_prometheus_metrics_exposed() -> None:
    assert target_client.get("/metrics").status_code == 200
    assert inference_client.get("/metrics").status_code == 200
