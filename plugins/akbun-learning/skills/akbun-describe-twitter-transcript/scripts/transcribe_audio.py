#!/usr/bin/env python3
# Transcribe an X (Twitter) video's audio with faster-whisper into a flat
# "[HH:MM:SS] text" file, matching the format clean_vtt.py produces on the
# subtitle path so the SKILL workflow reads both the same way.
#
# faster-whisper decodes the input container (mp4/m4a) via PyAV, so no
# ffmpeg binary is needed. The "small" model balances accuracy and download
# size (~460MB, cached under ~/.cache/huggingface) for short social videos.
import sys
from pathlib import Path


def fmt_ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def transcribe(src: Path, dst: Path, model_size: str = "small") -> int:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(src), vad_filter=True)

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            lines.append(f"[{fmt_ts(seg.start)}] {text}")

    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"transcribe_audio: language={info.language} "
        f"(p={info.language_probability:.2f}), wrote {len(lines)} lines to {dst}",
        file=sys.stderr,
    )
    return len(lines)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("usage: transcribe_audio.py <input_media> <output.txt> [model_size]", file=sys.stderr)
        sys.exit(2)
    model_size = sys.argv[3] if len(sys.argv) == 4 else "small"
    n = transcribe(Path(sys.argv[1]), Path(sys.argv[2]), model_size)
    if n == 0:
        print("transcribe_audio: no speech detected", file=sys.stderr)
        sys.exit(1)
