#!/usr/bin/env python3
"""Locate or create the akbun-analysis knowledge store for one project.

Idempotent — run it at the start of every akbun-analysiscode session:

    python3 init_store.py [PROJECT_ROOT]

and once more when an analysis (or incremental update) is finished:

    python3 init_store.py [PROJECT_ROOT] --mark-analyzed

Resolves the OS-standard store root ($AKBUN_ANALYSIS_HOME override first),
derives a stable project id from the git remote (or absolute path), creates
the directory layout and SQLite schema if missing, registers the project in
projects.json, and prints resolved paths plus freshness info as JSON.
--mark-analyzed additionally records the current HEAD, timestamp, and store
counts in meta.json and syncs the registry.

Standard library only. Never deletes existing analysis data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

DDL = """
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nodes (
  name      TEXT PRIMARY KEY,
  kind      TEXT NOT NULL,
  role      TEXT,
  path      TEXT,
  wiki_page TEXT
);

CREATE TABLE IF NOT EXISTS edges (
  source         TEXT NOT NULL,
  target         TEXT NOT NULL,
  kind           TEXT NOT NULL,
  detail         TEXT,
  evidence       TEXT,
  target_project TEXT NOT NULL DEFAULT '',
  UNIQUE (source, target, kind, target_project)
);

CREATE TABLE IF NOT EXISTS files (
  path TEXT NOT NULL,
  node TEXT NOT NULL,
  PRIMARY KEY (path, node)
);
"""


def store_root() -> Path:
    override = os.environ.get("AKBUN_ANALYSIS_HOME")
    if override:
        return Path(override).expanduser()
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "akbun-analysis"
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / "akbun-analysis"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"
    return base / "akbun-analysis"


def run_git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else None


def project_identity(root: Path) -> tuple[str, str, str | None]:
    """Return (project_id, name, remote). Stable across machines for the same remote."""
    remote = run_git(root, "remote", "get-url", "origin")
    seed = remote or str(root)
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]
    name = root.name
    if remote:
        tail = remote.rstrip("/").rsplit("/", 1)[-1]
        tail = tail[:-4] if tail.endswith(".git") else tail
        name = tail or name
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.").lower() or "project"
    return f"{slug}-{digest}", slug, remote


def ensure_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(DDL)
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        conn.commit()
    finally:
        conn.close()


def store_counts(db_path: Path, wiki_dir: Path) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("nodes", "edges", "files")
        }
    finally:
        conn.close()
    counts["wiki_pages"] = len(list(wiki_dir.rglob("*.md")))
    return counts


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Locate or create the akbun-analysis knowledge store")
    parser.add_argument("project_root", nargs="?", default=".", help="project root (default: cwd)")
    parser.add_argument(
        "--mark-analyzed",
        action="store_true",
        help="record current HEAD, timestamp, and store counts as the completed analysis",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        print(json.dumps({"error": f"project root not found: {project_root}"}), file=sys.stderr)
        return 1

    project_id, name, remote = project_identity(project_root)
    root = store_root()
    project_dir = root / "projects" / project_id
    wiki_dir = project_dir / "wiki"
    created = not project_dir.exists()
    for sub in (wiki_dir / "services", wiki_dir / "decisions"):
        sub.mkdir(parents=True, exist_ok=True)

    db_path = project_dir / "graph.sqlite"
    ensure_db(db_path)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    head = run_git(project_root, "rev-parse", "HEAD")

    meta_path = project_dir / "meta.json"
    meta = load_json(meta_path) or {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "name": name,
        "analyzed_commit": None,
        "analyzed_at": None,
        "counts": {},
    }
    meta["root_path"] = str(project_root)
    meta["remote"] = remote
    if args.mark_analyzed:
        meta["analyzed_commit"] = head
        meta["analyzed_at"] = now
        meta["counts"] = store_counts(db_path, wiki_dir)
    write_json(meta_path, meta)

    registry_path = root / "projects.json"
    registry = load_json(registry_path) or {"schema_version": SCHEMA_VERSION, "projects": []}
    projects = registry.setdefault("projects", [])
    entry = next((p for p in projects if p.get("project_id") == project_id), None)
    if entry is None:
        entry = {"project_id": project_id, "registered_at": now}
        projects.append(entry)
    entry.update(
        {
            "name": name,
            "root_path": str(project_root),
            "remote": remote,
            "last_analyzed_at": meta.get("analyzed_at"),
        }
    )
    write_json(registry_path, registry)

    analyzed = meta.get("analyzed_commit")
    stale = (analyzed != head) if (head and analyzed) else None

    print(
        json.dumps(
            {
                "store_root": str(root),
                "project_id": project_id,
                "project_dir": str(project_dir),
                "db": str(db_path),
                "wiki_dir": str(wiki_dir),
                "meta": str(meta_path),
                "projects_registry": str(registry_path),
                "created": created,
                "marked_analyzed": args.mark_analyzed,
                "analyzed_commit": analyzed,
                "head_commit": head,
                "stale": stale,
                "counts": meta.get("counts", {}),
                "other_projects": [
                    p.get("project_id") for p in projects if p.get("project_id") != project_id
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
