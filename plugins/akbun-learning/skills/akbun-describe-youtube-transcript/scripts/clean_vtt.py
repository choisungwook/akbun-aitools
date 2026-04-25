#!/usr/bin/env python3
# Clean a YouTube VTT into a flat, deduplicated transcript that fits in
# the model's Read budget.
#
# Why this exists: YouTube auto-captions emit "rolling" cues where each new
# cue repeats the tail of the previous cue plus a few new words, and they
# carry karaoke-style word-level timing tags like <00:00:15.440><c> hello</c>.
# Reading the raw VTT often blows past Claude's per-Read token limit.
#
# Output format (one line per cue, no blank lines):
#   [HH:MM:SS] new_text_only
import re
import sys
from pathlib import Path


def clean_vtt(src: Path, dst: Path) -> int:
    text = src.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
    text = re.sub(r"</?c[^>]*>", "", text)

    cues = []
    cue_pat = re.compile(
        r"(\d{2}:\d{2}:\d{2})\.\d+ --> \d{2}:\d{2}:\d{2}\.\d+[^\n]*\n((?:[^\n]+\n?)+)"
    )
    for m in cue_pat.finditer(text):
        ts = m.group(1)
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        body = body.replace("&gt;&gt;", ">>").replace("&amp;", "&").replace("&#39;", "'")
        if body:
            cues.append((ts, body))

    out_lines = []
    rolling = ""
    for ts, body in cues:
        if not rolling:
            out_lines.append(f"[{ts}] {body}")
            rolling = body
            continue
        # Find longest k where rolling ends with body[:k]; emit only body[k:].
        k_best = 0
        for k in range(min(len(body), len(rolling)), 0, -1):
            if rolling.endswith(body[:k]):
                k_best = k
                break
        new_tail = body[k_best:].lstrip()
        if new_tail and new_tail not in rolling[-200:]:
            out_lines.append(f"[{ts}] {new_tail}")
            rolling = (rolling + " " + new_tail).strip()

    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return len(out_lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: clean_vtt.py <input.vtt> <output.txt>", file=sys.stderr)
        sys.exit(2)
    n = clean_vtt(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"clean_vtt: wrote {n} cue lines to {sys.argv[2]}", file=sys.stderr)
