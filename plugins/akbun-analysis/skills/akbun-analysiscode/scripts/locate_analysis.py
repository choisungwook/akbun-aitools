#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from analysis_common import analysis_status


def main() -> int:
  root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser().resolve()
  if not root.is_dir():
    print(json.dumps({"error": f"project root not found: {root}"}), file=sys.stderr)
    return 1
  print(json.dumps(analysis_status(root), ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
