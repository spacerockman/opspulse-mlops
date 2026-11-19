# Training & Model Evaluation Pipeline (`pipelines/training/`)

- **Owner**: メンバー B（ML / LLMOps 担当）
- **対象 Issue**:
  - Sprint 1, **Issue #5**: `train.py` を実装し、`StaticThreshold` vs `IsolationForest` vs `LightGBM` を MLflow へ記録。
  - Sprint 1, **Issue #6**: ベースライン比較レポート `docs/evidence/01_model_vs_baseline.md` を作成。
  - Sprint 2, **Issue #10**: 自動品質ゲート（Quality Gate）を実装し、合格モデルのみ `@challenger` → `@champion` 昇格。

まず `make eval-baseline` を実行し、現行 v0.1 静的ルールのスコア（特に誤報率とメモリリーク見逃し）を確認してください。
