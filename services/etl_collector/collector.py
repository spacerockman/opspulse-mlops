"""ETL Collector stub for Sprint 1 (Member A, Issue #2).

TODO(Sprint 1, Member A, Issue #2):
1. Poll `TARGET_APP_URL/admin/telemetry` (and/or Prometheus PromQL API).
2. Validate every row with `opspulse_core.schemas.MetricWindowInput`.
3. Buffer rows into a Pandas/PyArrow table and upload Parquet to MinIO/S3
   using `boto3` with `S3_ENDPOINT_URL` for local-cloud parity.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "ETL Collector is assigned to Member A in Sprint 1 (Issue #2). "
        "See services/etl_collector/README.md and docs/03_sprint_backlog.md."
    )


if __name__ == "__main__":
    main()
