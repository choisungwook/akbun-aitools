# Architecture

## Responsibility

Turns technical notes and study material into a Korean akbun-style blog post for future self and working engineers.

## Boundary

Write only from supplied facts, organize around mechanism and practical judgment, and leave unsupported facts as `확인 필요` or further study rather than inventing them.

The post is one Diátaxis mode, explanation. Hands-on steps are a separated how-to section; drifting into reference tables or tool tutorials is a defect. Sentence rules are four layers adapted from pstack `technical-writing` (three top rules, Google developer style, STE one-instruction sentences, Global English disambiguation). The `tokenops` section name is referenced by `akbun-writing-easy` and `akbun-writing-persuasive`; keep it. The final pass applies `akbun-writing-naturalize` in called mode and overwrites the output file.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Extract the core mechanisms first, build the body around definition, operation, exception, and judgment, write a short promise-driven introduction, close with one practical point, run naturalize in called mode, then walk the nine-item checklist at the end of `SKILL.md`.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/structure-rhythms.md`](../references/structure-rhythms.md): paragraph rhythms and signpost headings, read before writing.
- Related: `plugins/akbun-writing/skills/akbun-writing-naturalize/` rules are applied in called mode; this skill does not modify them.
- Variants: `akbun-writing-with-question` and `akbun-writing-persuasive` inherit every rule here by reference and add one axis each; `akbun-writing-easy` reuses the `tokenops` rule. A base change changes their output.
- Related: `plugins/akbun-writing/agents/akbun-style-reviewer.md reviews drafts against `SKILL.md` and defers to it on conflict.
