## 概要（Summary / 変更内容）
<!-- 关联 Issue 必填，例如 Closes #1 -->
Closes #

- 何を変更したか（3行以内で簡潔に）：
  -

## なぜこの変更が必要か（Why）
-

## 検証エビデンス（Verification Evidence）
<!-- AI で生成したコードでも、必ず自分で実行したコマンドと結果を貼ること！ -->
```bash
# 実行したコマンド（例: make lint && make test）
```
- テスト結果 / スクリーンショット：

## MLOps セルフレビューチェックリスト
- [ ] `make lint`（ruff）と `make test`（pytest）がローカルで全てパスした
- [ ] 機密情報（APIキー、AWS認証情報、`.env`）が含まれていないことを確認した
- [ ] 特徴量やスキーマを変更した場合、`packages/opspulse_core/` 経由で学習・推論の一貫性を保っている
- [ ] 必要に応じて `docs/` や `.env.example` を更新した
- [ ] PR の変更量をレビューしやすいサイズ（目安 300 行以内）に抑えた
