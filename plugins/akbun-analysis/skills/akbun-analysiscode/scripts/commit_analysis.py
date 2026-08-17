#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from analysis_artifacts import render_drawio, render_html
from analysis_common import (
  load_json,
  normalize_analysis,
  project_paths,
  register_project,
  registry_analysis_paths,
  validate_analysis,
)


def write_candidate(path: Path, content: str) -> Path:
  candidate = path.with_name(f".{path.name}.candidate-{os.getpid()}")
  candidate.write_text(content, encoding="utf-8")
  return candidate


def carry_over_layout(normalized: dict, stored_path: Path, candidate_set_layout: bool) -> None:
  """candidate가 배치를 담고 있지 않으면 이미 저장된 드래그 위치를 잃지 않게 옮긴다.

  candidate가 layout 키를 직접 넣었으면 그 값을 그대로 존중한다. 빈 객체는 배치를
  지우겠다는 뜻이므로 저장된 값으로 되살리지 않는다.
  """
  if candidate_set_layout:
    return
  stored = load_json(stored_path) or {}
  layout = stored.get("layout")
  if not isinstance(layout, dict):
    return
  known = {component["id"] for component in normalized.get("components", []) if isinstance(component, dict)}
  carried = {
    view: {key: value for key, value in positions.items() if key in known}
    for view, positions in layout.items()
    if isinstance(positions, dict)
  }
  normalized["layout"] = {view: positions for view, positions in carried.items() if positions}


def file_receipt(path: Path) -> dict[str, object]:
  content = path.read_bytes()
  return {
    "path": str(path),
    "sha256": hashlib.sha256(content).hexdigest(),
    "bytes": len(content),
  }


def main() -> int:
  if len(sys.argv) != 3:
    print("usage: commit_analysis.py PROJECT_ROOT CANDIDATE_JSON", file=sys.stderr)
    return 2
  root = Path(sys.argv[1]).expanduser().resolve()
  candidate_path = Path(sys.argv[2]).expanduser().resolve()
  data = load_json(candidate_path)
  if not root.is_dir() or data is None:
    print(json.dumps({"ok": False, "error": "project root or candidate JSON is invalid"}))
    return 1
  register_project(root)
  paths = project_paths(root)
  normalized = normalize_analysis(data, root)
  carry_over_layout(normalized, paths["analysis"], "layout" in data)
  validation = validate_analysis(normalized, root)
  if not validation["ok"]:
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1

  bundle = [normalized]
  for path in registry_analysis_paths(paths["analysis"], normalized.get("related_project_ids", [])):
    related = load_json(path)
    if related is None:
      continue
    related_root = Path(related.get("project", {}).get("root_path", ""))
    related_validation = validate_analysis(related, related_root if related_root.is_dir() else None)
    if not related_validation["ok"]:
      print(json.dumps({"ok": False, "related_project": str(path), "validation": related_validation}, ensure_ascii=False, indent=2))
      return 1
    bundle.append(related)

  json_content = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
  html_content = render_html(bundle)
  drawio_content = render_drawio(bundle) if paths["drawio"].exists() else None
  staged: list[tuple[Path, Path]] = []
  try:
    staged.append((write_candidate(paths["html"], html_content), paths["html"]))
    if drawio_content is not None:
      staged.append((write_candidate(paths["drawio"], drawio_content), paths["drawio"]))
    staged.append((write_candidate(paths["analysis"], json_content), paths["analysis"]))
    for source, target in staged:
      os.replace(source, target)
  finally:
    for source, _ in staged:
      source.unlink(missing_ok=True)

  artifacts = {
    "analysis": file_receipt(paths["analysis"]),
    "html": file_receipt(paths["html"]),
    "drawio": file_receipt(paths["drawio"]) if paths["drawio"].exists() else None,
  }
  print(json.dumps({
    "ok": True,
    "validation": validation,
    "projects": [item["project"]["id"] for item in bundle],
    "artifacts": artifacts,
  }, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
