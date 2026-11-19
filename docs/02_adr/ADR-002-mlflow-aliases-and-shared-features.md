# ADR-002: MLflow Model Aliases (`@champion`/`@challenger`) と共有特徴量パッケージの採用

- **ステータス**: Accepted（承認済）
- **決定日**: 2026-11-19
- **決定者**: Tech Lead / ML チーム

## コンテキスト（Context）
ML モデルの継続的デプロイにおいて、現場で最も事故が多いのは次の 2 点である：
1. **Train-Serving Skew**：学習ノートブックと推論 API で特徴量計算ロジックが微妙に食い違い、本番精度が劣化する。
2. **モデルバージョン切替・ロールバックの属人化**：ファイルパスを手動で書き換えてデプロイすると、障害発生時に数分以内で安全にロールバックできない。

## 決定（Decision）
1. 特徴量計算およびデータ契約（Pydantic / Pandera）を **`packages/opspulse_core/`** に集約し、学習パイプラインと推論 API の双方から必ず同一関数を import する。
2. MLflow 2.x 以降で非推奨となった旧 `Stages (Staging/Production)` は使用せず、最新の **Model Aliases（`@challenger` / `@champion`）** によるデプロイ・ロールバック方式を採用する。

## 理由（Rationale）
- 推論 API は常に `models:/opspulse-anomaly-detector@champion` を参照するため、コード変更なしで品質ゲート合格モデルの昇格や、障害時の旧バージョンへのロールバック（`@champion` エイリアス付け替え＋サービス再読み込み）が可能になる。
- `tests/` に学習・推論間の特徴量一致テスト（Train-Serving Consistency Test）を組み込むことで、CI で不整合を自動ブロックできる。
