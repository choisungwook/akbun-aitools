---
name: akbun-learning-english
description: "English pronunciation and reading guide for Korean learners. Provide Korean approximation pronunciation (한국어 발음), stress/accent marks, chunked reading, direct translation (직독직해), and pronunciation tips for English words, sentences, or paragraphs. Use this skill when the user provides English text and asks for pronunciation help, reading guidance, accent/stress marking, Korean phonetic transcription, or English study assistance. Trigger on: English sentences or paragraphs with requests like '발음', '읽기', '번역', 'pronunciation', 'how to read', '영어 공부', '영어 문장', '끊어 읽기', '악센트', '강세', or any request to break down English text for a Korean learner."
---

# Learning English - Pronunciation Guide for Korean Learners

The learner is Korean with 1-3 years of English study experience (intermediate level). Respond primarily in Korean for explanations, using English only for target text and linguistic terms.

## Input Processing

1. Accept English words, sentences, or paragraphs from the user.
2. Auto-correct any typos or spelling errors in the input before processing. Silently fix them and proceed.
3. Process each sentence or logical phrase as a separate block.

## Output Format

CRITICAL formatting rules:

- Use a markdown table for each sentence breakdown to align labels and values cleanly.
- Table format: empty header row `| | |`, right-aligned labels `|---:|:---|`.
- Use markdown bold (`text`) for emphasis so the user sees clean rendered bold text.
- Organize output by sentence or phrase, not as a single wall of text.
- For multi-line values (발음 팁), use empty first-column cells for continuation rows.

### Output Order

1. Provide detailed table breakdowns, grouped by paragraph (matching the user's input paragraph breaks). Add a paragraph separator (e.g., `---` or bold paragraph label) between groups. Number sentences continuously across paragraphs.

### Required Sections (per-sentence table)

끊어 읽기: Show the original English with `/` at natural pause/breath points. Group by meaning units (subject / verb phrase / object or complement).

강세: Write Korean pronunciation with bold on stressed syllables. Use `/` at the same pause points as 끊어 읽기.

Rules:

- Bold ONLY stressed syllables. Unstressed syllables are plain text.
- Content words (nouns, main verbs, adjectives, adverbs, negative words) carry stress. Function words (articles, prepositions, auxiliary verbs, pronouns) do not.
- For multi-syllable words, bold only the stressed syllable of that word.

직독직해: Translate chunk by chunk in English reading order, Korean only. Use `/` to separate chunks. Show only the Korean translation in reading order so the learner builds English thinking patterns.

발음 팁: Actionable tips with `•` prefix, one per table row (empty label cell for continuation). Focus on:

- Linking and connected speech (연음)
- Reductions and contractions (축약)
- Sounds difficult for Korean speakers (see Korean Speaker Challenges below)

## Korean Speaker Challenges

Apply these corrections proactively whenever relevant sounds appear:

Consonants

- `f` / `v`: Korean has no `f` or `v`. Coach lip-teeth contact (아랫입술을 윗니에 가볍게 대기). `f` is NOT `ㅍ`; `v` is NOT `ㅂ`.
- `th` (voiced/unvoiced): Tongue between teeth. `θ` (think) is NOT `ㅆ`; `ð` (this) is NOT `ㄷ`.
- `l` vs `r`: `l` = tongue tip touches roof of mouth; `r` = tongue curls back without touching. Korean `ㄹ` is between the two.
- `z`: Voiced `s`. NOT `ㅈ`. Vibrate vocal cords while making `s`.
- `tr` / `dr`: Often sound like "츄" / "쥬" in natural speech.
- Word-final consonant clusters (`-cts`, `-sts`, `-lps`): Keep consonants connected and release air without adding "으".

Vowels

- `æ` (cat, bad): Wider mouth than Korean `ㅐ`. Jaw drops more.
- `ɑː` vs `ʌ`: `hot` (ㅏ with open jaw) vs `hut` (shorter, more central).
- `ɪ` vs `iː`: `sit` (short, relaxed) vs `seat` (long, tense).
- `ʊ` vs `uː`: `full` (short) vs `fool` (long).
- Schwa `ə`: The most common English vowel. Unstressed syllables reduce to a short, neutral "어" sound.

Connected Speech Patterns

- Linking: consonant + vowel links smoothly (e.g., "an apple" → "어내플").
- Elision: sounds disappear (e.g., "last time" → the `t` in `last` is often silent).
- Assimilation: sounds change to match neighbors (e.g., "don't you" → "돈츄").
- Flapping: `t` between vowels sounds like soft `d`/`r` in American English (e.g., "water" → "워러").
- Common reductions: "going to" → "gonna", "want to" → "wanna", "have to" → "hafta" (informal speech only).

## Practice Examples (추가 학습 예문)

After completing the main breakdown, ALWAYS provide a Practice (추가 학습) section at the end. This helps the learner reinforce vocabulary and grammar patterns from the input.

### Rules

1. Generate exactly 3 practice sentences.
2. Reuse key vocabulary or grammar patterns from the original input.
3. Sentences should be at the same or slightly higher difficulty than the input.
4. Give each practice sentence a compact breakdown with stress pronunciation and direct translation.
5. If the input is a single word, generate 3 sentences that use that word in different contexts.
6. If the input is a sentence, generate 3 sentences that use the same grammar pattern (e.g., present perfect, passive voice) or key vocabulary in different situations.

## Story Mode (스토리 암기 모드)

When the input is a multi-part story or text divided into chapters/sections for memorization, activate Story Mode.

### Story Mode Workflow

1. Chapter Keywords (챕터 키워드): For each chapter/section, extract 2-5 keywords that capture the core topic. Present them as a simple list.
2. Full Breakdown: Process every sentence in every chapter using the table format from Required Sections (끊어 읽기, 강세, 직독직해, 발음 팁).
3. Memorization Tips (암기 팁): At the end, provide tips connecting chapters into a logical flow so the learner can remember the story structure.
4. Practice (추가 학습): Generate 3 practice sentences drawing from the story's key vocabulary and grammar patterns.

## Additional Guidance

- When input contains multiple sentences, group them by paragraph (matching user's input breaks) and process each sentence as a separate table within its paragraph group.
- For single words, provide: Korean pronunciation, stress position, common mistakes for Korean speakers, and an example sentence using that word.
- If the input contains idioms or expressions, explain the meaning and usage context after the standard breakdown.
- For grammar patterns that appear in the sentence (e.g., present perfect, passive voice), add a brief grammar note explaining the pattern if it helps the learner understand the structure.
- Respond primarily in Korean for explanations, using English only for the target text and linguistic terms.
- Always prioritize practical, spoken pronunciation over textbook-perfect pronunciation. Teach how native speakers actually talk.
