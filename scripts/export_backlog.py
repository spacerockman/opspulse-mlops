"""Generate Markdown backlog (`docs/03_sprint_backlog.md`) and Jira CSV import
(`docs/jira_backlog_import.csv`) from the single source of truth `docs/backlog_tasks.json`.

Usage:
    python scripts/export_backlog.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_JSON = ROOT / "docs" / "backlog_tasks.json"
MARKDOWN_OUT = ROOT / "docs" / "03_sprint_backlog.md"
JIRA_CSV_OUT = ROOT / "docs" / "jira_backlog_import.csv"


def load_tasks() -> list[dict]:
    with TASKS_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_markdown(tasks: list[dict]) -> str:
    lines: list[str] = [
        "# 03. Sprint バックログ＆タスク詳細台帳（全 22 チケット）",
        "",
        "> **Single Source of Truth**: 本ファイルは `docs/backlog_tasks.json` から "
        "`python scripts/export_backlog.py` により自動生成されています。",
        "> オンライン管理ツール（**GitHub Projects + Issues** 推奨、または **Jira Cloud Free**）へ"
        "そのまま一括登録できます。",
        "",
        "## 一括インポート手順",
        "- **GitHub Issues / Projects を使う場合（推奨）**:",
        "  ```bash",
        "  export GITHUB_TOKEN=ghp_xxx",
        "  python scripts/bootstrap_github_board.py --repo <owner>/opspulse-mlops "
        "--member-a <gh_user_a> --member-b <gh_user_b>",
        "  ```",
        "- **Jira Cloud (Free) を使う場合**:",
        "  Jira プロジェクト設定 → **System → External System Import → CSV** から "
        "`docs/jira_backlog_import.csv` をそのまま取り込むと、全 22 チケットが一括作成されます。",
        "",
        "---",
        "",
        "## 全体アサイン早見表（各自の担当を確認してピックアップ）",
        "",
        "| ID | Sprint | Owner | Reviewer | 工数 | 依存 | タスク名 |",
        "| :---: | :--- | :--- | :--- | :---: | :--- | :--- |",
    ]

    for t in tasks:
        deps = ", ".join(f"#{d}" for d in t["depends_on"]) if t["depends_on"] else "-"
        lines.append(
            f"| **#{t['id']}** | {t['sprint']} | `{t['owner']}` | `{t['reviewer']}` | "
            f"{t['estimate_hours']}h | {deps} | {t['title']} |"
        )

    lines.extend(["", "---", ""])

    current_sprint = None
    for t in tasks:
        if t["sprint"] != current_sprint:
            current_sprint = t["sprint"]
            lines.append(f"## {current_sprint}")
            lines.append("")

        deps = ", ".join(f"#{d}" for d in t["depends_on"]) if t["depends_on"] else "なし"
        lines.append(f"### Issue #{t['id']}: {t['title']}")
        lines.append(
            f"- **Owner**: `{t['owner']}` | **Reviewer**: `{t['reviewer']}` | "
            f"**目安工数**: {t['estimate_hours']}h | **優先度**: {t['priority']} | "
            f"**依存**: {deps}"
        )
        lines.append(f"- **目的（Goal）**: {t['goal']}")
        lines.append(
            "- **対象ファイル**: " + ", ".join(f"`{p}`" for p in t["target_files"])
        )
        lines.append("- **実装ステップ（具体作業）**:")
        for idx, step in enumerate(t["steps"], start=1):
            lines.append(f"  {idx}. {step}")
        lines.append(f"- **動作確認コマンド**: `{t['verify_cmd']}`")
        lines.append("- **完了条件（Definition of Done）**:")
        for item in t["dod"]:
            lines.append(f"  - [ ] {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def format_jira_description(t: dict) -> str:
    deps = ", ".join(f"#{d}" for d in t["depends_on"]) if t["depends_on"] else "None"
    steps_txt = "\n".join(f"{i}. {s}" for i, s in enumerate(t["steps"], start=1))
    dod_txt = "\n".join(f"* [ ] {d}" for d in t["dod"])
    files_txt = "\n".join(f"* {p}" for p in t["target_files"])
    return (
        f"h3. Goal\n{t['goal']}\n\n"
        f"*Owner:* {t['owner']} | *Reviewer:* {t['reviewer']} | *Dependencies:* {deps}\n\n"
        f"h3. Target Files\n{files_txt}\n\n"
        f"h3. Implementation Steps\n{steps_txt}\n\n"
        f"h3. Verification Command\n{{code:bash}}\n{t['verify_cmd']}\n{{code}}\n\n"
        f"h3. Definition of Done\n{dod_txt}"
    )


def export_jira_csv(tasks: list[dict]) -> None:
    fieldnames = [
        "Issue Key",
        "Summary",
        "Issue Type",
        "Priority",
        "Sprint",
        "Story Points",
        "Original Estimate (h)",
        "Owner Role",
        "Reviewer Role",
        "Labels",
        "Description",
    ]
    with JIRA_CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in tasks:
            writer.writerow(
                {
                    "Issue Key": f"OPS-{t['id'] + 1}",
                    "Summary": t["title"],
                    "Issue Type": t["issue_type"],
                    "Priority": t["priority"],
                    "Sprint": t["sprint"],
                    "Story Points": max(1, round(t["estimate_hours"] / 2)),
                    "Original Estimate (h)": t["estimate_hours"],
                    "Owner Role": t["owner"],
                    "Reviewer Role": t["reviewer"],
                    "Labels": " ".join(t["labels"]),
                    "Description": format_jira_description(t),
                }
            )


def main() -> None:
    tasks = load_tasks()
    MARKDOWN_OUT.write_text(render_markdown(tasks), encoding="utf-8")
    export_jira_csv(tasks)
    print(f"Generated {MARKDOWN_OUT} and {JIRA_CSV_OUT} ({len(tasks)} tasks).")


if __name__ == "__main__":
    main()
