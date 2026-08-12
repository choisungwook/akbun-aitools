#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from analysis_artifacts import render_html
from analysis_common import atomic_write_text, load_analysis_bundle, validate_analysis


def main() -> int:
  if len(sys.argv) != 3:
    print("usage: render_analysis.py ANALYSIS_JSON OUTPUT_HTML", file=sys.stderr)
    return 2
  source = Path(sys.argv[1]).expanduser().resolve()
  output = Path(sys.argv[2]).expanduser().resolve()
  try:
    bundle = load_analysis_bundle(source)
  except ValueError as error:
    print(json.dumps({"ok": False, "error": str(error)}))
    return 1
  for analysis in bundle:
    root = Path(analysis["project"]["root_path"])
    receipt = validate_analysis(analysis, root if root.is_dir() else None)
    if not receipt["ok"]:
      print(json.dumps(receipt, ensure_ascii=False, indent=2))
      return 1
  content = render_html(bundle)
  atomic_write_text(output, content)
  print(json.dumps({
    "ok": True,
    "output": str(output),
    "projects": [item["project"]["id"] for item in bundle],
    "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    "bytes": len(content.encode("utf-8")),
  }, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
