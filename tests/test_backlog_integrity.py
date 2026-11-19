"""Integrity tests ensuring backlog JSON, Markdown, and Jira CSV stay in sync."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.export_backlog import JIRA_CSV_OUT, MARKDOWN_OUT, TASKS_JSON, render_markdown


def test_backlog_tasks_schema_and_sync() -> None:
    tasks = json.loads(TASKS_JSON.read_text(encoding="utf-8"))
    assert len(tasks) == 24
    ids = [t["id"] for t in tasks]
    assert ids == list(range(24))

    valid_owners = {"Member A", "Member B", "Both"}
    for t in tasks:
        assert t["owner"] in valid_owners
        assert t["estimate_hours"] > 0
        assert len(t["target_files"]) >= 1
        assert len(t["steps"]) >= 2
        assert len(t["dod"]) >= 1
        assert t["verify_cmd"].strip()

    assert MARKDOWN_OUT.read_text(encoding="utf-8") == render_markdown(tasks)
    with Path(JIRA_CSV_OUT).open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 24
