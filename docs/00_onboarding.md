# 00. 新人オンボーディングガイド（Day 1 入职指南）

ようこそ **OpsPulse MLOps** チームへ！
このガイドは、既存の `v0.1 PoC` コードベースを 30 分以内に手元で動かし、**「なぜ現行の静的閾値アラートではダメで、MLOps が必要なのか」** を実体験するための手順書です。

---

## Step 1. 開発ツールの準備

> **前提環境**：Python 3.11+（本機は Python 3.12 確認済）、Git、Make。
> **推奨追加ツール**：`uv`（超高速パッケージ管理）および Docker Engine / Docker Compose（Sprint 1 以降で必須）。

```bash
# (任意・推奨) uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. リポジトリの Python 仮想環境と依存をセットアップ
make setup
source .venv/bin/activate

# 2. 環境変数ファイルを作成（.env は .gitignore 済。絶対にコミットしないこと！）
cp .env.example .env

# 3. 既存テストと Lint が全パスすることを確認
make lint
make test
```

---

## Step 2. 現行 v0.1 システムの弱点を自分の目で確認する

### 実験 A：オフライン・ベンチマーク（10 秒で完了）
```bash
make eval-baseline
```
出力を見て、以下の 2 点を確認してください：
1. `traffic_surge_normal`（正常なセール時トラフィック急増）で大量の **False Positive（誤報）** が出ている。
2. `memory_leak`（緩やかなメモリリーク）の初期段階で **False Negative（見逃し）** が発生している。

### 実験 B：リアルタイム障害注入を体験（ターミナル 3 つ）
```bash
# Terminal 1: 模擬注文サービスを起動 (http://localhost:8001/docs)
make run-target

# Terminal 2: 現行の静的閾値推論 API を起動 (http://localhost:8002/docs)
make run-inference

# Terminal 3: 正常トラフィック急増を注入 → 現行ルールが誤報を連発するのを観察！
make inject-drift

# 続いてメモリリークを注入 → 初期に見逃すのを観察！
make inject-memleak
```

*(Docker 導入後は `make up` 1 コマンドで `target-app` + `inference-api` + `prometheus` (:9090) が一括起動します。)*

---

## Step 3. Git / GitHub 開発フロー（チーム鉄則）

1. **Issue から始める**：[docs/03_sprint_backlog.md](03_sprint_backlog.md) から自分の担当 Issue を GitHub Issues ＆ Projects 看板に登録する。
2. **ブランチ命名規則**：`feat/<issue番号>-<短い英語名>`（例：`feat/1-local-mlflow-minio`、`ml/4-shared-features`）。
3. **Commit メッセージ規則**：Conventional Commits（`feat:`, `fix:`, `infra:`, `ml:`, `docs:`, `test:`）。
4. **PR 提出前チェック**：
   - `make lint && make test` が緑灯であること。
   - PR テンプレートに従い、**自分の手で実行した検証結果**を貼ること。
   - 相手メンバーに Review を依頼すること（メンバー A ↔ メンバー B 相互レビュー）。
5. **Tech Lead（Antigravity）の使い方**：
   - 設計で迷ったら ADR の相談をする。
   - PR を出したら差分を貼ってコードレビューを依頼する。
   - 絶対に「AI が出したコードを検証せずにマージする」ことはしない！
