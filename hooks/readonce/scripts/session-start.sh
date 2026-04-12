#!/bin/bash
set -euo pipefail

# --- Parse input ---

parse_input() {
  INPUT=$(cat)
  SOURCE=$(echo "$INPUT" | jq -r '.source')
  TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
  CACHE_FILE="${TRANSCRIPT%.jsonl}-read-cache.json"
  CACHE_DIR=$(dirname "$CACHE_FILE")
}

# --- Cache management ---

delete_current_cache() {
  rm -f "$CACHE_FILE"
}

cleanup_old_caches() {
  find "$CACHE_DIR" -name "*-read-cache.json" -mtime +7 -delete 2>/dev/null
}

# --- Main ---

main() {
  parse_input

  case "$SOURCE" in
    clear)
      delete_current_cache
      ;;
    startup)
      cleanup_old_caches
      ;;
  esac
}

main
