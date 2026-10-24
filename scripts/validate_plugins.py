# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.3"]
# ///

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")
VERSION = re.compile(r"\d+\.\d+\.\d+")


def frontmatter(content):
  match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
  if not match:
    return None
  try:
    data = yaml.safe_load(match[1])
    if isinstance(data, dict):
      return data
  except yaml.YAMLError:
    pass
  lines = re.findall(r"^([A-Za-z][\w-]*):[ \t]*(.*)$", match[1], re.M)
  return {key: value.strip() for key, value in lines} or None


def manifest_versions(plugin):
  versions = []
  errors = []
  for rel in MANIFESTS:
    path = plugin / rel
    if not path.exists():
      errors.append(f"{plugin.name}: {rel} 없음")
      continue
    try:
      data = json.loads(path.read_text())
    except json.JSONDecodeError as error:
      errors.append(f"{plugin.name}: {rel} JSON 오류: {error}")
      continue
    versions.append(data.get("version"))
  if len(versions) == 2 and (versions[0] != versions[1] or not isinstance(versions[0], str) or not VERSION.fullmatch(versions[0])):
    errors.append(f"{plugin.name}: manifest 두 파일의 version이 다르거나 형식 오류 {versions}")
  return errors


def skill_errors(plugin, found):
  errors = []
  for skill in sorted((plugin / "skills").glob("*/SKILL.md")):
    rel = f"{plugin.name}/skills/{skill.parent.name}"
    found.add(rel)
    data = frontmatter(skill.read_text())
    if data is None:
      errors.append(f"{rel}: frontmatter 없음 또는 YAML 오류")
      continue
    if data.get("name") != skill.parent.name:
      errors.append(f"{rel}: frontmatter name이 디렉터리 이름과 다름 ({data.get('name')})")
  return errors


def plugin_errors(root):
  errors = []
  readme = (root / "README.md").read_text()
  _, marker, index = readme.partition("## plugin 목록")
  if not marker:
    errors.append("README.md: '## plugin 목록' 섹션 없음")
  listed = set(re.findall(r"plugins/([^/\s)]+/skills/[^/\s)]+)/", index))
  found = set()
  for plugin in sorted(path for path in (root / "plugins").iterdir() if path.is_dir()):
    errors.extend(manifest_versions(plugin))
    errors.extend(skill_errors(plugin, found))
  errors.extend(f"README.md: '## plugin 목록'에 없는 skill {rel}" for rel in sorted(found - listed))
  errors.extend(f"README.md: 존재하지 않는 skill 링크 {rel}" for rel in sorted(listed - found))
  errors.extend(table_errors(index))
  errors.extend(manual_errors(root, found))
  return errors


def table_errors(index):
  """plugin 목록의 skill 표: 머리줄은 '| skill | 이럴 때 쓰세요 |', 표는 plugin 절마다 하나, 행은 '때'로 끝난다."""
  errors = []
  headers = re.findall(r"^\|\s*skill\s*\|.*$", index, re.M | re.I)
  errors += [f"README.md: skill 표 머리줄은 '| skill | 이럴 때 쓰세요 |'여야 함 ('{h.strip()}')" for h in headers if h.strip() != "| skill | 이럴 때 쓰세요 |"]
  sections = len(re.findall(r"^### ", index, re.M))
  if len(headers) != sections:
    errors.append(f"README.md: plugin 절 {sections}개, skill 표 머리줄 {len(headers)}개")
  for name, text in re.findall(r"^\| \[([^\]]+)\]\(\./plugins/[^)]+\) \|([^|\n]*)\|\s*$", index, re.M):
    if not text.strip().endswith("때"):
      errors.append(f"README.md: {name} 행은 쓰면 좋은 상황을 '~할 때'로 끝내야 함 ('{text.strip()}')")
  return errors


def manual_errors(root, found):
  """docs/manual_draw.md가 akbun-draw의 skill을 빠짐없이, 없는 skill 없이 다루는지 본다."""
  manual = root / "docs/manual_draw.md"
  draw = {rel.split("/")[-1] for rel in found if rel.startswith("akbun-draw/")}
  if not manual.exists():
    return ["docs/manual_draw.md 없음"]
  linked = set(re.findall(r"plugins/akbun-draw/skills/([^/\s)]+)/", manual.read_text()))
  errors = [f"docs/manual_draw.md: 빠진 skill {name}" for name in sorted(draw - linked)]
  errors += [f"docs/manual_draw.md: 존재하지 않는 skill {name}" for name in sorted(linked - draw)]
  for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", manual.read_text()):
    if "://" not in target and not (manual.parent / target).exists():
      errors.append(f"docs/manual_draw.md: 깨진 링크 {target}")
  return errors


def parse_version(text):
  return tuple(int(part) for part in text.split("."))


def bump_errors(changed, base_versions, head_versions):
  errors = []
  for name in sorted(changed):
    base = base_versions.get(name)
    head = head_versions.get(name)
    if base is None or head is None or not VERSION.fullmatch(base) or not VERSION.fullmatch(head):
      continue
    major, minor, patch = parse_version(base)
    allowed = {(major, minor, patch + 1), (major, minor + 1, 0), (major + 1, 0, 0)}
    if parse_version(head) == (major, minor, patch):
      errors.append(f"{name}: plugin 파일이 바뀌었는데 version이 base와 같음 ({base})")
    elif parse_version(head) not in allowed:
      errors.append(f"{name}: version은 base에서 한 번만 올림 ({base} -> {head})")
  return errors


def git(root, *args):
  return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def plugins_in_paths(paths):
  names = set()
  for line in paths:
    parts = line.split("/")
    if len(parts) < 3 or parts[0] != "plugins":
      continue
    if "/".join(parts[2:]) in MANIFESTS:
      continue
    names.add(parts[1])
  return names


def changed_plugins(root, base):
  return plugins_in_paths(git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD").splitlines())


def version_at(root, ref, name):
  try:
    return json.loads(git(root, "show", f"{ref}:plugins/{name}/{MANIFESTS[0]}")).get("version")
  except (subprocess.CalledProcessError, json.JSONDecodeError):
    return None


def version_errors(root, base):
  changed = changed_plugins(root, base)
  base_versions = {name: version_at(root, base, name) for name in changed}
  head_versions = {name: version_at(root, "HEAD", name) for name in changed}
  return bump_errors(changed, base_versions, head_versions)


def main():
  parser = argparse.ArgumentParser(description="plugin manifest·SKILL.md frontmatter·README 목록·manual_draw 정합성 검사")
  parser.add_argument("--base", help="이 ref와 비교해 바뀐 plugin의 version 증가를 검사")
  args = parser.parse_args()
  errors = plugin_errors(ROOT)
  if args.base:
    errors.extend(version_errors(ROOT, args.base))
  if errors:
    print("\n".join(errors))
    return 1
  plugins = len([path for path in (ROOT / "plugins").iterdir() if path.is_dir()])
  skills = len(list((ROOT / "plugins").glob("*/skills/*/SKILL.md")))
  print(f"plugin {plugins}개, skill {skills}개: manifest version·frontmatter·README 목록·manual_draw 정합성 확인")
  return 0


if __name__ == "__main__":
  sys.exit(main())
