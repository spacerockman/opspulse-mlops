# SRE Triage AI Agent (`services/triage_agent/`)

- **Owner**: メンバー B（ML / LLMOps 担当）
- **対象 Issue**: Sprint 4, **Issue #18 & #19**
- **責務**:
  1. 推論 API が検知した異常イベント（メトリクス・Top-3 寄与特徴量・直近エラーログ）を受け取る。
  2. `knowledge_base/runbooks/` 配下の日本語運用手順書を RAG 検索。
  3. 日本語の一次障害分析レポート（推定原因・根拠・確認コマンド・初動手順）を生成。
  4. Langfuse Cloud へ全トレースを送信し、15〜20 件の評価データセットで品質評価（Root Cause 命中率・ハルシネーション抑制）を実施。
