# Changelog

## 2026-04-25 #4

- Add `akbun-describe-youtube-transcript` skill: download YouTube subtitles via `yt-dlp` (auto-bootstrapped venv at `~/.cache/akbun-youtube-summary/venv`) and produce a transcript-grounded Korean markdown report saved to `~/Downloads/{영상제목}.md` plus stdout. The goal is a faithful walkthrough of what the speaker says, not a short summary.
- Output structure: frontmatter (title/url/channel/categories/language/published) → 영상의 의도 (1~3문장) → 요약 (≤5문장, 방향잡이 용도) → 인사이트와 질문 10개 → 타임라인 (`[HH:MM:SS~HH:MM:SS] 주제` blocks, 본체).
- Use the creator's chapters when available; otherwise infer 4–8 sections. Strip 추임새/농담, keep speaker's words verbatim (translated to Korean).
- Bundle `scripts/clean_vtt.py` post-processor that strips karaoke `<00:00:15.440><c>...</c>` tags and merges YouTube auto-caption rolling duplicates into a flat `[HH:MM:SS] 발화` file. Keeps a 10-minute video well under the per-`Read` 25k-token budget. SKILL.md now reads the cleaned file by default and falls back to raw VTT only when the cleaner output is missing.
- SKILL.md fully rewritten in Korean; add rule that auto-caption transcription errors of proper nouns (e.g. `Adrien` → `Adria`) should be corrected against title/channel metadata when the metadata gives an unambiguous spelling.

## 2026-04-16 #3

- `akbun-make-anki-japanese`: play Japanese TTS on the back of the card too (previously only the front spoke).
- Darken and bold the Korean meaning (#111, 28px, weight 600) so 해석 is clearly readable.
- Bump Anki model id to 1730000003.

## 2026-04-16 #2

- `akbun-make-anki-japanese`: add `Kanji` field to the card template so the back of the card shows 한자 훈음 (예: `学: 배울 학 · 校: 학교 교`) directly below the Korean meaning whenever the front contains kanji.
- Bump Anki model id to 1730000002 to reflect the new field.

## 2026-04-12 #1

- Add `akbun-japan-textbook` skill: convert Japanese textbook screenshots and PDFs into an Anki `.apkg` deck for a Korean week-4 beginner (front: Japanese, back: hiragana reading + Korean meaning).
- Bundle `scripts/build_deck.py` which auto-bootstraps a venv with `genanki` at `~/.cache/akbun-japan-textbook/venv` and writes `~/Downloads/{timestamp}.apkg`.
- Include macOS Anki import + AnkiWeb sync walkthrough in the skill output.
