# Architecture

## Responsibility

Creates an image prompt and editable SVG for a gray issue-card doodle using the akbun whale characters.

## Boundary

Keep the gray gradient, beige border, thin naive linework, olive accent, and mascot specification while changing the actual scene to fit the input.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Reduce the issue to one visual beat, map roles to whale characters, compose the card, then produce the prompt and editable-text SVG.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
