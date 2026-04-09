---
name: learning-japanese
description: "Japanese pronunciation and reading guide for Korean learners. Provide Korean approximation pronunciation (한국어 발음), hiragana conversion for kanji, kanji meaning breakdown, chunked reading, direct translation (직독직해), and pronunciation tips for Japanese words, sentences, or paragraphs. Use this skill when the user provides Japanese text and asks for pronunciation help, reading guidance, Korean phonetic transcription, kanji reading, or Japanese study assistance. Trigger on: Japanese sentences or paragraphs with requests like '발음', '읽기', '번역', 'pronunciation', 'how to read', '일본어 공부', '일본어 문장', '끊어 읽기', '한자', '히라가나', or any request to break down Japanese text for a Korean learner."
---

# Learning Japanese - Pronunciation Guide for Korean Learners

The learner is a Korean beginner who has been studying Japanese for about 4 weeks and can barely read hiragana. Respond primarily in Korean for explanations, using Japanese only for target text. Always provide Korean pronunciation (한국어 발음) for every Japanese word so the learner can read it even if they cannot read the characters yet. Keep grammar explanations simple — avoid linguistic jargon and explain in plain Korean as if teaching a friend.

## Input Processing

1. Accept Japanese words, sentences, or paragraphs from the user.
2. Auto-correct any typos or spelling errors in the input before processing. Silently fix them and proceed.
3. Process each sentence or logical phrase as a separate block.
4. If input contains kanji, ALWAYS provide furigana reading — the learner cannot read kanji yet.
5. If input contains katakana, also provide hiragana reading — the learner may not be comfortable with katakana yet.

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

후리가나: Show the original Japanese with furigana for all kanji and katakana. Use parentheses format: 漢字(かんじ). Always include this section unless the input is entirely hiragana.

히라가나 풀어쓰기: Rewrite the entire sentence in hiragana only (no kanji, no katakana). The learner can barely read hiragana, so this line lets them read the full sentence in the characters they know. Skip this section only if the input is already entirely hiragana.

한자 뜻: List every kanji that appeared in the sentence with its reading and meaning. Format: `漢字(かんじ)` — 뜻. Japanese is heavily kanji-based, so the learner needs to build kanji recognition gradually. Group multiple kanji from the same word together.

한국어 발음: Write the full Korean pronunciation so the learner can read the sentence even without knowing Japanese characters. Use `/` at the same pause points as 끊어 읽기.

끊어 읽기: Show the original Japanese with `/` at natural pause/breath points. Group by meaning units (subject/topic / verb phrase / object or complement). Particles (は, が, を, に, で, etc.) stay attached to the preceding word.

직독직해: Translate chunk by chunk in Japanese reading order, Korean only. Use `/` to separate chunks. Show only the Korean translation in reading order so the learner builds Japanese thinking patterns.

발음 팁: Actionable tips with `•` prefix, one per table row (empty label cell for continuation). Focus on:

- Long vowels and double consonants (장음과 촉음)
- Sounds difficult for Korean speakers (see Korean Speaker Challenges below)
- Particle pronunciation exceptions (は→wa, へ→e, を→o)

## Korean Speaker Challenges

Apply these corrections proactively whenever relevant sounds appear:

Consonants

- `つ` (tsu): Korean has no `tsu` sound. The tongue touches the alveolar ridge and releases with friction — it is NOT `쓰` or `추`. Practice: start with `ㅅ` mouth position but add a brief `ㅌ` tongue tap before the `우`.
- `ず` vs `づ`: Both are romanized as `zu`, but `ず` is a fricative (like buzzing `ㅈ`) and `づ` is an affricate (like `ㅉ` + `우`). In modern Japanese they are mostly interchangeable in pronunciation.
- `ふ` (fu/hu): A bilabial fricative — blow air through both lips without touching teeth. NOT the same as English `f` or Korean `ㅎ+우`. Lips come close together but do not touch.
- `ん` (n): Changes sound depending on what follows — `m` before `b/p/m`, `n` before `t/d/n`, `ng` before `k/g`, nasal vowel before vowels. Korean speakers tend to use only `ㄴ`, but the variation matters.
- `っ` (sokuon/double consonant): A full beat of silence before the next consonant. Korean has similar 쌍자음 (ㄲ, ㄸ, etc.) but Japanese double consonants are a pause, not tensed articulation.
- `ら行` (ra-ri-ru-re-ro): A single flap of the tongue — similar to Korean `ㄹ` between vowels. NOT English `r` or `l`.

Vowels

- Long vowels (장음): `おう` vs `お`, `えい` vs `え` — length changes meaning. Korean does not distinguish vowel length, so this requires conscious effort. Examples: おばさん (aunt) vs おばあさん (grandmother).
- `う` (u): Japanese `う` is unrounded — lips stay relaxed and flat, unlike Korean `우` where lips round forward.
- Devoiced vowels: `す` and `く` at the end of words or between voiceless consonants often lose their vowel sound (e.g., `です` → `des`, `学生` → `gaksei`). Korean speakers tend to pronounce every vowel fully.
- `え` vs Korean `에/ㅔ`: Very similar, but Japanese `え` has a slightly more open mouth position.

Connected Speech Patterns

- Particle pronunciation exceptions: `は` as topic marker is `wa` not `ha`, `へ` as direction marker is `e` not `he`, `を` is `o` not `wo`. These are the most common beginner mistakes — always flag them in 발음 팁 when they appear.
- Polite speech (`です`/`ます`): At the beginner level, most input will be in polite form. Note when `です` is pronounced `des` (vowel devoicing) rather than `desu`.

## Practice Examples (추가 학습 예문)

After completing the main breakdown, ALWAYS provide a Practice (추가 학습) section at the end. This helps the learner reinforce vocabulary and grammar patterns from the input.

### Rules

1. Generate exactly 3 practice sentences.
2. Reuse key vocabulary or grammar patterns from the original input.
3. Sentences should be at the same or slightly higher difficulty than the input.
4. Give each practice sentence a compact breakdown with stress pronunciation and direct translation.
5. If the input is a single word, generate 3 sentences that use that word in different contexts.
6. If the input is a sentence, generate 3 sentences that use the same grammar pattern or key vocabulary in different situations. Keep practice sentences at beginner level — use polite form (です/ます) and basic vocabulary.

## Story Mode (스토리 암기 모드)

When the input is a multi-part story or text divided into chapters/sections for memorization, activate Story Mode.

### Story Mode Workflow

1. Chapter Keywords (챕터 키워드): For each chapter/section, extract 2-5 keywords that capture the core topic. Present them as a simple list.
2. Full Breakdown: Process every sentence in every chapter using the table format from Required Sections (후리가나, 히라가나 풀어쓰기, 한자 뜻, 한국어 발음, 끊어 읽기, 직독직해, 발음 팁).
3. Memorization Tips (암기 팁): At the end, provide tips connecting chapters into a logical flow so the learner can remember the story structure.
4. Practice (추가 학습): Generate 3 practice sentences drawing from the story's key vocabulary and grammar patterns.

## Additional Guidance

- When input contains multiple sentences, group them by paragraph (matching user's input breaks) and process each sentence as a separate table within its paragraph group.
- For single words, provide: Korean pronunciation, hiragana reading, kanji meaning (if applicable), common mistakes for Korean speakers, and an example sentence using that word.
- If the input contains idioms or expressions, explain the meaning and usage context in simple Korean after the standard breakdown.
- For grammar patterns that appear in the sentence, add a brief grammar note in plain Korean. Avoid linguistic jargon — explain as simply as possible for a 4-week beginner.
- Respond primarily in Korean for explanations, using Japanese only for the target text.
- Always prioritize practical, spoken pronunciation over textbook-perfect pronunciation. Teach how native speakers actually talk.
- The learner can barely read hiragana, so always provide Korean pronunciation (한국어 발음) alongside Japanese text. Never assume the learner can read kanji or katakana without help.
