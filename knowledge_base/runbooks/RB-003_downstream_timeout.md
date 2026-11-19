# RB-003: 外部決済 API タイムアウト（ERR_PAYMENT_GATEWAY_TIMEOUT）対応手順書

- **対象サービス**: `order-service`
- **関連エラーコード**: `ERR_PAYMENT_GATEWAY_TIMEOUT`
- **関連メトリクス**: `p95_latency_ms` (> 2000ms), `error_rate` (> 5%), `db_pool_utilization`（正常範囲 30〜50%）
- **重要度**: Critical（決済完了不可）

## 1. 典型的な兆候（Symptoms）
- `p95_latency_ms` が 2,000ms 以上へ急上昇し、エラー率が 10% 前後へ跳ね上がる。
- RB-002（DB 枯渇）とは異なり、`db_pool_utilization` および CPU/メモリは正常範囲に留まる。
- アプリログに `ERR_PAYMENT_GATEWAY_TIMEOUT`（`Upstream payment gateway did not respond within 2000ms`）が集中記録される。

## 2. 一次確認チェックリスト
1. 外部決済プロバイダのステータスページおよび障害通知メールを確認する。
2. アプリサーバーから外部決済エンドポイントへのネットワーク到達性（DNS / TLS / NAT）を確認する。
3. リトライストームが発生して自社のスレッドを枯渇させていないか確認する。

## 3. 初動切り分け・暫定復旧手順（Mitigation）
1. **サーキットブレーカー / タイムアウト短縮**：外部障害が確定した場合、決済呼び出しのサーキットブレーカーを有効化し、リトライ過多による連鎖障害を防止する。
2. **顧客告知（メンテナンス表示）**：決済処理のみ一時停止（Degraded Mode）へ切り替え、運用窓口より顧客向けステータスページを更新する。
3. **復旧確認**：外部決済 API の応答時間が 300ms 未満で 5 分間安定したことを確認してから通常モードへ復帰する。
