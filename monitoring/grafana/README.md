# Grafana Dashboards (`monitoring/grafana/`)

- **Owner**: メンバー A（Platform / SRE 担当）
- **対象 Issue**: Sprint 3, **Issue #14**
- **責務**:
  - Prometheus（`order-service` および `inference-api`）のメトリクスを可視化するダッシュボードを構築し、JSON としてこのディレクトリへエクスポート・バージョン管理する。
  - 必須パネル：
    1. Target App CPU / Memory / RPS / Error Rate / P95 Latency / DB Pool 使用率
    2. Inference API P95 推論レイテンシ・QPS・異常検知率推移
    3. アクティブモデルバージョン（`@champion`）切替マーカー
