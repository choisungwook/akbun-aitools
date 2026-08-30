# Architecture

## Responsibility

Creates an image prompt for stitched text on linen with one yellow highlighter emphasis.

## Boundary

Treat the lettering as embroidery with tactile thread and fabric detail, and limit the yellow mark to the phrase that carries the message.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Choose the phrase hierarchy, identify the highlighted words, then specify linen, stitch, spacing, and lighting in the final prompt.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
