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

# --- 캐시 조회 ---

get_cached_value() {
  local key="$1"
  jq -r --arg p "$REL_PATH" ".[\$p].${key} // empty" "$CACHE_FILE" 2>/dev/null
}

# --- 캐시 업데이트 ---

update_cached_mtime() {
  local new_mtime="$1"
  jq --arg p "$REL_PATH" --argjson m "$new_mtime" \
    '.[$p].mtime = $m' "$CACHE_FILE" > "${CACHE_FILE}.tmp" \
    && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
}

# --- 차단 메시지 ---

block_read() {
  local reason="$1"
  echo "파일 미변경 (${reason}): ${REL_PATH} — 이전에 읽은 내용을 사용하세요. 컨텍스트에 내용이 없으면 다시 Read를 요청하세요." >&2
  exit 2
}

# --- 비교 로직 ---

check_mtime() {
  local cached_mtime="$1"
  local current_mtime
  current_mtime=$(get_file_mtime)

  if [[ "$cached_mtime" == "$current_mtime" ]]; then
    block_read "mtime 동일"
  fi

  # mtime이 다르면 sha256으로 한 번 더 확인
  check_sha256 "$current_mtime"
}

check_sha256() {
  local current_mtime="$1"
  local cached_sha
  local current_sha

  cached_sha=$(get_cached_value "sha256")
  current_sha=$(get_file_sha256)

  if [[ "$cached_sha" == "$current_sha" ]]; then
    update_cached_mtime "$current_mtime"
    block_read "hash 동일"
  fi
}

# --- 메인 ---

main() {
  parse_input

  # 파일이 없으면 Read 허용 (Read가 에러 처리)
  [[ ! -f "$FILE_PATH" ]] && exit 0

  # 캐시 파일 없으면 허용
  [[ ! -f "$CACHE_FILE" ]] && exit 0

  # 캐시에 없으면 허용
  local cached_mtime
  cached_mtime=$(get_cached_value "mtime")
  [[ -z "$cached_mtime" ]] && exit 0

  # mtime → sha256 순서로 비교
  check_mtime "$cached_mtime"
}

main
