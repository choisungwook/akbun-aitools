# Architecture

## Responsibility

Creates one hand-drawn marker illustration prompt per scene for presentations, posts, or video stories.

## Boundary

Each cream-paper scene communicates one message with dark ink contours and restrained marker fills; do not compress multiple story beats into one image.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Split the source into visual beats, define one message and composition per beat, maintain character and style continuity, then return ordered prompts.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
