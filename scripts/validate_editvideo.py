# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.3"]
# ///

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "disable-model-invocation"}


def frontmatter_errors(content, directory_name):
  match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
  if not match:
    return ["YAML frontmatter 없음"]
  try:
    data = yaml.safe_load(match[1])
  except yaml.YAMLError as error:
    return [f"잘못된 YAML: {error}"]
  if not isinstance(data, dict):
    return ["frontmatter는 mapping이어야 함"]
  errors = []
  unknown = set(data) - ALLOWED_KEYS
  if unknown:
    errors.append(f"허용하지 않은 키: {sorted(map(str, unknown))}")
  name = data.get("name")
  if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
    errors.append("name 형식 오류")
  if name != directory_name:
    errors.append("name과 디렉터리 불일치")
  description = data.get("description")
  if not isinstance(description, str) or not description.strip() or len(description) > 1024 or any(c in description for c in "<>"):
    errors.append("description 형식 오류")
  if data.get("disable-model-invocation") is not True:
    errors.append("직접 호출 전용 boolean true 필요")
  return errors


def local_link_errors(path):
  errors = []
  for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text()):
    target = target.strip("<>")
    if urlsplit(target).scheme or target.startswith("#"):
      continue
    destination = unquote(target.split("#", 1)[0])
    if not (path.parent / destination).exists():
      errors.append(f"없는 링크: {target}")
  return errors


def indexed_skills(content):
  return set(re.findall(r"plugins/akbun-editvideo/skills/([^/\s)]+)/", content))


def repository_errors(root):
  plugin = root / "plugins/akbun-editvideo"
  files = sorted((plugin / "skills").glob("*/SKILL.md"))
  names = {path.parent.name for path in files}
  errors = []
  if not files:
    return ["영상 스킬 없음"]
  for path in files:
    errors.extend(f"{path.relative_to(root)}: {error}" for error in frontmatter_errors(path.read_text(), path.parent.name))
  for document in ("README.md", "docs/manual_editvideo.md"):
    indexed = indexed_skills((root / document).read_text())
    if indexed != names:
      errors.append(f"{document}: 목록 누락={sorted(names - indexed)}, 오래된 항목={sorted(indexed - names)}")
  documents = list((plugin / "skills").rglob("*.md"))
  documents += [root / name for name in ("README.md", "docs/manual_editvideo.md", "docs/terms_editvideo.md", "docs/README.md")]
  for path in documents:
    errors.extend(f"{path.relative_to(root)}: {error}" for error in local_link_errors(path))
  manifests = [json.loads((plugin / kind / "plugin.json").read_text()) for kind in (".claude-plugin", ".codex-plugin")]
  versions = [data.get("version") for data in manifests]
  if versions[0] != versions[1] or not isinstance(versions[0], str) or not re.fullmatch(r"\d+\.\d+\.\d+", versions[0]):
    errors.append(f"manifest 버전 오류: {versions}")
  prompts = manifests[1].get("interface", {}).get("defaultPrompt", [])
  if not isinstance(prompts, list) or not all(isinstance(prompt, str) for prompt in prompts):
    errors.append("defaultPrompt는 문자열 목록이어야 함")
    prompts = []
  called = set(re.findall(r"\(((?:akbun-|davinciresolve-)[a-z0-9-]+)\)", "\n".join(prompts)))
  required = {name for name in names if name.startswith("akbun-davinciresolve-look-")}
  required |= {"akbun-vlog-prepared-devtalk", "akbun-davinciresolve-cut-new-york"}
  if called - names or required - called:
    errors.append(f"prompt 오류: 없는 스킬={sorted(called - names)}, 새 스킬 예시 누락={sorted(required - called)}")
  agents = (root / "AGENTS.md").read_text()
  for document in ("docs/manual_editvideo.md", "docs/terms_editvideo.md"):
    if document not in agents:
      errors.append(f"AGENTS 문서 갱신 규칙 누락: {document}")
  return errors


def main():
  errors = repository_errors(ROOT)
  if errors:
    print("\n".join(errors))
    return 1
  count = len(list((ROOT / "plugins/akbun-editvideo/skills").glob("*/SKILL.md")))
  print(f"{count}개 스킬: frontmatter·README·매뉴얼·로컬 링크·manifest·prompt 정합성 확인")
  return 0


if __name__ == "__main__":
  sys.exit(main())
