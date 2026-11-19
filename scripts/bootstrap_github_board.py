"""Bootstrap GitHub Labels, Milestones (Sprint 0-4), Issues (#0-#21), and an
optional GitHub Project (v2) Kanban board directly from `docs/backlog_tasks.json`.

Usage:
    export GITHUB_TOKEN="ghp_..."  # needs `repo` scope (+ `project` scope for Kanban board)
    python scripts/bootstrap_github_board.py \
        --repo <github-owner>/opspulse-mlops \
        --member-a <github-username-a> \
        --member-b <github-username-b>

Dry-run preview (no network calls):
    python scripts/bootstrap_github_board.py --repo demo/opspulse-mlops --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
TASKS_JSON = ROOT / "docs" / "backlog_tasks.json"

LABEL_COLORS: dict[str, str] = {
    "sprint:0": "cfd3d7",
    "sprint:1": "0e8a16",
    "sprint:2": "1d76db",
    "sprint:3": "5319e7",
    "sprint:4": "d93f0b",
    "owner:member-a": "0052cc",
    "owner:member-b": "c5def5",
    "owner:both": "fbca04",
    "area:infra": "006b75",
    "area:ml": "b60205",
    "area:llmops": "e99695",
    "area:ci-cd": "2cbe4e",
    "area:monitoring": "f9d0c4",
    "area:docs": "fef2c0",
}


def format_issue_body(task: dict) -> str:
    deps = ", ".join(f"#{d}" for d in task["depends_on"]) if task["depends_on"] else "なし"
    files = "\n".join(f"- `{p}`" for p in task["target_files"])
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(task["steps"], start=1))
    dod = "\n".join(f"- [ ] {d}" for d in task["dod"])
    return (
        f"## タスク概要（Goal）\n{task['goal']}\n\n"
        f"| 項目 | 内容 |\n| :--- | :--- |\n"
        f"| **Sprint** | {task['sprint']} |\n"
        f"| **Owner** | {task['owner']} |\n"
        f"| **Reviewer** | {task['reviewer']} |\n"
        f"| **目安工数** | {task['estimate_hours']}h |\n"
        f"| **優先度** | {task['priority']} |\n"
        f"| **依存チケット** | {deps} |\n\n"
        f"## 対象ファイル\n{files}\n\n"
        f"## 実装ステップ（具体作業）\n{steps}\n\n"
        f"## 動作確認コマンド\n```bash\n{task['verify_cmd']}\n```\n\n"
        f"## 完了条件（Definition of Done）\n{dod}\n"
    )


def resolve_assignees(owner: str, member_a: str | None, member_b: str | None) -> list[str]:
    assignees: list[str] = []
    if owner == "Member A" and member_a:
        assignees.append(member_a)
    elif owner == "Member B" and member_b:
        assignees.append(member_b)
    elif owner == "Both":
        if member_a:
            assignees.append(member_a)
        if member_b and member_b != member_a:
            assignees.append(member_b)
    return assignees


def ensure_labels(client: httpx.Client, repo: str) -> None:
    existing = {
        lbl["name"] for lbl in client.get(f"/repos/{repo}/labels", params={"per_page": 100}).json()
    }
    for name, color in LABEL_COLORS.items():
        if name not in existing:
            resp = client.post(
                f"/repos/{repo}/labels",
                json={"name": name, "color": color},
            )
            if resp.status_code not in (200, 201, 422):
                resp.raise_for_status()


def ensure_milestones(client: httpx.Client, repo: str, tasks: list[dict]) -> dict[str, int]:
    existing = {
        m["title"]: m["number"]
        for m in client.get(
            f"/repos/{repo}/milestones", params={"state": "all", "per_page": 100}
        ).json()
    }
    for task in tasks:
        sprint = task["sprint"]
        if sprint not in existing:
            resp = client.post(f"/repos/{repo}/milestones", json={"title": sprint})
            resp.raise_for_status()
            existing[sprint] = resp.json()["number"]
    return existing


def existing_issue_titles(client: httpx.Client, repo: str) -> dict[str, str]:
    found: dict[str, str] = {}
    page = 1
    while True:
        resp = client.get(
            f"/repos/{repo}/issues",
            params={"state": "all", "per_page": 100, "page": page},
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        for it in items:
            if "pull_request" not in it:
                found[it["title"]] = it["node_id"]
        page += 1
    return found


def try_create_project_v2(
    client: httpx.Client, repo: str, issue_node_ids: list[str]
) -> str | None:
    """Create a GitHub Project v2 board, link it to the repo, and add all issues."""
    repo_owner, repo_name = repo.split("/", 1)
    owner_q = """
    query($login: String!, $repoOwner: String!, $repoName: String!) {
      repositoryOwner(login: $login) { id }
      repository(owner: $repoOwner, name: $repoName) { id }
    }
    """
    r = client.post(
        "/graphql",
        json={
            "query": owner_q,
            "variables": {"login": repo_owner, "repoOwner": repo_owner, "repoName": repo_name},
        },
    )
    if r.status_code != 200 or "errors" in r.json():
        return None
    data = r.json()["data"]
    owner_data = data.get("repositoryOwner")
    repo_data = data.get("repository")
    if not owner_data or not repo_data:
        return None

    create_proj = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id url }
      }
    }
    """
    pr = client.post(
        "/graphql",
        json={
            "query": create_proj,
            "variables": {"ownerId": owner_data["id"], "title": "OpsPulse MLOps Sprint Board"},
        },
    )
    if pr.status_code != 200 or "errors" in pr.json():
        return None
    proj = pr.json()["data"]["createProjectV2"]["projectV2"]

    link_repo = """
    mutation($projectId: ID!, $repositoryId: ID!) {
      linkProjectV2ToRepository(input: {projectId: $projectId, repositoryId: $repositoryId}) {
        repository { id }
      }
    }
    """
    client.post(
        "/graphql",
        json={
            "query": link_repo,
            "variables": {"projectId": proj["id"], "repositoryId": repo_data["id"]},
        },
    )

    add_item = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }
    """
    for node_id in issue_node_ids:
        client.post(
            "/graphql",
            json={"query": add_item, "variables": {"projectId": proj["id"], "contentId": node_id}},
        )
    return proj["url"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap OpsPulse GitHub Issues & Project board")
    parser.add_argument("--repo", required=True, help="GitHub repo in `owner/name` format")
    parser.add_argument("--member-a", default=None, help="GitHub username for Member A")
    parser.add_argument("--member-b", default=None, help="GitHub username for Member B")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without calling GitHub")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = json.loads(TASKS_JSON.read_text(encoding="utf-8"))

    if args.dry_run:
        print(f"[DRY-RUN] Target repo: {args.repo} | Total tasks: {len(tasks)}")
        for t in tasks:
            assignees = resolve_assignees(t["owner"], args.member_a, args.member_b)
            print(f"  - #{t['id']:02d} [{t['sprint']}] {t['title']} -> assignees={assignees}")
        return 0

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("[ERROR] Set GITHUB_TOKEN (or GH_TOKEN) before running.", file=sys.stderr)
        return 1

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    with httpx.Client(base_url="https://api.github.com", headers=headers, timeout=20.0) as client:
        ensure_labels(client, args.repo)
        milestones = ensure_milestones(client, args.repo, tasks)
        existing = existing_issue_titles(client, args.repo)

        node_ids: list[str] = []
        created_count = 0
        for task in tasks:
            title = task["title"]
            if title in existing:
                print(f"[SKIP] Already exists: {title}")
                node_ids.append(existing[title])
                continue

            payload = {
                "title": title,
                "body": format_issue_body(task),
                "labels": task["labels"],
                "milestone": milestones[task["sprint"]],
                "assignees": resolve_assignees(task["owner"], args.member_a, args.member_b),
            }
            resp = client.post(f"/repos/{args.repo}/issues", json=payload)
            resp.raise_for_status()
            issue_data = resp.json()
            node_ids.append(issue_data["node_id"])
            created_count += 1
            print(f"[CREATED] #{issue_data['number']} -> {title}")

        proj_url = try_create_project_v2(client, args.repo, node_ids)
        print("-" * 60)
        print(f"Done! Created {created_count} new issues (total tracked: {len(node_ids)}).")
        print(f"Issues URL: https://github.com/{args.repo}/issues")
        if proj_url:
            print(f"Project Board URL: {proj_url}")
        else:
            print(
                "Note: Project v2 board was not auto-created (token may lack `project` scope). "
                "You can link all created issues in GitHub UI -> Projects -> New project."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
