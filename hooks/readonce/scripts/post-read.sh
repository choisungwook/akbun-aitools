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

# --- Cache initialization ---

ensure_cache_file() {
  [[ ! -f "$CACHE_FILE" ]] && echo '{}' > "$CACHE_FILE"
}

# --- Cache write ---

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

# --- Main ---

main() {
  parse_input

  # Skip caching for partial reads (offset/limit)
  [[ -n "$OFFSET" || -n "$LIMIT" ]] && exit 0

  # Skip if file does not exist
  [[ ! -f "$FILE_PATH" ]] && exit 0

  ensure_cache_file
  write_cache
}

main
