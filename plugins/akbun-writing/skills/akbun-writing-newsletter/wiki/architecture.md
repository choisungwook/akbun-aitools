# Architecture

## Responsibility

Writes an akbun newsletter issue from the user's weekly agent-work log and news candidates, in the fixed order hook header, quantified story, curation.

## Boundary

Paywall, membership benefits, CTA, social proof, and unsubscribe footer are owned by the publishing tool, not this skill, even when the user asks for them. Every number (time, cost, count, number of candidates) must come from the input; missing numbers are reported as `확인 필요`, never invented.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Collect the three inputs (work log with numbers, news candidates with links, reader), pick a title from a real quote or number in the log, write the pain point and agent task list with quantified results, then write the curation section with the candidate-to-pick count and one summary/why-now/source card per item, and close with the `확인 필요` list.

## Terminology

- Module: one of the three fixed sections (header, intro, curation).
- Card: a three-line news entry (summary, why-now, source).
- Why-now: the author's one-sentence reason the reader should see the item now; a card without it is dropped.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`references/newsletter-layout.md`](../references/newsletter-layout.md): annotated module templates and a short example.
