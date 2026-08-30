# Architecture

## Responsibility

Creates an image prompt and editable SVG for a one-page cream handwritten explainer card.

## Boundary

Use a cream paper, bold handwritten hierarchy, simple causal doodles, and exactly one royal-blue hatched accent while adapting the diagram to the subject.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Extract one teachable concept, arrange headline, causal copy, and doodle diagram, then produce the image prompt and editable-text SVG.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
