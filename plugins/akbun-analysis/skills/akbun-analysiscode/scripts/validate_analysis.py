#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from analysis_common import load_json, validate_analysis


def main() -> int:
  if len(sys.argv) not in {2, 3}:
    print("usage: validate_analysis.py ANALYSIS_JSON [PROJECT_ROOT]", file=sys.stderr)
    return 2
  path = Path(sys.argv[1]).expanduser().resolve()
  data = load_json(path)
  if data is None:
    receipt = {"ok": False, "errors": [{"subject": "$", "message": f"invalid JSON: {path}"}], "warnings": []}
  else:
    root = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) == 3 else Path(data.get("project", {}).get("root_path", ""))
    receipt = validate_analysis(data, root if root.is_dir() else None)
  print(json.dumps(receipt, ensure_ascii=False, indent=2))
  return 0 if receipt["ok"] else 1


if __name__ == "__main__":
  raise SystemExit(main())
