#!/usr/bin/env bash
set -euo pipefail

input_path="${1:-}"
format="${2:-png}"
output_path="${3:-}"

if [[ -z "$input_path" ]]; then
  echo "usage: export_drawio.sh <input.drawio> [png|svg|pdf|jpg] [output]" >&2
  exit 2
fi

if [[ ! -f "$input_path" ]]; then
  echo "input file not found: $input_path" >&2
  exit 2
fi

if [[ -z "$output_path" ]]; then
  output_path="${input_path}.${format}"
fi

find_drawio() {
  if [[ -n "${DRAWIO_CLI:-}" && -x "${DRAWIO_CLI:-}" ]]; then
    printf '%s\n' "$DRAWIO_CLI"
    return 0
  fi

  if command -v drawio >/dev/null 2>&1; then
    command -v drawio
    return 0
  fi

  if [[ -x "/Applications/draw.io.app/Contents/MacOS/draw.io" ]]; then
    printf '%s\n' "/Applications/draw.io.app/Contents/MacOS/draw.io"
    return 0
  fi

  return 1
}

drawio_cmd="$(find_drawio)" || {
  echo "draw.io CLI not found. Install draw.io Desktop or set DRAWIO_CLI." >&2
  exit 1
}

border="${DRAWIO_BORDER:-10}"

"$drawio_cmd" -x -f "$format" -e -b "$border" -o "$output_path" "$input_path"
printf '%s\n' "$output_path"
