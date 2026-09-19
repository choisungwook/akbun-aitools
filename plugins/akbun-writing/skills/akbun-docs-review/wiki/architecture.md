# Architecture

## Responsibility

Correct terminology (official spelling, one name per thing) and evidence-backed factual errors in existing Korean technical documents. Owns accuracy; sentence quality is delegated.

## Boundary

Preserve the document's intent, voice, layout, and code. Do not create or restructure sections, impose a writing style, or modify code, commands, settings, and paths. Report uncertain claims and errors that require code changes instead of guessing.

Spelling, spacing, typos, and mechanical prose belong to `akbun-writing-naturalize`, applied in its called mode (comparison baseline is this skill's corrected text; output overwrites the original file, no `-v1` copy). Do not duplicate those rules here. Evidence for a factual fix is one of: official doc URL, an actual run result, or a repository `file:line`.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Read the source → unify terminology and fix evidenced factual errors → apply `akbun-writing-naturalize` in called mode on the corrected text → overwrite the original file → report the term table, factual fixes, naturalize changes with rule ids, and `확인 필요` items. The report is the change record because overwriting leaves no diff.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- Related: `plugins/akbun-writing/skills/akbun-writing-naturalize/` rules and procedure are applied in called mode; this skill does not modify them.
