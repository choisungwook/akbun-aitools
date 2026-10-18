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
  parser = argparse.ArgumentParser(description="plugin manifest·SKILL.md frontmatter·README 목록 정합성 검사")
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
  print(f"plugin {plugins}개, skill {skills}개: manifest version·frontmatter·README 목록 정합성 확인")
  return 0


if __name__ == "__main__":
  sys.exit(main())
