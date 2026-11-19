# RB-001: メモリリーク・OOMKill 予兆対応手順書

- **対象サービス**: `order-service`
- **関連メトリクス**: `memory_percent`, `memory_slope_per_min` (> 2.5%/min), `p95_latency_ms`（緩やかな上昇）
- **重要度**: High（放置すると 20〜40 分以内に OOMKill 発生）

## 1. 典型的な兆候（Symptoms）
- `memory_percent` がリクエスト数（RPS）と無関係に単調増加し、`memory_slope_per_min` がプラスで張り付く。
- 初期段階では CPU 使用率（< 80%）および 5xx エラー率はまだ正常範囲内に見えることが多い。
- ガベージコレクション（GC）頻発により `p95_latency_ms` が通常の 2〜4 倍（150〜400ms）へ徐々に悪化する。

## 2. 一次確認コマンド
```bash
# コンテナのメモリ使用推移と OOMKill 履歴を確認
docker stats --no-stream opspulse-target-app
# AWS ECS の場合
aws ecs describe-tasks --cluster opspulse-prod --tasks <TASK_ARN> --query "tasks[].containers[].{name:name,reason:reason,exitCode:exitCode}"
```

## 3. 初動切り分け・暫定復旧手順（Mitigation）
1. **ローリング再起動によるメモリ解放**：ECS タスクまたはコンテナを 1 台ずつローリング再起動し、OOMKill によるサービス全面停止を防ぐ。
2. **直近デプロイの確認**：過去 24 時間以内のリリース（特にインメモリキャッシュやグローバル辞書への追記処理）を確認し、該当する場合は前バージョンへロールバックする。
3. **プロファイル取得**：再起動前に可能であれば Python `tracemalloc` スナップショットを取得し、開発チームへエスカレーションする。

## 4. エスカレーション先
- 一次対応でメモリ増加が再発する場合：`#sre-incident` チャンネルおよび Backend 開発担当へ起票。
