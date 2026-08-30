# Architecture

## Responsibility

Creates an image prompt for a spiral-sketchbook concept card with a handwritten title, checklist, and framed pencil illustration.

## Boundary

Keep the physical sketchbook hierarchy and readable learning cues while choosing illustration content from the concept.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Reduce the topic to a title and short checklist, select the framed illustration, then describe the full sketchbook composition in the prompt.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
