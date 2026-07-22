#!/usr/bin/env bash
# Bootstrap yt-dlp inside a managed venv, then fetch an X (Twitter) post
# video's subtitles + metadata to a temp directory. X videos rarely expose
# subtitle tracks, so when none are found this script downloads the video's
# audio and transcribes it locally with faster-whisper.
# Prints JSON paths on stdout so the caller can read them with the Read tool.
#
# Usage: fetch_transcript.sh <X_POST_URL> [LANG_PRIORITY]
#   LANG_PRIORITY defaults to "ko,en,ja" (subtitle path only;
#   whisper auto-detects the spoken language)
set -euo pipefail

URL="${1:?X (Twitter) post URL is required}"
LANGS="${2:-ko,en,ja}"

case "$(uname -s 2>/dev/null || echo unknown)" in
  Linux*|Darwin*) TMP_BASE="/tmp" ;;
  MINGW*|MSYS*|CYGWIN*) TMP_BASE="${TEMP:-/tmp}" ;;
  *) TMP_BASE="${TMPDIR:-/tmp}" ;;
esac

WORKDIR="${TMP_BASE}/akbun-twitter-summary/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$WORKDIR"

VENV="$HOME/.cache/akbun-twitter-summary/venv"
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

# 1) Write metadata JSON (tweet text lives in "description"; uploader,
#    uploader_id, upload_date, duration are also present).
"$YTDLP" --skip-download --write-info-json --no-write-comments \
  -o "$WORKDIR/%(id)s.%(ext)s" "$URL" >/dev/null

INFO_JSON="$(ls "$WORKDIR"/*.info.json | head -n1)"

# 2) Try subtitle tracks first. Most X videos have none, but when a track
#    exists it is cheaper and more accurate than local transcription.
COMMON_FLAGS=(--retries 10 --retry-sleep linear=1::5 --sleep-subtitles 2)

"$YTDLP" --skip-download --write-subs --write-auto-subs --sub-langs "$LANGS" \
  --sub-format "vtt" "${COMMON_FLAGS[@]}" \
  -o "$WORKDIR/%(id)s.%(ext)s" "$URL" >/dev/null 2>&1 || true

# Pick the highest-priority language that actually downloaded.
SUB_FILE=""
IFS=',' read -ra LANG_ARR <<< "$LANGS"
for lang in "${LANG_ARR[@]}"; do
  match="$(ls "$WORKDIR"/*."$lang".vtt 2>/dev/null | head -n1 || true)"
  if [ -n "$match" ]; then SUB_FILE="$match"; break; fi
done
if [ -z "$SUB_FILE" ]; then
  SUB_FILE="$(ls "$WORKDIR"/*.vtt 2>/dev/null | head -n1 || true)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 3a) Subtitle path: dedupe cues + strip tags into a flat
#     "[HH:MM:SS] text" file the model should Read by default.
CLEANED=""
SOURCE="none"
if [ -n "$SUB_FILE" ]; then
  CLEANED="${SUB_FILE%.vtt}.cleaned.txt"
  if "$VENV/bin/python" "$SCRIPT_DIR/clean_vtt.py" "$SUB_FILE" "$CLEANED" 2>/dev/null; then
    SOURCE="subtitles"
  else
    CLEANED=""
  fi
fi

# 3b) Whisper fallback: download the smallest stream that carries audio
#     (X serves muxed mp4; there is usually no audio-only format) and
#     transcribe it locally. faster-whisper decodes mp4 directly via PyAV,
#     so ffmpeg is not required.
if [ -z "$CLEANED" ]; then
  if [ ! -f "$VENV/lib/installed-faster-whisper" ]; then
    "$VENV/bin/pip" install --quiet faster-whisper >/dev/null
    touch "$VENV/lib/installed-faster-whisper"
  fi

  "$YTDLP" -f "worstvideo*+bestaudio/best" -o "$WORKDIR/media.%(ext)s" \
    "${COMMON_FLAGS[@]}" "$URL" >/dev/null 2>&1 || \
  "$YTDLP" -f "best" -o "$WORKDIR/media.%(ext)s" \
    "${COMMON_FLAGS[@]}" "$URL" >/dev/null

  MEDIA_FILE="$(ls "$WORKDIR"/media.* 2>/dev/null | head -n1 || true)"
  if [ -n "$MEDIA_FILE" ]; then
    CLEANED="$WORKDIR/transcript.cleaned.txt"
    if "$VENV/bin/python" "$SCRIPT_DIR/transcribe_audio.py" \
      "$MEDIA_FILE" "$CLEANED" >&2; then
      SOURCE="whisper"
    else
      CLEANED=""
    fi
  fi
fi

printf '{"workdir":"%s","info_json":"%s","subtitles":"%s","cleaned":"%s","source":"%s"}\n' \
  "$WORKDIR" "$INFO_JSON" "${SUB_FILE:-}" "${CLEANED:-}" "$SOURCE"
