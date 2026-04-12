#!/bin/bash
set -euo pipefail

# --- Disable via env var ---

[[ "${READ_ONCE_DISABLED:-0}" == "1" ]] && exit 0

# --- Parse input ---

parse_input() {
  INPUT=$(cat)
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')
  TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
  CWD=$(echo "$INPUT" | jq -r '.cwd')
  OFFSET=$(echo "$INPUT" | jq -r '.tool_input.offset // empty')
  LIMIT=$(echo "$INPUT" | jq -r '.tool_input.limit // empty')
  CACHE_FILE="${TRANSCRIPT%.jsonl}-read-cache.json"
  REL_PATH="${FILE_PATH#$CWD/}"
}

# --- File stat helpers ---

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

# --- Cache lookup ---

get_cached_value() {
  local key="$1"
  jq -r --arg p "$REL_PATH" ".[\$p].${key} // empty" "$CACHE_FILE" 2>/dev/null
}

# --- Cache update ---

update_cached_mtime() {
  local new_mtime="$1"
  jq --arg p "$REL_PATH" --argjson m "$new_mtime" \
    '.[$p].mtime = $m' "$CACHE_FILE" > "${CACHE_FILE}.tmp" \
    && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
}

# --- Block message ---

block_read() {
  local reason="$1"
  local mode="${READ_ONCE_MODE:-deny}"
  local file_size estimated_tokens
  file_size=$(wc -c < "$FILE_PATH" | tr -d ' ')
  estimated_tokens=$(( (file_size / 4) * 170 / 100 ))
  local message="파일 미변경 (${reason}): ${REL_PATH} (~${estimated_tokens} 토큰 절약) — 이전에 읽은 내용을 사용하세요. 컨텍스트에 내용이 없으면 다시 Read를 요청하세요."

  if [[ "$mode" == "warn" ]]; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"permissionDecisionReason\":\"${message}\"}}"
    exit 0
  else
    echo "$message" >&2
    exit 2
  fi
}

# --- Comparison logic ---

check_mtime() {
  local cached_mtime="$1"
  local current_mtime
  current_mtime=$(get_file_mtime)

  if [[ "$cached_mtime" == "$current_mtime" ]]; then
    block_read "mtime 동일"
  fi

  # mtime differs — verify with sha256 to catch touch-only changes
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

# --- Main ---

main() {
  parse_input

  # Always allow partial reads (offset/limit)
  [[ -n "$OFFSET" || -n "$LIMIT" ]] && exit 0

  # Allow if file does not exist (let Read handle the error)
  [[ ! -f "$FILE_PATH" ]] && exit 0

  # Allow if no cache file exists
  [[ ! -f "$CACHE_FILE" ]] && exit 0

  # Allow if file not in cache
  local cached_mtime
  cached_mtime=$(get_cached_value "mtime")
  [[ -z "$cached_mtime" ]] && exit 0

  # Compare mtime first, then sha256
  check_mtime "$cached_mtime"
}

main
