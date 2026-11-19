# ETL Telemetry Collector (`services/etl_collector/`)

- **Owner**: メンバー A（Platform / Infra 担当）
- **対象 Issue**: Sprint 1, **Issue #2 & #3**
- **責務**:
  1. `target-app` (`/admin/telemetry`) および Prometheus から一定間隔でメトリクスとグラウンドトゥルース・ラベルを収集。
  2. Pydantic スキーマ（`opspulse_core.schemas.MetricWindowInput`）でバリデーション。
  3. 日付パーティション付き Parquet ファイル（例: `s3://opspulse-data/raw/dt=YYYY-MM-DD/batch_*.parquet`）として MinIO（本番は AWS S3）へ書き出し。
