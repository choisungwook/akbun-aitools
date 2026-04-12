#!/bin/bash
set -eEuo pipefail

# --- Error trap ---
# Exit code 30 identifies pre-compact.sh as the source.

trap 'rc=$?; echo "[readonce/pre-compact.sh] unexpected failure at line $LINENO (rc=$rc, code=30)" >&2; exit 30' ERR

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
