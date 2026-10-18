# /// script
# requires-python = ">=3.12"
# ///

import argparse
import os
import re
import sys
from pathlib import Path


HIGH_RISK = ("AGENTS.md", "CLAUDE.md", ".github/", ".claude/", ".claude-plugin/", ".agents/", "scripts/")
MEDIUM_RISK = ("plugins/",)
MAX_LINES = 40


def risk_tier(files):
  high = [path for path in files if path.startswith(HIGH_RISK)]
  if high:
    return "높음", high
  medium = [path for path in files if path.startswith(MEDIUM_RISK)]
  if medium:
    return "중간", medium
  return "낮음", []


def sections(body):
  text = re.sub(r"<!--.*?-->", "", body, flags=re.S)
  result = {}
  current = None
  for line in text.splitlines():
    heading = re.fullmatch(r"#\s+(\S+)\s*", line)
    if heading:
      current = heading[1]
      result.setdefault(current, [])
      continue
    if current is not None and line.strip() and not line.startswith("Closes #"):
      result[current].append(line.strip())
  return result, text


def prose_lines(text):
  inside = False
  for line in text.splitlines():
    if line.startswith("```"):
      inside = not inside
      continue
    if not inside:
      yield line


def table_rows(lines):
  rows = [line for line in lines if line.startswith("|") and line.count("|") >= 4]
  separators = [line for line in rows if re.fullmatch(r"[\s|:-]+", line)]
  return len(rows) - len(separators) - 1


def body_errors(body, tier):
  found, text = sections(body)
  errors = []
  if not found.get("구현"):
    errors.append("# 구현: 무엇이 달라지는지 한 줄 필요")
  if table_rows(found.get("검증", [])) < 1:
    errors.append("# 검증: '| 대상 | 방법 | 결과 |' 표에 실제로 돌린 것 한 줄 이상 필요")
  if not re.search(r"Closes #\d+", text):
    errors.append("Closes #<issue 번호> 필요")
  structure = found.get("구조", [])
  if tier != "낮음" and not any(line.startswith("```mermaid") for line in structure):
    errors.append(f"등급 {tier}: # 구조에 바뀐 것의 위치를 그린 mermaid 코드블록 필요")
  risk = found.get("리스크", [])
  declared = next((re.match(r"등급:\s*(\S+)", line)[1] for line in risk if re.match(r"등급:\s*(\S+)", line)), None)
  if declared and declared != tier:
    errors.append(f"# 리스크: 등급은 바뀐 경로가 정함. 선언 {declared}, 계산 {tier}")
  if tier != "낮음":
    if declared is None:
      errors.append(f"# 리스크: 첫 줄 '등급: {tier}' 필요")
    if len(risk) < 2:
      errors.append("# 리스크: 등급 줄 아래에 자동 검사와 리뷰가 못 보는 것 한 줄 필요")
  lines = [line for line in prose_lines(text) if line.strip()]
  if len(lines) > MAX_LINES:
    errors.append(f"PR 본문 {len(lines)}줄: {MAX_LINES}줄 이내")
  return errors


def summary(tier, reasons):
  lines = [f"리스크 등급: {tier}"]
  lines.extend(f"- {path}" for path in reasons[:10])
  return "\n".join(lines)


def main():
  parser = argparse.ArgumentParser(description="PR 본문 구조와 리스크 등급 검사")
  parser.add_argument("--files", required=True, help="바뀐 파일 경로 목록 파일 (줄마다 하나)")
  parser.add_argument("--body-file", help="PR 본문 파일. 없으면 환경변수 PR_BODY")
  args = parser.parse_args()
  files = [line.strip() for line in Path(args.files).read_text().splitlines() if line.strip()]
  body = Path(args.body_file).read_text() if args.body_file else os.environ.get("PR_BODY", "")
  tier, reasons = risk_tier(files)
  errors = body_errors(body, tier)
  report = summary(tier, reasons)
  print(report)
  step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
  if step_summary:
    with open(step_summary, "a") as handle:
      handle.write(report + "\n")
  if errors:
    print("\n".join(errors))
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
