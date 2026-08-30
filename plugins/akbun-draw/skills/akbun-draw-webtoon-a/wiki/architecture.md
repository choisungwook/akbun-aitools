# Architecture

## Responsibility

Turns a topic or situation into a three- or four-panel black-and-white stick-figure webtoon image prompt.

## Boundary

Keep the xkcd-like minimal line language and make each panel advance the story rather than repeat the same beat.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Find the setup, escalation, turn, and ending, map them to three or four panels, then write one coherent page prompt.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
