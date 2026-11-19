# GitHub Actions Workflows (Sprint 2–3 Scope)

このディレクトリは **Sprint 2〜3** にてメンバー A（主担当）およびメンバー B（協働）が構築します。

予定ワークフロー一覧：
1. `ci.yml`（**Sprint 2, Issue #8, メンバー A**）
   - PR 作成・更新時に `ruff check`、`pytest`、Docker build 検証を自動実行。
2. `cd-ecs.yml`（**Sprint 3, Issue #14, メンバー A**）
   - `main` マージ時に推論 API イメージを ECR へ push し、AWS ECS Fargate をローリング更新＋Smoke Test 実行。
3. `retrain-hitl.yml`（**Sprint 3, Issue #17, メンバー B & A**）
   - Evidently がドリフトを検知後、GitHub Environment の **Manual Approval（人工承認）** を経て再学習→品質ゲート→MLflow `@champion` 昇格を実行。
