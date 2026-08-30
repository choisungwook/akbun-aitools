# Architecture

## Responsibility

Generates Korean headline candidates from supplied notes, drafts, files, code, or a topic.

## Boundary

Promise only what the source actually supports and vary the editorial angle without using empty exaggeration or clickbait.

The skill wiki records maintenance context. [SKILL.md](../SKILL.md) remains the executable instruction source and must not depend on an agent loading this wiki during an ordinary user request.

## Flow

Identify subject, reader, practical tension, and supported payoff, generate distinct headline angles, then rank or explain the strongest candidates.

## Resources

- [`SKILL.md`](../SKILL.md): invocation boundary and runtime instructions.
- This skill is instruction-only; `SKILL.md` contains its complete runtime behavior.
