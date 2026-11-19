"""Fault & Traffic Injector CLI for OpsPulse v0.1.

Usage:
    python scripts/fault_injector.py --scenario memory_leak --duration 30
    python scripts/fault_injector.py --scenario traffic_surge_normal --duration 25

Switches `target_app` into the chosen scenario, sends simulated order traffic,
forwards telemetry snapshots to `inference_api`, and prints live ground-truth
vs prediction comparisons so new team members can immediately observe legacy
static-threshold false positives and missed early warnings.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import httpx

from opspulse_core.schemas import FaultScenario


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inject faults/traffic into OpsPulse target_app")
    parser.add_argument(
        "--scenario",
        type=str,
        choices=[s.value for s in FaultScenario],
        default=FaultScenario.NORMAL.value,
        help="Simulation scenario to activate on target_app",
    )
    parser.add_argument("--duration", type=int, default=20, help="Duration in seconds")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds")
    parser.add_argument(
        "--target-url",
        type=str,
        default=os.getenv("TARGET_APP_URL", "http://localhost:8001"),
    )
    parser.add_argument(
        "--inference-url",
        type=str,
        default=os.getenv("INFERENCE_API_URL", "http://localhost:8002"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario = FaultScenario(args.scenario)

    print(
        f"=== OpsPulse Fault Injector | scenario={scenario.value} "
        f"(ground_truth_fault={scenario.is_fault}) ==="
    )
    print(f"Target App    : {args.target_url}")
    print(f"Inference API : {args.inference_url}")
    print("-" * 92)

    total = 0
    correct = 0
    false_positives = 0
    false_negatives = 0

    with httpx.Client(timeout=5.0) as client:
        try:
            resp = client.post(
                f"{args.target_url}/admin/fault",
                json={"scenario": scenario.value},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"[ERROR] Failed to reach target_app at {args.target_url}: {exc}")
            print("Hint: Run `make run-target` (or `make up`) first.")
            return 1

        end_time = time.time() + args.duration
        try:
            while time.time() < end_time:
                # 1. Trigger a couple of simulated business requests
                for _ in range(3):
                    try:
                        client.post(
                            f"{args.target_url}/orders",
                            json={
                                "customer_id": "cust-jp-demo",
                                "item_sku": "SKU-001",
                                "amount_jpy": 9800,
                            },
                        )
                    except httpx.HTTPError:
                        pass

                # 2. Fetch telemetry snapshot
                tel_resp = client.get(f"{args.target_url}/admin/telemetry")
                tel_resp.raise_for_status()
                telemetry = tel_resp.json()
                gt_fault: bool = telemetry["is_fault_ground_truth"]
                m = telemetry["metrics"]

                # 3. Call inference API
                pred_resp = client.post(f"{args.inference_url}/predict", json=m)
                pred_resp.raise_for_status()
                pred = pred_resp.json()
                pred_fault: bool = pred["is_anomaly"]

                total += 1
                if pred_fault == gt_fault:
                    correct += 1
                    verdict = "OK"
                elif pred_fault and not gt_fault:
                    false_positives += 1
                    verdict = "FALSE_POSITIVE (誤報!)"
                else:
                    false_negatives += 1
                    verdict = "FALSE_NEGATIVE (見逃し!)"

                print(
                    f"[{total:02d}] CPU={m['cpu_percent']:5.1f}% MEM={m['memory_percent']:5.1f}% "
                    f"(+{m['memory_slope_per_min']:4.1f}/m) ERR={m['error_rate']*100:4.1f}% "
                    f"P95={m['p95_latency_ms']:6.1f}ms DB={m['db_pool_utilization']*100:4.0f}% | "
                    f"GT={str(gt_fault):5s} PRED={str(pred_fault):5s} -> {verdict}"
                )
                time.sleep(args.interval)
        finally:
            # Always reset target_app back to normal on exit
            try:
                client.post(
                    f"{args.target_url}/admin/fault",
                    json={"scenario": FaultScenario.NORMAL.value},
                )
            except httpx.HTTPError:
                pass

    print("-" * 92)
    accuracy = (correct / total * 100.0) if total else 0.0
    print(
        f"Summary ({total} windows): Accuracy={accuracy:.1f}% | "
        f"False Positives={false_positives} | False Negatives={false_negatives}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
