#!/usr/bin/env python3
"""Build an Anki .apkg from a JSON list of Japanese study cards.

Usage: python3 build_deck.py <cards.json> [--name "Deck name"]

Input JSON schema: a list of objects, each with:
  - japanese (str, required): front of card, original Japanese text
  - reading  (str, required): full hiragana reading of the line
  - meaning  (str, required): Korean meaning
  - kanji    (str, optional): kanji gloss line, e.g. "高: 높을 고 · 校: 학교 교"
  - tip      (str, optional): short pronunciation/grammar note

Output: ~/anki-jp-{YYYYMMDD-HHMMSS}.apkg (path is printed on success).
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

VENV_DIR = os.path.expanduser("~/.cache/akbun-make-anki-japanese/venv")


def _ensure_venv_and_reexec() -> None:
    """If genanki isn't importable, create a private venv, install it there, and re-exec."""
    try:
        import genanki  # noqa: F401
        return
    except ImportError:
        pass

    venv_python = os.path.join(VENV_DIR, "bin", "python")
    if not os.path.exists(venv_python):
        sys.stderr.write(f"creating venv at {VENV_DIR} ...\n")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "--quiet", "--upgrade", "pip"]
        )
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "--quiet", "genanki"]
        )

    os.execv(venv_python, [venv_python, os.path.abspath(__file__), *sys.argv[1:]])


_ensure_venv_and_reexec()
import genanki  # noqa: E402


MODEL_ID = 1730000003  # bumped when back-side TTS + darker meaning color added
DECK_ID_BASE = 1730000100

CARD_CSS = """
.card {
  font-family: -apple-system, "Hiragino Sans", "Noto Sans CJK JP", sans-serif;
  font-size: 26px;
  text-align: center;
  color: #222;
  background: #fffdf7;
  padding: 24px;
}
.jp { font-family: "Hiragino Mincho ProN", "Noto Serif CJK JP", serif; font-size: 42px; }
.reading { color: #0b6; font-size: 28px; margin-top: 10px; }
.meaning { color: #111; font-size: 28px; font-weight: 600; margin-top: 14px; }
.kanji { color: #a44; font-size: 20px; margin-top: 8px; }
.tip { color: #888; font-size: 18px; margin-top: 18px; font-style: italic; }
hr { border: none; border-top: 1px solid #ddd; margin: 18px 0; }
"""

FRONT_TMPL = (
    '<div class="jp">{{Japanese}}</div>'
    '<div class="tts">{{tts ja_JP voices=Apple_Kyoko,Apple_Otoya,Google_ja-JP:Japanese}}</div>'
)
BACK_TMPL = (
    '<div class="jp">{{Japanese}}</div>'
    '<div class="tts">{{tts ja_JP voices=Apple_Kyoko,Apple_Otoya,Google_ja-JP:Japanese}}</div>'
    "<hr>"
    '<div class="reading">{{Reading}}</div>'
    '<div class="meaning">{{Meaning}}</div>'
    "{{#Kanji}}"
    '<div class="kanji">🈶 {{Kanji}}</div>'
    "{{/Kanji}}"
    "{{#Tip}}"
    '<div class="tip">💡 {{Tip}}</div>'
    "{{/Tip}}"
)


def build_model() -> "genanki.Model":
    return genanki.Model(
        MODEL_ID,
        "Akbun Japanese",
        fields=[
            {"name": "Japanese"},
            {"name": "Reading"},
            {"name": "Meaning"},
            {"name": "Kanji"},
            {"name": "Tip"},
        ],
        templates=[
            {
                "name": "JP → Reading + Meaning",
                "qfmt": FRONT_TMPL,
                "afmt": BACK_TMPL,
            }
        ],
        css=CARD_CSS,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cards_json", help="Path to cards JSON file")
    parser.add_argument(
        "--name",
        default=None,
        help="Deck name (default: 'Akbun Japanese — YYYY-MM-DD')",
    )
    args = parser.parse_args()

    with open(args.cards_json, "r", encoding="utf-8") as f:
        cards = json.load(f)

    if not isinstance(cards, list) or not cards:
        sys.stderr.write("cards JSON must be a non-empty list\n")
        return 1

    now = dt.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    deck_name = args.name or f"Akbun Japanese — {now.strftime('%Y-%m-%d')}"
    deck_id = DECK_ID_BASE + int(now.strftime("%H%M%S"))

    model = build_model()
    deck = genanki.Deck(deck_id, deck_name)

    skipped = 0
    for idx, c in enumerate(cards):
        jp = (c.get("japanese") or "").strip()
        reading = (c.get("reading") or "").strip()
        meaning = (c.get("meaning") or "").strip()
        kanji = (c.get("kanji") or "").strip()
        tip = (c.get("tip") or "").strip()
        if not jp or not reading or not meaning:
            skipped += 1
            continue
        deck.add_note(
            genanki.Note(
                model=model,
                fields=[jp, reading, meaning, kanji, tip],
            )
        )

    if not deck.notes:
        sys.stderr.write("no valid cards to write\n")
        return 1

    out_path = os.path.expanduser(f"~/anki-jp-{timestamp}.apkg")
    genanki.Package(deck).write_to_file(out_path)

    print(f"wrote {len(deck.notes)} cards to {out_path}")
    if skipped:
        print(f"skipped {skipped} incomplete card(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
