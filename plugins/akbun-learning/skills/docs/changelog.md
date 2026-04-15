# Changelog

## 2026-04-16 #2

- `akbun-make-anki-japanese`: add `Kanji` field to the card template so the back of the card shows 한자 훈음 (예: `学: 배울 학 · 校: 학교 교`) directly below the Korean meaning whenever the front contains kanji.
- Bump Anki model id to 1730000002 to reflect the new field.

## 2026-04-12 #1

- Add `akbun-japan-textbook` skill: convert Japanese textbook screenshots and PDFs into an Anki `.apkg` deck for a Korean week-4 beginner (front: Japanese, back: hiragana reading + Korean meaning).
- Bundle `scripts/build_deck.py` which auto-bootstraps a venv with `genanki` at `~/.cache/akbun-japan-textbook/venv` and writes `~/Downloads/{timestamp}.apkg`.
- Include macOS Anki import + AnkiWeb sync walkthrough in the skill output.
