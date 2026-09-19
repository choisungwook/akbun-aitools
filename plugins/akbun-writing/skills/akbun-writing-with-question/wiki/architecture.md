# Architecture

## Responsibility

Writes an akbun study post in which a central question and linked section questions drive the explanation.

## Boundary

Questions are entrances to dense answers in the order definition, mechanism, exception, and judgment; they are not a fictional interview.

Every base rule (voice, explanation mode, sentence layers, format, tokenops, naturalize finish, checklist) is inherited from `akbun-writing` by reference and not restated here. This `SKILL.md` holds only the question axis and wins on conflict. A question-form heading is the one allowed exception to the base "headings carry the point" rule, provided the section's first sentence is the answer.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Choose the central why or what-if question, open sections with linked questions, answer each with technical depth, then return to and close the opening question.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- Related: `plugins/akbun-writing/skills/akbun-writing/SKILL.md` is the base; changing a base rule changes this skill's output.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
