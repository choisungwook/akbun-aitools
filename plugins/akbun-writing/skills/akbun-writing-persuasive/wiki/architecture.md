# Architecture

## Responsibility

Writes an akbun technical post in a persuasive form that earns continued reading and supports acceptance of its conclusion.

## Boundary

Persuasion means honest reader retention plus a dense, supported answer; never invent experience or promise more than the article delivers.

Every base rule (voice, explanation mode, sentence layers, format, tokenops, naturalize finish, checklist) is inherited from `akbun-writing` by reference and not restated here. This `SKILL.md` holds only the two persuasion axes (read-to-the-end, acceptance) and wins on conflict. Acceptance adds three rules from pstack `technical-writing`: have a view, be specific over sterile, and label each claim as measured, cited, or inferred.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Define the reader's problem and supported promise, choose a truthful headline and hook, build evidence and trade-offs, anticipate the next objection, then close the argument.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- Related: `plugins/akbun-writing/skills/akbun-writing/SKILL.md` is the base; changing a base rule changes this skill's output.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
