# Architecture

## Responsibility

Writes an akbun technical post in a persuasive form that earns continued reading and supports acceptance of its conclusion.

## Boundary

Persuasion means honest reader retention plus a dense, supported answer; never invent experience or promise more than the article delivers.

Every base rule (voice, explanation mode, sentence layers, format, tokenops, naturalize finish, checklist) is inherited from `akbun-writing` by reference and not restated here. This `SKILL.md` holds only the two persuasion axes (read-to-the-end, acceptance) and wins on conflict. Acceptance adds three rules from pstack `technical-writing`: have a view, be specific over sterile, and label each claim as measured, cited, or inferred.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Choose a truthful symptom/why/trade-off headline, hook with one unexpected point, narrate history and why before mechanics top-down, pre-empt the reader's objection, then close the hook with recommendation, trade-offs, and labeled evidence. The skill has no supporting references; the rules fit in `SKILL.md`.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- Related: `plugins/akbun-writing/skills/akbun-writing/SKILL.md` is the base; changing a base rule changes this skill's output.
