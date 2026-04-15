---
name: akbun-make-anki-japanese
description: "Convert photos or PDFs of Japanese words and sentences into an Anki deck (.apkg) for a Korean beginner learner. Takes one or more screenshot images and/or a PDF containing Japanese vocabulary or example sentences, extracts each item, and generates an Anki package where the front shows the Japanese (kanji/kana) with built-in Anki TTS audio and the back shows hiragana reading + Korean meaning. Saves the deck to ~/anki-jp-{timestamp}.apkg. Trigger on: '일본어 사진', '일본어 스크린샷', '일본어 pdf', '일본어 단어', '일본어 문장', 'anki 만들어', '앙키 덱', '일본어 단어장', 'japanese photo to anki', 'japanese screenshot to anki', 'japanese pdf to anki', or any request to turn photos/PDFs of Japanese words or sentences into an Anki import file. Use this skill whenever the user provides Japanese images or PDFs and wants flashcards — even if they don't explicitly say 'Anki'."
---

# Akbun Make Anki (Japanese)

The learner is a Korean beginner in week 4 of studying Japanese. They can barely read hiragana and cannot yet read kanji or katakana fluently. Every card must give them a reading aid, spoken audio, and a Korean meaning on the back.

## Purpose

Turn **photos (screenshots) or PDF files containing Japanese words or sentences** into an Anki deck. The source is whatever the user attaches — a vocab list snapshot, a page of example sentences, a handwritten note photo, a PDF export, etc. This skill is *not* limited to formal textbooks; any image or PDF with Japanese text is valid input.

## What this skill does

1. Read Japanese text from every attached image and/or every page of the PDF.
2. Extract each learnable unit (one card per word or per sentence).
3. Build an Anki deck where:
   - **Front** = the original Japanese exactly as printed (kanji + kana intact) **plus Anki TTS audio** of that Japanese so the learner hears it the moment the card flips up.
   - **Back** = hiragana reading (furigana for the whole line) + Korean 발음 approximation + Korean meaning + optional short tip.
4. Package the deck as `.apkg` and save it to `~/anki-jp-{YYYYMMDD-HHMMSS}.apkg`.
5. Tell the user how to import it into Anki for macOS and sync to AnkiWeb.

## Step 1 — Read the source material

The user may attach **multiple screenshot images**, **a PDF file**, or a mix of both. Handle all of it in one pass.

**If the input is images:** Use the Read tool on each image path the user provided. Read every single one — do not skip any.

**If the input is a PDF:** Use the Read tool with the `pages` parameter to read the PDF. PDFs over 10 pages must be read in chunks of at most 20 pages per call (e.g. `pages: "1-20"`, then `"21-40"`, etc.). For each chunk, extract items before moving to the next chunk so nothing is lost between calls. If the PDF is short (≤10 pages), read it in one call without the `pages` parameter.

**If the input mixes images and PDFs:** Process the PDF first (it is usually the bulk of the material), then the loose screenshots, then merge everything into a single cards list in the order the user gave them.

For every page/image:

- Transcribe the Japanese text as it appears, preserving kanji and katakana.
- If furigana is already printed above a kanji, record that reading — don't re-guess it.
- If a page shows a vocabulary list with Korean/English glosses, capture those glosses; they're more reliable than your own translation.
- If a page shows example sentences, capture each sentence as its own item.

Silently fix obvious OCR-style ambiguities (e.g., `ロ` vs `口`, `一` vs `ー`) using context. If something is genuinely unreadable (glare, cropped), skip it and note the count of skipped items at the end.

**Granularity rule** — one card per learnable unit:

- Vocabulary images → one card per vocabulary entry.
- Sentence images → one card per full sentence (not per word inside the sentence).
- If a page mixes both, produce both kinds of cards.

## Step 2 — Build each card

For every extracted item, prepare three fields:

| Field | Content |
|---:|:---|
| `japanese` | Original Japanese, kanji + kana as printed. This is what Anki TTS will speak on the front of the card. |
| `reading` | The entire line rewritten in hiragana only, followed by ` · ` and the Korean approximation pronunciation (한국어 발음). Example: `たかい · 타카이`, `がっこうはちかいですか · 각코-와 치카이데스카`. Use `-` for long vowels (장음: `おお`, `おう`, `えい` → `오-`, `에-`), keep particle `は` as `와`, `へ` as `에`, `を` as `오`, and drop the devoiced vowel of `です` (`데스`). |
| `meaning` | Korean meaning. Short and natural, not word-for-word. For sentences, give a clean Korean sentence. For single words, give the Korean word plus a part-of-speech hint only when it helps (e.g., `먹다 (동사)`). |

Optionally, append a one-line `tip` (prefixed with `💡`) when there's a genuine pronunciation trap (촉음, 장음, `は`→wa, devoiced `です`, etc.). Do not invent tips for every card.

## Step 3 — Generate the .apkg

Use the bundled script `scripts/build_deck.py`. It takes a JSON file of cards and writes the `.apkg` to `~/anki-jp-{timestamp}.apkg`. The card template has Anki TTS wired into the front, so no extra audio files need to be generated — Anki speaks the `Japanese` field on the user's device using the system Japanese voice.

Workflow:

1. Write the extracted cards to a temp JSON file, e.g. `/tmp/japan_cards.json`, as an array of `{japanese, reading, meaning}` objects (include `tip` only when present).
2. Run the build script:

    ```bash
    python3 scripts/build_deck.py /tmp/japan_cards.json
    ```

3. The script prints the output path. Confirm it to the user.

The script uses [`genanki`](https://github.com/kerrickstaley/genanki) and bootstraps its own virtualenv at `~/.cache/akbun-make-anki-japanese/venv` on first run, so the user does not need to install anything globally. Do not silently fall back to a `.txt` file — the user asked for a proper Anki package.

The deck name is `Akbun Japanese — {YYYY-MM-DD}`. The front shows the Japanese in a large serif font and plays Anki TTS automatically; the back shows reading (hiragana · 한국어 발음) on one line and Korean meaning on the next line, with the tip (if any) in a smaller muted style.

### Anki TTS requirement

Anki's built-in TTS needs a Japanese voice installed on the playback device:

- **macOS / iOS**: System Settings → Accessibility → Spoken Content → System Voice → add a Japanese voice (e.g., Kyoko, Otoya).
- **Android (AnkiDroid)**: Install Google 텍스트 음성 변환 and add a Japanese language pack.
- **AnkiWeb (browser)**: Uses the browser's speech synthesis; modern Chrome/Safari already include a Japanese voice.

Mention this requirement to the user once, after generating the deck, so they know why audio might be silent on a fresh device.

## Step 4 — Tell the user how to import and sync

After the file is written, print these instructions verbatim in Korean (adjust the filename to match what was actually generated):

```
✅ Anki 덱이 생성되었습니다: ~/anki-jp-{timestamp}.apkg

📥 Anki (macOS)에 import하기
1. Anki를 실행합니다. (없다면 https://apps.ankiweb.net 에서 설치)
2. 메뉴에서 파일 → 가져오기(File → Import) 를 선택합니다.
3. ~/anki-jp-{timestamp}.apkg 를 선택하고 열기.
4. "가져오기 완료" 메시지가 뜨면 좌측 덱 목록에 "Akbun Japanese — {날짜}" 가 보입니다.

🔊 TTS(음성) 안내
- 카드 앞면이 뜨면 Anki가 일본어 TTS로 읽어줍니다.
- macOS: 시스템 설정 → 손쉬운 사용 → 말하기(Spoken Content) → 시스템 음성에서 일본어 음성(Kyoko, Otoya 등) 추가.
- AnkiDroid: Google 텍스트 음성 변환에서 일본어 언어 팩 설치.

☁️  AnkiWeb으로 동기화하기
1. 처음이라면 https://ankiweb.net 에서 무료 계정을 만듭니다.
2. Anki 메인 화면 우측 상단의 "동기화(Sync)" 버튼을 클릭합니다. (단축키: F5 또는 Cmd+Shift+Y)
3. 처음 로그인할 때만 AnkiWeb 이메일/비밀번호를 입력합니다.
4. "업로드 / 다운로드" 를 묻는 창이 뜨면 "업로드(Upload to AnkiWeb)" 를 선택합니다. (처음 동기화일 때만)
5. 이후에는 동기화 버튼만 누르면 자동으로 양방향 동기화됩니다.

📱 AnkiMobile / AnkiDroid 에서도 같은 계정으로 로그인 후 동기화하면 동일한 덱을 바로 사용할 수 있습니다.
```

## Study Guide Mode (공부 가이드 생성)

When the user asks for a study guide, learning plan, or "공부해야 할 주제/목표/공부방법" based on the material they attached, generate a standalone markdown file and save it to `~/Downloads/{YYYYMMDD-HHMMSS}.md` in addition to (or instead of) the Anki deck, depending on what the user asked for. This mode produces a Notion-uploadable study plan.

### Study Guide Output Rules

- Save the file to `~/Downloads/{YYYYMMDD-HHMMSS}.md` using the current timestamp. Tell the user the full path after writing.
- The file is meant for Notion upload, so:
  - Do NOT use markdown tables. Notion's markdown importer mangles them.
  - Use nested bullet lists (list depth) for every structured piece of information — vocabulary groups, activation patterns, schedules, etc.
  - Headings: one `#` for the title, `##` for top-level sections. Do not skip heading levels.
- Always include every Japanese term with both hiragana reading and Korean approximation in parentheses. Example: `高い(타카이, 비싸다)`, `学校(각코-, 학교)`.
  - Use `-` for long vowels (장음: `おお`, `おう`, `えい` → `오-`, `에-`).
  - Apply particle exceptions (`は`→와, `へ`→에, `を`→오) inside sentence examples.
- Required sections, in this order:
    1. `## 공부해야 할 주제` — what to study from the attached material. Break into sub-bullets: vocabulary (grouped by meaning pairs when possible), grammar patterns, exceptions, pronunciation points.
    2. `## 목표` — measurable goals. Break into 단기(this week) / 중기(2 weeks) / 장기(1 month) sub-bullets.
    3. `## 공부 방법` — concrete daily routine. Break into numbered 단계(steps) with time budget per step, plus a 주간 점검(weekly review) bullet.
    4. `## 피해야 할 함정` — common traps and anti-patterns specific to this material (e.g., `いい → よくありません` irregular).
- Keep bullets action-oriented and specific to the material the user provided. Do not write generic advice.
- Do not invent vocabulary or grammar that was not in the user's input — stay faithful to what the user attached.
- If the user already received an Anki deck in the same turn, reference the deck filename in the 공부 방법 section so the routine ties back to the cards.

## Guardrails

- Never produce cards whose reading is identical to the front. If the front is already all hiragana, repeat it in the `reading` field anyway — blank fields break the template.
- Never leave `meaning` empty. If you truly cannot determine a meaning, skip that card rather than ship a blank one.
- Do not merge multiple vocabulary items into one card to "save space." Each card must test exactly one thing.
- Never output the Japanese in romaji on the back. The learner is building hiragana fluency; romaji is a crutch. Korean 발음 (한글 approximation) is allowed and required — it is NOT romaji.
- Do not reorder or re-interpret the source. The user's image/PDF is the source of truth; your job is faithful extraction, not curation.
