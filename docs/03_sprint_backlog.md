# 03. Sprint バックログ＆タスク詳細台帳（全 24 チケット）

> **Single Source of Truth**: 本ファイルは `docs/backlog_tasks.json` から `python scripts/export_backlog.py` により自動生成されています。
> オンライン管理ツール（**GitHub Projects + Issues** 推奨、または **Jira Cloud Free**）へそのまま一括登録できます。

## 一括インポート手順
- **GitHub Issues / Projects を使う場合（推奨）**:
  ```bash
  export GITHUB_TOKEN=ghp_xxx
  python scripts/bootstrap_github_board.py --repo <owner>/opspulse-mlops --member-a <gh_user_a> --member-b <gh_user_b>
  ```
- **Jira Cloud (Free) を使う場合**:
  Jira プロジェクト設定 → **System → External System Import → CSV** から `docs/jira_backlog_import.csv` をそのまま取り込むと、全 24 チケットが一括作成されます。

---

## 全体アサイン早見表（各自の担当を確認してピックアップ）

| ID | Sprint | Owner | Reviewer | 工数 | 依存 | タスク名 |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **#0** | Sprint 0 (Week 0) | `Both` | `Tech Lead` | 2h | - | [S0][Joint] GitHub リポジトリ・ブランチ保護・オンライン看板の初期化と v0.1 不具合再現 |
| **#1** | Sprint 1 (Week 1-2) | `Member A` | `Member B` | 4h | #0 | [S1][A] Docker Compose 拡張：PostgreSQL + MinIO（自動バケット作成）+ MLflow Server の導入 |
| **#2** | Sprint 1 (Week 1-2) | `Member A` | `Member B` | 5h | #1 | [S1][A] ETL コレクター開発：target_app のメトリクスを抽出し Parquet 形式で MinIO/S3 へ保存 |
| **#3** | Sprint 1 (Week 1-2) | `Member A` | `Member B` | 3h | #2 | [S1][A] 再現可能なデータセット生成コマンド `make data-collect` の整備（5 シナリオ混在 >=3,000 件） |
| **#4** | Sprint 1 (Week 1-2) | `Member B` | `Member A` | 4h | #0 | [S1][B] `opspulse_core` 拡充：Pandera バッチデータ契約と高識別特徴量の実装 |
| **#5** | Sprint 1 (Week 1-2) | `Member B` | `Member A` | 6h | #1, #3, #4 | [S1][B] 学習比較パイプライン構築：`Static` vs `IsolationForest` vs `LightGBM` と MLflow 記録 |
| **#6** | Sprint 1 (Week 1-2) | `Member B` | `Member A` | 2h | #5 | [S1][B] エビデンスレポート #1 作成：`docs/evidence/01_model_vs_baseline.md` |
| **#7** | Sprint 2 (Week 3-4) | `Member A` | `Member B` | 4h | #1 | [S2][A] Inference API コンテナ最適化：マルチステージビルド (<300MB) + `/ready` + 推論メトリクス |
| **#8** | Sprint 2 (Week 3-4) | `Member A` | `Member B` | 4h | #7 | [S2][A] GitHub Actions CI パイプライン構築（Lint + Unit/Consistency Test + Docker Build） |
| **#9** | Sprint 2 (Week 3-4) | `Member B` | `Member A` | 5h | #5 | [S2][B] モデル自動品質ゲート（Quality Gate）と MLflow `@challenger` → `@champion` 昇格の実装 |
| **#10** | Sprint 2 (Week 3-4) | `Member B` | `Member A` | 5h | #9 | [S2][B] Inference API 刷新：`MLflowChampionDetector`、`/admin/reload-model` と Top-3 寄与特徴量出力 |
| **#11** | Sprint 2 (Week 3-4) | `Member B` | `Member A` | 3h | #4, #10 | [S2][B] Train-Serving 一貫性テスト実装（学習・推論間の特徴量ズレ防止） |
| **#12** | Sprint 2 (Week 3-4) | `Member A` | `Member B` | 4h | #1, #10 | [S2][A] 推論監査ログ永続化 & エラーログ参照 API 整備（Drift 監視・AI Agent 向けデータ連携） |
| **#13** | Sprint 2 (Week 3-4) | `Member A` | `Member B` | 3h | #7, #10, #12 | [S2][A] 推論 API 負荷試験とエビデンスレポート #2：`docs/evidence/02_load_test.md` |
| **#14** | Sprint 3 (Week 5-6) | `Member A` | `Member B` | 6h | #7, #8 | [S3][A] Terraform による低コスト AWS 推論基盤構築（S3 + ECR + IAM + ECS Fargate、NAT なし） |
| **#15** | Sprint 3 (Week 5-6) | `Member A` | `Member B` | 5h | #14 | [S3][A] AWS CD 自動デプロイパイプライン＆Grafana 監視ダッシュボード構築 |
| **#16** | Sprint 3 (Week 5-6) | `Member A` | `Member B` | 4h | #10, #15 | [S3][A] モデルワンクリックロールバック機構と手動ロールバック Workflow 実装（RTO < 3 分） |
| **#17** | Sprint 3 (Week 5-6) | `Member B` | `Member A` | 5h | #3, #5, #12 | [S3][B] Evidently による入力特徴量＆予測分布ドリフト監視の実装 |
| **#18** | Sprint 3 (Week 5-6) | `Both` | `Tech Lead` | 5h | #16, #17 | [S3][Both] 「ドリフト検知 → 人工承認再学習」および「劣化モデルロールバック」結合演習・証跡 #3 記録 |
| **#19** | Sprint 4 (Week 7-8) | `Member B` | `Member A` | 6h | #10, #12 | [S4][B] SRE Triage AI Agent 開発：日本語 Runbook RAG による障害一次分析レポート生成 |
| **#20** | Sprint 4 (Week 7-8) | `Member B` | `Member A` | 4h | #19 | [S4][B] Langfuse Cloud トレース連携と Agent オフライン評価レポート #4：`docs/evidence/04_agent_eval.md` |
| **#21** | Sprint 4 (Week 7-8) | `Member A` | `Member B` | 4h | #15, #16 | [S4][A] セキュリティ監査（シークレット・IAM・tfsec）と日本語《運用手順書》完成 |
| **#22** | Sprint 4 (Week 7-8) | `Both` | `Tech Lead` | 5h | #18, #19, #20, #21 | [S4][Both] 異常検知→Triage Agent 自動連携＆長期連続稼働試験（Soak Test）・職務経歴書最終化 |
| **#23** | Sprint 4 (Week 7-8) | `Both` | `Tech Lead` | 4h | #9, #10 | [S4][Optional] 製造業設備予知保全モジュール（UCI AI4I 2020）：MLOps 基盤の汎用性実証 |

---

## Sprint 0 (Week 0)

### Issue #0: [S0][Joint] GitHub リポジトリ・ブランチ保護・オンライン看板の初期化と v0.1 不具合再現
- **Owner**: `Both` | **Reviewer**: `Tech Lead` | **目安工数**: 2h | **優先度**: Highest | **依存**: なし
- **目的（Goal）**: 2 名が各自の Mac から SSH で LAN 内 Linux 開発サーバー（192.168.0.253）へ接続し、v0.1 コードを GitHub へプッシュしてオンライン看板を有効化した上で、各自の独立ディレクトリでベースラインテストと障害注入デモを完走させる。
- **対象ファイル**: `.env.example`, `docs/00_onboarding.md`, `docs/04_lan_dev_server_setup.md`
- **実装ステップ（具体作業）**:
  1. メンバー A（jintao）とメンバー B（xinchen）が各自の Mac で ssh-copy-id を実行し、192.168.0.253 へ接続して Remote-SSH を設定する。
  2. メンバー A が GitHub リポジトリ opspulse-mlops に xinchen を Collaborator として招待し（xinchen は招待を Accept）、main ブランチ保護（Require PR before merging）を有効化する。
  3. メンバー B が xinchen アカウントでログインし、/home/xinchen/opspulse-mlops に独立して git clone を行い、.env 作成と make setup を実行する。
  4. scripts/bootstrap_github_board.py を使って全 24 件のタスク・Milestone・Project 看板をオンラインへ同期する。
  5. 双方が各自の環境で make lint && make test && make eval-baseline を実行し、fault_injector.py で静的閾値の誤報（traffic_surge_normal）と見逃し（memory_leak）を確認する。
- **動作確認コマンド**: `make lint && make test && make eval-baseline`
- **完了条件（Definition of Done）**:
  - [ ] 2 台の Mac からパスワードなしで SSH 接続でき、Remote-SSH で各自の独立コードディレクトリを開ける
  - [ ] GitHub の main ブランチが保護されており、全 24 件の Issue が Project 看板に表示されている
  - [ ] 双方が静的ルールの誤報と見逃しの出力を再現確認済み

## Sprint 1 (Week 1-2)

### Issue #1: [S1][A] Docker Compose 拡張：PostgreSQL + MinIO（自動バケット作成）+ MLflow Server の導入
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: Highest | **依存**: #0
- **目的（Goal）**: ローカル MLOps 基盤（将来の AWS RDS/S3 と同じ構成）を整え、:5000 で MLflow UI、:9001 で MinIO Console、:5432 で PostgreSQL にアクセスできるようにする。
- **対象ファイル**: `docker-compose.yml`, `infra/docker/mlflow.Dockerfile`, `.env.example`
- **実装ステップ（具体作業）**:
  1. infra/docker/mlflow.Dockerfile を新規作成し、ghcr.io/mlflow/mlflow:v2.16.2 をベースに psycopg2-binary と boto3（公式イメージに未同梱）をインストールする。
  2. docker-compose.yml に postgres（postgres:16-alpine、名前付きボリューム pg_data、healthcheck: pg_isready）を追加する。
  3. minio（minio/minio、名前付きボリューム minio_data、9000/9001 公開）およびワンショット init コンテナ minio-init（minio/mc）を追加し、起動後に opspulse-data と mlflow-artifacts を自動作成する。
  4. mlflow サービス（:5000）を追加し、--backend-store-uri postgresql+psycopg2://... --artifacts-destination s3://mlflow-artifacts/ --serve-artifacts と MLFLOW_S3_ENDPOINT_URL=http://minio:9000 を設定する。
  5. docker compose restart 後も実験データ・アーティファクトが永続化されていることを確認する。
- **動作確認コマンド**: `docker compose up -d --build && docker compose ps && curl -sf http://localhost:5000/health`
- **完了条件（Definition of Done）**:
  - [ ] Mac のブラウザから http://192.168.0.253:5000 (MLflow) と :9001 (MinIO) を開ける
  - [ ] MinIO 上に opspulse-data と mlflow-artifacts バケットが自動作成されている
  - [ ] PostgreSQL と MinIO に永続ボリュームとヘルスチェックが設定されている

### Issue #2: [S1][A] ETL コレクター開発：target_app のメトリクスを抽出し Parquet 形式で MinIO/S3 へ保存
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 5h | **優先度**: High | **依存**: #1
- **目的（Goal）**: データ収集パイプラインを疎通し、模擬業務システムのテレメトリスナップショットと障害ラベルを検証した上で日付パーティションごとに MinIO へ書き込む（将来の AWS S3 移行時もコード変更不要）。
- **対象ファイル**: `services/etl_collector/collector.py`, `services/etl_collector/__init__.py`, `tests/test_etl_collector.py`
- **実装ステップ（具体作業）**:
  1. services/etl_collector/collector.py に収集ループを実装し、TARGET_APP_URL/admin/telemetry（および必要に応じ Prometheus /api/v1/query）から指標を取得する。
  2. 全レコードを opspulse_core.schemas.MetricWindowInput で厳密検証し、scenario (str) と is_fault (bool) ラベル列を保持する。
  3. バッファしたバッチを Pandas DataFrame（8 基礎メトリクス + timestamp + service + scenario + is_fault）へ変換し、PyArrow で Parquet 化する。
  4. boto3 ストレージヘルパーを実装し（S3_ENDPOINT_URL が空なら AWS S3 直結、指定時は MinIO 接続）、s3://opspulse-data/raw/dt=YYYY-MM-DD/batch_<ts>.parquet へ保存する。
  5. tests/test_etl_collector.py を作成し、Parquet スキーマ整合性・空バッチ処理・S3 キー形式を単体テストで検証する。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_etl_collector.py`
- **完了条件（Definition of Done）**:
  - [ ] collector.py がラベル付き Parquet を MinIO opspulse-data バケットへ保存できる
  - [ ] S3_ENDPOINT_URL 未設定時は AWS S3 に互換動作する（Local-Cloud Parity）
  - [ ] 単体テストおよび ruff チェックが全てパスする

### Issue #3: [S1][A] 再現可能なデータセット生成コマンド `make data-collect` の整備（5 シナリオ混在 >=3,000 件）
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 3h | **優先度**: High | **依存**: #2
- **目的（Goal）**: メンバー B が毎回同じ基準で学習・検証データセットを再現生成できるよう、ワンコマンドのデータ生成フローを構築する。
- **対象ファイル**: `scripts/generate_dataset.py`, `Makefile`
- **実装ステップ（具体作業）**:
  1. scripts/generate_dataset.py を実装し、5 シナリオ（normal 45%, traffic_surge_normal 20%, memory_leak 15%, db_pool_exhaustion 10%, downstream_timeout 10%）を実運用に近い比率で生成する。
  2. 時系列リークを防ぐため時間順序で分割し、train.parquet（>=2,400 件）と test.parquet（>=600 件）を s3://opspulse-data/datasets/v1/ へ保存する。
  3. --seed による再現性および --output-mode s3|local をサポートする。
  4. Makefile に data-collect ターゲットを追加し、各シナリオの件数・正負比率サマリーを表示する。
- **動作確認コマンド**: `make data-collect`
- **完了条件（Definition of Done）**:
  - [ ] make data-collect 実行後に MinIO へ datasets/v1/train.parquet (>=2,400行) と test.parquet (>=600行) が保存される
  - [ ] 全 5 種類の FaultScenario が含まれ、NaN や範囲外データが存在しない

### Issue #4: [S1][B] `opspulse_core` 拡充：Pandera バッチデータ契約と高識別特徴量の実装
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 4h | **優先度**: Highest | **依存**: #0
- **目的（Goal）**: バッチ DataFrame 向けのデータ品質ゲート（Pandera）を導入し、「正常なセール高負荷」と「障害・メモリリーク」を高精度に切り分ける共有特徴量を設計する。
- **対象ファイル**: `packages/opspulse_core/contracts.py`, `packages/opspulse_core/features.py`, `tests/test_core_schemas.py`
- **実装ステップ（具体作業）**:
  1. packages/opspulse_core/contracts.py に TelemetryDataFrameSchema（Pandera）を定義し、型・値域（cpu_percent 0..100, error_rate 0..1, p95_latency_ms >= 0）・nullable=False を検証する。
  2. packages/opspulse_core/features.py に rps_per_cpu（正常高負荷と I/O 障害を識別）および mem_leak_pressure（memory_percent * max(memory_slope_per_min, 0)）を追加し、FEATURE_NAMES を更新する。
  3. バッチ用 extract_features_df(df) を実装し、内部で単一レコード用 extract_features() を再利用して計算ロジックの二重化を防ぐ。
  4. tests/test_core_schemas.py に不正データ（負のレイテンシ・CPU 100% 超・必須列欠損）の拒否テストを追加する。
- **動作確認コマンド**: `make lint && make test`
- **完了条件（Definition of Done）**:
  - [ ] Pandera が不正 DataFrame を SchemaError で拒否し、正常データを通過させる
  - [ ] 単一推論とバッチ学習で同一の特徴量計算関数が共有され、全テストがパスする

### Issue #5: [S1][B] 学習比較パイプライン構築：`Static` vs `IsolationForest` vs `LightGBM` と MLflow 記録
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 6h | **優先度**: Highest | **依存**: #1, #3, #4
- **目的（Goal）**: 現行の静的ルールを上回る初の ML モデル学習パイプラインを実装し、全パラメータ・評価指標・混同行列・特徴量重要度を MLflow に集約記録する。
- **対象ファイル**: `pipelines/training/train.py`, `pyproject.toml`, `Makefile`
- **実装ステップ（具体作業）**:
  1. .[dev,ml] 依存関係（pandas/pyarrow/scikit-learn/lightgbm/mlflow/pandera/boto3）がセットアップ済みであることを確認する。
  2. pipelines/training/train.py にて MinIO（s3://opspulse-data/datasets/v1/）から train.parquet / test.parquet を読み込み、TelemetryDataFrameSchema で先頭検証する。
  3. extract_features_df() で特徴量変換後、同一 test.parquet 上で StaticThresholdDetector・IsolationForest・LightGBMClassifier を比較評価する。
  4. MLflow Experiment `opspulse-anomaly-detection` に全パラメータ、precision/recall/f1/fpr/p95_predict_ms、および重要シナリオ別指標（memory_leak_recall, traffic_surge_fpr）を記録する。
  5. 混同行列 PNG と LightGBM 特徴量重要度 PNG を生成し、MLflow Artifact としてアップロードする。
- **動作確認コマンド**: `PYTHONPATH=packages:. python pipelines/training/train.py`
- **完了条件（Definition of Done）**:
  - [ ] MLflow UI (http://192.168.0.253:5000) 上に 3 モデル分の Run と画像 Artifact が記録されている
  - [ ] LightGBM が静的ルール比で全体 FPR 50% 以上削減、かつ memory_leak 再現率 85% 以上を達成している

### Issue #6: [S1][B] エビデンスレポート #1 作成：`docs/evidence/01_model_vs_baseline.md`
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 2h | **優先度**: Medium | **依存**: #5
- **目的（Goal）**: Sprint 1 の実測実験データを技術面接でも説明可能な日本語／バイリンガル比較レポートとして文書化する。
- **対象ファイル**: `docs/evidence/01_model_vs_baseline.md`
- **実装ステップ（具体作業）**:
  1. StaticThreshold vs IsolationForest vs LightGBM の指標比較表（Precision / Recall / F1 / FPR / memory_leak Recall / traffic_surge 誤報率）を作成する。
  2. 特徴量重要度に基づき、なぜ memory_slope_per_min や rps_per_cpu が誤報削減と早期検知に効いたかを解説する。
  3. 再現コマンドと MLflow UI 比較画面のスクリーンショットを添付する。
- **動作確認コマンド**: `cat docs/evidence/01_model_vs_baseline.md`
- **完了条件（Definition of Done）**:
  - [ ] レポート内の全数値が MLflow UI 上の実測値と完全に一致している
  - [ ] メンバー A のレビューを経て main にマージされている

## Sprint 2 (Week 3-4)

### Issue #7: [S2][A] Inference API コンテナ最適化：マルチステージビルド (<300MB) + `/ready` + 推論メトリクス
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: High | **依存**: #1
- **目的（Goal）**: PoC 版 Dockerfile を本番運用基準の軽量・非 root セキュアコンテナへ刷新し、ECS/ALB 向けヘルスチェックとモデル別メトリクスを整備する。
- **対象ファイル**: `services/inference_api/Dockerfile`, `services/inference_api/app.py`
- **実装ステップ（具体作業）**:
  1. services/inference_api/Dockerfile をマルチステージビルド化し、実行ステージに非 root ユーザー（appuser）を設定する。
  2. services/inference_api/app.py に GET /ready を追加する（モデルロード完了時は 200、未準備時は 503 を返却）。
  3. Prometheus /metrics の opspulse_predictions_total に result・severity・model_version ラベルを整備する。
  4. ビルド後のイメージサイズを確認し（不要キャッシュ・ビルドツール削除で軽量化）、実サイズを記録する。
- **動作確認コマンド**: `docker build -f services/inference_api/Dockerfile -t opspulse-inference:test . && docker run --rm opspulse-inference:test id`
- **完了条件（Definition of Done）**:
  - [ ] コンテナが非 root ユーザーで動作する（id コマンドが uid=0 以外）
  - [ ] /health・/ready・/model-info・/metrics が全て正常応答する

### Issue #8: [S2][A] GitHub Actions CI パイプライン構築（Lint + Unit/Consistency Test + Docker Build）
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: Highest | **依存**: #7
- **目的（Goal）**: PR マージ前の自動品質ゲートを確立し、Ruff・Pytest・Docker ビルドがすべて通らないコードの main 流入を自動ブロックする。
- **対象ファイル**: `.github/workflows/ci.yml`
- **実装ステップ（具体作業）**:
  1. .github/workflows/ci.yml を作成し、pull_request (main) および push (main) をトリガーに設定する。
  2. Job 1 (lint-and-test)：Python 3.12 + 依存キャッシュを設定し、ruff check と pytest（Train-Serving 一貫性テスト含む）を実行する。
  3. Job 2 (docker-build)：docker/setup-buildx-action を使い、target_app と inference_api の Docker ビルド検証を行う。
  4. GitHub Settings -> Branches の保護ルールで lint-and-test / docker-build を必須ステータスチェックに登録する。
- **動作確認コマンド**: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" || cat .github/workflows/ci.yml`
- **完了条件（Definition of Done）**:
  - [ ] PR 作成時に GitHub Actions CI が自動実行され全 Job が成功する
  - [ ] 意図的にフォーマットエラーやテスト失敗を入れた PR が CI でブロックされる

### Issue #9: [S2][B] モデル自動品質ゲート（Quality Gate）と MLflow `@challenger` → `@champion` 昇格の実装
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 5h | **優先度**: Highest | **依存**: #5
- **目的（Goal）**: 低品質モデルの本番混入を防ぐ自動評価ゲートを実装し、旧 Stages API ではなく最新の MLflow Model Aliases でモデル昇格を管理する。
- **対象ファイル**: `pipelines/training/quality_gate.py`, `pipelines/training/train.py`, `tests/test_quality_gate.py`
- **実装ステップ（具体作業）**:
  1. pipelines/training/quality_gate.py に evaluate_promotion_gate(candidate, champion) を実装する（基準：F1 >= 0.90, FPR <= 0.05, memory_leak_recall >= 0.85, p95_predict_ms <= 15.0、かつ既存 @champion から F1 劣化 0.01 以内）。
  2. train.py にて最良モデルを opspulse-anomaly-detector へ登録して alias `challenger` を付与し、git_commit・dataset_uri・f1・fpr タグを書き込む。
  3. 品質ゲート合格時のみ MlflowClient().set_registered_model_alias(..., 'champion', version) を実行し、不合格時は昇格をブロックして理由を出力する。
  4. tests/test_quality_gate.py を作成し、初回登録・昇格成功・ゲート却下の 3 ケースをテストする。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_quality_gate.py`
- **完了条件（Definition of Done）**:
  - [ ] MLflow Models 画面でバージョン履歴と @champion / @challenger エイリアスが確認できる
  - [ ] 意図的に精度を落とした候補モデルが品質ゲートで確実にブロックされる

### Issue #10: [S2][B] Inference API 刷新：`MLflowChampionDetector`、`/admin/reload-model` と Top-3 寄与特徴量出力
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 5h | **優先度**: Highest | **依存**: #9
- **目的（Goal）**: 静的閾値ルールを廃止し、推論 API が MLflow @champion モデルを動的ロードして無停止再読み込みと Top-3 異常寄与特徴量（説明可能性）を返せるようにする。
- **対象ファイル**: `services/inference_api/detector.py`, `services/inference_api/app.py`
- **実装ステップ（具体作業）**:
  1. services/inference_api/detector.py の MLflowChampionDetector を実装し、MlflowClient.get_model_version_by_alias(name, 'champion') でバージョン番号を解決してモデルを読み込む。
  2. predict() にて opspulse_core.features.extract_features() を呼び出して推論を実行し、確率に応じて normal (<0.4) / warning (0.4~0.75) / critical (>=0.75) を判定する。
  3. LightGBM の pred_contrib=True または標準化乖離度を用いて Top-3 寄与特徴量（例: 'memory_slope_per_min=3.80 (+contrib=0.42)'）を triggered_reasons に出力する。
  4. app.py に POST /admin/reload-model を追加して @champion 切替を無停止反映できるようにし、DETECTOR_BACKEND=mlflow_champion で結合確認する。
- **動作確認コマンド**: `curl -s http://localhost:8002/model-info && make inject-drift && make inject-memleak`
- **完了条件（Definition of Done）**:
  - [ ] /model-info が backend='mlflow_champion' と実バージョン番号を返却する
  - [ ] inject-drift の誤報が激減し、inject-memleak が早期検知され triggered_reasons にメモリ勾配特徴が出力される

### Issue #11: [S2][B] Train-Serving 一貫性テスト実装（学習・推論間の特徴量ズレ防止）
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 3h | **優先度**: High | **依存**: #4, #10
- **目的（Goal）**: MLOps 本番障害の最大要因である Train-Serving Skew を自動テストで固定し、CI で毎回不整合を検出できるようにする。
- **対象ファイル**: `tests/test_train_serving_consistency.py`
- **実装ステップ（具体作業）**:
  1. 全 5 シナリオの境界値を含む固定テストサンプル群を定義する。
  2. 学習パイプライン側の extract_features_df() と推論側の extract_feature_vector() を同一データに対して実行する。
  3. 全特徴量の数値誤差が < 1e-6 であり、列順序が FEATURE_NAMES と完全一致することをアサートする。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_train_serving_consistency.py`
- **完了条件（Definition of Done）**:
  - [ ] テストが CI で自動実行され、特徴量誤差 < 1e-6 が保証されている

### Issue #12: [S2][A] 推論監査ログ永続化 & エラーログ参照 API 整備（Drift 監視・AI Agent 向けデータ連携）
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: Highest | **依存**: #1, #10
- **目的（Goal）**: 重い ELK を導入せずに「Evidently が参照する本番推論ログ」と「Triage Agent が参照する直近エラーログ」の 2 つのデータ断絶を解消する。
- **対象ファイル**: `services/target_app/app.py`, `services/inference_api/prediction_store.py`, `services/inference_api/app.py`, `tests/test_prediction_store.py`
- **実装ステップ（具体作業）**:
  1. services/target_app/app.py にリングバッファ（collections.deque(maxlen=200)）を追加して直近 JSON ログを保持し、GET /admin/logs?level=ERROR&limit=20 を公開する。
  2. services/inference_api/prediction_store.py を新規作成し、/predict の入力特徴量・is_anomaly・anomaly_score・model_version・timestamp を PostgreSQL（未接続時は JSONL フォールバック）へ記録する。
  3. inference_api に GET /admin/predictions?limit=500（または Parquet エクスポート機能）を追加し、Sprint 3 の Evidently が current データセットとして直接取得できるようにする。
  4. tests/test_prediction_store.py を作成し、ログ検索と推論遅延への影響がないことを検証する。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_prediction_store.py`
- **完了条件（Definition of Done）**:
  - [ ] target_app /admin/logs から直近の ERROR ログ（ERR_DB_POOL_TIMEOUT 等）を取得できる
  - [ ] inference_api の全推論履歴が永続化され、Sprint 3 のドリフト検知から参照可能

### Issue #13: [S2][A] 推論 API 負荷試験とエビデンスレポート #2：`docs/evidence/02_load_test.md`
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 3h | **優先度**: Medium | **依存**: #7, #10, #12
- **目的（Goal）**: MLflow @champion モデルと監査ロギング有効化後の FastAPI 推論サービスを実測負荷試験し、SLO（P95 < 50ms）達成を証明する。
- **対象ファイル**: `scripts/load_test.py`, `docs/evidence/02_load_test.md`
- **実装ステップ（具体作業）**:
  1. scripts/load_test.py（asyncio + httpx または Locust）を実装し、--concurrency 10/50/100 と --duration を指定して負荷試験を実行できるようにする。
  2. Docker コンテナ稼働中の inference_api に対して負荷をかけ、docker stats で CPU・メモリ使用量を同時計測する。
  3. QPS・P50/P95/P99 レイテンシ・エラー率を docs/evidence/02_load_test.md に記録する。
- **動作確認コマンド**: `PYTHONPATH=packages:. python scripts/load_test.py --concurrency 50 --duration 30`
- **完了条件（Definition of Done）**:
  - [ ] 50 並列下でエラー率 0% かつ P95 レイテンシ < 50ms を達成
  - [ ] 負荷試験コマンドと実測値が docs/evidence/02_load_test.md に記録されている

## Sprint 3 (Week 5-6)

### Issue #14: [S3][A] Terraform による低コスト AWS 推論基盤構築（S3 + ECR + IAM + ECS Fargate、NAT なし）
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 6h | **優先度**: Highest | **依存**: #7, #8
- **目的（Goal）**: AWS 東京リージョン（ap-northeast-1）に IaC で推論コンテナ基盤を一括構築し、検証終了後はワンコマンドで完全破棄できるコスト最適構成を実現する（検証費 < $5）。
- **対象ファイル**: `infra/terraform/main.tf`, `infra/terraform/variables.tf`, `infra/terraform/outputs.tf`, `infra/terraform/ecs.tf`, `infra/terraform/iam.tf`, `Makefile`
- **実装ステップ（具体作業）**:
  1. VPC + パブリックサブネット x2 + Internet Gateway（月額約 $32 の NAT Gateway と ALB は省略）および最小開放 Security Group（指定 IP からの 8002 のみ許可）を定義する。
  2. S3 バケット、ECR リポジトリ（opspulse-inference）、CloudWatch Log Group、最小権限 IAM Task Execution Role / Task Role を定義する。
  3. ECS Cluster・Task Definition（0.25 vCPU / 512 MB の省コスト構成）・ECS Service（assign_public_ip = true）を定義する。
  4. Makefile に aws-plan / aws-up / aws-down を追加し、terraform validate がパスすることを確認する。
- **動作確認コマンド**: `cd infra/terraform && terraform init -backend=false && terraform validate`
- **完了条件（Definition of Done）**:
  - [ ] terraform apply で AWS 東京リージョンに ECS Fargate タスクが正常起動する
  - [ ] パブリック IP:8002/model-info でクラウド上の推論 API に疎通できる
  - [ ] make aws-down (terraform destroy) で課金リソースが残留なく削除される

### Issue #15: [S3][A] AWS CD 自動デプロイパイプライン＆Grafana 監視ダッシュボード構築
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 5h | **優先度**: High | **依存**: #14
- **目的（Goal）**: main マージ後の自動 ECR プッシュ＆ECS ローリング更新＋Smoke Test を構築し、ローカル Grafana で業務・推論メトリクスとアラートを常時可視化する。
- **対象ファイル**: `.github/workflows/cd-ecs.yml`, `docker-compose.yml`, `monitoring/grafana/provisioning/datasources/prometheus.yml`, `monitoring/grafana/dashboards/opspulse_overview.json`, `monitoring/prometheus/alert_rules.yml`
- **実装ステップ（具体作業）**:
  1. .github/workflows/cd-ecs.yml を構築し、ECR build & push → ECS タスク更新 → パブリック IP 取得 → /health & /model-info Smoke Test までを自動化する。
  2. docker-compose.yml に grafana (:3000) を追加し、provisioning 設定により Prometheus データソースとダッシュボードを自動読み込みさせる。
  3. target_app 指標・推論 P95 レイテンシ・異常検知率・アクティブモデルバージョンを表示するダッシュボード JSON を保存する。
  4. monitoring/prometheus/alert_rules.yml に高異常率および P95 > 100ms のアラートルールを追加する。
- **動作確認コマンド**: `docker compose up -d grafana && curl -sf http://localhost:3000/api/health`
- **完了条件（Definition of Done）**:
  - [ ] CD ワークフローにより AWS ECS のイメージ更新と Smoke Test が自動成功する
  - [ ] Mac ブラウザで http://192.168.0.253:3000 を開くとリアルタイム監視パネルが表示される

### Issue #16: [S3][A] モデルワンクリックロールバック機構と手動ロールバック Workflow 実装（RTO < 3 分）
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: Highest | **依存**: #10, #15
- **目的（Goal）**: 本番モデルの精度劣化や誤報急増時に、1 コマンドまたはボタン操作だけで 3 分以内に @champion を直前の安定バージョンへ切り戻せるようにする。
- **対象ファイル**: `scripts/rollback_model.py`, `.github/workflows/rollback.yml`, `Makefile`
- **実装ステップ（具体作業）**:
  1. scripts/rollback_model.py を実装し、--target-version（未指定時は直前の非劣化バージョンを自動選択）を指定して MLflow @champion エイリアスを切り戻し、rollback_reason 監査タグを記録する。
  2. エイリアス変更後に POST /admin/reload-model（または ECS force-new-deployment）を呼び出し、/model-info で切替完了を検証する。
  3. Makefile に make rollback VERSION=... を追加し、.github/workflows/rollback.yml（workflow_dispatch）を作成する。
- **動作確認コマンド**: `PYTHONPATH=packages:. python scripts/rollback_model.py --dry-run`
- **完了条件（Definition of Done）**:
  - [ ] 実環境演習にて、実行開始から /model-info 切り戻し完了まで 3 分未満で復旧できる

### Issue #17: [S3][B] Evidently による入力特徴量＆予測分布ドリフト監視の実装
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 5h | **優先度**: Highest | **依存**: #3, #5, #12
- **目的（Goal）**: 本番推論の蓄積ログ（Issue #12）と学習ベースライン分布を定期比較し、Data Drift / Prediction Drift を定量検知して HTML レポートを出力する。
- **対象ファイル**: `pipelines/monitoring/drift_check.py`, `tests/test_drift_check.py`
- **実装ステップ（具体作業）**:
  1. pipelines/monitoring/drift_check.py にて参照データ（train.parquet）と直近本番推論ログ（prediction_logs / current.parquet）を読み込む。
  2. Evidently Report([DataDriftPreset()]) により各特徴量の PSI/KS 検定とドリフト列割合（share_of_drifted_columns）および予測異常率の変動を算出する。
  3. HTML レポートおよび JSON サマリー（drift_detected: bool, drifted_features）を生成し、s3://opspulse-data/reports/drift/ へ保存する。
  4. tests/test_drift_check.py を作成し、同分布では False、request_rate_rps を 3 倍にシフトさせると True になることを検証する。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_drift_check.py`
- **完了条件（Definition of Done）**:
  - [ ] Evidently の HTML ドリフトレポートが MinIO/S3 に保存される
  - [ ] 分布シフト注入時に drift_detected=true を正確に検出する

### Issue #18: [S3][Both] 「ドリフト検知 → 人工承認再学習」および「劣化モデルロールバック」結合演習・証跡 #3 記録
- **Owner**: `Both` | **Reviewer**: `Tech Lead` | **目安工数**: 5h | **優先度**: Highest | **依存**: #16, #17
- **目的（Goal）**: MLOps 最大の見せ場である「Human-in-the-Loop 再学習」と「障害ロールバック」の E2E 閉ループを実地演習し、タイムライン証跡を残す。
- **対象ファイル**: `.github/workflows/retrain-hitl.yml`, `docs/evidence/03_drift_and_rollback.md`
- **実装ステップ（具体作業）**:
  1. .github/workflows/retrain-hitl.yml を構築する（Step 1: ドリフト検知時に incident_report テンプレートで GitHub Issue 自動起票 → Step 2: GitHub Environment `production-approval` で人工承認待ち → Step 3: Approve 後に自動再学習＆品質ゲート昇格）。
  2. 結合演習 A：トラフィック分布シフトを注入 → ドリフトアラート確認 → 人工承認 → 新モデル自動昇格までを通しで実行する。
  3. 結合演習 B：意図的に誤報だらけの劣化モデルを @champion に登録 → 異常監視 → make rollback で 1 分以内に安定版へ復旧する。
  4. 両演習のタイムライン・実行ログ・スクリーンショットを docs/evidence/03_drift_and_rollback.md に整理する。
- **動作確認コマンド**: `cat docs/evidence/03_drift_and_rollback.md`
- **完了条件（Definition of Done）**:
  - [ ] HITL 承認を挟んだ自動再学習サイクルを 1 回以上完走している
  - [ ] 劣化モデル投入からのロールバック演習を実測時間付きで記録している

## Sprint 4 (Week 7-8)

### Issue #19: [S4][B] SRE Triage AI Agent 開発：日本語 Runbook RAG による障害一次分析レポート生成
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 6h | **優先度**: Highest | **依存**: #10, #12
- **目的（Goal）**: ML の異常検知後に AI Agent がメトリクス・Top-3 寄与特徴量・直近エラーログ（Issue #12）・日本語運用手順書を組み合わせて構造化一次分析レポートを生成し、MTTR を短縮する。
- **対象ファイル**: `services/triage_agent/rag.py`, `services/triage_agent/agent.py`, `services/triage_agent/app.py`, `tests/test_triage_agent.py`
- **実装ステップ（具体作業）**:
  1. services/triage_agent/rag.py を実装し、knowledge_base/runbooks/RB-*.md をセクション分割して検索し上位 Runbook 原文とファイル名を返す。
  2. agent.py に Pydantic 構造化出力 TriageReport（推定原因・該当Runbook番号・根拠メトリクス/ログ・一次確認コマンド・初動復旧手順・信頼度）を定義し、手順書外のコマンド創作を厳禁とする。
  3. 環境変数 LLM_PROVIDER=gemini|openai|ollama の切替および CI テスト用のモック応答をサポートする。
  4. app.py に POST /triage を実装し、tests/test_triage_agent.py で 4 シナリオの検索・生成と根拠不足時のエスカレーション応答を検証する。
- **動作確認コマンド**: `PYTHONPATH=packages:. pytest tests/test_triage_agent.py`
- **完了条件（Definition of Done）**:
  - [ ] 4 種類のシナリオに対し適切な RB-001〜RB-004 を引用した日本語レポートが生成される
  - [ ] 根拠がない未知事象では推測コマンドを出さず「根拠不足・要人間エスカレーション」を返せる

### Issue #20: [S4][B] Langfuse Cloud トレース連携と Agent オフライン評価レポート #4：`docs/evidence/04_agent_eval.md`
- **Owner**: `Member B` | **Reviewer**: `Member A` | **目安工数**: 4h | **優先度**: High | **依存**: #19
- **目的（Goal）**: LLMOps の可観測性と定量的品質評価を実装し、プロンプト任せではなく数値で AI Agent の信頼性を証明する。
- **対象ファイル**: `services/triage_agent/eval.py`, `knowledge_base/eval_dataset.jsonl`, `docs/evidence/04_agent_eval.md`
- **実装ステップ（具体作業）**:
  1. services/triage_agent/agent.py に Langfuse Cloud SDK（無料枠）を統合し、RAG 検索チャンク・プロンプト・レイテンシ・トークン数を Trace/Span 記録する。
  2. knowledge_base/eval_dataset.jsonl に 15〜20 件の評価ケース（4 障害・正常高負荷・未知ノイズ）を作成する。
  3. eval.py を実装し、Runbook 引用正解率（Citation Accuracy）・Root Cause 命中率・ハルシネーション有無・平均応答時間を集計する。
  4. 評価結果と Langfuse Trace スクリーンショットを docs/evidence/04_agent_eval.md にまとめる。
- **動作確認コマンド**: `PYTHONPATH=packages:. python services/triage_agent/eval.py`
- **完了条件（Definition of Done）**:
  - [ ] Langfuse Cloud ダッシュボード上に全実行の Trace/Span が記録されている
  - [ ] 評価データセットの Runbook 命中率 >= 90% を達成しレポートに記録されている

### Issue #21: [S4][A] セキュリティ監査（シークレット・IAM・tfsec）と日本語《運用手順書》完成
- **Owner**: `Member A` | **Reviewer**: `Member B` | **目安工数**: 4h | **優先度**: High | **依存**: #15, #16
- **目的（Goal）**: 公開ポートフォリオ／企業提出レベルを満たすセキュリティ検査を完遂し、運用チームが迷わず使える日本語《運用手順書》を仕上げる。
- **対象ファイル**: `.github/workflows/ci.yml`, `docs/03_runbook_ops.md`
- **実装ステップ（具体作業）**:
  1. 全 Git 履歴に対して gitleaks 等でシークレット混入検査を実施し、infra/terraform/ に tfsec 静的解析をかけて高リスク指摘を解消する。
  2. AWS IAM ロールの最小権限を点検し、権限設計表を文書化する。
  3. 日本語《運用手順書（docs/03_runbook_ops.md）》を作成し、日常監視・再学習承認手順・緊急ロールバック手順・AWS 課金停止手順（make aws-down）を網羅する。
- **動作確認コマンド**: `gitleaks detect --source . -v || echo 'Verify gitleaks in CI'`
- **完了条件（Definition of Done）**:
  - [ ] Git 履歴内の機密情報リーク 0 件、tfsec 重大指摘 0 件
  - [ ] docs/03_runbook_ops.md を双方が読み合わせ、手順通りに実行できることを確認済み

### Issue #22: [S4][Both] 異常検知→Triage Agent 自動連携＆長期連続稼働試験（Soak Test）・職務経歴書最終化
- **Owner**: `Both` | **Reviewer**: `Tech Lead` | **目安工数**: 5h | **優先度**: Highest | **依存**: #18, #19, #20, #21
- **目的（Goal）**: ML 異常検知・ログ取得・AI Agent 分析を完全自動連携させ、LAN Linux サーバーで長期連続稼働を実証した上で、職務経歴書に載せる実測数値を確定させる。
- **対象ファイル**: `scripts/monitor_and_triage.py`, `scripts/soak_runner.py`, `README.md`, `docs/evidence/05_soak_and_final_acceptance.md`
- **実装ステップ（具体作業）**:
  1. scripts/monitor_and_triage.py を実装し、target_app 監視 → /predict 異常検知が連続発生時に /admin/logs を取得 → triage_agent /triage で日本語一次分析レポートを自動出力する。
  2. scripts/soak_runner.py を 192.168.0.253 上で連続稼働させ（通常負荷・キャンペーン急増・間欠障害を混合）、長期稼働時のメモリ安定性・Grafana 推移・Evidently 定期チェックを記録する。
  3. ルート README.md に全 5 本のエビデンス表と最終構成を反映する。
  4. 実測数値のみを docs/evidence/05_soak_and_final_acceptance.md に集約し、Tech Lead と双方の日本語職務経歴書アピール文・想定質問 Q&A を最終化する。
- **動作確認コマンド**: `PYTHONPATH=packages:. python scripts/monitor_and_triage.py --once`
- **完了条件（Definition of Done）**:
  - [ ] 異常注入 → ML 検知 → ログ収集 → Agent 日本語レポート生成までの E2E 自動連携がワンコマンドで完走する
  - [ ] 全エビデンスレポートの数値が実測値で埋まり、模擬面接の受け答え準備が完了している

### Issue #23: [S4][Optional] 製造業設備予知保全モジュール（UCI AI4I 2020）：MLOps 基盤の汎用性実証
- **Owner**: `Both` | **Reviewer**: `Tech Lead` | **目安工数**: 4h | **優先度**: Low | **依存**: #9, #10
- **目的（Goal）**: （任意・加点タスク）MLflow・品質ゲート・CI/CD 基盤を一切作り直さず、製造業設備データセットを載せ替えるだけで別ドメインへ展開できるプラットフォーム汎用性を実証する。
- **対象ファイル**: `pipelines/training/train_predictive_maintenance.py`, `docs/evidence/06_platform_reusability.md`
- **実装ステップ（具体作業）**:
  1. UCI AI4I 2020 Predictive Maintenance 合成データセット（10,000 件・合成公開データである旨を明記）を取得する。
  2. train_predictive_maintenance.py を実装し、同じ MLflow Registry 上に第 2 モデル（opspulse-ai4i-pdm）を登録・評価する。
  3. 基盤再利用による立ち上げコスト削減効果を docs/evidence/06_platform_reusability.md にまとめる。
- **動作確認コマンド**: `PYTHONPATH=packages:. python pipelines/training/train_predictive_maintenance.py`
- **完了条件（Definition of Done）**:
  - [ ] MLflow 上に第 2 業務モデルが登録され、同一の実験管理・品質ゲートフローで動作することが確認できている
