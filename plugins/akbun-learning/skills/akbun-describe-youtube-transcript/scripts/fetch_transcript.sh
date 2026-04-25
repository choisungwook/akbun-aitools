#!/usr/bin/env bash
# Bootstrap yt-dlp inside a managed venv, then fetch a YouTube video's
# subtitles + metadata to a temp directory. Prints JSON paths on stdout
# so the caller can read them with the Read tool.
#
# Usage: fetch_transcript.sh <YOUTUBE_URL> [LANG_PRIORITY]
#   LANG_PRIORITY defaults to "ko,en,ja"
set -euo pipefail

URL="${1:?YouTube URL is required}"
LANGS="${2:-ko,en,ja}"

case "$(uname -s 2>/dev/null || echo unknown)" in
  Linux*|Darwin*) TMP_BASE="/tmp" ;;
  MINGW*|MSYS*|CYGWIN*) TMP_BASE="${TEMP:-/tmp}" ;;
  *) TMP_BASE="${TMPDIR:-/tmp}" ;;
esac

WORKDIR="${TMP_BASE}/akbun-youtube-summary/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$WORKDIR"

VENV="$HOME/.cache/akbun-youtube-summary/venv"
if [ ! -x "$VENV/bin/yt-dlp" ]; then
  PYBIN="$(command -v python3 || command -v python)"
  if [ -z "${PYBIN:-}" ]; then
    echo "python3 not found; install python first" >&2
    exit 1
  fi
  "$PYBIN" -m venv "$VENV" >/dev/null
  "$VENV/bin/pip" install --quiet --upgrade pip >/dev/null
  "$VENV/bin/pip" install --quiet yt-dlp >/dev/null
fi
YTDLP="$VENV/bin/yt-dlp"

# 1) Write metadata JSON (title, uploader, upload_date, chapters, categories, tags, language).
"$YTDLP" --skip-download --write-info-json --no-write-comments \
  -o "$WORKDIR/%(id)s.%(ext)s" "$URL" >/dev/null

INFO_JSON="$(ls "$WORKDIR"/*.info.json | head -n1)"

# 2) Try real subtitles first, then auto-generated, in the user's preferred languages.
#    Keep VTT and do NOT --convert-subs to SRT — yt-dlp's SRT converter
#    requires ffmpeg. VTT carries the same HH:MM:SS timestamps and the model
#    reads it just as well.
#
#    YouTube rate-limits auto-caption requests aggressively (HTTP 429), so we
#    pass --retries / --retry-sleep / --sleep-subtitles to ride out transient
#    429s. We also try each requested language one at a time on the auto-subs
#    pass so a single bad language does not abort the whole download.
COMMON_FLAGS=(--retries 10 --retry-sleep linear=1::5 --sleep-subtitles 2)

"$YTDLP" --skip-download --write-subs --sub-langs "$LANGS" \
  --sub-format "vtt" "${COMMON_FLAGS[@]}" \
  -o "$WORKDIR/%(id)s.%(ext)s" "$URL" >/dev/null 2>&1 || true

if ! ls "$WORKDIR"/*.vtt >/dev/null 2>&1; then
  IFS=',' read -ra TRY_LANGS <<< "$LANGS"
  for lang in "${TRY_LANGS[@]}"; do
    "$YTDLP" --skip-download --write-auto-subs --sub-langs "$lang" \
      --sub-format "vtt" "${COMMON_FLAGS[@]}" \
      -o "$WORKDIR/%(id)s.%(ext)s" "$URL" >/dev/null 2>&1 || true
    if ls "$WORKDIR"/*.vtt >/dev/null 2>&1; then break; fi
  done
fi

# Pick the highest-priority language that actually downloaded. $LANGS is a
# comma-separated priority list ("ko,en,ja"); honor that ordering rather
# than whatever filesystem `ls` returns first.
SUB_FILE=""
IFS=',' read -ra LANG_ARR <<< "$LANGS"
for lang in "${LANG_ARR[@]}"; do
  match="$(ls "$WORKDIR"/*."$lang".vtt 2>/dev/null | head -n1 || true)"
  if [ -n "$match" ]; then SUB_FILE="$match"; break; fi
done
if [ -z "$SUB_FILE" ]; then
  SUB_FILE="$(ls "$WORKDIR"/*.vtt 2>/dev/null | head -n1 || true)"
fi

# 3) Post-process: dedupe rolling cues + strip karaoke tags into a flat
#    "[HH:MM:SS] new_text" file. The raw VTT for a 10-minute video can be
#    >25k tokens and exceed Claude's per-Read budget; this cleaned file is
#    what the model should Read by default.
CLEANED=""
if [ -n "$SUB_FILE" ]; then
  CLEANED="${SUB_FILE%.vtt}.cleaned.txt"
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  "$VENV/bin/python" "$SCRIPT_DIR/clean_vtt.py" "$SUB_FILE" "$CLEANED" 2>/dev/null || CLEANED=""
fi

printf '{"workdir":"%s","info_json":"%s","subtitles":"%s","cleaned":"%s"}\n' \
  "$WORKDIR" "$INFO_JSON" "${SUB_FILE:-}" "${CLEANED:-}"
