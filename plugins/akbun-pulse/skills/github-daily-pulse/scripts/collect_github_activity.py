#!/usr/bin/env python3
"""Collect today's GitHub activity across every repo the gh-authenticated account can access.

Output is a single JSON document (stdout or --out) that the skill turns into the Korean digest.
Requires an authenticated `gh` CLI. Nothing is written to GitHub.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

BODY_LIMIT = 1500
COMMENT_LIMIT = 800
DISCUSSIONS_PER_REPO = 30

DISCUSSIONS_QUERY = """
query($owner: String!, $name: String!, $first: Int!) {
  repository(owner: $owner, name: $name) {
    discussions(first: $first, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        url
        body
        createdAt
        updatedAt
        isAnswered
        author { login }
        category { name }
        comments(last: 20) {
          nodes { body createdAt author { login } }
        }
      }
    }
  }
}
"""


def gh(args: list[str], stdin: str | None = None) -> str:
  result = subprocess.run(
    ["gh", *args],
    input=stdin,
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr.strip() or f"gh {' '.join(args)} failed")
  return result.stdout


def gh_json(args: list[str]) -> Any:
  out = gh(args)
  return json.loads(out) if out.strip() else []


def parse_time(value: str) -> datetime:
  return datetime.fromisoformat(value.replace("Z", "+00:00"))


def to_utc_iso(value: datetime) -> str:
  return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def truncate(text: str | None, limit: int) -> str:
  text = (text or "").strip()
  return text if len(text) <= limit else text[:limit] + "…"


def default_since() -> datetime:
  now = datetime.now().astimezone()
  return now.replace(hour=0, minute=0, second=0, microsecond=0)


def list_repos() -> list[dict[str, Any]]:
  repos = gh_json([
    "api",
    "--paginate",
    "--slurp",
    "/user/repos?affiliation=owner,collaborator,organization_member&sort=pushed&per_page=100",
  ])
  flat: list[dict[str, Any]] = []
  for page in repos:
    flat.extend(page)
  return [r for r in flat if not r.get("archived")]


def issue_state(item: dict[str, Any], pr: dict[str, Any] | None) -> str:
  if pr is not None:
    if pr.get("merged_at"):
      return "merged"
    if pr.get("state") == "closed":
      return "closed"
    return "draft" if pr.get("draft") else "open"
  return item.get("state", "open")


def comments_since(full_name: str, number: int, since_iso: str) -> list[dict[str, Any]]:
  raw = gh_json([
    "api",
    "--paginate",
    f"/repos/{full_name}/issues/{number}/comments?since={since_iso}&per_page=100",
  ])
  return [
    {
      "author": (c.get("user") or {}).get("login"),
      "created_at": c.get("created_at"),
      "body": truncate(c.get("body"), COMMENT_LIMIT),
    }
    for c in raw
  ]


def collect_issues_and_prs(full_name: str, since: datetime, until: datetime) -> list[dict[str, Any]]:
  since_iso = to_utc_iso(since)
  raw = gh_json([
    "api",
    "--paginate",
    f"/repos/{full_name}/issues?state=all&since={since_iso}&per_page=100&sort=updated&direction=desc",
  ])
  items: list[dict[str, Any]] = []
  for it in raw:
    updated = parse_time(it["updated_at"])
    if updated < since or updated > until:
      continue
    is_pr = "pull_request" in it
    pr = gh_json(["api", f"/repos/{full_name}/pulls/{it['number']}"]) if is_pr else None
    items.append({
      "repo": full_name,
      "type": "pull_request" if is_pr else "issue",
      "number": it["number"],
      "title": it.get("title"),
      "url": it.get("html_url"),
      "state": issue_state(it, pr),
      "author": (it.get("user") or {}).get("login"),
      "labels": [l.get("name") for l in it.get("labels") or []],
      "created_at": it.get("created_at"),
      "updated_at": it.get("updated_at"),
      "closed_at": it.get("closed_at"),
      "merged_at": pr.get("merged_at") if pr else None,
      "base": (pr.get("base") or {}).get("ref") if pr else None,
      "head": (pr.get("head") or {}).get("ref") if pr else None,
      "body": truncate(it.get("body"), BODY_LIMIT),
      "comments_since": comments_since(full_name, it["number"], since_iso),
    })
  return items


def collect_discussions(full_name: str, since: datetime, until: datetime) -> list[dict[str, Any]]:
  owner, name = full_name.split("/", 1)
  data = gh_json([
    "api", "graphql",
    "-f", f"query={DISCUSSIONS_QUERY}",
    "-F", f"owner={owner}",
    "-F", f"name={name}",
    "-F", f"first={DISCUSSIONS_PER_REPO}",
  ])
  nodes = (((data.get("data") or {}).get("repository") or {}).get("discussions") or {}).get("nodes") or []
  items: list[dict[str, Any]] = []
  for d in nodes:
    updated = parse_time(d["updatedAt"])
    if updated < since or updated > until:
      continue
    comments = [
      {
        "author": (c.get("author") or {}).get("login"),
        "created_at": c.get("createdAt"),
        "body": truncate(c.get("body"), COMMENT_LIMIT),
      }
      for c in (d.get("comments") or {}).get("nodes") or []
      if parse_time(c["createdAt"]) >= since
    ]
    items.append({
      "repo": full_name,
      "type": "discussion",
      "number": d["number"],
      "title": d.get("title"),
      "url": d.get("url"),
      "state": "answered" if d.get("isAnswered") else "open",
      "author": (d.get("author") or {}).get("login"),
      "labels": [(d.get("category") or {}).get("name")],
      "created_at": d.get("createdAt"),
      "updated_at": d.get("updatedAt"),
      "closed_at": None,
      "merged_at": None,
      "base": None,
      "head": None,
      "body": truncate(d.get("body"), BODY_LIMIT),
      "comments_since": comments,
    })
  return items


def collect_repo(repo: dict[str, Any], since: datetime, until: datetime) -> tuple[list[dict[str, Any]], list[str]]:
  full_name = repo["full_name"]
  items: list[dict[str, Any]] = []
  errors: list[str] = []
  try:
    items.extend(collect_issues_and_prs(full_name, since, until))
  except Exception as exc:
    errors.append(f"{full_name}: issues/prs: {exc}")
  if repo.get("has_discussions"):
    try:
      items.extend(collect_discussions(full_name, since, until))
    except Exception as exc:
      errors.append(f"{full_name}: discussions: {exc}")
  return items, errors


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--since", help="ISO datetime; default is today 00:00 in the local timezone")
  parser.add_argument("--until", help="ISO datetime; default is now")
  parser.add_argument("--workers", type=int, default=8)
  parser.add_argument("--out", help="write JSON here instead of stdout")
  args = parser.parse_args()

  since = datetime.fromisoformat(args.since).astimezone() if args.since else default_since()
  until = datetime.fromisoformat(args.until).astimezone() if args.until else datetime.now().astimezone()

  try:
    login = gh_json(["api", "/user"]).get("login")
  except Exception as exc:
    print(f"gh is not available or not authenticated: {exc}", file=sys.stderr)
    return 2

  repos = list_repos()
  items: list[dict[str, Any]] = []
  errors: list[str] = []
  with ThreadPoolExecutor(max_workers=args.workers) as pool:
    for repo_items, repo_errors in pool.map(lambda r: collect_repo(r, since, until), repos):
      items.extend(repo_items)
      errors.extend(repo_errors)

  items.sort(key=lambda i: (i["repo"], i["updated_at"]), reverse=False)
  summary = {
    "issue": sum(1 for i in items if i["type"] == "issue"),
    "pull_request_merged": sum(1 for i in items if i["type"] == "pull_request" and i["state"] == "merged"),
    "pull_request_open": sum(1 for i in items if i["type"] == "pull_request" and i["state"] == "open"),
    "pull_request_draft": sum(1 for i in items if i["type"] == "pull_request" and i["state"] == "draft"),
    "pull_request_closed": sum(1 for i in items if i["type"] == "pull_request" and i["state"] == "closed"),
    "discussion": sum(1 for i in items if i["type"] == "discussion"),
  }
  result = {
    "user": login,
    "range": {
      "since": since.isoformat(),
      "until": until.isoformat(),
      "timezone": since.tzname(),
    },
    "repos_scanned": len(repos),
    "repos_with_activity": sorted({i["repo"] for i in items}),
    "summary": summary,
    "items": items,
    "errors": errors,
  }
  text = json.dumps(result, ensure_ascii=False, indent=2)
  if args.out:
    with open(args.out, "w", encoding="utf-8") as fh:
      fh.write(text)
    print(f"wrote {args.out}: {len(items)} items from {len(repos)} repos", file=sys.stderr)
  else:
    print(text)
  return 0


if __name__ == "__main__":
  sys.exit(main())
