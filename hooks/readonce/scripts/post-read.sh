#!/bin/bash
set -euo pipefail

# --- 입력 파싱 ---

parse_input() {
  INPUT=$(cat)
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')
  TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
  CWD=$(echo "$INPUT" | jq -r '.cwd')
  CACHE_FILE="${TRANSCRIPT%.jsonl}-read-cache.json"
  REL_PATH="${FILE_PATH#$CWD/}"
}

# --- 파일 상태 조회 ---

get_file_mtime() {
  if [[ "$(uname)" == "Darwin" ]]; then
    stat -f %m "$FILE_PATH"
  else
    stat -c %Y "$FILE_PATH"
  fi
}

get_file_sha256() {
  shasum -a 256 "$FILE_PATH" | cut -d' ' -f1
}

# --- 캐시 초기화 ---

ensure_cache_file() {
  [[ ! -f "$CACHE_FILE" ]] && echo '{}' > "$CACHE_FILE"
}

# --- 캐시 기록 ---

write_cache() {
  local mtime sha256
  mtime=$(get_file_mtime)
  sha256=$(get_file_sha256)

  jq --arg p "$REL_PATH" \
     --argjson m "$mtime" \
     --arg s "$sha256" \
     '.[$p] = {sha256: $s, mtime: $m}' "$CACHE_FILE" > "${CACHE_FILE}.tmp" \
    && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
}

# --- 메인 ---

main() {
  parse_input

  # 파일이 없으면 무시
  [[ ! -f "$FILE_PATH" ]] && exit 0

  ensure_cache_file
  write_cache
}

main
