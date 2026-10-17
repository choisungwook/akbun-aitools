#!/usr/bin/env bash
# mods/ 아래 Claude Code mod를 ~/.claude/mods/ 로 복사하고, 원하면 settings.json에 로드 경로를 등록한다.
# 사용법: mods/install.sh [--settings] [mod-name ...]
#   --settings  ~/.claude/settings.json 의 env.CLAUDE_CODE_PLUGIN_DIRS 에 복사한 경로를 합친다 (백업 생성).
#   mod-name    생략하면 mods/ 아래 모든 mod.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_MODS_DIR:-$HOME/.claude/mods}"
SETTINGS="$HOME/.claude/settings.json"
WRITE_SETTINGS=0
MODS=()

for arg in "$@"; do
  case "$arg" in
    --settings) WRITE_SETTINGS=1 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) MODS+=("$arg") ;;
  esac
done

if [ "${#MODS[@]}" -eq 0 ]; then
  for d in "$SRC"/*/; do
    [ -f "$d/.claude-plugin/plugin.json" ] && MODS+=("$(basename "$d")")
  done
fi

mkdir -p "$DEST"
INSTALLED=()
for mod in "${MODS[@]}"; do
  if [ ! -f "$SRC/$mod/.claude-plugin/plugin.json" ]; then
    echo "건너뜀: $mod (mods/$mod/.claude-plugin/plugin.json 없음)" >&2
    continue
  fi
  rm -rf "${DEST:?}/$mod"
  mkdir -p "$DEST/$mod"
  (cd "$SRC/$mod" && tar --exclude='.claude-plugin/types' --exclude='*.test.ts' -cf - .) | (cd "$DEST/$mod" && tar -xf -)
  INSTALLED+=("$DEST/$mod")
  echo "복사: $mod -> $DEST/$mod"
done

[ "${#INSTALLED[@]}" -eq 0 ] && { echo "설치한 mod가 없다." >&2; exit 1; }

JOINED="$(IFS=:; echo "${INSTALLED[*]}")"

if [ "$WRITE_SETTINGS" -eq 1 ]; then
  mkdir -p "$(dirname "$SETTINGS")"
  [ -f "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y%m%d%H%M%S)"
  SETTINGS="$SETTINGS" JOINED="$JOINED" python3 - <<'PY'
import json, os
path = os.environ["SETTINGS"]
new = os.environ["JOINED"].split(":")
data = json.load(open(path)) if os.path.exists(path) else {}
env = data.setdefault("env", {})
current = [p for p in env.get("CLAUDE_CODE_PLUGIN_DIRS", "").split(":") if p]
for p in new:
  if p not in current:
    current.append(p)
env["CLAUDE_CODE_PLUGIN_DIRS"] = ":".join(current)
json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
open(path, "a").write("\n")
print(f"등록: {path} env.CLAUDE_CODE_PLUGIN_DIRS = {env['CLAUDE_CODE_PLUGIN_DIRS']}")
PY
  echo "Claude Code를 다시 시작하면 mod가 로드된다."
else
  cat <<MSG

다음 중 하나로 로드한다.
  1) 이번 세션만:  claude $(for p in "${INSTALLED[@]}"; do printf -- '--plugin-dir %q ' "$p"; done)
  2) 항상:        mods/install.sh --settings   (settings.json env.CLAUDE_CODE_PLUGIN_DIRS 에 등록)
MSG
fi
