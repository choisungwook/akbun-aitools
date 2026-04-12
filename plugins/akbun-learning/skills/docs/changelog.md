# Changelog

## 2026-04-12 #1

- Add `akbun-japan-textbook` skill: convert Japanese textbook screenshots and PDFs into an Anki `.apkg` deck for a Korean week-4 beginner (front: Japanese, back: hiragana reading + Korean meaning).
- Bundle `scripts/build_deck.py` which auto-bootstraps a venv with `genanki` at `~/.cache/akbun-japan-textbook/venv` and writes `~/Downloads/{timestamp}.apkg`.
- Include macOS Anki import + AnkiWeb sync walkthrough in the skill output.
