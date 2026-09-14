#!/usr/bin/env python3
"""Validate a readwise-daily-pulse mail body before the Gmail draft is created.

Exit 0 when every check passes, 1 with one message per failure, 2 on a usage error.
"""
from __future__ import annotations

import re
import sys

CHANGELOG_TYPES = ("new feature", "update", "hotfix", "bugfix", "security fix", "deprecation", "pricing", "region", "release")
SECTIONS = ("## changelog", "## 읽을 것", "## 나머지")
FIRST_LINE = re.compile(r"^변경사항 \d+건 · 읽을 것 \d+건 · 나머지 \d+건 \(저장 \d+ · RSS \d+\) · 하이라이트 \d+개$")
NUMBERED = re.compile(r"^(\d+)\. ")
TYPE_SUFFIX = re.compile(r" \((" + "|".join(re.escape(t) for t in CHANGELOG_TYPES) + r")\)$")
URL_ONLY = re.compile(r"https?://\S+")


def check(lines: list[str]) -> list[str]:
  failures: list[str] = []
  if not lines:
    return ["body is empty"]
  if lines[0].strip() == "어제 들어온 항목 없음":
    return failures
  if not FIRST_LINE.match(lines[0].strip()):
    failures.append("line 1: expected '변경사항 N건 · 읽을 것 N건 · 나머지 N건 (저장 N · RSS N) · 하이라이트 N개'")

  for number, line in enumerate(lines, 1):
    if "`" in line:
      failures.append(f"line {number}: backtick")
    if "http://" in line or "https://" in line:
      if not URL_ONLY.fullmatch(line.strip()):
        failures.append(f"line {number}: URL must stand alone on its own line")
      continue

  positions = {section: [i for i, line in enumerate(lines) if line.strip() == section] for section in SECTIONS}
  for section, found in positions.items():
    if len(found) > 1:
      failures.append(f"{section} appears {len(found)} times")
  present = [(positions[s][0], s) for s in SECTIONS if positions[s]]
  if [s for _, s in sorted(present)] != [s for _, s in present]:
    failures.append("sections out of order; expected ## changelog → ## 읽을 것 → ## 나머지")

  current = None
  expected = 1
  for number, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped in SECTIONS:
      current = stripped
      continue
    match = NUMBERED.match(stripped)
    if not match:
      continue
    if int(match.group(1)) != expected:
      failures.append(f"line {number}: expected item number {expected}, got {match.group(1)}")
    expected = int(match.group(1)) + 1
    has_type = bool(TYPE_SUFFIX.search(stripped))
    if current == "## changelog" and not has_type:
      failures.append(f"line {number}: changelog item lacks a type suffix such as (update)")
    if current == "## changelog" and not stripped[len(match.group(0)):].startswith("▶ "):
      failures.append(f"line {number}: changelog item must start with ▶")
    if current == "## 나머지" and has_type:
      failures.append(f"line {number}: typed changelog item placed under ## 나머지")
  return failures


def main() -> int:
  if len(sys.argv) != 2:
    print("usage: check_draft.py <body-file>", file=sys.stderr)
    return 2
  with open(sys.argv[1], encoding="utf-8") as handle:
    lines = handle.read().splitlines()
  failures = check(lines)
  for failure in failures:
    print(failure)
  print("PASS" if not failures else f"FAIL ({len(failures)})")
  return 1 if failures else 0


if __name__ == "__main__":
  sys.exit(main())
