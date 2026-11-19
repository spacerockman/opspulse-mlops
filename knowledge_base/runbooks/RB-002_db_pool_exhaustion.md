# RB-002: DB 接続プール枯渇（ERR_DB_POOL_TIMEOUT）対応手順書

- **対象サービス**: `order-service`
- **関連エラーコード**: `ERR_DB_POOL_TIMEOUT`
- **関連メトリクス**: `db_pool_utilization` (> 0.90), `p95_latency_ms` (> 1500ms), `error_rate` (> 5%), `cpu_percent`（むしろ低下傾向）
- **重要度**: Critical（注文処理の大幅遅延・失敗が発生）

## 1. 典型的な兆候（Symptoms）
- アプリケーションの CPU 使用率は低い（20〜30%）にもかかわらず、レイテンシと HTTP 500 エラーが急増する（典型的 I/O 待ちボトルネック）。
- ログに `ERR_DB_POOL_TIMEOUT`（`Database connection pool exhausted`）が出力される。
- `db_pool_utilization` が 95〜100% に張り付き、`latency_per_cpu` が異常に高い値を示す。

## 2. 一次確認コマンド
```sql
-- PostgreSQL 上の長時間実行クエリおよびロック待ちを確認
SELECT pid, now() - query_start AS duration, state, wait_event_type, left(query, 120)
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;
```

## 3. 初動切り分け・暫定復旧手順（Mitigation）
1. **ブロッキングクエリの特定と停止**：スロークエリまたはデッドロックが接続を占有している場合、DB 管理者承認のうえ `pg_terminate_backend(pid)` で該当セッションを解放する。
2. **接続リーク確認**：トランザクション未クローズやバッチ処理の同時実行による接続占有がないか確認する。
3. **暫定スケール調整**：DB 側の `max_connections` 上限を確認した上で、必要に応じアプリ側コネクションプール設定およびリードレプリカ振り分けを検討する。

## 4. 事後対応
- 該当クエリの `EXPLAIN ANALYZE` 取得とインデックス追加チケット作成。
