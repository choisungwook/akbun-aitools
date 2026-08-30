# Architecture

## Responsibility

Turns a real experience into vertical 3:4 black-and-white documentary webtoon scenes with subtitle narration.

## Boundary

Preserve the truth of the supplied experience, use rough ink and faceless crowd silhouettes, and place narration as documentary subtitles rather than invented dialogue.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Identify factual beats, order them into documentary scenes, write restrained captions and compositions, then return one prompt per scene.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- [`design.md`](../design.md): supporting document retained outside the maintenance wiki.
- [`references/`](../references/): supporting resources retained outside the maintenance wiki.
