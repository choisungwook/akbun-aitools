#!/bin/bash
set -euo pipefail

# --- Parse input ---

parse_input() {
  INPUT=$(cat)
  TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
  CACHE_FILE="${TRANSCRIPT%.jsonl}-read-cache.json"
}

# --- Main ---

main() {
  parse_input
  rm -f "$CACHE_FILE"
}

main
