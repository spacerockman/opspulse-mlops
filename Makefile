.PHONY: help setup lint fmt test up down logs run-target run-inference \
        inject-normal inject-memleak inject-dbpool inject-timeout inject-drift \
        eval-baseline export-backlog

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PYTHONPATH_ENV := PYTHONPATH=packages:.

help: ## 利用可能なコマンド一覧を表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## ローカル開発環境をセットアップ (uv があれば uv、なければ venv+pip)
	@if command -v uv >/dev/null 2>&1; then \
		uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]"; \
	else \
		python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -e ".[dev]"; \
	fi
	@echo "✅ Setup complete! Activate with: source .venv/bin/activate"

lint: ## Ruff による静的解析
	$(PYTHON) -m ruff check packages services pipelines scripts tests

fmt: ## Ruff によるコード自動整形
	$(PYTHON) -m ruff format packages services pipelines scripts tests

test: ## 自動テスト (pytest) を実行
	$(PYTHONPATH_ENV) $(PYTHON) -m pytest

up: ## Docker Compose でローカル基盤を起動 (v0.1)
	docker compose up -d --build

down: ## Docker Compose を停止
	docker compose down

logs: ## Docker Compose のログを確認
	docker compose logs -f

run-target: ## [Docker不要] 模擬業務アプリ (target_app) をローカル起動 (:8001)
	$(PYTHONPATH_ENV) $(PYTHON) -m uvicorn services.target_app.app:app --host 0.0.0.0 --port 8001 --reload

run-inference: ## [Docker不要] 推論 API (inference_api) をローカル起動 (:8002)
	$(PYTHONPATH_ENV) $(PYTHON) -m uvicorn services.inference_api.app:app --host 0.0.0.0 --port 8002 --reload

inject-normal: ## 正常トラフィックを 20 秒間注入
	$(PYTHONPATH_ENV) $(PYTHON) scripts/fault_injector.py --scenario normal --duration 20

inject-memleak: ## 故障注入: メモリリーク予兆 (現行ルールで見逃しやすい)
	$(PYTHONPATH_ENV) $(PYTHON) scripts/fault_injector.py --scenario memory_leak --duration 30

inject-dbpool: ## 故障注入: DB接続プール枯渇
	$(PYTHONPATH_ENV) $(PYTHON) scripts/fault_injector.py --scenario db_pool_exhaustion --duration 25

inject-timeout: ## 故障注入: 外部決済APIタイムアウト
	$(PYTHONPATH_ENV) $(PYTHON) scripts/fault_injector.py --scenario downstream_timeout --duration 25

inject-drift: ## 正常トラフィック急増 (現行静的ルールの誤報を再現!)
	$(PYTHONPATH_ENV) $(PYTHON) scripts/fault_injector.py --scenario traffic_surge_normal --duration 25

eval-baseline: ## オフライン合成データで v0.1 静的ルール基線のスコアを計測
	$(PYTHONPATH_ENV) $(PYTHON) pipelines/training/evaluate_baseline.py

export-backlog: ## backlog_tasks.json から 03_sprint_backlog.md と Jira CSV を生成
	$(PYTHONPATH_ENV) $(PYTHON) scripts/export_backlog.py
