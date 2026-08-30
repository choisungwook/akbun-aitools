# Architecture

## Responsibility

Creates an image prompt and editable SVG in a free-layout monogray technical-poster style.

## Boundary

Fix the dark hand-ink, flat gray, off-white paper, and one orange accent, but let subject and composition follow the input.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Find the single message, choose a subject-appropriate composition, write the prompt, and create an SVG with editable text.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
