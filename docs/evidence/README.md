# 実証エビデンス保管庫（`docs/evidence/`）

日本企業の技術面接・職務経歴書では「作りました」だけでなく、**定量的な検証結果（数字・スクショ・再現コマンド）** が圧倒的な説得力を生みます。各 Sprint の完了時に以下 4 つのレポートを必ずここに蓄積してください。

- [ ] `01_model_vs_baseline.md`（Sprint 1, Issue #6）：ML モデル vs 現行静的閾値ルールの比較表・混同行列・誤報率改善幅
- [ ] `02_load_test.md`（Sprint 2, Issue #9）：推論 API の P50/P95/P99 レイテンシ・最大 QPS・コンテナ CPU/メモリ計測値
- [ ] `03_drift_and_rollback.md`（Sprint 3, Issue #15 & #17）：Evidently ドリフト検知 → HITL 承認再学習 → 不良モデル投入＆1分以内ロールバックのタイムライン記録
- [ ] `04_agent_eval.md`（Sprint 4, Issue #19）：SRE Triage Agent の Langfuse Trace 証跡および 15〜20 件オフライン評価スコア
