# 01. 基本設計書・システムアーキテクチャ（System Architecture）

## 1. 対象業務と要件定義（Requirements）

- **対象システム**：B2B SaaS 注文処理サービス `order-service`
- **非機能要件（目標 SLO）**：
  - 推論 API P95 レイテンシ：`< 50ms`（ローカル / ECS Fargate 単体）
  - 誤報率（False Positive Rate）：現行静的ルール比 **50% 以上削減**
  - メモリリーク初期予兆の再現率（Recall）：現行ルール比 **大幅改善（目標 >= 0.85）**
  - ロールバック目標時間（RTO）：悪化モデル検知から **`< 3 分` 以内に旧 `@champion` へ復旧**
  - クラウド検証コスト：**月額 \$20 以下**（検証時のみ起動し、終了時は `terraform destroy`）

---

## 2. コンポーネント設計

| コンポーネント | パス | 状態 | 役割 |
| :--- | :--- | :--- | :--- |
| **Shared Core** | `packages/opspulse_core/` | v0.1 済 → S1 拡張 | Pydantic データ契約、Pandera 検証、学習・推論共通特徴量 |
| **Target App** | `services/target_app/` | v0.1 済 | 模擬注文サービス、Prometheus 指標、JSON ログ、5 シナリオ故障制御 |
| **Inference API** | `services/inference_api/` | v0.1 済 → S2 切替 | FastAPI 推論エンドポイント。S2 より MLflow `@champion` をロード |
| **ETL Collector** | `services/etl_collector/` | S1 メンバーA | メトリクス＆ラベル収集 → Parquet 変換 → MinIO / S3 保存 |
| **Training Pipeline** | `pipelines/training/` | S1-2 メンバーB | 特徴量抽出・学習・ベースライン比較・品質ゲート・MLflow 登録 |
| **Drift Monitor** | `pipelines/monitoring/` | S3 メンバーB | Evidently による入力/予測ドリフト評価と HTML レポート出力 |
| **SRE Triage Agent** | `services/triage_agent/` | S4 メンバーB | 日本語 Runbook RAG＋障害一次分析＋Langfuse Cloud 評価 |
| **AWS IaC** | `infra/terraform/` | S3 メンバーA | S3 / ECR / IAM / ECS Fargate / CloudWatch Logs 定義 |

---

## 3. データ契約（Telemetry Schema）

すべてのデータパイプライン・学習・推論は `opspulse_core.schemas.MetricWindowInput` を単一の真実（Single Source of Truth）とする：

| フィールド | 型 | 範囲 | 説明 |
| :--- | :--- | :--- | :--- |
| `cpu_percent` | float | 0–100 | CPU 使用率（%） |
| `memory_percent` | float | 0–100 | メモリ使用率（%） |
| `request_rate_rps` | float | >= 0 | 秒間リクエスト数 |
| `error_rate` | float | 0–1 | HTTP 5xx エラー比率 |
| `p95_latency_ms` | float | >= 0 | P95 応答時間（ms） |
| `db_pool_utilization` | float | 0–1 | DB コネクションプール使用率 |
| `memory_slope_per_min` | float | float | 1 分あたりメモリ増加勾配（%/min） |
| `latency_ratio_to_baseline` | float | >= 0 | 正常時ベースライン（70ms）比のレイテンシ倍率 |

---

## 4. Local-Cloud Parity（ローカルと本番 AWS の設計一貫性）

| 機能 | ローカル開発（Sprint 1–2） | AWS 準本番（Sprint 3–4） | 切替方法 |
| :--- | :--- | :--- | :--- |
| オブジェクトストレージ | MinIO (`http://localhost:9000`) | AWS S3 (`ap-northeast-1`) | 環境変数 `S3_ENDPOINT_URL` を空にするだけ |
| 推論コンテナ実行 | Docker Compose | AWS ECS Fargate + ECR | GitHub Actions CD ワークフロー |
| 監視・可視化 | Prometheus + Grafana (Local) | Prometheus/Grafana + CloudWatch Logs | 同一 Grafana Dashboard JSON |
| LLMOps 評価 | Langfuse Cloud (Free Tier) | Langfuse Cloud (Free Tier) | 変更なし |

---

## 5. 関連 ADR（Architecture Decision Records）
- [ADR-001: EKS ではなく AWS ECS Fargate を採用する理由](02_adr/ADR-001-ecs-over-eks.md)
- [ADR-002: MLflow Model Aliases (`@champion`/`@challenger`) と共有特徴量パッケージ](02_adr/ADR-002-mlflow-aliases-and-shared-features.md)
